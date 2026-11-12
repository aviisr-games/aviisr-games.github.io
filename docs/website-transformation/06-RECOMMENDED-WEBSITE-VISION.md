# 06 - Recommended website vision

## 1. What the website is for

Four models were weighed against the facts: four games with 1+ to 50+ installs, one unreleased kids app, one maker, almost no traffic, a free host.

| Model | Fit | Why |
|---|---|---|
| A. Studio showcase | Secondary | There is no audience yet looking for the studio. A short, credible studio section is enough. |
| **B. Mobile acquisition engine** | **Primary** | Every visitor the studio earns (a post, a guide, a search, a QR code) should leave with a store visit or a browser play. This is the only model that feeds the games. |
| C. Browser gaming destination | Rejected as a goal | It needs content volume, retention features and ad sales the studio cannot staff, and ads are already deferred. |
| D. Hybrid | Rejected as a label | "Hybrid" would excuse an unfocused page. |

**Decision: Model B.** The browser playables are kept as the acquisition tool ("try it, then install"), not as a destination. The studio story is one short section. Search content is limited to what already works: the Ninely guides and daily puzzle.

A caution that belongs here: a store click is not an install, and the site will not create traffic by being prettier. The redesign raises the share of visitors who act. Traffic comes from the founder's posts and from search.

## 2. The chosen design

**Five Worlds (direction B) as the look, with the conversion rules of Play First (direction C).** Working name: "Worlds, play first".

From B: the charcoal studio frame, one full-width band per game in the game's own colours, real screenshots as the art, the "Pick a world" icon rail, game pages that borrow the game's look.

From C: a play button and the store badge in the first screen of every band and page, device-aware ordering of the two actions, an end-of-play card on every playable, and event measurement.

Not taken from C: the sticky store bar, the single featured game, the generic dark tiles.
Not taken from A: the cream studio background. Its restraint is kept in the spacing and in the absence of decoration.

Why not A: it is the safest and cheapest, and it would be a clear improvement. It does not answer the main weakness, which is that nothing on the page feels like a game.

## 3. Home page, top to bottom

1. **Header.** Ring and "Aviisr Games". Links: Games, Play now, Support. Language control with a visible label.
2. **Hero.** Headline "Pick a world." One line naming the five products in plain words. A rail of the five app icons, each a link to its band. The hero is kept short (about 300 px on a phone) so that the first band's play button and the top of a real screenshot fall inside the first 700 px. The mockup's hero is too tall on phones and must be tightened.
3. **Ninely band** (blue). "Sudoku that explains every move." Play today's puzzle, Google Play badge, two phones.
4. **Middle East 2030 band** (newsprint). "2030. Can you hold the region for one term?" Fiction tag in red. Read the 3-month briefing, badge, two phones.
5. **Baylight band** (navy). "Stack three. Ship the truck." Load a dock, badge, two phones.
6. **Morning Paper Route band** (sunrise). "Deliver before sunrise." Try the throw, badge, two phones.
7. **Mila band** (lilac, Hebrew, right to left). Parent-facing line, the three privacy facts, free worksheets as the action, "coming to the stores" as text. No store badge, no cross-links out of Mila pages.
8. **Studio section.** Three sentences about who makes the games and how, the contact address, a press kit link.
9. **Footer.** Support, Privacy, app-ads.txt, ads.txt, Security.

On phones each band shows one phone, not two, and is capped at about 600 px so the whole page stays near five screens.

Until the Baylight and Paper Route previews look like the games, their bands lead with the store badge and screenshots and carry no play button. A band never promises a play experience the site cannot deliver.

Band order is a list in one data file, so the featured game can change without a redesign. Start with the order above: Ninely first because its playable is the strongest and its guides bring search visitors.

Headline copy sources: Ninely and Baylight lines come from the live site; the Middle East 2030 line is the caption on its first store screenshot; "Deliver before sunrise" paraphrases the live description; "Pick a world." is new.

## 4. Game pages

One template, five skins. Order on every page:

1. Studio header.
2. Game masthead in the game's style.
3. Headline, one paragraph, play action and store badge (ordered by device), availability note.
4. Three facts, each verified against the store listing.
5. Screenshots; later a short muted gameplay loop where it helps.
6. The playable or a link to it.
7. Guides and help links (Ninely strategy, Middle East 2030 guide).
8. "More from Aviisr Games": two other games. Not on Mila.
9. Game footer: support, privacy.

## 5. Keep, redesign, remove, add, avoid

| | Items |
|---|---|
| Keep | Static hosting with plain committed HTML and no package manager; speed; honest availability copy; official badges; the counter and its privacy rules; Mila isolation; tests and generators; QR handoff; Ninely guides |
| Redesign | Home page; the five hubs; the look of the Baylight and Paper Route previews; shared header and footer; the share image |
| Remove | Green and gold palette; "prototype" and "Development Notice" wording; the lazy attribute on first screenshots; legacy casino pages and the root `privacy.html` and `support.html` (owner decision; `/redline-2030/` stays) |
| Add | Ring logo; per-game colour tokens; play buttons; end-of-play cards; device-aware action order; `play_start` and `play_complete` events; `hreflang` once languages have their own URLs; a short studio section |
| Avoid | Video hero; third-party fonts, scripts or embeds; ratings and install counts; a blog; sticky bars and pop-ups; website ads; a JavaScript framework |

## 6. Intended visitor experience

A phone visitor arrives from a link. Inside one screen they see the studio name, five icons and the top of a bright blue band with a Sudoku board on a phone. They tap "Play today's puzzle", solve a few cells, get a hint that explains itself, and at the end see one card: the badge and one sentence about what the app adds. If they scroll instead, each band is a different colour and a different kind of game, and each asks for the same two things in the same place.

## 7. Timing

The owner's notes make the hub redesign and the logo change wait on 28 days of counter data (about 2026-12-08). That gate decides whether to redesign at all; it is not a launch date. So the order is: Phase 0 fixes and the new measurement events now, four weeks of baseline, the gate review, and only then the build. This proposal and its mockups are input to that review, including the logo choice. Search Console data will not be available at the gate, because its export is deferred until three months exist.
