#!/usr/bin/env python3
"""R2 acquisition fixes: honest platform claims, store CTA in every language, Mila script isolation."""

from pathlib import Path
import json
import re
import unittest

ROOT = Path(__file__).resolve().parent.parent
HUBS = ['ninely/index.html', 'baylight/index.html', 'middle-east-2030/index.html', 'paper-route/index.html']
MILA_PAGES = sorted(p for p in (ROOT / 'mila').rglob('*.html'))


def read(rel):
    return (ROOT / rel).read_text(encoding='utf-8')


class R2AcquisitionTests(unittest.TestCase):

    def test_structured_data_claims_only_live_platforms(self):
        # No app is on the App Store yet, so no page may tell search engines it runs on iOS.
        for rel in HUBS + ['morning-route/index.html', 'redline-2030/index.html', 'mila/index.html']:
            for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', read(rel), re.S):
                data = json.loads(block)
                text = json.dumps({k: data.get(k) for k in ('gamePlatform', 'operatingSystem')})
                self.assertNotIn('iOS', text, rel)

    def test_no_page_claims_ios_availability(self):
        # Covers visible copy and meta/OG descriptions, in every language, outside policy pages.
        pat = re.compile(r'(iOS (and|&amp;|&) Android|Android (and|&amp;|&) iOS|ל-iOS|closed test builds)')
        for page in ROOT.rglob('*.html'):
            rel = page.relative_to(ROOT).as_posix()
            if rel.startswith('casino/') or 'privacy' in rel or 'support' in rel or rel in ('privacy.html', 'support.html'):
                continue
            self.assertIsNone(pat.search(page.read_text(encoding='utf-8')), rel)

    def test_unreleased_mila_has_no_offer_markup(self):
        block = re.search(r'<script type="application/ld\+json">(.*?)</script>', read('mila/index.html'), re.S).group(1)
        self.assertNotIn('offers', json.loads(block))

    def test_every_language_section_has_a_store_button(self):
        for rel in HUBS:
            html = read(rel)
            for lang, body in re.findall(r'<section id="(en|he|ar)"[^>]*>(.*?)</section>', html, re.S):
                self.assertIn('class="play-badge"', body, f'{rel} section {lang}')

    def test_hub_screenshots_exist_and_reserve_space(self):
        for rel in HUBS:
            # The first screenshot is the LCP element: eager with fetchpriority. The rest stay lazy.
            imgs = re.findall(r'<img src="(/assets/screens/[^"]+)" width="\d+" height="\d+" (?:loading="lazy"|fetchpriority="high")', read(rel))
            self.assertGreaterEqual(len(imgs), 3, rel)
            strip = re.search(r'<div class="screens"[^>]*>\s*(<img[^>]*>)', read(rel)).group(1)
            self.assertIn('fetchpriority="high"', strip, rel)
            self.assertNotIn('loading="lazy"', strip, rel)
            self.assertEqual(read(rel).count('fetchpriority="high"'), 1, rel)
            for src in imgs:
                self.assertTrue((ROOT / src.lstrip('/')).is_file(), src)

    def test_middle_east_fiction_notice_survives_translation(self):
        # A data-i18n attribute would let a shared string replace the notice at runtime.
        sub = re.search(r'<p class="sub"[^>]*>.*?</p>', read('middle-east-2030/index.html'), re.S).group(0)
        self.assertNotIn('data-i18n', sub)
        self.assertIn('fiction', sub)
        self.assertNotIn('iOS', sub)

    def test_homepage_does_not_count_mila_as_released(self):
        html = read('index.html')
        self.assertNotIn('Five apps: Android now', html)
        self.assertIn('Four games on Google Play now', html)

    def test_mila_pages_load_no_shared_studio_scripts(self):
        self.assertTrue(MILA_PAGES)
        for page in MILA_PAGES:
            for src in re.findall(r'<script[^>]*\ssrc="([^"]+)"', page.read_text(encoding='utf-8')):
                resolved = (page.parent / src).resolve()
                self.assertTrue(str(resolved).startswith(str((ROOT / 'mila').resolve())),
                                f'{page.relative_to(ROOT)} loads {src}')

    def test_mila_language_script_has_no_studio_strings(self):
        js = read('mila/assets/lang.js')
        self.assertIn('var AVIISR_STRINGS = {};', js)
        self.assertNotRegex(js.lower(), r'casino|blackjack|roulette|poker|goatcounter|adsbygoogle')


if __name__ == '__main__':
    unittest.main()
