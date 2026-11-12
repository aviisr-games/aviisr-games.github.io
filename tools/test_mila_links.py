#!/usr/bin/env python3
"""Mila isolation: Mila pages link to, load and mention nothing from the other products."""

from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parent.parent
MILA_PAGES = sorted((ROOT / 'mila').rglob('*.html'))
OTHER_PRODUCTS = ('ninely', 'middle-east-2030', 'redline-2030', 'baylight', 'paper-route', 'morning-route')
# Stylesheets Mila pages load from outside mila/ today (the worksheets pages use the shared root style.css).
# Resolved from the repo root. Add a path here only by deliberate decision.
ALLOWED_OUTSIDE = {'style.css'}
FORBIDDEN_STRINGS = ('aviisrCount', 'goatcounter', 'More from', 'data-world')


def read(rel):
    return (ROOT / rel).read_text(encoding='utf-8')


def rel_of(page):
    return page.relative_to(ROOT).as_posix()


def resolve_rel(page, ref):
    """Repo-relative POSIX path that a reference on `page` points at, or None if external or outside the repo."""
    if ref.startswith(('http://', 'https://', '//')):
        return None
    path = ref.split('#')[0].split('?')[0]
    base = ROOT if path.startswith('/') else page.parent
    target = (base / path.lstrip('/')).resolve()
    try:
        return target.relative_to(ROOT).as_posix()
    except ValueError:
        return None


class MilaIsolationTests(unittest.TestCase):

    def test_mila_pages_are_found(self):
        self.assertGreaterEqual(len(MILA_PAGES), 1)

    def test_no_link_points_into_another_product(self):
        # Links to the site root ("../", "../../") and to mila/ itself are allowed (the "All games" link).
        for page in MILA_PAGES:
            for href in re.findall(r'<a\b[^>]*\shref="([^"]*)"', read(rel_of(page))):
                if not href or href.startswith(('mailto:', '#')):
                    continue
                rel = resolve_rel(page, href)
                if rel is None and href.startswith(('http://', 'https://', '//')):
                    continue
                self.assertIsNotNone(rel, f'{rel_of(page)} has a link leaving the repo: {href}')
                self.assertNotIn(rel.split('/')[0], OTHER_PRODUCTS, f'{rel_of(page)} links to {href}')

    def test_no_store_listing_links_until_mila_launches(self):
        """Mila is not released, so its pages may not link to any Play or App Store listing.

        This must be relaxed deliberately when Mila launches: then assert the exact Mila
        package id and store URL instead of forbidding store links outright.
        """
        for page in MILA_PAGES:
            html = read(rel_of(page))
            self.assertNotIn('play.google.com', html, rel_of(page))
            self.assertNotIn('apps.apple.com', html, rel_of(page))

    def test_scripts_and_stylesheets_stay_inside_mila(self):
        for page in MILA_PAGES:
            html = read(rel_of(page))
            for src in re.findall(r'<script\b[^>]*\ssrc="([^"]*)"', html):
                rel = resolve_rel(page, src)
                self.assertTrue(rel and rel.split('/')[0] == 'mila',
                                f'{rel_of(page)} loads script {src}')
            for tag in re.findall(r'<link\b[^>]*>', html):
                if not re.search(r'\brel="stylesheet"', tag):
                    continue
                href = re.search(r'\shref="([^"]*)"', tag).group(1)
                rel = resolve_rel(page, href)
                if rel is not None and rel.split('/')[0] == 'mila':
                    continue
                self.assertIn(rel, ALLOWED_OUTSIDE, f'{rel_of(page)} loads stylesheet {href}')

    def test_no_studio_tracking_or_cross_promo_strings(self):
        for page in MILA_PAGES:
            html = read(rel_of(page))
            for s in FORBIDDEN_STRINGS:
                self.assertNotIn(s, html, f'{rel_of(page)} contains {s!r}')


if __name__ == '__main__':
    unittest.main()
