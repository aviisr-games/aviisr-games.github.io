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
