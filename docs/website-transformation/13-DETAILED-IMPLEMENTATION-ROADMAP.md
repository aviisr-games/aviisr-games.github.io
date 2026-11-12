# 13 - Detailed implementation roadmap

Nothing in this document has been implemented. Every task ships through a pull request with CI green, per the repository rules.
Effort is in focused working days for one developer or agent with review. Rollback for every task is `git revert` of its squash commit unless stated.
Standard checks for every task: `python3 -m unittest discover -s tools -p "test_*.py"`, `python3 tools/agent_workflow.py check`, `python3 tools/build_sitemap.py --check`, and a visual check at 390, 768 and 1440 px in English and Hebrew.

## Quick wins (can ship before the data gate)

P0-1, P0-2, P0-3, P0-4, P0-6, P0-7, plus the measurement tasks P5-1 and P5-2, which must run for four weeks before any redesign. Together about two days.

---

## Phase 0 - Critical fixes

| Id | Objective and current problem | Change | Files | Depends on | Effort | Acceptance | Tests | Analytics | Risk |
|---|---|---|---|---|---|---|---|---|---|
| P0-1 | Share image shows the old name "aviisr-games" and omits Mila | New 1200x630 image with the ring, "Aviisr Games" and five icons | `assets/og/studio.jpg` | Ring logo (P1-1) or current favicon | 0.25 | Image shows the correct name and five icons; under 100 KB | Existing | None | None |
| P0-2 | First hub screenshot is lazy-loaded though it is the LCP element | Remove `loading="lazy"` from the first image, add `fetchpriority="high"` | Four hubs, `mila/index.html` | None | 0.1 | Lighthouse no longer flags `lcp-lazy-loaded` | Add an assertion | None | None |
| P0-3 | `favicon.ico` 404 | Add `.ico` and a 180 px touch icon | Root | None | 0.1 | Both return 200 | Link check | None | None |
| P0-4 | Small touch targets (polish, not a WCAG failure) | Padding on card and footer links | `style.css`, `index.html` | None | 0.25 | All links at least 24 px high at 390 px | Add a CSS assertion | None | Small layout shift |
| P0-5 | Legacy `/casino/`, `/casino/trainer/`, root `privacy.html`, `support.html` are live and indexable; the trainer has a dead App Store link and a dead Play link. `/redline-2030/` is out of scope: it is a deliberate canonical stub and its privacy page is the Play Console URL for Middle East 2030 | Owner decides: delete, or `noindex` plus fix links. Check store listings for references first. Extend the store-link test to scan every HTML file | Those files | Owner decision | 0.25 | No indexable page outside the allowlist; no dead store link | Extend allowlist test | None | A store listing may still point at an old URL: verify before deleting |
| P0-6 | Titles too long, descriptions missing or weak, Open Graph gaps | Edit metadata on about 20 pages | Listed in document 09 | None | 0.5 | No title over 60 characters, every indexable page has a description of 70 to 160 characters and Open Graph tags | Add a metadata test | None | None |
| P0-7 | Two playables call themselves a prototype and open with a "Development Notice"; the word is also in their meta descriptions and JSON-LD names | Reword visible copy, meta descriptions and structured data to player-facing copy | `baylight/dock/index.html`, `morning-route/preview/index.html` and their strings | None | 0.25 | The words "prototype" and "Development Notice" are gone from visible copy | Add a string test | None | None |
| P0-8 | Public webhook token in `baylight/flags.json` | Owner confirms the endpoint is harmless and rate-limited, or empties the field | `baylight/flags.json`, possibly the Baylight privacy page | Owner | 0.25 | Decision recorded in `.agent/TODO.md` | None | None | Emptying the field disables the in-app signal |

## Phase 1 - Brand and information architecture

