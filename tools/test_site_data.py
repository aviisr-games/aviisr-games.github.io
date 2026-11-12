#!/usr/bin/env python3
"""site/games.json is the single source for the five products; index.html must agree with it."""

from pathlib import Path
import html as htmllib
import json
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
import build_sitemap as sm  # noqa: E402

GAMES = json.loads((ROOT / 'site/games.json').read_text(encoding='utf-8'))['games']
HOME = (ROOT / 'index.html').read_text(encoding='utf-8')
BANDS = re.findall(r'<section id="([\w-]+)" data-world="([\w-]+)"[^>]*>(.*?)</section>', HOME, re.S)


def band(game_id):
    for sid, world, body in BANDS:
        if sid == game_id:
            return body
    raise AssertionError(f'no band for {game_id}')


class SiteDataTests(unittest.TestCase):

    def test_band_order_matches_the_data_file_and_the_allowlist(self):
        self.assertEqual([b[0] for b in BANDS], [g['id'] for g in GAMES])
        self.assertTrue(all(sid == world for sid, world, _ in BANDS))
        self.assertEqual([g['storeTitle'] for g in GAMES], [name for name, _ in sm.ALLOWLIST])

    def test_each_band_shows_its_exact_store_title_and_links_its_hub(self):
        for g in GAMES:
            body = band(g['id'])
            title = htmllib.unescape(re.sub(r'</?bdi>', '', re.search(r'<h3>(.*?)</h3>', body, re.S).group(1)))
            self.assertEqual(title, g['storeTitle'])
            self.assertIn(f'<a class="app-more" href="{g["hub"]}">', body)
            self.assertTrue((ROOT / g['hub'] / 'index.html').is_file(), g['hub'])
            if g['browser']:
                self.assertIn(f'href="{g["browser"]}"', body)
            else:
                self.assertNotIn('class="link"', body, g['id'])

    def test_play_badges_exist_exactly_for_live_products_with_the_exact_link(self):
        for g in GAMES:
            body = band(g['id'])
            badges = re.findall(r'<a class="play-badge" href="([^"]+)"><img data-play-badge', body)
            gp = g['googlePlay']
            if gp['status'] == 'live':
                self.assertEqual([htmllib.unescape(b) for b in badges], [g['playLink']], g['id'])
                self.assertIn(f'id={gp["package"]}&', g['playLink'])
                self.assertIn(f'data-app="{g["storeTitle"].split(":")[0]}"', body)
                self.assertIn('Get it on Google Play: ', body)
            else:
                self.assertEqual(badges, [], g['id'])
                self.assertNotIn('play.google.com', body, g['id'])
                self.assertNotIn('data-play-badge', body, g['id'])

    def test_live_packages_are_exactly_the_play_links_on_the_page(self):
        live = {g['googlePlay']['package'] for g in GAMES if g['googlePlay']['status'] == 'live'}
        on_page = set(re.findall(r'play\.google\.com/store/apps/details\?id=([\w.]+)', HOME))
        self.assertEqual(on_page, live)

    def test_no_app_store_link_anywhere_and_statuses_say_none(self):
        self.assertNotIn('apps.apple.com', HOME)
        self.assertNotIn('apps.apple.com', (ROOT / 'site/games.json').read_text(encoding='utf-8'))
        for g in GAMES:
            self.assertEqual(g['appStore']['status'], 'none', g['id'])

    def test_mila_is_isolated(self):
        g = next(x for x in GAMES if x['id'] == 'mila')
        self.assertFalse(g['analytics'])
        self.assertFalse(g['crossPromo'])
        self.assertIsNone(g['playLink'])
        body = band('mila')
        self.assertIn('lang="he" dir="rtl"', re.search(r'<section id="mila"[^>]*>', HOME).group(0))
        self.assertNotIn('play.google.com', body)
        self.assertNotIn('apple.com', body)
        self.assertNotIn('data-play-badge', body)

    def test_only_the_existing_scripts_run_on_the_page(self):
        srcs = re.findall(r'<script[^>]*\ssrc="([^"]+)"', HOME)
        self.assertEqual(srcs, ['assets/i18n.js', '/assets/play-badge.js', '/assets/count.js', 'assets/site.js'])
        self.assertEqual(len(re.findall(r'<script(?![^>]*(?:src=|ld\+json))[^>]*>', HOME)), 1)
        self.assertNotRegex(HOME, r'\son[a-z]+=')
        self.assertNotRegex(HOME.split('<body>')[1], r'(?:href|src)="https?://(?!play\.google\.com/store/apps/)')


if __name__ == '__main__':
    unittest.main()
