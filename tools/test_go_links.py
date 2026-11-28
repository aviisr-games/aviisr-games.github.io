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
# Social waves 2026-11-28: one wave per clip (w02 H1, w03 H2, w04 H3) per short-video channel.
BAYLIGHT_SOCIAL_SLUGS = {f'baylight-{c}-{w}{sfx}' for c in ('ytshorts', 'tiktok', 'reels')
                         for w in ('w02', 'w03', 'w04') for sfx in ('', '-ios')}


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
        } | BAYLIGHT_W01_SLUGS | BAYLIGHT_SOCIAL_SLUGS)
        for slug, _, _, target in entries:
            self.assertNotIn('com.aviisr.mila', target.lower(), slug)
            self.assertNotIn('6827490842', target, slug)
            if slug.endswith('-ios'):
                self.assertRegex(target, r'^https://apps\.apple\.com/app/id6826672657\?ct=baylight-[a-z0-9-]+-w0[1-4]&mt=8$', slug)
                self.assertLessEqual(len(target.split('ct=')[1].split('&')[0]), 40, slug)
            elif slug.startswith('baylight-') and slug[-4:] in ('-w01', '-w02', '-w03', '-w04'):
                self.assertIn('referrer=utm_source%3D', target, slug)
                self.assertIn('%26utm_medium%3Dorganic%26utm_campaign%3Dbaylight-' + slug[-3:], target, slug)
            else:
                self.assertIn('utm_medium=organic', target, slug)

    def test_generated_pages_match_config_and_enforce_safety_invariants(self):
        data = json.loads(go_links.CONFIG_PATH.read_text(encoding='utf-8'))
        entries = go_links.validate_links(data)
        expected_slugs = {slug for slug, _, _, _ in entries}
        group_slugs = {slug for slug, _, _, _ in go_links.validate_groups(data)}
        actual_slugs = {p.name for p in go_links.GO_DIR.iterdir() if p.is_dir()}
        self.assertTrue(expected_slugs.isdisjoint(group_slugs))
        self.assertEqual(actual_slugs - group_slugs, expected_slugs)

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


EN_GROUP = 'https://www.facebook.com/groups/learnsudokutechniques'
DE_GROUP = 'https://www.facebook.com/groups/sudokutechnikenlernen'
GROUP_SLUGS = {
    'nfb-en-site': 'en',
    'nfb-en-hub': 'en',
    'nfb-en-playable': 'en',
    'nfb-en-page': 'en',
    'nfb-en-play': 'en',
    'nfb-en-app': 'en',
    'nfb-en-yt': 'en',
    'nfb-en-reply': 'en',
    'nfb-de-site': 'de',
    'nfb-de-page': 'de',
    'nfb-de-play': 'de',
    'nfb-de-app': 'de',
    'nfb-de-yt': 'de',
    'nfb-de-reply': 'de',
}
STRATEGY_LINE = (
    'Want to talk through these techniques with other players? '
    '<a href="/go/nfb-en-site/">Learn Sudoku Techniques</a> is a small public Facebook group '
    'run by the solo developer of Ninely at aviisr games. You do not need the app to join.'
)
HUB_LINE = (
    'Want to talk through techniques with other players? '
    '<a href="/go/nfb-en-hub/">Learn Sudoku Techniques</a> is a small public Facebook group '
    'run by the solo developer of Ninely at aviisr games. You do not need the app to join.'
)
PLAY_LINE = (
    'If you want company on the techniques, there is a small public group here: '
    '<a href="/go/nfb-en-playable/">Learn Sudoku Techniques</a>.'
)


