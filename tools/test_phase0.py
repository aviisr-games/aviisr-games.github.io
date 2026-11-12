#!/usr/bin/env python3
"""Phase 0: player-facing copy on the two browser-playable pages must not say 'prototype'."""

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent.parent


class Phase0Tests(unittest.TestCase):

    def test_browser_pages_have_no_prototype_wording(self):
        for rel in ['baylight/dock/index.html', 'morning-route/preview/index.html']:
            text = (ROOT / rel).read_text(encoding='utf-8').lower()
            self.assertNotIn('prototype', text, rel)
            self.assertNotIn('development notice', text, rel)

    def test_root_favicon_files_exist(self):
        self.assertTrue((ROOT / 'favicon.ico').is_file())
        self.assertTrue((ROOT / 'apple-touch-icon.png').is_file())


if __name__ == '__main__':
    unittest.main()
