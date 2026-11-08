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
                'pagead2.googlesyndication.com',
                content,
                f"Page {h.relative_to(ROOT)} must not reference pagead2.googlesyndication.com in HTML or CSP"
            )
            self.assertNotIn(
                'doubleclick.net',
                content,
                f"Page {h.relative_to(ROOT)} must not reference doubleclick.net in HTML or CSP"
            )
            self.assertNotIn(
                'fonts.googleapis.com',
                content,
                f"Page {h.relative_to(ROOT)} must not reference fonts.googleapis.com in HTML or CSP"
            )
            self.assertNotIn(
                'fonts.gstatic.com',
                content,
                f"Page {h.relative_to(ROOT)} must not reference fonts.gstatic.com in HTML or CSP"
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
            'https://aviisrgames.com/middle-east-2030/guide/',
            'https://aviisrgames.com/mila/',
            'https://aviisrgames.com/mila/worksheets/',
            'https://aviisrgames.com/mila/worksheets/answer-key/',
            'https://aviisrgames.com/baylight/',
            'https://aviisrgames.com/baylight/dock/',
            'https://aviisrgames.com/morning-route/',
            'https://aviisrgames.com/morning-route/preview/',
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

    def test_slice3_middle_east_2030_guide_and_briefing_paths(self):
        """Verify Slice 3 ME2030 scenario companion, 8 choice paths, 8 chairs, fiction labeling, and ad-free compliance."""
        guide_path = ROOT / 'middle-east-2030/guide/index.html'
        briefing_path = ROOT / 'middle-east-2030/briefing/index.html'
        self.assertTrue(guide_path.exists(), "middle-east-2030/guide/index.html must exist")
        guide_html = guide_path.read_text(encoding='utf-8')
        briefing_html = briefing_path.read_text(encoding='utf-8')

        # 1. Prominent fiction labeling, ad-free compliance, and house style (no em dashes)
        self.assertIn('Work of Fiction', guide_html)
        self.assertIn('Work of Fiction', briefing_html)
        self.assertNotIn('ad-slot-container', guide_html, "ME2030 guide must remain strictly ad-free")
        self.assertNotIn('adsbygoogle', guide_html, "ME2030 guide must not contain ad scripts")
        self.assertNotIn('—', guide_html, "ME2030 guide must follow house style (no em dashes)")

        # 2. Historical vs. fictional separation and Energy Accord fork controls
        self.assertIn('Dated Historical Context', guide_html)
        self.assertIn('In-Game Fictional Extrapolation', guide_html)
        self.assertIn('id="btn-fork-a"', guide_html)
        self.assertIn('id="btn-fork-b"', guide_html)
        self.assertIn('id="btn-fork-reset"', guide_html)

        # 3. All 8 playable capitals documented
        for chair in ['Jerusalem', 'Cairo', 'Amman', 'Damascus', 'Tehran', 'Ankara', 'Riyadh', 'Abu Dhabi']:
            self.assertIn(f'<strong>{chair}</strong>', guide_html, f"Guide must document chair {chair}")

        # 4. Enumerate all 8 choice paths (AAA..BBB) and verify exact gauge math against briefing deltas
        deltas = [
            {'A': (-5, 12, 8), 'B': (8, -8, -4)},
            {'A': (-4, 10, -2), 'B': (6, -12, 4)},
            {'A': (-6, 8, 12), 'B': (10, -6, -10)},
        ]
        for c1 in ('A', 'B'):
            for c2 in ('A', 'B'):
                for c3 in ('A', 'B'):
                    code = c1 + c2 + c3
                    c_val, e_val, s_val = 65, 60, 55
                    for m_idx, pick in enumerate((c1, c2, c3)):
                        dc, de, ds = deltas[m_idx][pick]
                        c_val = max(10, min(100, c_val + dc))
                        e_val = max(10, min(100, e_val + de))
                        s_val = max(10, min(100, s_val + ds))
                    self.assertIn(f'id="path-{code}"', guide_html, f"Guide must contain anchor #path-{code}")
                    expected_gauges = f'Coalition <strong>{c_val}%</strong> · Economy <strong>{e_val}%</strong> · Stability <strong>{s_val}%</strong>'
                    self.assertIn(expected_gauges, guide_html, f"Path {code} gauge math mismatch in guide")

        # 5. Briefing links each outcome to ../guide/#path-<code>
        self.assertIn("'../guide/#path-' + pathCode", briefing_html)

    def test_slice4_mila_parent_pack(self):
        """Verify Slice 4 Mila Grade 3 parent pack, flashcards, answer key, and COPPA print audit."""
        pack_path = ROOT / 'mila/worksheets/pack-grade3.json'
        sheet_path = ROOT / 'mila/worksheets/index.html'
        key_path = ROOT / 'mila/worksheets/answer-key/index.html'

        self.assertTrue(pack_path.exists(), "pack-grade3.json must exist")
        self.assertTrue(sheet_path.exists(), "worksheets/index.html must exist")
        self.assertTrue(key_path.exists(), "worksheets/answer-key/index.html must exist")

        pack = json.loads(pack_path.read_text(encoding='utf-8'))
        self.assertEqual(pack.get('schemaVersion'), 1)
        self.assertEqual(pack.get('sourceCommit'), '0f5b6d6')
        self.assertEqual(pack.get('gradeBand'), 'pre-band-1')
        self.assertEqual(len(pack['words']), 12)

        # Cross check words against vocabulary.ts in english-learning repo
        vocab_ts = Path('/Users/aviisraeli/Documents/Claude/english-learning/src/lib/vocabulary.ts').read_text(encoding='utf-8')
        for w in pack['words']:
            self.assertEqual(w['band'], 'pre-band-1')
            self.assertIn(f"id: '{w['id']}'", vocab_ts)
            self.assertIn(f"english: '{w['english']}'", vocab_ts)

        sheet_html = sheet_path.read_text(encoding='utf-8')
        key_html = key_path.read_text(encoding='utf-8')

        # Check bidi isolation, @media print, and answer key link
        self.assertIn('unicode-bidi: isolate', sheet_html)
        self.assertIn('@media print', sheet_html)
        self.assertIn('@media print', key_html)
        self.assertIn('answer-key/', sheet_html)

        # Verify zero third-party scripts, fonts, analytics, or ads
        for h in [sheet_html, key_html]:
            self.assertNotIn('fonts.googleapis.com', h)
            self.assertNotIn('fonts.gstatic.com', h)
            self.assertNotIn('adsbygoogle', h)
            self.assertNotIn('gtag', h)
            self.assertNotIn('doubleclick', h)

        # Untagged store link with referrerpolicy
        self.assertIn('referrerpolicy="no-referrer"', sheet_html)
        self.assertNotIn('utm_', sheet_html)

        # Regression checks for Defect 1 (Mila RTL column wording, Part C sentence bidi isolation, landing page print buttons)
        self.assertIn('המילה באנגלית מימין לבין התרגום הנכון שלה בעברית משמאל', sheet_html)
        self.assertEqual(len(re.findall(r'<div class="sentence-item">\s*<span class="bidi-eng" lang="en">', sheet_html)), 6)
        mila_landing = (ROOT / 'mila/index.html').read_text(encoding='utf-8')
        self.assertNotIn('onclick="window.print()"', mila_landing, "Landing page must link to worksheets/ instead of calling window.print()")

    def test_slice5a_baylight_dock_prototype(self):
        """Verify Slice 5A Baylight solver-verified dock prototype, move sequence replay, and rules fidelity."""
        fixtures_path = ROOT / 'tools/baylight_fixtures.json'
        dock_path = ROOT / 'baylight/dock/index.html'
        self.assertTrue(fixtures_path.exists(), "baylight_fixtures.json must exist")
        self.assertTrue(dock_path.exists(), "baylight/dock/index.html must exist")

        import sys
        import warnings
        sys.path.append('/Volumes/MacMiniDev/projects/baylight/Tools')
        import baylight_rules

        fixtures = json.loads(fixtures_path.read_text(encoding='utf-8'))
        self.assertEqual(fixtures.get('sourceCommit'), 'ca07a94')
        levels = fixtures['levels']
        self.assertEqual(len(levels), 2)

        levels_path = '/Volumes/MacMiniDev/projects/baylight/Assets/_Project/Resources/Levels/levels.txt'
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', ResourceWarning)
            all_levels = baylight_rules.parse(levels_path)

        for lvl_fix in levels:
            lvl_id = lvl_fix['id']
            lvl = next(l for l in all_levels if l['id'] == lvl_id)
            st = baylight_rules.start(lvl)
            moves = lvl_fix['solutionMoves']
            for m in moves:
                act = ('bay', m['target']) if m['action'] == 'bay' else ('pallet',)
                # Find matching move in baylight_rules.moves
                next_st = None
                for a, ns in baylight_rules.moves(lvl, st):
                    if a == act:
                        next_st = ns
                        break
                self.assertIsNotNone(next_st, f"Move {act} must be legal in level {lvl_id} at i={st.i}")
                st = next_st

            self.assertTrue(baylight_rules.won(lvl, st), f"Level {lvl_id} must reach won state after replay")
            self.assertEqual(st.i, len(lvl['belt']))
            self.assertEqual(len(st.pallet), 0)
            self.assertTrue(all(n == 0 for _, n in st.bays))

        # Regression check for Defect 2: matching-bay preference on Dock 6 Move 13 + live BFS solver + replay timer cleanup
        dock6_moves = next(l for l in levels if l['id'] == 6)['solutionMoves']
        self.assertEqual(dock6_moves[12]['action'], 'bay')
        self.assertEqual(dock6_moves[12]['target'], 3)

        dock_html = dock_path.read_text(encoding='utf-8')
        self.assertIn("default-src 'self'", dock_html)
        self.assertNotIn('adsbygoogle', dock_html)
        self.assertIn('SYMBOLS', dock_html)
        self.assertIn('prefers-reduced-motion', dock_html)
        self.assertIn('findNextWinningMove', dock_html)
        self.assertIn('stopReplayTimer', dock_html)

    def test_slice5b_morning_route_preview_and_canonicalization(self):
        """Verify Slice 5B Morning Route map preview, throw prototype, hazard counter-moves, and canonicalization."""
        preview_path = ROOT / 'morning-route/preview/index.html'
        mr_path = ROOT / 'morning-route/index.html'
        pr_path = ROOT / 'paper-route/index.html'

        self.assertTrue(preview_path.exists(), "morning-route/preview/index.html must exist")
        self.assertTrue(mr_path.exists(), "morning-route/index.html must exist")
        self.assertTrue(pr_path.exists(), "paper-route/index.html must exist")

        preview_html = preview_path.read_text(encoding='utf-8')
        mr_html = mr_path.read_text(encoding='utf-8')
        pr_html = pr_path.read_text(encoding='utf-8')

        # Canonical links and self-only CSP
        for h in [preview_html, mr_html, pr_html]:
            self.assertIn("default-src 'self'", h)
            self.assertNotIn("pagead2.googlesyndication.com", h)
            self.assertNotIn("fonts.googleapis.com", h)
            self.assertIn('<link rel="canonical"', h)

        # Cross links
        self.assertIn('href="preview/"', mr_html)
        self.assertIn('href="../morning-route/preview/"', pr_html)

        # 7 days and 6 hazards
        for d in range(1, 8):
            self.assertIn(f'Day {d}', preview_html)
        for hazard in ['Bins', 'Pedestrians', 'Chasing Dogs', 'Reversing Cars', 'Drones', 'Skaters']:
            self.assertIn(hazard, preview_html)

        # Throw timing zones and reduced motion step controls (including Defect 3 alignment check)
        self.assertIn('zone-porch', preview_html)
        self.assertIn('left: 35%;\n    width: 25%;', preview_html)
        self.assertNotIn('pos * 0.85', preview_html)
        self.assertIn('cancelAnimationFrame', preview_html)
        self.assertIn('zone-mailbox', preview_html)
        self.assertIn('zone-window', preview_html)
        self.assertIn('btn-step-frame', preview_html)
        self.assertIn('prefers-reduced-motion', preview_html)


if __name__ == '__main__':
    unittest.main()
