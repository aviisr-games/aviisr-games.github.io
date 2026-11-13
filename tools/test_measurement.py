#!/usr/bin/env python3
"""Measurement events: only allowed cookieless event prefixes, never on Mila, playables wired."""

from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parent.parent
ALLOWED = {'store_click', 'qr_land', 'yt_land', 'card_click', 'play_start', 'play_complete', 'lang', 'contact_click'}
PLAYABLES = {
    'ninely/play/index.html': True,
    'middle-east-2030/briefing/index.html': True,
    'baylight/dock/index.html': True,
}


def read(rel):
    return (ROOT / rel).read_text(encoding='utf-8')


def repo_files(suffixes):
    return [p for p in ROOT.rglob('*') if p.suffix in suffixes and p.is_file()
            and '.git' not in p.relative_to(ROOT).parts]


class MeasurementTests(unittest.TestCase):

    def test_event_names_use_allowed_prefixes(self):
        names = []
        for p in repo_files({'.html', '.js'}):
            if p.relative_to(ROOT).parts[0] == 'mila':
                continue
            names += re.findall(r"aviisrCount\(\s*'([^']*)'", p.read_text(encoding='utf-8', errors='replace'))
        names += re.findall(r"(?:count|send)\(\s*'([a-z_]+)/", read('assets/count.js'))
        names += re.findall(r"send\(\s*'([a-z_]+)/", read('assets/count.js'))
        self.assertTrue(names)
        for n in names:
            self.assertIn(n.split('/')[0], ALLOWED, n)

    def test_mila_never_references_counter(self):
        for p in repo_files({'.html', '.js', '.json'}):
            if p.relative_to(ROOT).parts[0] != 'mila':
                continue
            text = p.read_text(encoding='utf-8', errors='replace')
            self.assertNotIn('aviisrCount', text, p)
            self.assertNotIn('count.js', text, p)

    def test_counter_guards_remain(self):
        js = read('assets/count.js')
        self.assertIn(r"/^\/mila(\/|$)/.test(location.pathname)", js)
        self.assertIn("navigator.doNotTrack === '1'", js)
        self.assertIn('navigator.globalPrivacyControl === true', js)
        self.assertIn(r"/^[a-z_]+(\/[A-Za-z0-9_-][A-Za-z0-9_.-]*){1,3}$/", js)
        card = js[js.index('card_click/<game>'):]
        self.assertRegex(card, r"/\^\\/mila\(\\/\|\$\)/\.test\(path\)")

    def test_youtube_landing_uses_src_yt(self):
        js = read('assets/count.js')
        self.assertIn(r"src=yt(&|$)", js)
        self.assertIn("send('yt_land' + location.pathname, true)", js)

    def test_i18n_lang_event_is_validated(self):
        js = read('assets/i18n.js')
        self.assertIn("supported.indexOf(this.value) !== -1 && window.aviisrCount", js)
        self.assertIn("window.aviisrCount('lang/' + this.value)", js)

    def test_playables_call_counter_defensively(self):
        for rel, has_end in PLAYABLES.items():
            text = read(rel)
            self.assertIn('/assets/count.js', text, rel)
            self.assertRegex(text, r"window\.aviisrCount[^\n]*\n?[^\n]*aviisrCount\('play_start/", rel)
            self.assertNotRegex(text, r"(?<!window\.)(?<![\w.])aviisrCount\(", rel)  # always via window.
            if has_end:
                self.assertRegex(text, r"window\.aviisrCount\([^)]*'play_complete/", rel)
            else:
                self.assertNotIn('play_complete', text, rel)

    def test_briefing_ending_code_is_validated(self):
        text = read('middle-east-2030/briefing/index.html')
        self.assertIn(r"/^[A-Z0-9_]{1,16}$/.test(pathCode)", text)


if __name__ == '__main__':
    unittest.main()
