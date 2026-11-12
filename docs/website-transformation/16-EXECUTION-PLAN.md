# 16 - Execution plan and model assignment

Written 2026-11-12 after the owner asked for all phases to be planned and handed to Haiku and Sonnet workers with Opus as supervisor and verifier. Task ids refer to document 13.

## 1. Roles

| Role | Model | Does | Does not |
|---|---|---|---|
| Worker, mechanical | Haiku | Attribute and metadata edits, asset exports, string changes, sitemap regeneration, simple tests | Decide copy, touch privacy pages, touch `/mila/**` |
| Worker, feature | Sonnet | Events, stylesheet and tokens, data file and drift test, home page, hub template, end cards, playable reskins | Publish policy text, change store links' targets |
| Supervisor and verifier | Opus | Writes the sensitive pieces (privacy wording, Middle East 2030 fiction copy, anything on Mila rules); reviews every branch adversarially before a pull request is opened: diff, tests, live preview at 390, 768 and 1440 px, English and Hebrew | Build ordinary tickets |
| Orchestrator | Session model | Splits work into disjoint file scopes, integrates, opens pull requests, reports | Merge anything that needs an owner decision |
| Owner | Avi | Decisions listed in section 4, merges | |

Rules for every worker brief (from `AGENTS.md`): goal, exact write scope, context paths, invariants, acceptance checks, stop conditions; one worker per file; at most three at once; report in 250 words.

## 2. Waves

Each wave is one branch in its own worktree under `/Volumes/DevSSD/work/`, one pull request, verified by Opus before it is opened. Later waves are stacked on earlier ones to avoid conflicts in `index.html`.

| Wave | Branch | Tasks | Workers | Verifier | Blocked on | Merge |
|---|---|---|---|---|---|---|
| 1 | `fix/site-phase0` | P0-1 share image, P0-2 eager first screenshot, P0-3 favicon files, P0-4 touch targets, P0-5 casino pages set to `noindex` and dead store links removed (least destructive option; deletion stays the owner's call), store-link test scans every page, P0-6 metadata, P0-7 "prototype" wording in copy and metadata | Haiku: P0-2, P0-6. Sonnet: P0-1, P0-3, P0-4, P0-5, P0-7 | Opus | Nothing | Owner go-ahead |
| 2 | `feat/site-measurement` (on wave 1) | P5-1 privacy wording draft (QR arrivals, browser plays, navigation clicks), P5-2 events on the current pages, tests that nothing fires on Mila | Opus writes P5-1. Sonnet builds P5-2 | Opus | Owner approval of the privacy wording | Owner, after reading the wording |
| 3 | `feat/site-stage1` (on wave 1) | P1-1 ring logo set, P1-2 `assets/site.css`, P1-3 `site/games.json` with drift test, P2-1 art-led home page (short hero, one phone per band on mobile, no play button on Baylight and Paper Route bands), P2-3 device-aware order, P2-4 studio section | Sonnet: P1-2, P1-3, P2-1, P2-3. Haiku: P1-1 exports, P2-2 image checks | Opus | Nothing to build; draft pull request | Not before the owner's gate review and four weeks of baseline from wave 2 |
| 4 | `feat/site-stage2` (on wave 3) | P1-5 Paper Route URLs, P3-1 hub skins, P3-2 Middle East 2030 front page and Hebrew URL, P3-3 end-of-play cards, P3-6 "More from Aviisr Games", P3-7 Mila band test, P5-4 `hreflang` | Sonnet builds. Opus writes P3-2 copy. Haiku: sitemap, metadata | Opus | Wave 3 verified | After stage 1 results |
| 5 | `feat/site-previews` | P3-4 Baylight dock reskin, P3-5 Paper Route preview rebuild or retirement, P4-2 optional video loops | Sonnet | Opus | Art exported from the Baylight and Paper Route projects; owner decision on Paper Route | After art exists |
| 6 | validation | P6-1 to P6-5 on each branch before merge; P6-7 reads after launch | Opus | | | |

Not assigned to any worker: P0-8 (`baylight/flags.json` webhook) and deletion of legacy pages. Both are owner decisions.

## 3. Verification checklist used by Opus on every wave

1. `python3 -m unittest discover -s tools -p "test_*.py"`, `python3 tools/agent_workflow.py check`, `python3 tools/build_sitemap.py --check` all pass.
2. Diff touches only the wave's write scope; nothing under `/mila/**` unless the ticket says so; `app-ads.txt`, `ads.txt`, `/redline-2030/**`, `.well-known/**` untouched.
3. No App Store link; no store badge for an app that is not live; no invented rating, count or feature.
4. Local preview at 390, 768 and 1440 px, English and Hebrew: no horizontal scroll, one `h1`, focus visible.
5. Lighthouse on changed pages stays within the budgets in document 07.
6. Privacy page text matches what `assets/count.js` sends.
7. Verdict per ticket: pass, fix required, or escalate to owner.

## 4. Owner decisions that gate merges

1. Merge wave 1.
2. Approve the privacy wording in wave 2.
3. Gate review: redesign or not, and the logo, before wave 3 merges.
4. Casino pages: keep with `noindex`, or delete.
5. `baylight/flags.json` webhook field.
6. Art export for wave 5, and whether the Paper Route preview is rebuilt or retired.
