# 14 - Independent Opus review

A separate Opus reviewer, acting as a creative director and chief product officer judging an outside agency's proposal, read documents 01 to 13 and 15, the findings register, the mockups and their captures, the site source, the owner's notes in `.agent/`, the Lighthouse results and the live site. The review was read-only. This document records what it verified, where it disagreed, and what was changed as a result.

## 1. Fact-check

| # | Claim | Result | Action taken |
|---|---|---|---|
| 1 | Baylight dock and Paper Route preview say "prototype" and "Development Notice" | Confirmed. The word is also in their meta descriptions and JSON-LD names | P0-7 widened to metadata |
| 2 | Casino trainer links to an App Store id with no listing | Confirmed | None |
| 3 | The trainer's Play package is "not on the developer page" | Understated: the package returns 404 | Corrected in 11, 13, 15, register |
| 4 | A test blocks App Store links until an app is live | Partly: it scans allowlisted pages only, so the dead casino links pass | Corrected; P0-5 now extends the test |
| 5 | `/redline-2030/` is a legacy page to remove or de-index | Wrong. It is a deliberate canonical stub, and `/redline-2030/privacy/` is the privacy URL registered in the Play Console for Middle East 2030 | Removed from every clean-up task; stated as "keep" in 01, 06, 09, 11, 13, 15 |
| 6 | `baylight/flags.json` exposes a hook with a token; the policy line was removed | Confirmed | None |
| 7 | Touch targets fail WCAG 2.5.8 | Heights plausible, "fail" wrong: Lighthouse passes and the exceptions apply | Reclassified as polish in 03, 11, 13, register |
| 8 | The privacy page does not mention local storage | Wrong: it does | Finding withdrawn |
| 9 | The counter matches the privacy page | Wrong by one event: `qr_land` is sent and not listed | New finding PRIV-03; P5-1 moved to the front |
| 10 | Mila rules | Confirmed | None |
| 11 | 28-day gate around 2026-12-08 | Date confirmed, meaning misread (see section 3) | Roadmap re-sequenced |
| 12 | Lighthouse 100 everywhere | Numbers confirmed; "every category" wrong: one page scores 96 for best practice | Wording corrected in 01, 15 |
| 13 | Lazy LCP image; 10-minute cache | Confirmed | None |
| 14 | About 1,500 visitors per arm for 5.0% to 7.5% | Confirmed (1,471) | None |
| 15 | Contrast ratios in 07 | All confirmed by recomputation | None |
| 16 | 41 pages, 137 files, 51 tests, counter on 23 pages | Confirmed | None |
| 17 | Canonicals on 36 of 41 pages | Confirmed | None |
| 18 | Share image says "aviisr-games" with four icons | Confirmed | None |
| 19 | No app on the App Store; 2 Ninely acquisitions in 28 days | Confirmed. Play install buckets could not be re-verified by the reviewer | Left as reported by the store check |

## 2. The 25 questions

| # | Question | Verdict | Reviewer's reasoning |
|---|---|---|---|
| 1 | Genuinely better? | Partly | Real art in each game's colours beats a list of links, but the buttons lead to emoji previews |
| 2 | Feels like a gaming studio? | Agree on desktop | On a phone the first screen is still text and icons |
| 3 | Distinctive identity? | Partly | Coloured bands with phone pairs are a common template; the distinctiveness is borrowed from the games, which is acceptable |
| 4 | Captures attention quickly? | Partly | In the 390 px capture the first play button sits near 800 px and the phones near 960 px; today's badge is at about 490 px |
| 5 | Every game presented appropriately? | Partly | Ninely and Middle East 2030 yes; Baylight and Paper Route bands promise a play experience the site cannot yet deliver |
| 6 | CTAs clear? | Agree | One play action and one badge in the same place for every game |
| 7 | Would players click? | Partly | They would click "Load a dock" and be disappointed |
| 8 | Unique value communicated? | Agree for two | Weak for Paper Route: "no forced ads" is a feature, not a hook |
| 9 | Animations useful? | Partly | Press feedback yes; icon lift and band reveal are decoration, and the reveal risks hiding content |
| 10 | Mobile exceptional? | Disagree | Hero plus five tall bands is a very long page; the icon rail strands Mila on its own row |
| 11 | Accessible? | Partly | Tokens sound; Ninely blue has no margin; the mockup dims text with opacity |
| 12 | Technically efficient? | Agree | Concrete budgets, static stack kept |
| 13 | SEO realistic? | Agree | Restrained, no thin pages; Hebrew URLs need a maintainer |
| 14 | Conversion measurable? | Partly | Tiny aggregate counts; scroll depth cannot be measured; events shipping with the redesign leave no baseline |
| 15 | Privacy claims accurate? | Partly | Two errors in the proposal's own privacy audit (items 8 and 9 above) |
| 16 | Security addressed? | Agree | Sensible severities; the note that `docs/` would be publicly served is a good catch |
| 17 | Overengineered? | Partly | The generator covers 6 of 41 pages, and availability strings also live in `i18n.js`, so it would not be a single source of truth |
| 18 | Unnecessary pages or features? | Few | A press kit link to a press kit that does not exist; the `/he/` home page is optional |
| 19 | Works for an independent studio? | Partly | Tone fits; 20 to 24 days is heavy when the games need the same person |
| 20 | New recurring costs? | Agree, none | |
| 21 | What stays? | | Static hosting, tests, honest copy, official badges, QR handoff, Ninely guides and daily puzzle, the Mila hub design, the counter and its rules |
| 22 | What goes? | | Casino pages and root `privacy.html` and `support.html`; "prototype" in copy and metadata; the AdSense meta tag |
| 23 | Weakly supported? | | The acquisition-engine framing at 1+ to 50+ installs; the benefit of device-aware order; the band reveal; the generator's return; the day estimate |
| 24 | What would a leading studio do differently? | | Lead with a short muted loop of the real game and one hero game; never ship a preview weaker than the product |
| 25 | Most compelling reason to explore? | | Seeing the real game move and playing within ten seconds. True today only for Ninely and Middle East 2030 |

