#!/usr/bin/env python3
"""Portable agent-workflow checks and non-destructive scaffolding. Python >=3.11."""
import argparse
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]
KINDS = ('unity', 'web', 'dotnet', 'static', 'other')
EXCLUDED = {'.git', 'node_modules', 'vendor', 'Library', 'Temp', 'Obj', 'Builds',
            'build', 'dist', 'Pods', 'Packages', 'ThirdParty', 'Monetization~'}

def safe_path(root, value):
    p = PurePosixPath(value)
    if not value or p.is_absolute() or '..' in p.parts or '\\' in value:
        raise ValueError('Expected a repository-relative path without traversal')
    target = root.joinpath(*p.parts)
    if not target.resolve().is_relative_to(root.resolve()):
        raise ValueError('Path escapes repository through a symlink')
    return target

def file_list(root):
    try:
        actual = subprocess.check_output(['git', '-C', str(root), 'rev-parse', '--show-toplevel'], stderr=subprocess.DEVNULL, text=True).strip()
        if Path(actual).resolve() == root.resolve():
            return subprocess.check_output(['git', '-C', str(root), 'ls-files', '--cached', '--others', '--exclude-standard', '-z']).decode().split('\0')
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    result=[]
    for parent, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in EXCLUDED]
        result.extend((Path(parent)/f).relative_to(root).as_posix() for f in files)
    return result

def discover(paths):
    roots=set()
    for value in paths:
        p=PurePosixPath(value)
        if not value or set(p.parts) & EXCLUDED:
            continue
        if p.name == 'ProjectVersion.txt' and p.parent.name == 'ProjectSettings':
            roots.add(p.parent.parent.as_posix())
        elif p.name in ('package.json','pubspec.yaml','pyproject.toml','Cargo.toml'):
            # Unity asset packages are dependencies, not independently maintained apps.
            if 'Assets' not in p.parts:
                roots.add(p.parent.as_posix())
    return roots

def check(root, paths=None):
    errors=[]
    def require(condition, message):
        if not condition: errors.append(message)
    try:
        registry=json.loads((root/'.agent/apps.json').read_text())
        toolkit=json.loads((root/'.agent/toolkit.json').read_text())
        require(registry['version']==1 and toolkit['version']==1, 'Unsupported standard version')
        for path in toolkit['files']:
            require(safe_path(root,path).is_file(), f'Missing toolkit file: {path}')
        config=tomllib.loads((root/'.codex/config.toml').read_text())
        require(config.get('model')=='gpt-6.1-sol', 'Primary model must be gpt-6.1-sol')
        settings=config['agents']
        require(settings.get('enabled') is True, 'Subagents must be enabled')
        require(settings.get('max_concurrent_threads_per_session')==3, 'Worker cap must be 3')
        require(settings.get('default_subagent_model')=='gpt-6-luna', 'Default worker must be Luna')
        require(settings.get('default_subagent_reasoning_effort')=='low', 'Default worker effort must be low')
        for role, effort in [('workhorse','low'),('flow-checker','medium')]:
            agent=tomllib.loads((root/f'.codex/agents/{role}.toml').read_text())
            require(agent.get('name')==role and bool(agent.get('description')),f'Invalid Codex role: {role}')
            require(agent.get('model')=='gpt-6-luna' and agent.get('model_reasoning_effort')==effort,f'Incorrect routing: {role}')
            require(bool(agent.get('developer_instructions')),f'Missing prompt: {role}')
            text=(root/f'.claude/agents/{role}.md').read_text()
            require(text.startswith('---\n') and '\n---\n' in text[4:],f'Malformed Claude agent: {role}')
            front=text.split('---',2)[1]
            require(f'name: {role}' in front and 'model: haiku' in front and 'description:' in front,f'Incorrect Claude routing: {role}')
        require(json.loads((root/'.claude/settings.json').read_text()).get('model')=='opus','Claude primary must be opus')
        require('aviisr-agent-workflow:v1' in (root/'AGENTS.md').read_text(),'Missing root execution standard')
        require('@AGENTS.md' in (root/'CLAUDE.md').read_text(),'Claude must import root guidance')
        require((root/'.agent/context.md').is_file(),'Missing root context')
        app_paths=set()
        for app in registry['apps']:
            path=app['path']; safe_path(root,path)
            require(path not in app_paths,f'Duplicate app: {path}'); app_paths.add(path)
            require(app['kind'] in KINDS,f'Unknown app kind: {path}')
            context=safe_path(root,app['context'])
            require(context.is_file(),f'Missing app context: {path}')
            if context.is_file():
                require('UNCONFIGURED' not in context.read_text(),f'Complete app context: {path}')
            require((safe_path(root,path)/'AGENTS.md').is_file(),f'Missing local instructions: {path}')
        require(bool(app_paths),'Register at least one app')
        ignored=registry.get('ignored_app_roots',{})
        for path, reason in ignored.items():
            safe_path(root,path)
            require(bool(reason.strip()),f'Ignored root requires a reason: {path}')
        for found in discover(file_list(root) if paths is None else paths):
            # A .NET engine may expose a Unity package inside its registered component.
            covered=found in app_paths or found in ignored or any(a['kind']=='dotnet' and found.startswith(a['path']+'/') for a in registry['apps'])
            require(covered,f'Unregistered app manifest: {found}; run scaffold')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append(str(exc))
    return errors

