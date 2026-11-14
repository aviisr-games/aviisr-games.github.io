#!/usr/bin/env python3
"""Generate sitemap.xml from the studio allowlist.

Only studio pages and pages of allowlisted apps are listed. A page whose canonical
points at another URL is skipped (the canonical target is listed instead).

Usage: python3 tools/build_sitemap.py          # rewrite sitemap.xml
       python3 tools/build_sitemap.py --check  # exit 1 if sitemap.xml is stale
"""

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
BASE = 'https://aviisrgames.com/'

# Allowlisted apps: (display name, folders). The order is the order on the homepage.
ALLOWLIST = [
    ('Ninely: Sudoku & Logic Puzzle', ['ninely']),
    ('Middle East 2030: Politics Sim', ['middle-east-2030', 'redline-2030']),
    ('Baylight: Truck Sort Puzzle', ['baylight']),
    ('Morning Paper Route: Bike Game', ['paper-route', 'morning-route']),
    ('מילה · Mila', ['mila']),
]
STUDIO_PAGES = ['index.html', 'support/index.html', 'privacy/index.html']
# Apps with a privacy page but not yet on the homepage (unreleased): allowed, not listed as cards.
UNRELEASED_DIRS = ['beamwise']
ALLOWED_PREFIXES = [d for _, dirs in ALLOWLIST for d in dirs] + UNRELEASED_DIRS


def url_for(rel):
    rel = rel.replace('\\', '/')
    if rel == 'index.html':
        return BASE
    if rel.endswith('/index.html'):
        return BASE + rel[:-len('index.html')]
    return BASE + rel


def canonical_of(path):
    m = re.search(r'<link rel="canonical" href="([^"]+)"', path.read_text(encoding='utf-8'))
    return m.group(1) if m else None


def pages():
    rels = list(STUDIO_PAGES)
    for d in ALLOWED_PREFIXES:
        files = sorted((ROOT / d).rglob('*.html'), key=lambda p: (p.name != 'index.html' or p.parent != ROOT / d, str(p)))
        rels.extend(str(p.relative_to(ROOT)) for p in files)
    urls = []
    for rel in rels:
        path = ROOT / rel
        if not path.exists():
            continue
        text = path.read_text(encoding='utf-8')
        if 'name="robots" content="noindex' in text:
            continue
        url = url_for(rel)
        canon = canonical_of(path)
        if canon and canon != url:
            continue
        if url not in urls:
            urls.append(url)
    return urls


def render():
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    lines += [f'  <url><loc>{u}</loc></url>' for u in pages()]
    lines.append('</urlset>')
    return '\n'.join(lines) + '\n'


def main():
    out = render()
    target = ROOT / 'sitemap.xml'
    if '--check' in sys.argv:
        if target.read_text(encoding='utf-8') != out:
            print('sitemap.xml is stale: run python3 tools/build_sitemap.py')
            return 1
        print('sitemap.xml is up to date')
        return 0
    target.write_text(out, encoding='utf-8')
    print(f'Wrote {out.count("<loc>")} URLs to sitemap.xml')
    return 0


if __name__ == '__main__':
    sys.exit(main())