## 3. Significant disagreements and how each was resolved

| # | Reviewer's point | Resolution |
|---|---|---|
| 1 | Removing `/redline-2030/` would break a store requirement | Accepted. Taken out of all tasks |
| 2 | The 28-day gate decides whether to redesign; it is not a launch date. The proposal built before the gate and chose the logo in advance | Accepted. New order: fixes and events, four weeks of baseline, gate review, then build. The ring logo is one candidate in the owner's pending logo test |
| 3 | Events must ship before the redesign or there is no baseline | Accepted. P5-1 and P5-2 moved to "now" |
| 4 | The home page would send traffic into the weak previews | Accepted. Baylight and Paper Route bands show badge and screenshots only until their previews are reskinned |
| 5 | The mockups flatter: every game-page mockup is Middle East 2030 | Accepted as a limitation and not fixed. A Baylight page mockup using the real dock interface should be made before the gate review |
| 6 | The hero has no image and pushes art below the fold on phones | Accepted. Specification now requires the first play button and a screenshot inside 700 px, one phone per band on mobile, bands capped near 600 px. The mockup itself was not redrawn |
| 7 | The generator is not justified yet | Accepted. Step one is a data file plus a drift test; templating only if hand edits prove costly |
| 8 | A studio header on Mila pages would be cross-promotion | Accepted. No studio navigation on `/mila/**`; a new test checks links, not just scripts |
| 9 | Touch targets are polish | Accepted |
| 10 | P0-7 must cover metadata | Accepted |
| 11 | Inconsistencies: which game is the best video candidate; "no build chain" beside a generator | Fixed: Paper Route first, Baylight second; wording corrected |
| 12 | The acquisition-engine framing is weakly supported at this install volume | Partly accepted. The framing is kept because it is the only model that feeds the games, but the plan is now staged so that stage 2 happens only if stage 1 moves the numbers |
| 13 | A leading studio would open with a video loop of one hero game | Not adopted for now. It needs captured footage, adds weight, and the site has no evidence yet about which game to feature. It stays an optional later step, with Morning Paper Route as the first candidate |

## 4. Unresolved risks

1. Who exports the Baylight and Paper Route art, and when. Five to six days of stage 2 depend on it.
2. What the owner's "logo Route C" is. The repository does not define it.
3. Whether the `flags.json` webhook is rate-limited. Nobody should test that by calling it.
4. GoatCounter's terms for commercial use if traffic grows.
5. The Hebrew home page and Middle East 2030 Hebrew URL need a native-speaking maintainer.
6. No real VoiceOver or TalkBack session has been run.
7. Competitor research was text-only; no reference site's motion or mobile layout was actually watched.
8. All conversion claims are judgment. There is no data yet that browser play increases installs.

## 5. Reviewer's verdict

The proposal points the right way and is honest about traffic and measurement, and most audit facts are accurate.

- Approve Phase 0 (without the redline deletion) and the Five Worlds look in principle.
- Do not approve the roadmap as first sequenced: measure first, then run the gate; fix the two previews before giving them home-page buttons; drop the templating generator for now.
- Realistic scope for a solo studio: Phase 0 plus an art-led home page, in 8 to 10 days.

The roadmap in document 13 and the summary in document 15 now follow this verdict.
