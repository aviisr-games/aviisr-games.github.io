#!/usr/bin/env python3
"""Tests for the static, cookieless /go/ redirect generator and generated pages."""

from pathlib import Path
import html as htmllib
import json
import sys
import unittest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
import build_go_links as go_links  # noqa: E402
import build_sitemap as sm  # noqa: E402


class GoLinksValidationTests(unittest.TestCase):

    def test_accepts_allowlisted_play_and_apple_targets(self):
        slug, app, store, target = go_links.validate_entry({
            'slug': 'ninely-yt',
            'appName': 'Ninely: Sudoku & Logic Puzzle',
            'target': 'https://play.google.com/store/apps/details?id=com.aviisrgames.ninely&utm_source=youtube&utm_medium=organic&utm_campaign=ninely-yt',
        })
        self.assertEqual(slug, 'ninely-yt')
        self.assertEqual(app, 'Ninely: Sudoku & Logic Puzzle')
        self.assertEqual(store, 'Google Play')
        self.assertTrue(target.startswith('https://play.google.com/store/apps/details?id=com.aviisr'))

        _, _, apple_store, _ = go_links.validate_entry({
            'slug': 'ninely-ios',
            'appName': 'Ninely: Sudoku & Logic Puzzle',
            'target': 'https://apps.apple.com/app/id1234567890',
        })
        self.assertEqual(apple_store, 'App Store')

    def test_rejects_arbitrary_external_urls_and_open_redirects(self):
        bad_targets = [
            'https://evil.example/phish',
            'https://play.google.com/store/apps/details?id=com.other.app',
            'javascript:alert(1)',
            'http://play.google.com/store/apps/details?id=com.aviisrgames.ninely',
            'https://play.google.com/store/apps/details?id=com.aviisrgames.ninely" onclick="alert(1)',
            '',
        ]
        for target in bad_targets:
            with self.subTest(target=target):
                with self.assertRaises(ValueError):
                    go_links.validate_entry({
                        'slug': 'test-slug',
                        'appName': 'Test App',
                        'target': target,
                    })

    def test_rejects_invalid_and_duplicate_slugs(self):
        for bad_slug in ('', 'UPPER', 'has space', '../escape', 'a/b', 'bad_slug'):
            with self.subTest(slug=bad_slug):
                with self.assertRaises(ValueError):
                    go_links.validate_entry({
                        'slug': bad_slug,
                        'appName': 'Test App',
                        'target': 'https://play.google.com/store/apps/details?id=com.aviisrgames.ninely',
                    })

        with self.assertRaises(ValueError):
            go_links.validate_links({
                'links': [
                    {
                        'slug': 'dup-slug',
                        'appName': 'Ninely',
                        'target': 'https://play.google.com/store/apps/details?id=com.aviisrgames.ninely',
                    },
                    {
                        'slug': 'dup-slug',
                        'appName': 'Ninely',
                        'target': 'https://play.google.com/store/apps/details?id=com.aviisrgames.ninely',
                    },
                ]
            })

    def test_hard_rejects_mila_targets_and_slugs(self):
        mila_cases = [
            {
                'slug': 'promo-yt',
                'appName': 'Mila',
                'target': 'https://play.google.com/store/apps/details?id=com.aviisr.mila&utm_source=youtube',
            },
            {
                'slug': 'promo-ios',
                'appName': 'Mila',
                'target': 'https://apps.apple.com/il/app/id6827490842',
            },
            {
                'slug': 'mila-yt',
                'appName': 'Ninely',
                'target': 'https://play.google.com/store/apps/details?id=com.aviisrgames.ninely',
            },
        ]
        for entry in mila_cases:
            with self.subTest(entry=entry):
                with self.assertRaises(ValueError):
                    go_links.validate_entry(entry)


_W01_TOKENS = ('site', 'r-playmygame', 'r-puzzlevideogames', 'r-androidgaming', 'r-iosgaming',
               'ytshorts', 'il-gaming', 'press', 'playtest', 'featuring', 'dock')
BAYLIGHT_W01_SLUGS = {f'baylight-{t}-w01{sfx}' for t in _W01_TOKENS for sfx in ('', '-ios')}


class GoLinksGeneratedPagesTests(unittest.TestCase):

    def test_config_has_expected_live_non_mila_slugs(self):
        data = json.loads(go_links.CONFIG_PATH.read_text(encoding='utf-8'))
        entries = go_links.validate_links(data)
        slugs = {slug for slug, _, _, _ in entries}
        self.assertEqual(slugs, {
            'me2030-yt', 'me2030-reddit',
            'ninely-yt', 'ninely-reddit',
            'baylight-yt',
            'mpr-yt',
        } | BAYLIGHT_W01_SLUGS)
        for slug, _, _, target in entries:
            self.assertNotIn('com.aviisr.mila', target.lower(), slug)
            self.assertNotIn('6827490842', target, slug)
            if slug.endswith('-ios'):
                self.assertRegex(target, r'^https://apps\.apple\.com/app/id6826672657\?ct=baylight-[a-z0-9-]+-w01&mt=8$', slug)
                self.assertLessEqual(len(target.split('ct=')[1].split('&')[0]), 40, slug)
            elif slug.startswith('baylight-') and slug.endswith('-w01'):
                self.assertIn('referrer=utm_source%3D', target, slug)
                self.assertIn('%26utm_medium%3Dorganic%26utm_campaign%3Dbaylight-w01', target, slug)
            else:
                self.assertIn('utm_medium=organic', target, slug)

    def test_generated_pages_match_config_and_enforce_safety_invariants(self):
        data = json.loads(go_links.CONFIG_PATH.read_text(encoding='utf-8'))
        entries = go_links.validate_links(data)
        expected_slugs = {slug for slug, _, _, _ in entries}
        actual_slugs = {p.name for p in go_links.GO_DIR.iterdir() if p.is_dir()}
        self.assertEqual(actual_slugs, expected_slugs)

        for slug, app_name, store_name, target in entries:
            page_path = go_links.GO_DIR / slug / 'index.html'
            self.assertTrue(page_path.is_file(), f'Missing {page_path}')
            html = page_path.read_text(encoding='utf-8')
            self.assertEqual(html, go_links.render_page(slug, app_name, store_name, target), slug)

            # SEO & privacy directives
            self.assertIn('<meta name="robots" content="noindex, nofollow">', html, slug)
            self.assertIn('<noscript>', html, slug)
            self.assertIn(f'href="{htmllib.escape(target, quote=True)}"', html, slug)

            # Hardcoded target, zero open-redirect query parsing, zero cookies
            self.assertNotIn('location.search', html, slug)
            self.assertNotIn('URLSearchParams', html, slug)
            self.assertNotIn('document.cookie', html, slug)
            self.assertNotIn('localStorage', html, slug)

            # Cookieless GoatCounter event with DNT/GPC and 300ms redirect
            self.assertIn('https://aviisrgames.goatcounter.com/count', html, slug)
            self.assertIn('navigator.sendBeacon', html, slug)
            self.assertIn('keepalive: true', html, slug)
            self.assertIn("navigator.doNotTrack === '1'", html, slug)
            self.assertIn('navigator.globalPrivacyControl === true', html, slug)
            self.assertIn('}, 300);', html, slug)

    def test_go_pages_are_excluded_from_sitemap(self):
        sitemap_xml = sm.render()
        self.assertNotIn('/go/', sitemap_xml)


if __name__ == '__main__':
    unittest.main()
