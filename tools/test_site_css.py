#!/usr/bin/env python3
"""Home page design tokens: contrast, size budgets, one h1."""

from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parent.parent
CSS = (ROOT / 'assets/site.css').read_text(encoding='utf-8')
HOME = (ROOT / 'index.html').read_text(encoding='utf-8')


def lum(hex_):
    h = hex_.lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    chan = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255
        chan.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * chan[0] + 0.7152 * chan[1] + 0.0722 * chan[2]


def ratio(a, b):
    hi, lo = sorted((lum(a), lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def tokens(block):
    return dict(re.findall(r'--([\w-]+):(#[0-9A-Fa-f]{3,6})\b', block))


def worlds():
    out = {}
    for name, body in re.findall(r'\[data-world=([\w-]+)\]\{([^}]*)\}', CSS):
        out[name] = tokens(body)
    return out


class SiteCssTests(unittest.TestCase):

    def test_five_worlds_define_all_tokens(self):
        w = worlds()
        self.assertEqual(set(w), {'ninely', 'middle-east-2030', 'baylight', 'paper-route', 'mila'})
        for name, t in w.items():
            for k in ('w-bg', 'w-text', 'w-accent', 'w-on-accent'):
                self.assertIn(k, t, f'{name} lacks --{k}')

    def test_world_text_and_buttons_meet_aa(self):
        for name, t in worlds().items():
            for bg in (t['w-bg'], t.get('w-bg2', t['w-bg'])):
                self.assertGreaterEqual(ratio(t['w-text'], bg), 4.5, f'{name} text on {bg}')
            self.assertGreaterEqual(ratio(t['w-on-accent'], t['w-accent']), 4.5, f'{name} button text')
            self.assertGreaterEqual(ratio(t['w-accent'], t['w-bg']), 3.0, f'{name} button edge on band')

    def test_studio_frame_meets_aa(self):
        root = tokens(re.search(r':root\{([^}]*)\}', CSS).group(1))
        bg = root['studio-bg']
        for k in ('studio-text', 'studio-dim', 'studio-ring'):
            self.assertGreaterEqual(ratio(root[k], bg), 4.5, k)

    def test_fiction_flag_and_skip_link_meet_aa(self):
        flag = re.search(r'\.tag\.flag\{[^}]*border-color:(#\w+);background:(#\w+);color:(#\w+)', CSS)
        self.assertIsNotNone(flag)
        self.assertGreaterEqual(ratio(flag.group(3), flag.group(2)), 4.5)

    def test_no_opacity_dimming_no_scroll_reveal_only_transform_animates(self):
        self.assertNotIn('opacity', CSS)
        self.assertNotIn('animation', CSS)
        self.assertNotIn('@keyframes', CSS)
        for prop in re.findall(r'transition:([\w-]+)', CSS):
            self.assertIn(prop, ('transform', 'none'))  # 'none' only in the reduced-motion block
        self.assertIn('prefers-reduced-motion', CSS)
        self.assertRegex(CSS, r':focus-visible\{outline:3px')

    def test_logical_properties_only(self):
        self.assertNotRegex(CSS, r'(?<![\w-])(?:margin|padding)-(?:left|right)|(?<![\w-])(?:left|right):')

    def test_size_budgets(self):
        self.assertLess((ROOT / 'assets/site.css').stat().st_size, 8192)
        self.assertLess((ROOT / 'assets/site.js').stat().st_size, 3072)

    def test_home_has_exactly_one_h1_and_a_sane_outline(self):
        self.assertEqual(len(re.findall(r'<h1[\s>]', HOME)), 1)
        self.assertEqual(len(re.findall(r'<section id="[\w-]+" data-world=', HOME)), 5)
        self.assertEqual(len(re.findall(r'<h2[\s>]', HOME)), 6)  # five bands + studio
        for m in re.finditer(r'<img[^>]*>', HOME):
            self.assertIn('width=', m.group(0))
            self.assertIn('height=', m.group(0))
            self.assertIn(' alt=', m.group(0))
        self.assertEqual(HOME.count('fetchpriority="high"'), 1)
        self.assertEqual(HOME.count('assets/site.css'), 1)
        self.assertNotIn('<style', HOME)


if __name__ == '__main__':
    unittest.main()
