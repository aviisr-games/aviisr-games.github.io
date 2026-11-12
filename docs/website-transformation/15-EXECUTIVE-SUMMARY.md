# 15 - Executive summary

Audit, research and plan only. Nothing on the live site was changed.

## 1. Overall assessment

aviisrgames.com is a technically excellent, visually anonymous site. It scores 100 in almost every Lighthouse category (one page loses four points to a missing favicon file), loads in about one second on a phone, tracks nothing personal, and tells the truth about where the games are available. It also shows no picture of any game on its home page, wears a colour scheme left over from an older casino project, and offers two browser previews that look worse than the games they advertise.

## 2. What works today

1. Speed: 19 to 144 KB per page, no third-party code.
2. Honesty: availability copy matches the stores; a test blocks App Store links until an app is live.
3. Privacy: cookieless counter, strict isolation of the children's app pages.
4. Engineering: 51 tests, generated sitemap, weekly store-link check, pinned CI.
5. Real content: a daily Sudoku and eight worked technique guides.
6. Official, localised store badges with campaign tags, and a desktop QR handoff.

## 3. Biggest problems, ranked

1. No game art on the home page.
2. Baylight and Morning Paper Route previews are emoji prototypes that undersell the games.
3. No studio identity; favicon, palette and share image disagree.
4. Availability and names are hand-copied across pages, so launches mean many edits.
5. No shared navigation; Paper Route is split across two folders.
6. Legacy casino pages still live and indexable, with dead App Store and Google Play links that the tests do not scan.
7. Hebrew and Arabic text is not indexable on its own URLs.
8. No measurement of browser play, so its effect on installs is unknown.

## 4. Top 15 improvements

| # | Improvement | Impact | Confidence | Effort | Risk |
|---|---|---|---|---|---|
| 1 | Art-led home page with one colour band per game | High | High | 2 days | Low |
| 2 | Play button and store badge in the first screen of every band | High | Medium | 0.5 day | Low |
| 3 | Reskin or retire the Baylight and Paper Route previews | High | Medium | 2 to 5 days | Medium: needs game art |
| 4 | One data file for names, links and store status, with a drift test | Medium | High | 0.75 day | Low |
| 5 | Ring logo and charcoal studio frame | Medium | Medium | 1.5 days | Low |
| 6 | Remove "prototype" wording now | Medium | High | 2 hours | None |
| 7 | End-of-play cards with the store action | Medium | Medium | 1 day | Low |
| 8 | Play and navigation events in the existing counter, shipped first so a baseline exists | Medium | High | 1 day | Needs privacy text change |
| 9 | Device-aware action order | Medium | Medium | 0.5 day | Low |
| 10 | Retire legacy pages | Medium | High | 1 hour | Check store listings first |
| 11 | New share image, favicon.ico | Low | High | 1 hour | None |
| 12 | Metadata clean-up | Low | High | 0.5 day | None |
| 13 | Hebrew on its own URLs with `hreflang` | Medium | Medium | 1 day | Copy review |
| 14 | Game pages that borrow each game's look | Medium | Medium | 3 days | Low |
| 15 | "More from Aviisr Games" on hubs | Low | Medium | 0.5 day | None, never on Mila |

## 5. Three creative directions

| | A. Quiet Shelf | B. Five Worlds | C. Play First |
|---|---|---|---|
| Idea | Paper, serif, one phone per game | Dark studio frame, one bright band per game | Featured playable, tiles with two buttons, sticky store bar |
| Best at | Calm, cost, accessibility | Appeal, identity, showing each game as itself | Shortest path to play or store |
| Weak at | Feels like a portfolio, not games | Long page, five palettes to maintain | Generic look, exposes weak previews |
| Effort | 4 to 5 days | 7 to 9 days | 8 to 10 days |

Mockups: `mockups/` (HTML) and `mockups/screens/` (captures).

## 6. Recommended design

**"Worlds, play first": the look of B with the conversion rules of C**, without C's sticky bar and without video. Strategy: the site is an acquisition tool. Browser play is the taste, the store is the goal, the studio story is one short section.

