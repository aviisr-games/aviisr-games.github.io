#!/usr/bin/env python3
"""Focused regression tests for P1 fixes (A01-A06), A07 worksheet parity, and 2.0 pilot generation."""

import json
from pathlib import Path
import re
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parent.parent


def read(rel):
    return (ROOT / rel).read_text(encoding='utf-8')


class PilotAndP1Tests(unittest.TestCase):

    def test_build_site_check_passes(self):
        res = subprocess.run(
            [sys.executable, str(ROOT / 'tools/build_site.py'), '--check'],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)

    def test_pilot_css_budget_logical_properties_and_no_opacity_keyframes(self):
        css = read('assets/pilot-2.css')
        self.assertLess(len(css.encode('utf-8')), 8192)
        self.assertNotIn('opacity', css)
        self.assertNotIn('@keyframes', css)
        self.assertNotIn('animation', css)
        self.assertNotRegex(css, r'(?<![\w-])(?:margin|padding)-(?:left|right)|(?<![\w-])(?:left|right):')
        self.assertIn('prefers-reduced-motion', css)
        self.assertIn(':focus-visible', css)

    def test_a02_me2030_support_cards_couple_dark_ink_on_white(self):
        html = read('middle-east-2030/support/index.html')
        self.assertRegex(html, r'\.card\s*\{[^}]*background:\s*#fff;[^}]*color:\s*#111827;')
        self.assertIn('.card h2 { color: #0f172a;', html)
        self.assertIn('.card a { color: #0b3d91;', html)

    def test_a03_ninely_daily_has_aria_grid_and_roving_tabindex(self):
        html = read('ninely/play/index.html')
        self.assertIn('role="grid"', html)
        self.assertIn("cell.setAttribute('role', 'gridcell')", html)
        self.assertIn("cells[idx].setAttribute('tabindex', idx === activeCell ? '0' : '-1')", html)
        for key in ('ArrowRight', 'ArrowLeft', 'ArrowDown', 'ArrowUp', 'Home', 'End'):
            self.assertIn(f"'{key}'", html)

    def test_a04_mobile_nav_is_not_hidden(self):
        css = read('assets/site.css')
        self.assertNotRegex(css, r'@media\s*\(max-width:\s*759px\)\s*\{[^}]*\.links\s*\{\s*display\s*:\s*none')

    def test_a06_home_briefing_and_mila_translations_complete(self):
        home = read('index.html')
        for key in ('w_games', 'w_guides', 'w_notes', 'w_about', 'navSupport'):
            self.assertIn(f'data-i18n="{key}"', home)
        briefing = read('middle-east-2030/briefing/index.html')
        self.assertIn('הסכם צנרת אנרגיה', briefing)
        self.assertIn('מהדורת הבוקר', briefing)
        mila = read('mila/index.html')
        self.assertIn('data-i18n="faq1Q"', mila)
        self.assertIn('Which school grades is Mila designed for?', mila)
        self.assertNotIn('<strong>', json.loads(re.search(r'translations:\s*(\{.*?\n\s*\})\s*\}\);', mila, re.S).group(1))['he']['faq1A'])

    def test_a07_mila_worksheets_and_icon_provenance_parity(self):
        games = json.loads(read('site/games.json'))['games']
        mila_cfg = next(g for g in games if g['id'] == 'mila')
        mila_html = read('mila/index.html')
        self.assertIn('assets/icon-apple-il.jpg', mila_html)
        self.assertTrue((ROOT / 'mila/assets/icon-apple-il.jpg').is_file())
        self.assertIn('Google Play', mila_html)
        self.assertIn('id6827490842', mila_html)
        for w in mila_cfg['worksheets']:
            g = w['grade']
            self.assertIn(f'href="worksheets/?grade={g}"', mila_html)
            self.assertIn(w['heTitle'], mila_html)
            self.assertIn(w['heBtn'], mila_html)
            self.assertIn(w['enBtn'], mila_html)
            self.assertTrue((ROOT / f'mila/worksheets/pack-grade{g}.json').is_file())

    def test_a08_ad_disclosures_and_mobile_no_fill(self):
        about = read('about/index.html')
        privacy = read('privacy/index.html')
        me_guide = read('middle-east-2030/guide/index.html')
        for txt, label in ((about, 'about'), (privacy, 'privacy')):
            self.assertIn('12 Sudoku', txt, label)
            self.assertIn('Middle East 2030', txt, label)
        self.assertNotIn('completely ad-free', me_guide.lower())
        self.assertIn('Google AdSense', me_guide)
        ads_js = read('assets/ads.js')
        self.assertIn('min-height:90px', ads_js)
        self.assertNotIn('min-height:280px', ads_js)
        self.assertIn("data-ad-status", ads_js)

    def test_a10_privacy_and_guides_enable_wrapping(self):
        for rel in (
            'middle-east-2030/privacy/index.html',
            'redline-2030/privacy/index.html',
            'paper-route/privacy/index.html',
            'ninely/strategy/strategy.css',
            'middle-east-2030/guide/index.html',
        ):
            self.assertIn('overflow-wrap', read(rel), rel)
        for rel in (
            'middle-east-2030/privacy/index.html',
            'redline-2030/privacy/index.html',
            'paper-route/privacy/index.html',
            'baylight/privacy.html',
        ):
            self.assertIn("supported: ['en']", read(rel), rel)
        self.assertIn('overflow-wrap:anywhere', read('assets/pilot-2.css'))

    def test_a11_all_hubs_and_studio_pages_use_edition_shell(self):
        for rel in (
            'index.html', 'ninely/index.html', 'baylight/index.html', 'paper-route/index.html',
            'middle-east-2030/index.html', 'middle-east-2030/he/index.html', 'mila/index.html',
            'about/index.html', 'support/index.html', 'privacy/index.html', 'notes/index.html',
        ):
            html = read(rel)
            self.assertIn('class="edition', html, rel)
            self.assertIn('wordmark-light.svg', html, rel)
            self.assertIn('wordmark-dark.svg', html, rel)

    def test_a13_guide_attributions_verified_no_unverified_reviewer(self):
        for path in list((ROOT / 'ninely/strategy').rglob('*.html')) + [ROOT / 'middle-east-2030/guide/index.html']:
            txt = path.read_text(encoding='utf-8')
            for bad in ('Ninely Engine Logic Council', 'Ninely Sudoku Engine Team', 'Redline Engine Team'):
                self.assertNotIn(bad, txt, str(path.relative_to(ROOT)))

    def test_a14_protected_infrastructure_preserved(self):
        self.assertEqual(read('CNAME').strip(), 'aviisrgames.com')
        ads_txt = read('ads.txt')
        self.assertIn('pub-2451365263828795', ads_txt)
        self.assertIn('contact=aviisr@aviisrgames.com', ads_txt)
        self.assertTrue((ROOT / '.well-known/apple-app-site-association').is_file())
        self.assertTrue((ROOT / '.well-known/assetlinks.json').is_file())
        sec = read('.well-known/security.txt')
        self.assertIn('aviisr@aviisrgames.com', sec)
        aasa = json.loads(read('.well-known/apple-app-site-association'))
        self.assertIn('applinks', aasa)
        assetlinks = json.loads(read('.well-known/assetlinks.json'))
        self.assertTrue(isinstance(assetlinks, list) and len(assetlinks) >= 1)


if __name__ == '__main__':
    unittest.main()
