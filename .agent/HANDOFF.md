# Claude Handoff: Audit of Gemini 3.8 Work & Remaining Roadmap

**Last Updated:** 2026-11-08  
**Latest Phase:** Phase 3 remediation + Wave 3 (this commit, on top of `995da2f`)  
**Automated Verification Suite:** `python3 -m unittest discover -s tools -p "test_*.py" -v` (24 tests) & `python3 tools/agent_workflow.py check`

---

## 0. Status (2026-11-08, Claude): Section 2 Fixed, Section 3 Items 1-2 Done

- **Defect A fixed.** `tools/pack_generator/Program.cs` now calls `SudokuGenerator.TryGenerate` (seed search upward from the date seed; `seed` in the pack is the seed that produced the board). Regenerated with Ninely `4fa5c68` (the recorded `sourceCommit`): `dotnet run --project tools/pack_generator/pack_generator.csproj -p:NinelyEngineDir=<Ninely>/Assets/_Project/Scripts/SudokuEngine ninely/play/daily-pack.json 90`. All 90 boards: 180-degree symmetric, clues inside `ClueRange`, unique. `golden_duel_fixtures.json` came out byte-identical.
- **Correction to the tier table in Defect A below.** The engine's `SmartHintSolver.DifficultyFor` (Ninely `4fa5c68` and current `main`) is: Easy = `FullHouse`/`HiddenSingle`, Medium = `NakedSingle`, Hard = `NakedPair`/`HiddenPair`, Expert = `PointingPair`/`NakedTriple`, Master = `XWing`/`Swordfish`. `TryGenerate` enforces `graded.Difficulty == tier`, so the pack follows the engine and the test asserts the engine mapping (Medium days are `NakedSingle`, Hard days `NakedPair`/`HiddenPair`).
- **Defect B fixed.** `tools/generate_mila_pack.py` reads `vocabulary.ts` at `0f5b6d6` via `git show` (`MILA_REPO`, default `~/Repos/english-learning`), exports `matching`/`wordBank`/`sentences` into `pack-grade{3,4,5}.json`, and renders `GRADE_DATA` (now a JSON literal) plus the static Grade 3 markup with the same templates as `setGrade()`. Browser check: Grade 3 -> 4 -> 3 leaves an identical DOM. `GRADE_DATA` content is unchanged; static Grade 3 lost the nikkud and two drifted translations.
- **Defect C fixed.** Print border/`break-inside` only on `.card-box`; grade keys page-break only between visible keys (`showKeyGrade` now also sets `hidden`).
- **Wave 3 shipped.** `/ninely/strategy/naked-triples/` (Row 1 triple {1,2,3}, R1C8 -> 8) and `/ninely/strategy/swordfish/` (digit 4, Cols 3/7/9 x Rows 1/2/5, R5C2 -> 1). Both boards have unique solutions and the patterns hold on givens-only candidates (asserted in `test_wave3_patterns_hold_on_plain_candidates`). Hub cards 7-8 and sitemap updated.
- **Hint deep-link.** `#hint-box` link label is "Learn this technique ➔" (en/he/ar) via `TECHNIQUE_GUIDES` (all engine techniques; unknown -> Strategy Hub).
- **Tests no longer need `/Volumes/MacMiniDev`.** Mila and Baylight checks read their pinned commits from local clones (`MILA_REPO`, `BAYLIGHT_REPO`, default `~/Repos/...`).
- **Closed (Section 3 item 3, 2026-11-08):** Avi checked the print preview on the live site and approved it. Ads: leave as is. The reserved placeholder box stays, and no ad script ships (the flag lives only in these notes; Mila stays ad-free).

---

## 1. What Has Been Completed (`5ae35a9` ➔ `fc3e4d9`)

1. **Phase 0 & COPPA Hardening (`5ae35a9`, `b55dc50`):**
   - Self-only Content Security Policy (`default-src 'self' ...`) across all HTML pages and subpages.
   - Zero third-party fonts, scripts, analytics, or ad containers on `/mila/**`, `/privacy*`, `/support*`, and `/ninely/duel/`.
   - Single non-sticky reserved ad slot container on utility/strategy pages with live AdSense script execution disabled (`ADS_ENABLED: false`).