def render_context(root, name):
    return (root/'.agent/templates/context.md').read_text().replace('{{name}}',name)

def scaffold(root, path, name, kind):
    target=safe_path(root,path)
    if path=='.': raise ValueError('Use bootstrap for a new root; scaffold needs a child directory')
    registry=json.loads((root/'.agent/apps.json').read_text())
    relative=target.relative_to(root).as_posix()
    if any(a['path']==relative for a in registry['apps']): raise ValueError('App already registered')
    files={target/'AGENTS.md':f'# {name}\n\nInherit repository-root AGENTS.md. Read local `.agent/context.md` before work.\n',
           target/'CLAUDE.md':'@AGENTS.md\n@.agent/context.md\n',
           target/'.agent/context.md':render_context(root,name)}
    if any(p.exists() for p in files): raise ValueError('Refusing to overwrite existing app guidance')
    for p in files: safe_path(root,p.relative_to(root).as_posix())
    for p,text in files.items(): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(text)
    registry['apps'].append({'path':relative,'kind':kind,'context':relative+'/.agent/context.md'})
    (root/'.agent/apps.json').write_text(json.dumps(registry,indent=2)+'\n')

def bootstrap(root,target,name,kind):
    target=target.resolve()
    if target.exists() and any(target.iterdir()): raise ValueError('Bootstrap requires an empty target; existing repositories need an audited migration')
    toolkit=json.loads((root/'.agent/toolkit.json').read_text())
    files={p:safe_path(root,p).read_text() for p in toolkit['files']}
    files.update({'AGENTS.md':(root/'.agent/templates/AGENTS.md').read_text().replace('{{name}}',name),
                  'CLAUDE.md':'@AGENTS.md\n@.agent/context.md\n',
                  '.agent/context.md':render_context(root,name),
                  '.agent/apps.json':json.dumps({'version':1,'apps':[{'path':'.','kind':kind,'context':'.agent/context.md'}]},indent=2)+'\n'})
    for p,text in files.items():
        dest=safe_path(target,p); dest.parent.mkdir(parents=True,exist_ok=True); dest.write_text(text)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    sub.add_parser('check')
    for command in ('scaffold','bootstrap'):
        child=sub.add_parser(command); child.add_argument('path'); child.add_argument('--name',required=True); child.add_argument('--kind',choices=KINDS,required=True)
    args=parser.parse_args()
    try:
        if args.command=='check':
            errors=check(ROOT)
            for error in errors: print('FAIL:',error)
            if errors: return 1
            print('Agent workflow structure and app registration passed (not an app runtime test).')
        elif args.command=='scaffold': scaffold(ROOT,args.path,args.name,args.kind)
        else: bootstrap(ROOT,Path(args.path),args.name,args.kind)
        if args.command!='check': print('Created guidance. Complete UNCONFIGURED context before CI can pass.')
    except (OSError,ValueError,KeyError) as exc:
        print('ERROR:',exc,file=sys.stderr); return 1
    return 0

if __name__=='__main__': sys.exit(main())
