#!/usr/bin/env python3
"""Middle East 2030 hub: one page per language (English and Hebrew), both clearly fiction.

The game is fiction about a real region, so the fiction notice must be in the first screen of
each page and must not be replaceable by a shared translation string, and no page copy may
name real leaders, parties or places in the news.
"""

from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parent.parent
EN = 'middle-east-2030/index.html'
HE = 'middle-east-2030/he/index.html'
PAGES = {EN: 'Middle East 2030: Politics Sim', HE: 'המזרח התיכון 2030: משחק פוליטי'}
CANON = {EN: 'https://aviisrgames.com/middle-east-2030/', HE: 'https://aviisrgames.com/middle-east-2030/he/'}
PLAY = ('https://play.google.com/store/apps/details?id=com.aviisrgames.middleeast2030'
        '&amp;utm_source=aviisrgames&amp;utm_medium=hub&amp;utm_campaign=middle-east-2030-hub')

# Real-world names most likely to slip into copy, alt text or metadata during an edit:
# current regional leaders, armed groups and parties, and places that are in the news.
# Kept short on purpose; it is a tripwire, not a censor, and it cannot prove the copy is clean:
# a human read of both pages stays mandatory for every copy change. The screenshots are not checked
# (they are pixels from the shipped game).
DENY_EN = ['netanyahu', 'khamenei', 'erdogan', 'assad', 'trump', 'hamas', 'hezbollah', 'likud', 'gaza', 'idf',
           'west bank', 'israel', 'iran', 'saudi', 'tehran', 'jerusalem']
DENY_HE = ['נתניהו', 'חמאס', 'חיזבאללה', 'ליכוד', 'עזה', 'צה"ל', 'צה״ל', 'ישראל', 'איראן', 'ירושלים']
FLAG_EMOJI = re.compile('[\U0001F1E6-\U0001F1FF]')


def read(rel):
    return (ROOT / rel).read_text(encoding='utf-8')


class MiddleEastHubTests(unittest.TestCase):

    def test_exactly_one_h1_with_the_store_title(self):
        for rel, title in PAGES.items():
            h1s = [re.sub(r'<[^>]+>', '', h).replace('&amp;', '&').strip()
                   for h in re.findall(r'<h1[^>]*>(.*?)</h1>', read(rel), re.S)]
            self.assertEqual(h1s, [title], rel)

    def test_fiction_notice_is_in_the_first_screen_and_not_translatable(self):
        for rel, word in ((EN, 'no event, headline or leader in it is real'), (HE, 'יצירת בדיון')):
            html = read(rel)
            m = re.search(r'<p class="fiction"[^>]*>(.*?)</p>', html, re.S)
            self.assertIsNotNone(m, rel)
            self.assertNotIn('data-i18n', m.group(0), rel)
            self.assertIn(word, m.group(1), rel)
            # Before the headline copy and the screenshots, right under the masthead.
            self.assertLess(m.start(), html.index('class="screens"'), rel)
            self.assertLess(m.start(), html.index('class="hl"'), rel)
            self.assertLess(html.index('<h1'), m.start(), rel)

    def test_no_shared_translation_engine_can_rewrite_the_page(self):
        # Each language has its own URL, so nothing swaps strings at runtime.
        for rel in PAGES:
            html = read(rel)
            self.assertNotIn('i18n.js', html, rel)
            self.assertNotIn('data-i18n', html, rel)
            self.assertNotIn('data-lang=', html, rel)

    def test_hreflang_and_self_canonical(self):
        for rel in PAGES:
            html = read(rel)
            self.assertEqual(re.findall(r'<link rel="canonical" href="([^"]+)"', html), [CANON[rel]], rel)
            alts = dict(re.findall(r'<link rel="alternate" hreflang="([\w-]+)" href="([^"]+)"', html))
            self.assertEqual(alts, {'en': CANON[EN], 'he': CANON[HE], 'x-default': CANON[EN]}, rel)
            self.assertIn(f'<meta property="og:url" content="{CANON[rel]}">', html, rel)

    def test_pages_link_to_each_other_without_script(self):
        self.assertRegex(read(EN), r'<a id="he" href="he/" hreflang="he" lang="he">')
        self.assertIn('href="/middle-east-2030/" hreflang="en"', read(HE))

    def test_play_link_is_unchanged_and_no_app_store(self):
        for rel in PAGES:
            html = read(rel)
            self.assertEqual(re.findall(r'<a class="play-badge" href="([^"]+)"', html), [PLAY], rel)
            self.assertNotIn('apps.apple.com', html, rel)
            self.assertIn('class="store-note"', html, rel)
        self.assertIn('src="/assets/badges/google-play-iw.png"', read(HE))
        self.assertIn('<script src="/assets/play-badge.js"></script>', read(HE))

    def test_english_page_has_no_hebrew_section_and_hebrew_page_is_rtl(self):
        en = read(EN)
        self.assertTrue(en.startswith('<!doctype html>\n<html lang="en">'))
        self.assertNotRegex(en, r'<section id="(en|he)"')
        self.assertEqual(len(re.findall(r'\slang="he"', en)), 1)  # only the language link
        self.assertEqual(en.count('<html'), 1)
        self.assertIn('<html lang="he" dir="rtl">', read(HE))

    def test_screenshots_first_eager_rest_lazy(self):
        for rel in PAGES:
            html = read(rel)
            imgs = re.findall(r'<img src="/assets/screens/middle-east-2030-\d\.webp"[^>]*>', html)
            self.assertEqual(len(imgs), 3, rel)
            self.assertIn('fetchpriority="high"', imgs[0], rel)
            for img in imgs[1:]:
                self.assertIn('loading="lazy"', img, rel)
            for img in imgs:
                self.assertRegex(img, r'width="480" height="960"')
                self.assertRegex(img, r'alt="[^"]+"')

    def test_no_real_world_names_or_flags(self):
        for rel in PAGES:
            html = read(rel)
            low = html.lower()
            for term in DENY_EN:
                self.assertIsNone(re.search(r'\b' + re.escape(term) + r'\b', low), f'{rel}: {term}')
            for term in DENY_HE:
                self.assertNotIn(term, html, f'{rel}: {term}')
            self.assertIsNone(FLAG_EMOJI.search(html), rel)

    def test_skin_is_small_and_uses_logical_properties(self):
        css = read('assets/hub-me2030.css')
        self.assertLess(len(css.encode('utf-8')), 5 * 1024)
        self.assertNotRegex(css, r'(margin|padding|border)-(left|right)|text-align:\s*(left|right)')
        for rel in PAGES:
            html = read(rel)
            order = [html.index(f'assets/{f}"') for f in ('site.css', 'hub.css', 'hub-me2030.css')]
            self.assertEqual(order, sorted(order), rel)

    def test_no_long_dashes(self):
        for rel in list(PAGES) + ['assets/hub-me2030.css']:
            self.assertNotRegex(read(rel), '[\u2013\u2014]', rel)


if __name__ == '__main__':
    unittest.main()