| Id | Objective | Change | Files | Depends on | Effort | Acceptance | Tests | Risk |
|---|---|---|---|---|---|---|---|---|
| P1-1 | A studio mark | Ring logo set: mark, mark plus name, light and dark, favicon | `assets/logo/*`, `favicon.svg` | Owner sign-off on direction 1 | 0.5 | Renders crisply at 16, 32, 180 and 512 px | None | Conflicts with the pending "Route C" logo test: reconcile first |
| P1-2 | Tokens and base styles | `assets/site.css` with the tokens and components in document 07 | New file | None | 1 | Contrast test passes; file under 8 KB | New contrast test | None |
| P1-3 | Single source of truth | `site/games.json` plus a drift test over existing pages and `assets/i18n.js` availability strings. Templates and a generator only later, if hand edits prove costly (document 12) | New file, new test | None | 0.75 | Changing a status in the data file makes the test name every page and string that must change | Drift, status and Mila tests | Low |
| P1-4 | Shared header and footer | Template partials used by home and hubs | Templates | P1-2, P1-3 | 0.5 | Same header on all generated pages; language control has a visible label | One-`h1` test | None |
| P1-5 | URL clean-up | Paper Route preview to `/paper-route/play/`; old paths become canonical stubs | `paper-route/`, `morning-route/`, sitemap | P1-3 | 0.5 | Old URLs resolve and point to the new ones; sitemap updated | Sitemap check | Inbound links to old paths: stubs keep them working |

## Phase 2 - Home page

| Id | Objective | Change | Files | Depends on | Effort | Acceptance | Tests | Analytics | Risk |
|---|---|---|---|---|---|---|---|---|---|
| P2-1 | Art-led home | Short hero with icon rail and five world bands; first play button and screenshot inside 700 px on a phone; one phone per band on mobile. Baylight and Paper Route bands show badge and screenshots only until P3-4 and P3-5 are done | `index.html` | P1-2 to P1-4 | 2 | Matches the "Worlds, play first" specification; one `h1`; no horizontal scroll at 320 px | Budget test, allowlist test | `card_click` | Long page on phones: check scroll depth after launch |
| P2-2 | 720 px screenshots | Export larger WebP files, add `srcset` | `assets/screens/` | Source images from the store listings | 0.5 | Sharp on a 3x phone; first band under 40 KB of images | Budget test | None | Needs originals from the owner |
| P2-3 | Device-aware actions | `assets/site.js` ordering and iPhone note | New file | P2-1 | 0.5 | Android shows the badge first; iPhone shows no Google Play badge in bands; no-script view is complete | Unit test on the ordering function | None | Wrong detection: default order is always valid |
| P2-4 | Studio section | Three sentences and contact. A press kit link only once a press kit exists | Template | Owner supplies or approves the text | 0.25 | Present, no invented facts | None | `contact_click` | None |
| P2-5 | Hebrew home | `/he/` generated from the same data with `hreflang` | Template, sitemap | P2-1 | 0.5 | Right-to-left layout correct; `hreflang` pair valid | RTL screenshot check | None | Copy needs a native read |

## Phase 3 - Game pages and playables

| Id | Objective | Change | Files | Depends on | Effort | Acceptance | Risk |
|---|---|---|---|---|---|---|---|
| P3-1 | Hub template | One template, five skins, sections as in document 06 | Five hubs (generated) | P1, P2 | 2 | Each hub has one `h1`, actions in the first screen, verified facts only | Per-game copy must be re-verified against the store |
| P3-2 | Middle East 2030 front page | Newspaper layout, fiction banner, Hebrew at `/middle-east-2030/he/` | Hub, template | P3-1 | 1 | Fiction line visible in the first screen in both languages | Sensitive subject: owner reads the final copy |
| P3-3 | End-of-play cards | Result, one sentence, badge or note, play again | Briefing, dock, preview | P1-2 | 1 | Card appears at round end, receives focus, is announced | None |
| P3-4 | Baylight dock reskin | Replace emoji tiles with exported parcel and truck art | `baylight/dock/` | Art from the Baylight project | 2 | No emoji as game pieces; keyboard play still works; page under 150 KB | If art cannot be exported, fall back to screenshots and drop the playable from the band |
| P3-5 | Paper Route preview decision | Rebuild with the game's sprites, or retire it and lead with screenshots | `paper-route/play/` | Owner decision, art | 0.5 to 3 | Either a preview that resembles the game or none | Retiring removes a play action for this game |
| P3-6 | "More from Aviisr Games" | Two cards on each hub and playable, never on Mila | Template | P3-1 | 0.5 | Present on four games; absent on Mila (tested) | None |
| P3-7 | Mila band | Home band with the trust facts. Mila pages keep their own header and get no studio navigation and no links to other products | `index.html` | P2-1 | 0.25 | Mila isolation tests pass; a new test asserts that `/mila/**` has no links to other games | None |

