#!/usr/bin/env python3
"""T1 + T6: no dead store links on allowlisted pages; the aggregate counter stays off Mila
and off privacy/support pages, and is off by default."""

from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
import check_store_links as links  # noqa: E402

COUNTER_TAG = '<script src="/assets/count.js" defer></script>'


class StoreLinksAndCounterTests(unittest.TestCase):

    def test_no_app_store_links_while_no_app_is_live(self):
        """On 8 Nov 2026 no studio app is public on the App Store, so allowlisted pages must not
        link to one. When an app launches, add its id here and its badge to the page."""
        live_app_store_ids = set()
        _, apple = links.collect()
        self.assertEqual(set(apple) - live_app_store_ids, set(),
                         f"App Store links to apps that are not live: {apple}")

    def test_link_regexes_match_both_app_store_url_forms(self):
        self.assertEqual(links.APPLE_RE.findall('https://apps.apple.com/app/id6820597256'), ['6820597256'])
        self.assertEqual(links.APPLE_RE.findall('https://apps.apple.com/app/mila-english-for-kids/id6738379495'),
                         ['6738379495'])
        self.assertEqual(links.APPLE_RE.findall('https://apps.apple.com/il/app/x/id1'), ['1'])
        self.assertEqual(links.PLAY_RE.findall(
            'https://play.google.com/store/apps/details?id=com.aviisrgames.ninely&utm_source=web'),
            ['com.aviisrgames.ninely'])

    def test_iphone_fallback_shown_where_app_store_links_were(self):
        for rel in ['middle-east-2030/index.html', 'middle-east-2030/briefing/index.html',
                    'middle-east-2030/guide/index.html', 'redline-2030/index.html',
                    'ninely/play/index.html', 'ninely/duel/index.html']:
            self.assertIn('class="store-note"', (ROOT / rel).read_text(encoding='utf-8'), rel)
        self.assertIn('בקרוב ב-App Store', (ROOT / 'mila/index.html').read_text(encoding='utf-8'))
        self.assertNotIn('appstore-badge" href', (ROOT / 'mila/index.html').read_text(encoding='utf-8'))

    def test_counter_never_on_mila_privacy_or_support_pages(self):
        excluded = list((ROOT / 'mila').rglob('*.html'))
        excluded += [p for d in links.ALLOWLIST_DIRS for p in (ROOT / d).rglob('*.html')
                     if 'privacy' in str(p.relative_to(ROOT)) or '/support' in str(p.relative_to(ROOT))]
        self.assertTrue(excluded)
        for p in excluded:
            text = p.read_text(encoding='utf-8')
            self.assertNotIn('count.js', text, f"counter must not load on {p.relative_to(ROOT)}")
            self.assertNotIn('goatcounter', text, f"CSP must stay self-only on {p.relative_to(ROOT)}")

    def test_counter_pages_include_tag_and_allow_only_goatcounter_images(self):
        pages = [p for p in [ROOT / 'index.html'] + [q for d in links.ALLOWLIST_DIRS for q in (ROOT / d).rglob('*.html')]
                 if COUNTER_TAG in p.read_text(encoding='utf-8')]
        self.assertGreaterEqual(len(pages), 20)
        for p in pages:
            text = p.read_text(encoding='utf-8')
            csp = re.search(r'Content-Security-Policy" content="([^"]+)"', text).group(1)
            self.assertIn("script-src 'self'", csp, p)
            self.assertRegex(csp, r"img-src 'self' data: https://\*\.goatcounter\.com", p)
            self.assertNotRegex(csp, r'connect-src[^;]*goatcounter', p)  # pixel only, no XHR/beacon

    def test_counter_endpoint_is_owner_approved_and_guarded(self):
        js = (ROOT / 'assets/count.js').read_text(encoding='utf-8')
        # Enabled by the founder on 2026-11-09. Only this GoatCounter site (or off) is allowed.
        endpoint = re.search(r"var ENDPOINT = '([^']*)';", js).group(1)
        self.assertIn(endpoint, ('', 'https://aviisrgames.goatcounter.com/count'))
        self.assertIn(r"/^\/mila(\/|$)/.test(location.pathname)", js)
        self.assertIn("navigator.doNotTrack === '1'", js)
        self.assertIn('navigator.globalPrivacyControl === true', js)
        self.assertNotIn('document.cookie', js)
        self.assertNotIn('localStorage', js)


if __name__ == '__main__':
    unittest.main()