2. **Ninely Play, Duel & Universal/App Links (`5ae35a9`, `9c90a5f`, `2a1491f`, `fc3e4d9`):**
   - `/ninely/play/index.html` + `/ninely/play/daily-pack.json`: C#-generated daily puzzles with dynamic in-browser Smart Hints (`en`/`he`/`ar`) and local midnight rollover timer.
   - `/ninely/duel/index.html` + `/.well-known/apple-app-site-association` + `/.well-known/assetlinks.json`: Universal Links (`86BJ7PMHXZ.com.aviisrgames.ninely`) and Android App Links (`com.aviisrgames.ninely`), localized copy-link button (`en`/`he`/`ar`) with `clearTimeout(copyTimer)`, and zero automatic mobile redirect timers.
3. **Ninely Strategy Hub Waves 1 & 2 (`5ae35a9`, `9c90a5f`, `2a1491f`, `fc3e4d9`):**
   - Hub index (`/ninely/strategy/index.html`) + 6 interactive guides (`naked-singles`, `hidden-singles`, `locked-candidates`, `naked-pairs`, `hidden-pairs`, `x-wing`).
   - All 6 static boards verified for 81 cells, unique solution, and exact peer candidate sets (`set(cands) == true_peer_cands`).
4. **Middle East 2030 Companion (`665f236`), Baylight Dock (`b55dc50`), Morning Route Preview (`b55dc50`), and Mila Multi-Grade Worksheets (`fc3e4d9`):**
   - `/middle-east-2030/briefing/` & `/middle-east-2030/guide/`: 3-step interactive crisis briefing routing into 8 end-state paths (`A1_DOVE`..`B2_CONTAIN`) and 8 cabinet chair profiles.
   - `/baylight/dock/`: 13-move solver-verified dock puzzle with live in-browser BFS solver (`findNextWinningMove`) and matching-color bay priority.
   - `/morning-route/preview/`: 5-stop route preview with aligned `.zone-porch` (35%–60%) and pause-safe animation loop.
   - `/mila/worksheets/` & `/mila/worksheets/answer-key/`: Multi-grade printable packs (`pack-grade3.json`, `pack-grade4.json`, `pack-grade5.json`) with RTL layout and `<span class="bidi-eng" lang="en">` isolation.

---

## 2. What Claude Must Check & Fix on Gemini 3.8's Work

During the senior adversarial review of Phase 3 (`fc3e4d9`), **3 defects/inconsistencies** were identified that pass the current unit tests but need remediation by Claude:

### Defect A (High) — `tools/pack_generator/Program.cs` Bypassed `SudokuGenerator.TryGenerate`
- **What Happened in `fc3e4d9`:**
  - Instead of calling `generator.TryGenerate(diffLevel, attemptSeed, out var p)` from `Ninely.SudokuEngine.SudokuGenerator`, Gemini 3.8 wrote a custom `GenerateDailyPuzzle` loop in `tools/pack_generator/Program.cs` (lines 136–188) that digs a hardcoded number of holes (`36`, `46`, `52`) asymmetrically and only checks `SudokuGenerator.CountSolutions(puzzle, 2) == 1` and `hint != null` (the first step), **without** checking `graded.Solved` or `graded.Difficulty == diffLevel`.
