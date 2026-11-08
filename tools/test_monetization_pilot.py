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


def store_link_tags(html):
    """Every <a> pointing at a store listing (App Store or Google Play)."""
    return re.findall(r'<a\b[^>]*href="https://(?:apps\.apple\.com|play\.google\.com)[^"]*"[^>]*>', html)


def read_mila_vocabulary():
    """vocabulary.ts at the packs' pinned commit, or None when no english-learning clone is present
    (set MILA_REPO; defaults to ~/Repos/english-learning)."""
    import os
    import subprocess
    repo = Path(os.environ.get('MILA_REPO', str(Path.home() / 'Repos/english-learning'))).expanduser()
    try:
        return subprocess.run(['git', '-C', str(repo), 'show', '0f5b6d6:src/lib/vocabulary.ts'],
                              check=True, capture_output=True, text=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return None


def export_baylight_source(commit):
    """Baylight Tools/ and levels.txt at `commit`, exported to a temp dir, or None when no clone is
    present (set BAYLIGHT_REPO; defaults to ~/Repos/baylight)."""
    import os
    import subprocess
    import tempfile
    repo = Path(os.environ.get('BAYLIGHT_REPO', str(Path.home() / 'Repos/baylight'))).expanduser()
    out = Path(tempfile.mkdtemp(prefix='baylight-src-'))
    try:
        archive = subprocess.run(['git', '-C', str(repo), 'archive', commit, 'Tools/baylight_rules.py',
                                  'Assets/_Project/Resources/Levels/levels.txt'],
                                 check=True, capture_output=True).stdout
        subprocess.run(['tar', '-x', '-C', str(out)], input=archive, check=True)
        return out
    except (OSError, subprocess.CalledProcessError):
        return None


class DiagramBoardParser(HTMLParser):
    """Extracts the 81 cells of #interactive-board from a strategy guide HTML file, including candidate notes."""

    def __init__(self):
        super().__init__()
        self.in_board = False
        self.board_depth = 0
        self.in_cell = False
        self.cell_depth = 0
        self.in_candidates = False
        self.cand_depth = 0
        self.in_cand_num = False
        self.current_cell_text = []
        self.current_cell_candidates = []
        self.cells = []
        self.cell_candidates = []

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
                self.current_cell_candidates = []
                return
            if self.in_cell:
                self.cell_depth += 1
                if not self.in_candidates and 'candidates-grid' in cls.split():
                    self.in_candidates = True
                    self.cand_depth = 1
                elif self.in_candidates:
                    self.cand_depth += 1
                    if 'cand-num' in cls.split():
                        self.in_cand_num = True

    def handle_endtag(self, tag):
        if self.in_board:
            if self.in_candidates:
                if self.in_cand_num and tag == 'span':
                    self.in_cand_num = False
                self.cand_depth -= 1
                if self.cand_depth == 0:
                    self.in_candidates = False
            if self.in_cell:
                self.cell_depth -= 1
                if self.cell_depth == 0:
                    self.in_cell = False
                    txt = ''.join(self.current_cell_text).strip()
                    self.cells.append(int(txt) if txt.isdigit() and len(txt) == 1 else 0)
                    self.cell_candidates.append(list(self.current_cell_candidates))
            self.board_depth -= 1
            if self.board_depth == 0:
                self.in_board = False

    def handle_data(self, data):
        if self.in_cell:
            if not self.in_candidates:
                self.current_cell_text.append(data)
            elif self.in_cand_num:
                txt = data.strip()
                if txt.isdigit():
                    self.current_cell_candidates.append(int(txt))


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
        """Verifies all 90 days and fallback in daily-pack.json have exactly 1 valid solution and localized hints."""
        pack_path = ROOT / 'ninely/play/daily-pack.json'
        self.assertTrue(pack_path.exists(), "daily-pack.json must exist")
        data = json.loads(pack_path.read_text(encoding='utf-8'))

        self.assertEqual(data.get('schemaVersion'), 1)
        self.assertEqual(data.get('sourceCommit'), '4fa5c68')
        self.assertIn('fallback', data)
        self.assertIn('days', data)
        self.assertEqual(len(data['days']), 90, "Must contain exactly 90 dated puzzle days")

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
        # Mila is not public yet, so the hub shows "coming soon" with no store link. Any store link
        # added at launch must carry referrerpolicy="no-referrer" and no campaign tags.
        for tag in store_link_tags(landing):
            self.assertIn('referrerpolicy="no-referrer"', tag, "Store link on Mila must have no-referrer")
            self.assertNotIn('utm_', tag)
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
            ROOT / 'ninely/strategy/naked-pairs/index.html',
            ROOT / 'ninely/strategy/hidden-pairs/index.html',
            ROOT / 'ninely/strategy/x-wing/index.html',
            ROOT / 'ninely/strategy/naked-triples/index.html',
            ROOT / 'ninely/strategy/swordfish/index.html',
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

                # Verify mathematical validity of all rendered candidate notes against filled givens (exact set equality)
                for idx, cands in enumerate(parser.cell_candidates):
                    if not cands:
                        continue
                    r, c = divmod(idx, 9)
                    br, bc = (r // 3) * 3, (c // 3) * 3
                    used = set()
                    for i in range(9):
                        used.add(parser.cells[r * 9 + i])
                        used.add(parser.cells[i * 9 + c])
                        used.add(parser.cells[(br + i // 3) * 9 + (bc + i % 3)])
                    true_peer_cands = (set(range(1, 10)) - used)
                    self.assertEqual(
                        set(cands),
                        true_peer_cands,
                        f"Candidate set mismatch at R{r+1}C{c+1} in {g.parent.name}: shown={sorted(cands)}, expected={sorted(true_peer_cands)}"
                    )

                # Verify that interactive walkthrough steps produce distinct states (no duplicate Step 2 vs Step 3)
                step_htmls = re.findall(r'num:\s*([1-3]),.*?html1?:\s*([^\n]+)', content, re.DOTALL)
                if step_htmls and len(step_htmls) >= 3:
                    s2_html = next((h for n, h in step_htmls if n == '2'), None)
                    s3_html = next((h for n, h in step_htmls if n == '3'), None)
                    if s2_html and s3_html:
                        self.assertNotEqual(
                            s2_html.strip(), s3_html.strip(),
                            f"Step 2 and Step 3 in {g.parent.name} must produce visually distinct DOM states"
                        )

                # Verify board is completable to at least 1 valid Sudoku solution
                self.assertGreaterEqual(
                    count_sudoku_solutions(parser.cells, limit=1),
                    1,
                    f"Board in {g.parent.name} must be completable to a valid Sudoku solution"
                )

    def test_wave2_stepper_initial_load_polish(self):
        """Verify Wave 2 strategy guides (naked-pairs, hidden-pairs, x-wing) initialize at Step 2 with enabled controls."""
        wave2_guides = [
            ROOT / 'ninely/strategy/naked-pairs/index.html',
            ROOT / 'ninely/strategy/hidden-pairs/index.html',
            ROOT / 'ninely/strategy/x-wing/index.html',
            ROOT / 'ninely/strategy/naked-triples/index.html',
            ROOT / 'ninely/strategy/swordfish/index.html',
        ]
        for g in wave2_guides:
            content = g.read_text(encoding='utf-8')
            self.assertRegex(content, r'var\s+currentStep\s*=\s*2;', f"{g.parent.name} must initialize currentStep to 2")
            self.assertIn('stepText.textContent = steps[1].text', content, f"{g.parent.name} must set initial stepText to steps[1].text")
            self.assertIn('prevBtn.disabled = false;', content, f"{g.parent.name} must enable prev button on load")
            self.assertIn('nextBtn.disabled = false;', content, f"{g.parent.name} must enable next button on load")
            # Verify static HTML contains Step 2 indicator
            self.assertIn('Step 2 of 3:', content, f"{g.parent.name} static HTML must describe Step 2")
            # Verify static interactive board contains elimination candidate markers
            self.assertIn('cand-num elim', content, f"{g.parent.name} static HTML must retain elimination markers for Step 2")
            self.assertIn('cand-num keep', content, f"{g.parent.name} static HTML must retain keep markers for Step 2")

    def test_wave3_patterns_hold_on_plain_candidates(self):
        """Naked Triple and Swordfish boards: unique solution, the pattern holds on givens-only candidates,
        and the step-3 digit is the target cell's solution digit."""
        def parse(slug):
            content = (ROOT / f'ninely/strategy/{slug}/index.html').read_text(encoding='utf-8')
            parser = DiagramBoardParser()
            parser.feed(content)
            return content, parser.cells

        def cands(cells, i):
            r, c = divmod(i, 9)
            br, bc = (r // 3) * 3, (c // 3) * 3
            used = {cells[r * 9 + k] for k in range(9)} | {cells[k * 9 + c] for k in range(9)} | \
                   {cells[(br + k // 3) * 9 + bc + k % 3] for k in range(9)}
            return set() if cells[i] else set(range(1, 10)) - used

        def solve(cells):
            board = list(cells)
            def bt(idx):
                while idx < 81 and board[idx]:
                    idx += 1
                if idx == 81:
                    return True
                for d in sorted(cands(board, idx)):
                    board[idx] = d
                    if bt(idx + 1):
                        return True
                    board[idx] = 0
                return False
            self.assertTrue(bt(0))
            return board

        cell = lambda r, c: (r - 1) * 9 + (c - 1)

        # Naked Triple: Row 1 cells R1C2, R1C4, R1C9 hold only {1, 2, 3}; R1C8 {2, 8} -> 8
        content, cells = parse('naked-triples')
        self.assertEqual(count_sudoku_solutions(cells, 2), 1, "naked-triples board must have a unique solution")
        triple = [cell(1, 2), cell(1, 4), cell(1, 9)]
        self.assertEqual(set().union(*(cands(cells, i) for i in triple)), {1, 2, 3})
        for i in range(3):
            for j in range(i + 1, 3):
                self.assertGreater(len(cands(cells, triple[i]) | cands(cells, triple[j])), 2, "must not reduce to a pair")
        self.assertEqual(cands(cells, cell(1, 8)), {2, 8})
        self.assertEqual(solve(cells)[cell(1, 8)], 8)
        self.assertIn("html: '8'", content)

        # Swordfish on 4: Cols 3, 7, 9 confine 4 to Rows 1, 2, 5; R5C2 {1, 4} -> 1
        content, cells = parse('swordfish')
        self.assertEqual(count_sudoku_solutions(cells, 2), 1, "swordfish board must have a unique solution")
        base = {3: [1, 2, 5], 7: [2, 5], 9: [1, 2]}
        for c, rows in base.items():
            self.assertEqual([r for r in range(1, 10) if 4 in cands(cells, cell(r, c))], rows)
        for a, b in ((3, 7), (3, 9), (7, 9)):
            self.assertEqual(len(set(base[a]) | set(base[b])), 3, "must not reduce to an X-Wing")
        self.assertEqual(cands(cells, cell(5, 2)), {1, 4})
        self.assertEqual(solve(cells)[cell(5, 2)], 1)
        self.assertIn("html: '1'", content)

        hub = (ROOT / 'ninely/strategy/index.html').read_text(encoding='utf-8')
        self.assertIn('href="naked-triples/"', hub)
        self.assertIn('href="swordfish/"', hub)

    def test_play_hint_deep_links_to_strategy_guides(self):
        """#hint-box renders a localized "Learn this technique" link mapped from the hint technique to an
        existing /ninely/strategy/<slug>/ guide (or the hub when no guide exists)."""
        html = (ROOT / 'ninely/play/index.html').read_text(encoding='utf-8')
        m = re.search(r'var TECHNIQUE_GUIDES = \{(.*?)\};', html, re.DOTALL)
        self.assertIsNotNone(m)
        mapping = dict(re.findall(r'(\w+): \'([a-z-]+)\'', m.group(1)))
        expected = {
            'FullHouse': 'naked-singles', 'NakedSingle': 'naked-singles', 'HiddenSingle': 'hidden-singles',
            'PointingPair': 'locked-candidates', 'BoxLine': 'locked-candidates', 'BoxLineReduction': 'locked-candidates',
            'NakedPair': 'naked-pairs', 'HiddenPair': 'hidden-pairs', 'NakedTriple': 'naked-triples',
            'XWing': 'x-wing', 'Swordfish': 'swordfish',
        }
        self.assertEqual(mapping, expected)
        for slug in set(mapping.values()):
            self.assertTrue((ROOT / f'ninely/strategy/{slug}/index.html').exists(), f"missing guide for {slug}")
        self.assertIn('learnGuide: "Learn this technique ➔"', html)
        self.assertIn("guideLink.href = techSlug ? '../strategy/' + techSlug + '/' : '../strategy/';", html)
        self.assertIn('hintBox.appendChild(guideLink);', html)
        # Every technique the daily pack can emit has a guide.
        pack = json.loads((ROOT / 'ninely/play/daily-pack.json').read_text(encoding='utf-8'))
        for entry in list(pack['days'].values()) + [pack['fallback']]:
            self.assertIn(entry['hint']['technique'], mapping)
            self.assertIn(entry['hardestTechnique'], mapping)

    # Mirrors Ninely.SudokuEngine (aviisr-games/Ninely @ 4fa5c68, the pack's sourceCommit):
    # SudokuGenerator.ClueRange and SmartHintSolver.DifficultyFor. TryGenerate only accepts a board
    # whose graded tier equals the requested tier, so hardestTechnique must map back to its tier.
    ENGINE_CLUE_RANGE = {'Easy': (36, 42), 'Medium': (32, 35), 'Hard': (28, 31)}
    ENGINE_TIER_TECHNIQUES = {
        'Easy': {'FullHouse', 'HiddenSingle'},
        'Medium': {'NakedSingle'},
        'Hard': {'NakedPair', 'HiddenPair'},
    }

    def test_daily_pack_90_days_tier_progression(self):
        """90-day pack from SudokuGenerator.TryGenerate: Easy (0-29), Medium (30-59), Hard (60-89),
        clue counts inside ClueRange, engine-graded technique per tier, 180-degree symmetric clues,
        givens consistent with a valid solution, unique solution."""
        pack_path = ROOT / 'ninely/play/daily-pack.json'
        data = json.loads(pack_path.read_text(encoding='utf-8'))
        days = list(data['days'].keys())
        self.assertEqual(len(days), 90)
        self.assertEqual(days[0], '2026-11-08')
        self.assertEqual(days[-1], '2027-02-05')

        for idx, date_key in enumerate(days):
            entry = data['days'][date_key]
            expected = 'Easy' if idx < 30 else 'Medium' if idx < 60 else 'Hard'
            self.assertEqual(entry['difficulty'], expected, f"Day {date_key} (index {idx}) must be {expected}")

            puzzle, solution = entry['puzzle'], entry['solution']
            self.assertEqual(len(puzzle), 81)
            self.assertEqual(len(solution), 81)
            clues = sum(1 for c in puzzle if c != '0')
            self.assertEqual(entry['clueCount'], clues, f"Day {date_key} clueCount must match the givens")
            lo, hi = self.ENGINE_CLUE_RANGE[expected]
            self.assertTrue(lo <= clues <= hi, f"Day {date_key}: {clues} clues outside {expected} range {lo}..{hi}")
            self.assertIn(entry['hardestTechnique'], self.ENGINE_TIER_TECHNIQUES[expected],
                          f"Day {date_key}: {entry['hardestTechnique']} is not a {expected} technique")

            for i in range(81):
                self.assertEqual(puzzle[i] == '0', puzzle[80 - i] == '0',
                                 f"Day {date_key}: clues must be 180-degree rotationally symmetric (cell {i})")
                if puzzle[i] != '0':
                    self.assertEqual(puzzle[i], solution[i], f"Day {date_key}: given {i} disagrees with solution")
            sol = [int(c) for c in solution]
            units = [[r * 9 + c for c in range(9)] for r in range(9)] + \
                    [[r * 9 + c for r in range(9)] for c in range(9)] + \
                    [[(br * 3 + r) * 9 + bc * 3 + c for r in range(3) for c in range(3)]
                     for br in range(3) for bc in range(3)]
            for unit in units:
                self.assertEqual(sorted(sol[i] for i in unit), list(range(1, 10)), f"Day {date_key}: invalid solution")
            self.assertEqual(count_sudoku_solutions([int(c) for c in puzzle], 2), 1, f"Day {date_key} must be unique")

            self.assertIn('hint_en', entry, f"Day {date_key} must have hint_en")
            self.assertIn('hint_he', entry, f"Day {date_key} must have hint_he")
            self.assertIn('hint_ar', entry, f"Day {date_key} must have hint_ar")

    def test_sitemap_urls_preserved_and_expanded(self):
        """Verify the allowlist sitemap keeps every allowlisted URL plus the studio support/privacy pages."""
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
            'https://aviisrgames.com/ninely/strategy/naked-pairs/',
            'https://aviisrgames.com/ninely/strategy/hidden-pairs/',
            'https://aviisrgames.com/ninely/strategy/x-wing/',
            'https://aviisrgames.com/ninely/strategy/naked-triples/',
            'https://aviisrgames.com/ninely/strategy/swordfish/',
            'https://aviisrgames.com/middle-east-2030/',
            'https://aviisrgames.com/middle-east-2030/briefing/',
            'https://aviisrgames.com/middle-east-2030/guide/',
            'https://aviisrgames.com/mila/',
            'https://aviisrgames.com/mila/worksheets/',
            'https://aviisrgames.com/mila/worksheets/answer-key/',
            'https://aviisrgames.com/baylight/',
            'https://aviisrgames.com/baylight/dock/',
            'https://aviisrgames.com/morning-route/preview/',
            'https://aviisrgames.com/privacy/',
            'https://aviisrgames.com/support/'
        ]
        for url in expected_urls:
            self.assertIn(f'<loc>{url}</loc>', sitemap, f"Sitemap must contain {url}")
        # Duplicate hubs canonicalise to the survivor (T9) and are not listed themselves.
        for dup in ('https://aviisrgames.com/redline-2030/', 'https://aviisrgames.com/morning-route/'):
            self.assertNotIn(f'<loc>{dup}</loc>', sitemap)

    def test_duel_no_auto_redirect(self):
        """Verify duel/index.html removed the automatic mobile redirect timer and has copy link button."""
        duel = (ROOT / 'ninely/duel/index.html').read_text(encoding='utf-8')
        self.assertNotIn('setTimeout(function () { window.location.href = appUrl; }, 400);', duel)
        self.assertIn('Open Challenge in Ninely App', duel)
        self.assertIn('btn-copy-duel-link', duel)

    def test_universal_links_and_app_links(self):
        """Verify Apple App Site Association and Android AssetLinks configurations and Duel link integration."""
        aasa_path = ROOT / '.well-known/apple-app-site-association'
        assetlinks_path = ROOT / '.well-known/assetlinks.json'
        security_path = ROOT / '.well-known/security.txt'

        self.assertTrue(aasa_path.exists(), "apple-app-site-association must exist in .well-known/")
        self.assertTrue(assetlinks_path.exists(), "assetlinks.json must exist in .well-known/")
        self.assertTrue(security_path.exists(), "security.txt must be preserved in .well-known/")

        aasa_data = json.loads(aasa_path.read_text(encoding='utf-8'))
        applinks = aasa_data.get('applinks', {})
        self.assertIn('details', applinks)
        detail = applinks['details'][0]
        self.assertEqual(detail.get('appID'), '86BJ7PMHXZ.com.aviisrgames.ninely')
        self.assertIn('/ninely/duel/*', detail.get('paths', []))
        self.assertIn('/ninely/duel/', detail.get('paths', []))
        self.assertEqual(aasa_data.get('webcredentials', {}).get('apps'), ['86BJ7PMHXZ.com.aviisrgames.ninely'])

        assetlinks_data = json.loads(assetlinks_path.read_text(encoding='utf-8'))
        self.assertTrue(isinstance(assetlinks_data, list) and len(assetlinks_data) > 0)
        entry = assetlinks_data[0]
        self.assertIn('delegate_permission/common.handle_all_urls', entry.get('relation', []))
        target = entry.get('target', {})
        self.assertEqual(target.get('namespace'), 'android_app')
        self.assertEqual(target.get('package_name'), 'com.aviisrgames.ninely')
        self.assertIn(
            '65:B7:62:39:D7:36:B2:3D:D2:B6:EA:F1:98:B1:F5:08:80:52:BF:68:5A:D7:D0:84:CF:EC:E8:1E:B9:60:F5:16',
            target.get('sha256_cert_fingerprints', [])
        )

        duel_html = (ROOT / 'ninely/duel/index.html').read_text(encoding='utf-8')
        self.assertIn('<meta name="apple-itunes-app"', duel_html)
        self.assertIn('app-id=6824055538', duel_html)
        self.assertIn('id="btn-copy-duel-link"', duel_html)
        self.assertIn('data-i18n="copyLink"', duel_html)
        self.assertIn('copiedLink', duel_html)
        self.assertIn('clearTimeout(copyTimer)', duel_html)
        self.assertIn('navigator.clipboard', duel_html)

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
        """Verify Slice 4 Mila Grade 3-5 parent packs, grade tabs, flashcards, answer keys, and COPPA print audit."""
        sheet_path = ROOT / 'mila/worksheets/index.html'
        key_path = ROOT / 'mila/worksheets/answer-key/index.html'
        self.assertTrue(sheet_path.exists(), "worksheets/index.html must exist")
        self.assertTrue(key_path.exists(), "worksheets/answer-key/index.html must exist")

        vocab_ts = read_mila_vocabulary()

        grade_specs = [
            ('pack-grade3.json', 'pre-band-1', ['dog', 'cat', 'hen', 'sun', 'pen', 'bag', 'hat', 'box', 'egg', 'bed', 'boy', 'big']),
            ('pack-grade4.json', 'band-1-core-1', ['happy', 'cold', 'fish', 'book', 'girl', 'ball', 'car', 'apple', 'small', 'shoe', 'dress', 'coat']),
            ('pack-grade5.json', 'band-1-core-2', ['rabbit', 'snake', 'candy', 'cookie', 'soup', 'tomato', 'shirt', 'sock', 'glasses', 'camera', 'key', 'ruler']),
        ]

        for fname, expected_band, expected_words in grade_specs:
            pack_file = ROOT / 'mila/worksheets' / fname
            self.assertTrue(pack_file.exists(), f"{fname} must exist")
            pack = json.loads(pack_file.read_text(encoding='utf-8'))
            self.assertEqual(pack.get('schemaVersion'), 1)
            self.assertEqual(pack.get('sourceCommit'), '0f5b6d6')
            self.assertEqual(pack.get('gradeBand'), expected_band)
            self.assertEqual(len(pack['words']), 12)
            actual_ids = [w['id'] for w in pack['words']]
            self.assertEqual(actual_ids, expected_words, f"Word list mismatch in {fname}")

            # Cross check words against vocabulary.ts in english-learning repo (when a clone is available)
            for w in pack['words']:
                self.assertEqual(w['band'], expected_band)
                if vocab_ts is not None:
                    self.assertIn(f"id: '{w['id']}'", vocab_ts)
                    self.assertIn(f"english: '{w['english']}'", vocab_ts)

        # Backwards compatibility pack.json check
        compat_pack = ROOT / 'mila/worksheets/pack.json'
        self.assertTrue(compat_pack.exists(), "pack.json backwards-compatibility copy must exist")
        g3_pack = json.loads((ROOT / 'mila/worksheets/pack-grade3.json').read_text(encoding='utf-8'))
        self.assertEqual(json.loads(compat_pack.read_text(encoding='utf-8')), g3_pack)

        sheet_html = sheet_path.read_text(encoding='utf-8')
        key_html = key_path.read_text(encoding='utf-8')

        # Check bidi isolation, @media print, and answer key link
        self.assertIn('unicode-bidi: isolate', sheet_html)
        self.assertIn('@media print', sheet_html)
        self.assertIn('@media print', key_html)
        self.assertIn('answer-key/', sheet_html)

        # Verify grade switcher tabs in worksheets/index.html
        self.assertIn('role="tablist"', sheet_html)
        self.assertIn('id="tab-grade3"', sheet_html)
        self.assertIn('id="tab-grade4"', sheet_html)
        self.assertIn('id="tab-grade5"', sheet_html)

        # Verify answer key tabs and sections in answer-key/index.html
        self.assertIn('id="key-grade3"', key_html)
        self.assertIn('id="key-grade4"', key_html)
        self.assertIn('id="key-grade5"', key_html)
        self.assertIn('id="tab-key-grade3"', key_html)
        self.assertIn('id="tab-key-grade4"', key_html)
        self.assertIn('id="tab-key-grade5"', key_html)
        self.assertIn('id="tab-key-all"', key_html)

        # Verify zero third-party scripts, fonts, analytics, or ads
        for h in [sheet_html, key_html]:
            self.assertNotIn('fonts.googleapis.com', h)
            self.assertNotIn('fonts.gstatic.com', h)
            self.assertNotIn('adsbygoogle', h)
            self.assertNotIn('gtag', h)
            self.assertNotIn('doubleclick', h)

        # Any store link must be untagged and carry referrerpolicy (none while Mila is unreleased)
        for tag in store_link_tags(sheet_html):
            self.assertIn('referrerpolicy="no-referrer"', tag)
        self.assertNotIn('utm_', sheet_html)

        # Regression checks for Defect 1 (Mila RTL column wording, Part C sentence bidi isolation, landing page print buttons)
        self.assertIn('המילה באנגלית מימין לבין התרגום הנכון שלה בעברית משמאל', sheet_html)
        self.assertEqual(len(re.findall(r'<div class="sentence-item">\s*<span class="bidi-eng" lang="en">', sheet_html)), 6)
        mila_landing = (ROOT / 'mila/index.html').read_text(encoding='utf-8')
        self.assertNotIn('onclick="window.print()"', mila_landing, "Landing page must link to worksheets/ instead of calling window.print()")

    def test_mila_worksheet_and_answer_key_in_sync_with_packs(self):
        """pack-grade{3,4,5}.json are self-contained (words, matching, wordBank, sentences); GRADE_DATA,
        the static Grade 3 markup and the answer key all agree with them (Grade 3 -> 4 -> 3 is a DOM no-op)."""
        import sys
        sys.path.insert(0, str(ROOT / 'tools'))
        import generate_mila_pack as gen

        sheet_html = (ROOT / 'mila/worksheets/index.html').read_text(encoding='utf-8')
        key_html = (ROOT / 'mila/worksheets/answer-key/index.html').read_text(encoding='utf-8')
        m = re.search(r'var GRADE_DATA = (\{.*?\n\});\n', sheet_html, re.DOTALL)
        self.assertIsNotNone(m, "GRADE_DATA must be a JSON literal")
        grade_data = json.loads(m.group(1))
        cfg_by_grade = {c['grade']: c for c in gen.GRADES_CONFIG}

        for g in (2, 3, 4, 5):
            pack = json.loads((ROOT / f'mila/worksheets/pack-grade{g}.json').read_text(encoding='utf-8'))
            for key in ('words', 'matching', 'wordBank', 'sentences'):
                self.assertIn(key, pack, f"pack-grade{g}.json must export {key}")
            self.assertEqual(len(pack['matching']), 8)
            self.assertEqual(len(pack['sentences']), 6)
            self.assertEqual(grade_data[str(g)], gen.grade_data_entry(cfg_by_grade[g], pack),
                             f"GRADE_DATA[{g}] must match pack-grade{g}.json")

            words = {w['english']: w for w in pack['words']}
            english = {w['english'] for w in pack['words']}
            for s in pack['sentences']:
                self.assertIn(s['answer'], pack['wordBank'])
                if g == 2:  # first-letter exercise for pre-readers: _ow -> c (cow)
                    self.assertEqual(len(s['answer']), 1)
                    self.assertIn(s['answer'] + s['engPost'], english)
                else:
                    w = words[s['answer']]
                    self.assertEqual(s['engPre'] + s['answer'] + s['engPost'], w['exampleSentence'])

            # Answer key: matching answers and sentence answers per grade
            section = key_html[key_html.index(f'id="key-grade{g}"'):]
            section = section[:section.index('</article>')]
            rows = re.findall(r'<td><span class="bidi-eng" lang="en">([^<]+)</span> ([^<]+)</td>\s*'
                              r'<td class="ans-correct">([^.]+)\. ([^<]+)</td>', section)
            self.assertEqual(rows, [(mm['eng'], mm['emoji'], mm['answerLetter'], mm['answerText'])
                                    for mm in pack['matching']], f"Answer key grade {g} matching drifted")
            items = re.findall(r'<li><span class="bidi-eng" lang="en">(.*?)<span class="ans-correct">([^<]+)</span>'
                               r'(.*?)</span> &nbsp; \(([^)]+)\)</li>', section)
            self.assertEqual(items, [(s['engPre'], s['answer'], s['engPost'], s['hebHint'])
                                     for s in pack['sentences']], f"Answer key grade {g} sentences drifted")

        # Defect C: print border only on .card-box (no nested double border on the grade wrapper)
        print_css = key_html[key_html.index('@media print'):key_html.index('</style>')]
        self.assertRegex(print_css, r'\.card-box \{\s*border: 1pt solid #000 !important;')
        self.assertNotRegex(print_css, r'\.grade-key-section[^{]*\{[^}]*border: 1pt')
        self.assertIn('break-before: page', print_css)
        self.assertIn('sec.hidden = !show', key_html)

        # Static Grade 3 markup is exactly what setGrade(3) renders, so tab switching changes nothing.
        g3 = grade_data['3']
        for opening, closing, render in gen.STATIC_SLOTS:
            self.assertIn(opening + render(g3), sheet_html, f"Static Grade 3 markup drifted at {opening}")
        self.assertEqual(gen.render_worksheet(sheet_html, grade_data), sheet_html,
                         "Re-rendering the worksheet from the packs must be a no-op")
        # setGrade() must use the same templates as the generator's renderers.
        for fragment in [
            "'<div class=\"flashcard-sentence\"><span class=\"bidi-eng\" lang=\"en\">' + w.exampleSentence + '</span><br>' + w.exampleSentenceHebrew + '</div>'",
            "'<td>' + m.num + '. <span class=\"bidi-eng\" lang=\"en\">' + m.eng + '</span> ' + m.emoji + '</td>'",
            "'<td>' + m.hebLetter + '. ' + m.hebText + '</td>'",
            "data.bankLabel + ': &nbsp;' + data.wordBank.map(",
            "}).join(' &nbsp;·&nbsp; ')",
            "'<span class=\"bidi-eng\" lang=\"en\">' + s.num + '. ' + s.engPre + '<span class=\"blank-line\"></span>' + s.engPost + '</span> &nbsp; (' + s.hebHint + ')'",
        ]:
            self.assertIn(fragment, sheet_html)
        self.assertNotRegex(sheet_html[:sheet_html.index('<script>')], '[\u05B0-\u05C7]',
                            "Static Grade 3 must use the same unvocalized Hebrew as the packs")

    def test_slice5a_baylight_dock_prototype(self):
        """Verify Slice 5A Baylight solver-verified dock prototype, move sequence replay, and rules fidelity."""
        fixtures_path = ROOT / 'tools/baylight_fixtures.json'
        dock_path = ROOT / 'baylight/dock/index.html'
        self.assertTrue(fixtures_path.exists(), "baylight_fixtures.json must exist")
        self.assertTrue(dock_path.exists(), "baylight/dock/index.html must exist")

        import sys
        import warnings

        fixtures = json.loads(fixtures_path.read_text(encoding='utf-8'))
        self.assertEqual(fixtures.get('sourceCommit'), 'ca07a94')
        levels = fixtures['levels']
        self.assertEqual(len(levels), 2)

        # Rules replay against baylight_rules.py + levels.txt at the fixtures' pinned commit (needs a clone).
        src = export_baylight_source('ca07a94')
        all_levels = []
        baylight_rules = None
        if src is not None:
            sys.path.insert(0, str(src / 'Tools'))
            import baylight_rules
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', ResourceWarning)
                all_levels = baylight_rules.parse(str(src / 'Assets/_Project/Resources/Levels/levels.txt'))

        for lvl_fix in (levels if baylight_rules is not None else []):
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
