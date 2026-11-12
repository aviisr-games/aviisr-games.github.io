#!/usr/bin/env python3
"""Game hub template (assets/hub.css): one h1, store title, store link, cross-promo, screenshots.

Add a hub to HUBS once it is rebuilt from the template, and its entry to EXPECTED_PLAY."""

from pathlib import Path
import html as htmllib
import json
import re
import unittest

ROOT = Path(__file__).resolve().parent.parent
HUBS = ['ninely/index.html', 'baylight/index.html', 'paper-route/index.html']
# Play-first hubs lead with a .btn (the browser version is the headline); badge-first hubs lead with the
# Google Play badge and offer the browser preview as a plain text link, with no .btn in the mast.
PLAY_FIRST = ['ninely/index.html']
BADGE_FIRST = ['baylight/index.html', 'paper-route/index.html']
# Languages each hub supports today (Baylight is English only).
LANGS = {'ninely/index.html': ('en', 'he', 'ar'), 'baylight/index.html': ('en',), 'paper-route/index.html': ('en', 'he', 'ar')}
# Play link as written in the page source (byte-identical to the pre-redesign hub, utm_medium=hub).
EXPECTED_PLAY = {
    'ninely/index.html': 'https://play.google.com/store/apps/details?id=com.aviisrgames.ninely&amp;utm_source=aviisrgames&amp;utm_medium=hub&amp;utm_campaign=ninely-hub',
    'baylight/index.html': 'https://play.google.com/store/apps/details?id=com.aviisrgames.baylight&amp;utm_source=aviisrgames&amp;utm_medium=hub&amp;utm_campaign=baylight-hub',
    'paper-route/index.html': 'https://play.google.com/store/apps/details?id=com.aviisr.paperroute&amp;utm_source=aviisrgames&amp;utm_medium=hub&amp;utm_campaign=paper-route-hub',
}
SLUG = {'ninely/index.html': 'ninely', 'baylight/index.html': 'baylight', 'paper-route/index.html': 'paper-route'}
GAMES = {g['hub'].rstrip('/'): g for g in json.loads((ROOT / 'site/games.json').read_text(encoding='utf-8'))['games']}


def read(rel):
    return (ROOT / rel).read_text(encoding='utf-8')


class HubTemplateTests(unittest.TestCase):

    def test_hub_css_budget(self):
        self.assertLess((ROOT / 'assets/hub.css').stat().st_size, 6144)

    def test_each_hub_has_one_h1_equal_to_the_store_title(self):
        for rel in HUBS:
            h1s = re.findall(r'<h1[\s>].*?</h1>', read(rel), re.S)
            self.assertEqual(len(h1s), 1, rel)
            text = htmllib.unescape(re.sub(r'<[^>]+>', '', h1s[0])).strip()
            self.assertEqual(text, GAMES[SLUG[rel]]['storeTitle'], rel)

    def test_each_hub_loads_site_css_then_hub_css_and_site_js(self):
        for rel in HUBS:
            page = read(rel)
            self.assertLess(page.index('assets/site.css'), page.index('assets/hub.css'), rel)
            self.assertRegex(page, r'<script src="[./]*assets/site\.js" defer>', rel)
            self.assertEqual(page.count('data-world="%s"' % SLUG[rel]), 1, rel)

    def test_play_link_is_unchanged_and_there_is_no_app_store_link(self):
        for rel in HUBS:
            page = read(rel)
            self.assertEqual(page.count('href="%s"' % EXPECTED_PLAY[rel]), 1, rel)
            self.assertEqual(len(re.findall(r'class="play-badge"', page)), 1, rel)
            self.assertNotIn('apps.apple.com', page, rel)

    def test_more_from_has_exactly_two_other_hubs_and_never_mila(self):
        for rel in HUBS:
            block = re.search(r'<section class="more".*?</section>', read(rel), re.S).group(0)
            links = re.findall(r'<a class="mini"[^>]*href="([^"]+)"', block)
            self.assertEqual(len(links), 2, rel)
            self.assertEqual(len(set(links)), 2, rel)
            for href in links:
                slug = href.strip('/')
                self.assertIn(slug, GAMES, href)
                self.assertNotEqual(slug, SLUG[rel], rel)
                self.assertNotIn('mila', href)
                self.assertIn(htmllib.escape(GAMES[slug]['storeTitle'], quote=False), block)
            self.assertNotIn('mila', block.lower())

    def test_first_screenshot_is_eager_and_the_rest_lazy(self):
        for rel in HUBS:
            imgs = re.findall(r'<img[^>]*src="/assets/screens/[^"]+"[^>]*>', read(rel))
            self.assertGreaterEqual(len(imgs), 3, rel)
            self.assertIn('fetchpriority="high"', imgs[0], rel)
            self.assertNotIn('loading="lazy"', imgs[0], rel)
            for tag in imgs[1:]:
                self.assertIn('loading="lazy"', tag, rel)
                self.assertNotIn('fetchpriority', tag, rel)
            for tag in imgs:
                self.assertIn('width=', tag)
                self.assertIn('height=', tag)
                self.assertTrue((ROOT / re.search(r'src="/([^"]+)"', tag).group(1)).is_file(), tag)

    def test_languages_share_one_masthead_and_keep_the_supported_copy(self):
        for rel in HUBS:
            page = read(rel)
            langs = LANGS[rel]
            self.assertIn('supported: %s' % repr(list(langs)), page, rel)
            if rel in PLAY_FIRST:
                for lang in langs:
                    self.assertIn('data-lang="%s"' % lang, page, rel)
            self.assertIn('html[lang=he] [data-lang=he]', read('assets/hub.css'))

    def mast_acts(self, rel):
        mast = re.search(r'<section class="mast".*?</section>', read(rel), re.S).group(0)
        acts = re.search(r'<div class="acts">(.*?)</div>', mast, re.S).group(1)
        first = re.match(r'\s*<(\w+)([^>]*)>', acts)
        return mast, first

    def test_play_first_hubs_lead_with_a_primary_button(self):
        for rel in PLAY_FIRST:
            mast, first = self.mast_acts(rel)
            self.assertEqual(first.group(1), 'a', rel)
            self.assertIn('class="btn"', first.group(2), rel)
            self.assertEqual(len(re.findall(r'class="btn"', mast)), 1, rel)

    def test_badge_first_hubs_lead_with_the_play_badge_and_have_no_btn(self):
        for rel in BADGE_FIRST:
            mast, first = self.mast_acts(rel)
            self.assertEqual(first.group(1), 'a', rel)
            self.assertIn('class="play-badge"', first.group(2), rel)
            self.assertNotRegex(mast, r'class="btn[\s"]', rel)
            if rel == 'paper-route/index.html':
                # Browser preview retired: no secondary browser link (needs the paper-route/index.html edit).
                self.assertNotIn('class="link"', mast, rel)
                self.assertNotIn('morning-route/preview', read(rel), rel)
            else:
                self.assertIn('class="link"', mast, rel)


if __name__ == '__main__':
    unittest.main()