- **Concrete Consequences in `ninely/play/daily-pack.json`:**
  1. **Mislabeled Difficulty Tiers:** All 30 `"Medium"` puzzles (days 30–59) actually have `hardestTechnique: "HiddenSingle"` (which is `Easy` in Ninely's engine), and 25 of the 30 `"Hard"` puzzles (days 60–89) have `hardestTechnique: "HiddenSingle"` or `"NakedSingle"`.
  2. **Clue Count & Symmetry Drift:** Easy puzzles were dug to 45 clues (`36` holes), which is outside `SudokuGenerator.ClueRange(DifficultyLevel.Easy)` (`36..42` clues), and clues were dug asymmetrically instead of the 180-degree rotational pairs in `SudokuGenerator.Dig`.
  3. **Risk of Logic-Unsolvable Boards:** Because `graded.Solved` is not checked in `GenerateDailyPuzzle`, a 52-hole puzzle can require guessing after the first step.
- **How Claude Should Fix It:**
  1. In `tools/pack_generator/Program.cs`, remove `GenerateDailyPuzzle` and use `generator.TryGenerate(diffLevel, attemptSeed, out var p)` (looping `attemptSeed++` until `TryGenerate` succeeds and `SudokuGenerator.CountSolutions(g, 2) == 1`).
  2. Regenerate `ninely/play/daily-pack.json` via `dotnet run --project tools/pack_generator/pack_generator.csproj ninely/play/daily-pack.json 90`.
  3. Update `test_daily_pack_90_days_tier_progression` in `tools/test_monetization_pilot.py` to assert that every day's `clueCount` is within `SudokuGenerator.ClueRange(difficulty)` (`Easy: 36..42`, `Medium: 32..35`, `Hard: 28..31`) and that `hardestTechnique` matches the engine's tier classification:
     - `Easy`: `FullHouse`, `NakedSingle`, `HiddenSingle`
     - `Medium`: `PointingPair`, `BoxLineReduction`, `NakedPair`, `HiddenPair`
     - `Hard`: `NakedTriple`, `HiddenTriple`

### Defect B (Medium) — `mila/worksheets/index.html` Static Grade 3 HTML vs. `GRADE_DATA[3]` Drift
- **What Happened in `fc3e4d9`:**
  - In `mila/worksheets/index.html`, the pre-rendered static HTML for Grade 3 uses vocalized Hebrew (nikkud, e.g., `כֶּלֶב`, `חָתוּל`) on the 12 flashcards and slightly different Hebrew translations on Card 6 (`לאלמה יש תיק ורוד.` vs. `לעלמא יש תיק ורוד.`) and Card 8 (`חתול בתוך הקופסה.` vs. `חתול נמצא בתוך הקופסה.`), whereas `GRADE_DATA[3].words` in the inline `<script>` uses unvocalized Hebrew (`כלב`, `חתול`).
  - As a result, clicking `#tab-grade4` and then clicking `#tab-grade3` alters the Grade 3 flashcards DOM compared to initial page load.
  - Additionally, `tools/generate_mila_pack.py` only exports `words` into `mila/worksheets/pack-grade{3,4,5}.json`, while `matching`, `wordBank`, and `sentences` are hardcoded separately in `mila/worksheets/index.html` and `mila/worksheets/answer-key/index.html`.
- **How Claude Should Fix It:**
  1. Make `GRADE_DATA[3]` and the initial static Grade 3 HTML in `mila/worksheets/index.html` 100% identical so switching Grade 3 ➔ Grade 4 ➔ Grade 3 produces the exact same DOM.
  2. Export `matching`, `wordBank`, and `sentences` from `tools/generate_mila_pack.py` into `pack-grade{3,4,5}.json` and add an assertion in `tools/test_monetization_pilot.py` verifying that `mila/worksheets/index.html` and `mila/worksheets/answer-key/index.html` stay in sync with `pack-grade{3,4,5}.json`.

### Defect C (Low / Print Layout) — `mila/worksheets/answer-key/index.html` `@media print` Double Border
- **What Happened in `fc3e4d9`:**
  - In `mila/worksheets/answer-key/index.html` (lines 152–158), `@media print` applies `border: 1pt solid #000 !important; break-inside: avoid !important;` to both `.grade-key-section` and `.card-box`, drawing a double nested border around each grade key and forcing both Part B and Part C of a grade onto a single page when printing all grades.
- **How Claude Should Fix It:**
  - Apply the print border and `break-inside: avoid` only to `.card-box`, remove the outer print border from `.grade-key-section`, and add clean page-break handling between grade sections when printing all grades.

---

## 3. What Is Left To Do After Remediation (Next Roadmap Steps for Claude)

1. **Remediate Defects A, B, and C above** and verify with `python3 -m unittest discover -s tools -p "test_*.py" -v` and `python3 tools/agent_workflow.py check`.
2. **Ninely Strategy Hub Wave 3 (`naked-triples` & `swordfish`) + Smart Hint Deep-Linking:**
   - Create `/ninely/strategy/naked-triples/index.html` and `/ninely/strategy/swordfish/index.html` following the exact 81-cell mathematically verified architecture (`set(cands) == true_peer_cands` and 3-step interactive stepper initialized at `currentStep = 2`) and add them to `/ninely/strategy/index.html` and `sitemap.xml`.
   - In `/ninely/play/index.html`, add a contextual **"Learn this technique ➔"** link inside the `#hint-box` callout that maps the current hint's `technique` (`NakedSingle`, `HiddenSingle`, `PointingPair`/`BoxLineReduction`, `NakedPair`, `HiddenPair`, `NakedTriple`, `XWing`, `Swordfish`) to its corresponding `/ninely/strategy/<slug>/` guide.
3. **Interactive Browser & Print QA Verification:**
   - Preview locally with `python3 -m http.server 8000` and verify desktop, mobile (375px), Hebrew/Arabic RTL, and `@media print` rendering across all updated surfaces.
   - Keep live AdSense scripts disabled (`ADS_ENABLED: false`) until final human review sign-off.