class GroupHopTests(unittest.TestCase):

    def test_config_lists_every_touchpoint_and_only_the_two_groups(self):
        data = json.loads(go_links.CONFIG_PATH.read_text(encoding='utf-8'))
        groups = go_links.validate_groups(data)
        self.assertEqual({slug: lang for slug, lang, _, _ in groups}, GROUP_SLUGS)
        for slug, lang, name, target in groups:
            self.assertEqual(target, EN_GROUP if lang == 'en' else DE_GROUP, slug)
            self.assertNotIn('?', target, slug)
            self.assertNotIn('mila', slug)
            self.assertNotIn('com.aviisr.mila', target)
            if lang == 'en':
                self.assertEqual(name, 'Learn Sudoku Techniques')
            else:
                self.assertEqual(name, 'Sudoku-Techniken lernen')

    def test_rejects_open_redirects_and_mismatched_language(self):
        with self.assertRaises(ValueError):
            go_links.validate_groups({
                'links': [],
                'groups': [{'slug': 'nfb-en-reply', 'lang': 'de'}],
            })
        with self.assertRaises(ValueError):
            go_links.validate_groups({
                'links': [],
                'groups': [{'slug': 'nfb-en-mila', 'lang': 'en'}],
            })
        with self.assertRaises(ValueError):
            go_links.validate_groups({
                'links': [],
                'groups': [{'slug': 'custom-url', 'lang': 'en'}],
            })

    def test_generated_hops_count_with_count_js_then_redirect(self):
        data = json.loads(go_links.CONFIG_PATH.read_text(encoding='utf-8'))
        for slug, lang, _, target in go_links.validate_groups(data):
            page = go_links.GO_DIR / slug / 'index.html'
            html = page.read_text(encoding='utf-8')
            self.assertEqual(html, go_links.render_group_page(slug, lang), slug)
            self.assertIn('<meta name="robots" content="noindex, nofollow">', html, slug)
            self.assertIn('<script src="/assets/count.js" defer></script>', html, slug)
            self.assertIn(f'content="2; url={htmllib.escape(target, quote=True)}"', html, slug)
            self.assertIn(f'href="{htmllib.escape(target, quote=True)}"', html, slug)
            self.assertIn('window.location.replace', html, slug)
            self.assertIn('}, 2000);', html, slug)
            self.assertNotIn('location.search', html, slug)
            self.assertNotIn('URLSearchParams', html, slug)
            self.assertNotIn('document.cookie', html, slug)
            self.assertNotIn('goatcounter.com/count?', html, slug)
            self.assertIn('aviisr games', html, slug)
            self.assertNotIn('\u2014', html, slug)
            self.assertNotIn('\u2013', html, slug)
            if lang == 'en':
                self.assertIn('Taking you to the Ninely sudoku group on Facebook', html, slug)
            else:
                self.assertIn('öffentliche Facebook-Gruppe', html, slug)

    def test_group_hops_stay_out_of_the_sitemap(self):
        sitemap_xml = sm.render()
        for slug in GROUP_SLUGS:
            self.assertNotIn(slug, sitemap_xml)
            page = (go_links.GO_DIR / slug / 'index.html').read_text(encoding='utf-8')
            self.assertIn('noindex', page, slug)

    def test_ninely_pages_use_one_matching_hop_line(self):
        strategy_pages = sorted((ROOT / 'ninely' / 'strategy').rglob('index.html'))
        self.assertGreaterEqual(len(strategy_pages), 11)
        for page in strategy_pages:
            text = page.read_text(encoding='utf-8')
            self.assertIn(STRATEGY_LINE, text, page)
            self.assertNotIn('facebook.com', text, page)
            self.assertNotIn('/go/nfb-de-', text, page)
            self.assertNotIn('/go/nfb-en-hub/', text, page)
            self.assertNotIn('/go/nfb-en-playable/', text, page)
        hub = (ROOT / 'ninely' / 'index.html').read_text(encoding='utf-8')
        self.assertIn(HUB_LINE, hub)
        self.assertNotIn('/go/nfb-en-site/', hub)
        play = (ROOT / 'ninely' / 'play' / 'index.html').read_text(encoding='utf-8')
        self.assertIn(PLAY_LINE, play)
        win = play[play.index('id="win-box"'):play.index('class="store-links"')]
        self.assertIn(PLAY_LINE, win)
        self.assertNotIn('/go/nfb-en-site/', play)


if __name__ == '__main__':
    unittest.main()