## Phase 4 - Interactive polish

| Id | Change | Effort | Acceptance |
|---|---|---|---|
| P4-1 | Button press feedback and icon lift as specified in document 07. Band reveal is optional and the first to drop | 0.5 | Only transform and opacity animate; all motion off under reduced motion; content visible without script |
| P4-2 | Optional gameplay loops for Baylight and Paper Route | 1 plus capture time | Under 600 KB each, poster shown first, tap to play on phones, no autoplay under reduced motion or data saver |
| P4-3 | Mirrored phone fan and spacing check in right-to-left | 0.25 | Hebrew pages look deliberate |

P4-2 is the first item to drop if time is short.

## Phase 5 - Growth infrastructure

| Id | Change | Depends on | Effort | Acceptance |
|---|---|---|---|---|
| P5-1 | Update the privacy page sentence about what the counter records. Do this first: the page already omits the live `qr_land` event | Owner approval of the wording | 0.25 | Text lists page views, store clicks, QR arrivals, browser game plays and navigation clicks |
| P5-2 | New events in `assets/count.js` and the current playables, shipped before any redesign | P5-1 | 1 | Events appear in the counter; nothing fires on Mila pages or for Mila links; DNT and GPC still respected |
| P5-3 | Weekly table template and the list of numbers to record | P5-2 | 0.25 | Owner can fill it in ten minutes |
| P5-4 | `hreflang`, one `h1`, structured data logo | P2-5, P3-2 | 0.5 | Rich results test passes for Organization and VideoGame; no ratings in markup |
| P5-5 | App Store readiness | First iOS approval | 0.25 | Setting one status field adds the badge, campaign parameters and click counting |

## Phase 6 - Validation and launch

| Id | Check | Tool | Pass condition |
|---|---|---|---|
| P6-1 | Browsers | Chrome, Safari, Firefox on desktop; Safari on iPhone; Chrome on Android | No layout or script errors |
| P6-2 | Performance | Lighthouse mobile and desktop on home and five hubs | Budgets in document 07 |
| P6-3 | Accessibility | Lighthouse, keyboard pass, one VoiceOver and one TalkBack session | No blocker; findings logged |
| P6-4 | Links and stores | Existing weekly workflow run on the branch | Green |
| P6-5 | Security | Policy strings reduced to two; no inline script on new pages | Reviewed |
| P6-6 | Launch | Merge only after the gate review has approved the redesign and four baseline weeks are recorded | Baseline numbers saved |
| P6-7 | After launch | Read the counter at two and four weeks. Scroll depth cannot be measured with this setup; use `card_click` per band instead | Written note in `.agent/` |

## Order and total

1. **Now:** Phase 0, plus P5-1 and P5-2 (privacy wording, then events on the current pages). About two days.
2. **Four weeks of baseline**, no design work on the live site.
3. **Gate review** (about 2026-12-08 or later, once the baseline exists): the owner decides whether to redesign, and which logo, using the counter data and this proposal.
4. **Stage 1, if approved:** ring logo, tokens, data file with drift test, art-led home page. About 8 to 10 working days. This is the realistic scope for a solo studio and is worth doing on its own.
5. **Stage 2, only if stage 1 shows more plays and store clicks:** hub template, end cards, preview reskins, Hebrew URLs. About 10 to 12 further days, of which 5 to 6 depend on game art being exported from the game projects.
6. Motion and video last, if at all.

The estimates assume agent-built pull requests with owner review. They do not include waiting time for art, copy approval or native-language review.

## Decisions needed from the owner

1. At the gate review: redesign or not, and if so "Worlds, play first" or direction A.
2. Ring logo as the studio mark, as one candidate in the pending logo test.
3. Fate of the casino pages and root `privacy.html` and `support.html`.
4. The Baylight webhook field.
5. Whether Baylight and Paper Route art can be exported for the previews, or the previews are retired.
6. New wording for the privacy page before events ship.
7. Whether this `docs/` folder may be merged to `main` (it would be publicly served) or stays on a branch.