## 7. Home page vision

Header with the ring and name. Hero: "Pick a world." and five app icons. Then five full-width bands: Ninely in blue, Middle East 2030 as newsprint, Baylight in night navy, Morning Paper Route in sunrise orange, Mila in lilac and Hebrew. Each band: genre tag, one line, a play button, the store badge, two phones with real screenshots. Then a three-sentence studio section and the footer.

## 8. Game-specific

- **Ninely:** lead with the live daily board; keep the full puzzle; the app's drills and levels are the reason to install.
- **Middle East 2030:** make the page a newspaper front page; fiction line in the first screen in every language; Hebrew on its own URL.
- **Baylight:** keep the puzzle logic, replace emoji with the game's art, drop the development notice. Until then its home band shows the badge and screenshots, with no play button.
- **Morning Paper Route:** the preview is a timing bar that looks nothing like the 3D game; rebuild with game sprites or retire it and lead with screenshots. The best candidate for a short video loop.
- **Mila:** speak to parents in Hebrew; three trust facts already published; worksheets as the action; no badge until launch; no analytics or cross-promotion, ever.

## 9. Conversion strategy

Same two actions in the same place for every game. Android sees the store first, iPhone sees browser play and an honest note, desktop sees both plus the QR code. Every playable ends with one card. No ratings, counts, pop-ups or urgency.

## 10. Brand and logo

Refine, do not rebrand. Promote the existing amber ring to the studio mark, retire green and gold, let each game supply the colour. No change to app icons.

## 11. Growth and SEO

Best chances: long-tail Sudoku technique searches through the existing guides, the game names themselves, Hebrew worksheet searches for Mila, and the founder's own posts. No blog and no generated pages.

## 12. Analytics

Keep the cookieless counter, add play and navigation events, read four funnels weekly. Do not add GA4. Store clicks are the measure; installs cannot be attributed at this volume. No split tests until a page has about 3,000 visitors a month.

## 13. Security and privacy

No critical issue. To act on: a public webhook token in `baylight/flags.json` (confirm it is harmless), legacy casino pages with dead store links, internal working files served from the domain, and a privacy page sentence that already omits one live event (QR arrivals) and must be updated before new events ship. `/redline-2030/` must stay: its privacy page is registered in the Play Console.

## 14. Roadmap

1. Now: Phase 0 fixes and the new counter events on the current pages (about two days).
2. Four weeks of baseline.
3. The owner's gate review decides whether to redesign and which logo.
4. Stage 1 if approved: logo, tokens, data file, art-led home page (8 to 10 days).
5. Stage 2 only if stage 1 moves the numbers: hubs, end cards, preview reskins, Hebrew URLs (10 to 12 days, partly dependent on game art).

## 15. Quick wins

Share image, `favicon.ico`, eager first screenshot, metadata, remove "prototype" wording from copy and metadata, decide the casino pages, privacy wording and events.

## 16. What not to build

A video hero, a blog, web fonts, a JavaScript framework or static site generator, a page templating generator before it is proven necessary, studio navigation on Mila pages, GA4, website ads, a sticky store bar, pop-ups, ratings or install counters, a newsletter, user accounts, Arabic landing pages without a maintainer, split-test tooling.

## 17. Final recommendation

**What would a world-class agency build?** A fast, quiet studio frame around five loud, distinct game worlds, using the games' own art, with one play action and one store action per world, on the same static stack. It would spend the budget on making the previews look like the games, not on site decoration, because the games are the brand.

**What makes a visitor say "these look interesting, I want to try one"?** Seeing the actual game in the first screen, in its own colours, with a one-line promise they can test in ten seconds without installing anything. Today the site can keep that promise for Ninely and Middle East 2030 only.

**The three changes with the greatest likely effect:**
1. Real game art in full-width bands on the home page.
2. Previews that look like the games, each ending with a store card.
3. A play button and the store badge together in the first screen of every game.
