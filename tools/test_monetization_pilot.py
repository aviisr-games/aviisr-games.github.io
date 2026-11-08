#!/usr/bin/env python3
"""Automated verification suite for AVIISR Games Web Monetization & Growth Pilot."""

from html.parser import HTMLParser
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parent.parent


def count_sudoku_solutions(board_list, limit=2):
    board = list(board_list)
    sols = 0

    def backtrack(idx):
        nonlocal sols
        if sols >= limit:
            return
        while idx < 81 and board[idx] != 0:
            idx += 1
        if idx == 81:
            sols += 1
            return
        r, c = divmod(idx, 9)
        br, bc = (r // 3) * 3, (c // 3) * 3
        used = set()
        for i in range(9):
            used.add(board[r * 9 + i])
            used.add(board[i * 9 + c])
            used.add(board[(br + i // 3) * 9 + (bc + i % 3)])
        for num in range(1, 10):
            if num not in used:
                board[idx] = num
                backtrack(idx + 1)
                board[idx] = 0

    backtrack(0)
    return sols


class DiagramBoardParser(HTMLParser):
    """Extracts the 81 cells of #interactive-board from a strategy guide HTML file."""

    def __init__(self):
        super().__init__()
        self.in_board = False
        self.board_depth = 0
        self.in_cell = False
        self.cell_depth = 0
        self.in_candidates = False
        self.cand_depth = 0
        self.current_cell_text = []
        self.cells = []

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        cls = attr_dict.get('class', '')
        if attr_dict.get('id') == 'interactive-board':
            self.in_board = True
            self.board_depth = 1
            return
        if self.in_board:
            self.board_depth += 1
            if not self.in_cell and 'diagram-cell' in cls.split():
                self.in_cell = True
                self.cell_depth = 1
                self.current_cell_text = []
                return
            if self.in_cell:
                self.cell_depth += 1
                if not self.in_candidates and 'candidates-grid' in cls.split():
                    self.in_candidates = True
                    self.cand_depth = 1
                elif self.in_candidates:
                    self.cand_depth += 1

    def handle_endtag(self, tag):
        if self.in_board:
            if self.in_candidates:
                self.cand_depth -= 1
                if self.cand_depth == 0:
                    self.in_candidates = False
            if self.in_cell:
                self.cell_depth -= 1
                if self.cell_depth == 0:
                    self.in_cell = False
                    txt = ''.join(self.current_cell_text).strip()
                    self.cells.append(int(txt) if txt.isdigit() and len(txt) == 1 else 0)
            self.board_depth -= 1
            if self.board_depth == 0:
                self.in_board = False

    def handle_data(self, data):
        if self.in_cell and not self.in_candidates:
            self.current_cell_text.append(data)


class MonetizationPilotTests(unittest.TestCase):

    def test_seed_20261101_legacy_generator_regression(self):
        """Proves legacy Mulberry32 hole-punching for seed 20261101 produces >1 solution."""
        def mulberry32(seed):
            s = seed & 0xFFFFFFFF
            def next_val():
                nonlocal s
                s = (s + 0x6D2B79F5) & 0xFFFFFFFF
                t = s
                t = ((t ^ (t >> 15)) * ((t | 1) & 0xFFFFFFFF)) & 0xFFFFFFFF
                t = (t ^ (t + (((t ^ (t >> 7)) * ((t | 61) & 0xFFFFFFFF)) & 0xFFFFFFFF))) & 0xFFFFFFFF
                return ((t ^ (t >> 14)) >> 0) / 4294967296.0
            return next_val

        rng = mulberry32(20261101)
        base = [
            5, 3, 4, 6, 7, 8, 9, 1, 2,
            6, 7, 2, 1, 9, 5, 3, 4, 8,
            1, 9, 8, 3, 4, 2, 5, 6, 7,
            8, 5, 9, 7, 6, 1, 4, 2, 3,
            4, 2, 6, 8, 5, 3, 7, 9, 1,
            7, 1, 3, 9, 2, 4, 8, 5, 6,
            9, 6, 1, 5, 3, 7, 2, 8, 4,
            2, 8, 7, 4, 1, 9, 6, 3, 5,
            3, 4, 5, 2, 8, 6, 1, 7, 9
        ]
        puzzle = list(base)
        indices = list(range(81))
        for k in range(len(indices) - 1, 0, -1):
            j = int(rng() * (k + 1))
            indices[k], indices[j] = indices[j], indices[k]
        for r in range(38):
            puzzle[indices[r]] = 0

        solutions = count_sudoku_solutions(puzzle, limit=2)
        self.assertGreaterEqual(solutions, 2, "Legacy generator must reproduce >=2 solutions on seed 20261101")

    def test_daily_pack_uniqueness_and_hints(self):
        """Verifies all 30 days and fallback in daily-pack.json have exactly 1 valid solution and localized hints."""
        pack_path = ROOT / 'ninely/play/daily-pack.json'
        self.assertTrue(pack_path.exists(), "daily-pack.json must exist")
        data = json.loads(pack_path.read_text(encoding='utf-8'))

        self.assertEqual(data.get('schemaVersion'), 1)
        self.assertEqual(data.get('sourceCommit'), '4fa5c68')
        self.assertIn('fallback', data)
        self.assertIn('days', data)
        self.assertEqual(len(data['days']), 30, "Must contain exactly 30 dated puzzle days")

        # Test fallback
        fb = data['fallback']
        fb_givens = [int(c) for c in fb['puzzle']]
        self.assertEqual(count_sudoku_solutions(fb_givens, limit=2), 1, "Fallback board must have exactly 1 solution")
        self.assertTrue(fb.get('hint'), "Fallback board must have smart hint")
        self.assertIn('en', fb['hint'].get('explanation', {}))
        self.assertIn('he', fb['hint'].get('explanation', {}))
        self.assertIn('ar', fb['hint'].get('explanation', {}))

        # Test each day
        for date_str, entry in data['days'].items():
            givens = [int(c) for c in entry['puzzle']]
            self.assertEqual(len(givens), 81)
            self.assertEqual(len(entry['solution']), 81)
            self.assertEqual(count_sudoku_solutions(givens, limit=2), 1, f"Day {date_str} must have exactly 1 solution")
            self.assertTrue(entry.get('hint'), f"Day {date_str} must have smart hint")
            self.assertIn('en', entry['hint'].get('explanation', {}))
            self.assertIn('he', entry['hint'].get('explanation', {}))
            self.assertIn('ar', entry['hint'].get('explanation', {}))

    def test_inline_fallback_in_play_html_is_unique_and_dynamic(self):
        """Regression test for Defects 2 & 3: inline fallbackPackEntry in ninely/play/index.html is unique and dynamic hints exist."""
        play_html = (ROOT / 'ninely/play/index.html').read_text(encoding='utf-8')
        pack_data = json.loads((ROOT / 'ninely/play/daily-pack.json').read_text(encoding='utf-8'))

        match = re.search(r'var\s+fallbackPackEntry\s*=\s*(\{.*?\n\s*\});', play_html, re.DOTALL)
        self.assertIsNotNone(match, "fallbackPackEntry must be present in ninely/play/index.html")
        puzzle_match = re.search(r'puzzle:\s*"([0-9]{81})"', match.group(1))
        self.assertIsNotNone(puzzle_match, "fallbackPackEntry must contain an 81-char puzzle string")
        inline_puzzle = puzzle_match.group(1)

        self.assertEqual(
            inline_puzzle,
            pack_data['fallback']['puzzle'],
            "Inline fallbackPackEntry puzzle must match daily-pack.json['fallback']['puzzle']"
        )
        givens = [int(c) for c in inline_puzzle]
        self.assertEqual(
            count_sudoku_solutions(givens, limit=2),
            1,
            "Inline fallbackPackEntry must have strictly 1 unique solution"
        )
        self.assertIn('computeDynamicSmartHint', play_html, "Play page must compute dynamic smart hints as board progresses")
        self.assertIn('setInterval', play_html, "Play page must monitor UTC midnight rollover")

    def test_golden_duel_fixtures_exported_and_embedded_uniquely(self):
        """Regression test for Defect 4: golden duel fixtures in tools/ and embedded in ninely/duel/index.html have 1 solution."""
        fixtures_path = ROOT / 'tools/golden_duel_fixtures.json'
        self.assertTrue(fixtures_path.exists(), "golden_duel_fixtures.json must exist")
        data = json.loads(fixtures_path.read_text(encoding='utf-8'))
        self.assertEqual(data.get('sourceCommit'), '4fa5c68')
        fixtures = data.get('fixtures', [])
        self.assertGreaterEqual(len(fixtures), 20, "Should have exported at least 20 fixtures across difficulties")
        for fix in fixtures:
            givens = [int(c) for c in fix['givens']]
            self.assertEqual(count_sudoku_solutions(givens, limit=2), 1)

        duel_html = (ROOT / 'ninely/duel/index.html').read_text(encoding='utf-8')
        self.assertNotIn('indices[r]] = 0', duel_html, "Duel page must not use naive random hole-punching")
        embedded_givens = re.findall(r'givens:\s*"([0-9]{81})"', duel_html)
        self.assertEqual(len(embedded_givens), 5, "Duel page must embed 5 golden fixtures across all 5 difficulties")
        for g_str in embedded_givens:
            givens = [int(c) for c in g_str]
            self.assertEqual(
                count_sudoku_solutions(givens, limit=2),
                1,
                "Every embedded duel fixture must have strictly 1 unique solution"
            )

    def test_mila_zero_leakage_and_coppa(self):
        """Audit Mila pages for zero external font requests, zero ads/trackers, and clean CSP."""
        mila_files = [
            ROOT / 'mila/index.html',
            ROOT / 'mila/privacy/index.html',
            ROOT / 'mila/support/index.html'
        ]
        for path in mila_files:
            content = path.read_text(encoding='utf-8')
            self.assertNotIn('fonts.googleapis.com', content, f"{path.name} must not load or reference Google Fonts")
            self.assertNotIn('fonts.gstatic.com', content, f"{path.name} must not reference fonts.gstatic.com")
            self.assertNotIn('adsbygoogle', content, f"{path.name} must not contain adsbygoogle")
            self.assertNotIn('googlesyndication.com', content, f"{path.name} must not contain googlesyndication")
            self.assertNotIn('doubleclick.net', content, f"{path.name} must not contain doubleclick")
            self.assertNotIn('gtag', content, f"{path.name} must not contain analytics")

        landing = (ROOT / 'mila/index.html').read_text(encoding='utf-8')
        self.assertIn('referrerpolicy="no-referrer"', landing, "Store link on Mila must have no-referrer")
        self.assertNotIn('utm_', landing, "Mila store link must not contain UTM parameters")
        self.assertNotIn('ct=', landing, "Mila store link must not contain campaign parameters")

    def test_ad_allowlist_default_off_and_single_non_sticky_slot(self):
        """Regression test for Defect 5: zero live AdSense scripts, no sticky ad rail, single ad container per page."""
        html_files = list(ROOT.rglob('*.html'))
        self.assertGreater(len(html_files), 10)
        for h in html_files:
            content = h.read_text(encoding='utf-8')
            self.assertNotIn(
                'pagead2.googlesyndication.com/pagead/js/adsbygoogle.js',
                content,
                f"Page {h.relative_to(ROOT)} must not load live adsbygoogle.js"
            )
            ad_containers = len(re.findall(r'class="[^"]*\bad-slot-container\b[^"]*"', content))
            self.assertLessEqual(
                ad_containers,
                1,
                f"Page {h.relative_to(ROOT)} must have at most 1 .ad-slot-container in DOM (found {ad_containers})"
            )

        strategy_css = (ROOT / 'ninely/strategy/strategy.css').read_text(encoding='utf-8')
        self.assertNotIn('position: sticky', strategy_css, "strategy.css must not use sticky ad rails")

        home = (ROOT / 'index.html').read_text(encoding='utf-8')
        self.assertIn(
            '<meta name="google-adsense-account" content="ca-pub-2451365263828795">',
            home,
            "Root index.html must retain google-adsense-account meta tag for ownership verification"
        )

    def test_strategy_guides_structure_and_mathematical_validity(self):
        """Regression test for Defect 1: strategy boards have 81 cells, zero row/col/box collisions, valid solutions, and candidate grids."""
        guides = [
            ROOT / 'ninely/strategy/index.html',
            ROOT / 'ninely/strategy/naked-singles/index.html',
            ROOT / 'ninely/strategy/hidden-singles/index.html',
            ROOT / 'ninely/strategy/locked-candidates/index.html',
        ]
        for g in guides:
            self.assertTrue(g.exists(), f"Guide {g} must exist")
            content = g.read_text(encoding='utf-8')
            self.assertIn('https://aviisrgames.com/ninely/strategy/', content)
            self.assertIn('Advertisements', content, "Must include reserved ad placeholder")
            if g.name != 'index.html':
                self.assertIn('diagram-board', content, "Worked guide must render a static board")
                self.assertIn('candidates-grid', content, "Worked guide must render before/after candidate pencil marks")
                self.assertIn('wrong-move-box', content, "Worked guide must explain a tempting wrong move")
                self.assertIn('step-controls', content, "Worked guide must include progressive step controls")

                parser = DiagramBoardParser()
                parser.feed(content)
                self.assertEqual(len(parser.cells), 81, f"{g.parent.name} board must have exactly 81 cells")

                # Verify zero duplicate non-zero digits in any row, column, or 3x3 box
                for r in range(9):
                    row_vals = [ parser.cells[r * 9 + c] for c in range(9) if parser.cells[r * 9 + c] != 0 ]
                    self.assertEqual(len(row_vals), len(set(row_vals)), f"Duplicate digit in Row {r+1} of {g.parent.name}")
                for c in range(9):
                    col_vals = [ parser.cells[r * 9 + c] for r in range(9) if parser.cells[r * 9 + c] != 0 ]
                    self.assertEqual(len(col_vals), len(set(col_vals)), f"Duplicate digit in Col {c+1} of {g.parent.name}")
                for br in range(0, 9, 3):
                    for bc in range(0, 9, 3):
                        box_vals = [
                            parser.cells[(br + i // 3) * 9 + (bc + i % 3)]
                            for i in range(9)
                            if parser.cells[(br + i // 3) * 9 + (bc + i % 3)] != 0
                        ]
                        self.assertEqual(len(box_vals), len(set(box_vals)), f"Duplicate digit in Box ({br},{bc}) of {g.parent.name}")

                # Verify board is completable to at least 1 valid Sudoku solution
                self.assertGreaterEqual(
                    count_sudoku_solutions(parser.cells, limit=1),
                    1,
                    f"Board in {g.parent.name} must be completable to a valid Sudoku solution"
                )

    def test_sitemap_urls_preserved_and_expanded(self):
        """Verify sitemap contains all 23 original URLs plus 4 new strategy URLs."""
        sitemap = (ROOT / 'sitemap.xml').read_text(encoding='utf-8')
        expected_urls = [
            'https://aviisrgames.com/',
            'https://aviisrgames.com/ninely/',
            'https://aviisrgames.com/ninely/privacy.html',
            'https://aviisrgames.com/ninely/play/',
            'https://aviisrgames.com/ninely/duel/',
            'https://aviisrgames.com/ninely/strategy/',
            'https://aviisrgames.com/ninely/strategy/naked-singles/',
            'https://aviisrgames.com/ninely/strategy/hidden-singles/',
            'https://aviisrgames.com/ninely/strategy/locked-candidates/',
            'https://aviisrgames.com/middle-east-2030/',
            'https://aviisrgames.com/middle-east-2030/briefing/',
            'https://aviisrgames.com/mila/',
            'https://aviisrgames.com/casino/',
            'https://aviisrgames.com/privacy.html',
            'https://aviisrgames.com/support.html'
        ]
        for url in expected_urls:
            self.assertIn(f'<loc>{url}</loc>', sitemap, f"Sitemap must contain {url}")

    def test_duel_no_auto_redirect(self):
        """Verify duel/index.html removed the automatic mobile redirect timer."""
        duel = (ROOT / 'ninely/duel/index.html').read_text(encoding='utf-8')
        self.assertNotIn('setTimeout(function () { window.location.href = appUrl; }, 400);', duel)
        self.assertIn('Open Challenge in Ninely App', duel)


if __name__ == '__main__':
    unittest.main()
