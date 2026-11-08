#!/usr/bin/env python3
"""Studio surfaces show only allowlisted apps (T3).

The check is an allowlist, not a blocklist: every internal link and every app name on
studio pages, and every sitemap URL, must belong to an allowlisted app or to the studio
pages themselves. Pages of non-allowlisted titles are out of scope and never edited here.
"""

from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
import build_sitemap as sm  # noqa: E402

STUDIO_FILES = ['/', 'support/', 'privacy/', 'app-ads.txt', 'ads.txt', '.well-known/security.txt',
                'favicon.svg', 'style.css', 'assets/']
APP_NAMES = {name for name, _ in sm.ALLOWLIST}


def internal_targets(html, page_dir):
    out = []
    for href in re.findall(r'(?:href|src)="([^"]+)"', html):
        if href.startswith(('http://', 'https://', 'mailto:', '#', 'data:')):
            if href.startswith(sm.BASE):
                out.append(href[len(sm.BASE):] or '/')
            continue
        path = href.split('#')[0].split('?')[0]
        if path.startswith('/'):
            rel = path.lstrip('/') or '/'
        else:
            rel = str((Path(page_dir) / path)).replace('\\', '/')
            parts = []
            for seg in rel.split('/'):
                if seg == '..':
                    parts.pop() if parts else None
                elif seg not in ('', '.'):
                    parts.append(seg)
            rel = '/'.join(parts) + ('/' if path.endswith('/') else '') or '/'
        out.append(rel or '/')
    return out


def allowed(rel):
    if rel in ('/', ''):
        return True
    if any(rel == f or rel.startswith(f) for f in STUDIO_FILES if f != '/'):
        return True
    return any(rel == p or rel.startswith(p + '/') for p in sm.ALLOWED_PREFIXES)


class AllowlistTests(unittest.TestCase):

    def test_studio_pages_link_only_allowlisted_destinations(self):
        for page in sm.STUDIO_PAGES:
            html = (ROOT / page).read_text(encoding='utf-8')
            page_dir = str(Path(page).parent) if '/' in page else ''
            bad = [t for t in internal_targets(html, page_dir) if not allowed(t)]
            self.assertEqual(bad, [], f"{page} links to non-allowlisted paths: {bad}")

    def test_homepage_app_cards_are_exactly_the_allowlist(self):
        html = (ROOT / 'index.html').read_text(encoding='utf-8')
        cards = re.findall(r'<li class="app-card"[^>]*>.*?<h3>(.*?)</h3>', html, re.S)
        names = {c.replace('&amp;', '&') for c in cards}
        self.assertEqual(names, APP_NAMES)

    def test_homepage_store_links_are_allowlisted_packages(self):
        html = (ROOT / 'index.html').read_text(encoding='utf-8')
        pkgs = set(re.findall(r'play\.google\.com/store/apps/details\?id=([\w.]+)', html))
        self.assertEqual(pkgs, {'com.aviisrgames.ninely', 'com.aviisrgames.middleeast2030',
                                'com.aviisrgames.baylight', 'com.aviisr.paperroute'})
        self.assertNotIn('apps.apple.com', html)

    def test_sitemap_is_generated_from_the_allowlist(self):
        self.assertEqual((ROOT / 'sitemap.xml').read_text(encoding='utf-8'), sm.render(),
                         "sitemap.xml is stale: run python3 tools/build_sitemap.py")
        for url in re.findall(r'<loc>([^<]+)</loc>', sm.render()):
            rel = url[len(sm.BASE):] or '/'
            self.assertTrue(allowed(rel), f"sitemap lists a non-allowlisted URL: {url}")

    def test_structured_data_names_only_the_studio(self):
        html = (ROOT / 'index.html').read_text(encoding='utf-8')
        ld = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S).group(1)
        self.assertIn('developer?id=Aviisr', ld)
        self.assertNotIn('apps.apple.com', ld)

    def test_language_switcher_offers_only_translated_languages(self):
        html = (ROOT / 'index.html').read_text(encoding='utf-8')
        self.assertIn("supported: ['en', 'he', 'ar']", html)


if __name__ == '__main__':
    unittest.main()


class LinkNameTests(unittest.TestCase):
    """Screen-reader link lists must tell repeated links apart (WCAG 2.4.4)."""

    def test_every_play_badge_names_its_app(self):
        import glob
        files = ['index.html'] + [f for d in sm.ALLOWED_PREFIXES for f in glob.glob(str(ROOT / d / '**/*.html'), recursive=True)]
        count = 0
        for f in files:
            html = Path(f if f.startswith('/') else ROOT / f).read_text(encoding='utf-8')
            for img in re.findall(r'<img data-play-badge[^>]*>', html):
                count += 1
                app = re.search(r'data-app="([^"]+)"', img)
                self.assertIsNotNone(app, f"badge without data-app in {f}")
                self.assertIn(f'alt="Get it on Google Play: {app.group(1)}"', img, f)
        self.assertGreaterEqual(count, 10)

    def test_homepage_more_links_carry_a_hidden_app_name(self):
        html = (ROOT / 'index.html').read_text(encoding='utf-8')
        mores = re.findall(r'<a class="app-more"[^>]*>(.*?)</a>', html, re.S)
        self.assertEqual(len(mores), 5)
        for m in mores:
            self.assertIn('class="sr-only"', m)

    def test_ninely_hint_titles_use_readable_names_in_all_languages(self):
        html = (ROOT / 'ninely/play/index.html').read_text(encoding='utf-8')
        guides = re.search(r'var TECHNIQUE_GUIDES = \{(.*?)\};', html, re.S).group(1)
        techniques = set(re.findall(r'(\w+): \'', guides))
        names = re.search(r'var TECHNIQUE_NAMES = \{(.*?)\n  \};', html, re.S).group(1)
        for lang in ('en', 'he', 'ar'):
            block = re.search(lang + r': \{(.*?)\}', names, re.S).group(1)
            self.assertEqual(set(re.findall(r'(\w+): \'', block)), techniques, lang)
        self.assertIn('techniqueName(hint.technique, lang)', html)
        self.assertNotIn("(hint.technique || 'Smart Hint')", html)
