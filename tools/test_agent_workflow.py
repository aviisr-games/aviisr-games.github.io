#!/usr/bin/env python3
"""Regression checks for bootstrap, registration and routing enforcement."""
import json
from pathlib import Path
import tempfile
import unittest
import agent_workflow as workflow

class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)/'new'
        workflow.bootstrap(workflow.ROOT,self.root,'Test','web')
        (self.root/'.agent/context.md').write_text('# Test\nRun project tests; source is src/.\n')

    def tearDown(self): self.tmp.cleanup()

    def test_bootstrap_valid_and_no_overwrite(self):
        self.assertEqual(workflow.check(self.root),[])
        with self.assertRaises(ValueError): workflow.bootstrap(workflow.ROOT,self.root,'Again','web')

    def test_new_app_must_register_and_finish_context(self):
        app=self.root/'apps/demo'; app.mkdir(parents=True)
        (app/'package.json').write_text('{}')
        self.assertTrue(any('Unregistered' in e for e in workflow.check(self.root)))
        workflow.scaffold(self.root,'apps/demo','Demo','web')
        self.assertTrue(any('Complete app context' in e for e in workflow.check(self.root)))
        (app/'.agent/context.md').write_text('# Demo\nSource and test command verified.\n')
        self.assertEqual(workflow.check(self.root),[])
        with self.assertRaises(ValueError): workflow.scaffold(self.root,'apps/demo','Demo','web')

    def test_path_escape_and_existing_guidance(self):
        for path in ('../escape','/tmp/escape','x/../../escape'):
            with self.assertRaises(ValueError): workflow.scaffold(self.root,path,'Bad','web')
        outside=Path(self.tmp.name)/'outside'; outside.mkdir()
        (self.root/'link').symlink_to(outside,target_is_directory=True)
        with self.assertRaises(ValueError): workflow.scaffold(self.root,'link/child','Bad','web')
        child=self.root/'existing'; child.mkdir(); (child/'AGENTS.md').write_text('keep')
        with self.assertRaises(ValueError): workflow.scaffold(self.root,'existing','Existing','other')
        self.assertEqual((child/'AGENTS.md').read_text(),'keep')

    def test_routing_drift_fails(self):
        path=self.root/'.codex/config.toml'
        path.write_text(path.read_text().replace('gpt-6-luna','gpt-6.1-sol'))
        self.assertTrue(any('Default worker' in e for e in workflow.check(self.root)))

    def test_discovery_excludes_vendors_not_new_apps(self):
        self.assertEqual(workflow.discover(['ProjectSettings/ProjectVersion.txt','apps/a/package.json',
          'node_modules/pkg/package.json','Assets/SDK/package.json','Packages/pkg/package.json',
          'apps/game/ProjectSettings/ProjectVersion.txt']),{'.','apps/a','apps/game'})

if __name__=='__main__': unittest.main()
