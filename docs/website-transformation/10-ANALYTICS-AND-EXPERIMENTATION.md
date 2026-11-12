# 10 - Analytics and experimentation

## 1. What is implemented today

| Item | State |
|---|---|
| Counter | GoatCounter, cookieless, loaded by `assets/count.js` on 23 pages |
| Never loaded on | `/mila/**`, privacy and support pages; a path guard inside the script repeats the Mila rule |
| Respects | Do Not Track and Global Privacy Control |
| Sends | Page path, referrer origin, and two events: `store_click/<package>/<page>` and `qr_land/<page>` |
| Settings | Sessions, screen size, country, region and language are switched off; 400-day retention (owner-confirmed) |
| Campaign tags | Every Google Play link carries `utm_source=aviisrgames`, `utm_medium=<surface>`, `utm_campaign=<app>-<surface>` |
| GA4 | Not installed |
| Search Console | Verified (two verification tags), no export yet |
| Consent banner | None, and none needed for the current setup |
| Tests | `tools/test_store_links_and_counter.py` guards the counter rules |

This is a sound base. The recommendation is to extend it, not replace it.

## 2. Why not GA4

- It sets cookies and sends data to a third party, which would require a consent banner and a rewrite of the privacy page.
- The content security policy would have to open to Google hosts.
- At this traffic level it would report nothing the counter cannot.
- The privacy posture is a selling point for Mila's parents.

Revisit only if paid acquisition starts and needs it.

## 3. Event specification

All events are GoatCounter events (`e=true`) whose name is a path. No user ids, no session ids, no free text.

| Event name | Fires when | Once per | Notes |
|---|---|---|---|
| (page view) | Page load | Load | Exists |
| `store_click/<package>/<page>` | Click on a Google Play link | Link per page view | Exists. Extend the selector to `apps.apple.com` when a listing goes live |
| `qr_land/<page>` | Arrival with `?src=qr` | Load | Exists |
| `card_click/<game>/<target>` | Click in a home band; target is `play`, `hub` or `rail` | Target per page view | New |
| `play_start/<game>` | First input in a playable | Page view | New |
| `play_progress/<game>/<step>` | A defined midpoint: 20 cells filled, month 2, 5 parcels shipped | Step per page view | New |
| `play_complete/<game>` | Round finished; Middle East 2030 adds the ending code | Page view | New |
| `more_click/<from>/<to>` | Click in "More from Aviisr Games" | Pair per page view | New |
| `lang/<code>` | Explicit language change | Page view | New. The page already stores the choice locally |
| `contact_click/<page>` | Click on the mail link | Page view | New |
| `video_start/<game>`, `video_end/<game>` | Only if video ships | Page view | Later |

Not collected: card impressions. Counting what scrolled into view adds requests and noise for little value at this scale.

Mila: none of these events exist on `/mila/**`. On the home page, links into Mila fire nothing.

Privacy text: the privacy page lists what the counter records ("the page address, the referring website, clicks on a Google Play button"). It already omits one live event, `qr_land` (arrival from the QR code). Before any new event ships, that sentence must be updated to include QR arrivals, plays of browser games and navigation clicks. This is a published policy change and needs the owner's approval.

Timing: these events ship before the redesign, on the current pages, so that four weeks of baseline exist. Shipping them together with the new pages would leave nothing to compare against.

## 4. Funnels

| Funnel | Steps | Read as |
|---|---|---|
| Discovery to store | Home view, `card_click`, hub or playable view, `store_click` | Counts per week per game; ratios between steps. At current volumes expect single digits per week: read them as counts, not rates |
| Discovery to play | Home view, `play_start`, `play_progress`, `play_complete` | Same |
| Play to store | `play_complete`, `store_click` with `utm_medium=playable-win` | The test of whether browser play helps installs |
| Cross-promotion | Playable or hub view of A, `more_click/A/B`, `store_click` for B | Counts |

Because sessions are off, these are aggregate ratios, not per-visitor paths. That is enough for the decisions in this plan.

## 5. Attribution: what can and cannot be known

- A store click is not an install. The site can only count clicks.
- Play Console showed no UTM dimension for this account on 2026-11-10; with a handful of installs, any such report would be hidden by Google's privacy thresholds anyway.
- Google documents a `referrer` parameter on Play URLs that an app can read through the Install Referrer API. Using it means app-side work in each game and a privacy review. Worth doing only when a campaign is large enough to need it. [S: confirm the current Play Console behaviour before investing]
- For iOS, Apple offers campaign links (`pt`, `ct` parameters) that report in App Store Connect. Add them when the first listing goes live.
- Until then the honest measure is: store clicks from the site, set beside the Play Console's total listing visitors for the same weeks.

## 6. Does browser play help or hurt installs?

It can do either. A full daily Sudoku in the browser may satisfy a visitor who would otherwise install; a short taste may send them to the store. There is no data yet.

How to find out without a split test:

1. Record `play_complete` and `store_click` with `utm_medium=playable-win` for four weeks.
2. Compare store clicks per visitor on pages with a playable against hubs without one.
3. For Ninely, keep the full daily puzzle (it is the reason to return and the anchor for the guides) and rely on the win card and the drills, levels and progress that only the app has.
4. For the other games, keep previews short by design: one dock, three months, one street.
5. Remove or restrict nothing until the numbers exist.

## 7. Dashboard

GoatCounter's own dashboard, private, plus one saved weekly table (a spreadsheet kept outside the public repository):

| Row | Columns |
|---|---|
| Per game | Hub views, playable starts, completions, store clicks, store clicks per hub view |
| Site | Home views, top referrers, top pages, browser and system split |
| From Play Console | Listing visitors and installs per app, entered by hand |

Country, language and device model are deliberately not collected. Do not add them to fill a dashboard.

## 8. Experiment plan

See document 03, section 8 for the tests and the sample-size reasoning. Rules:

- One change at a time per page, four weeks before and four after.
- Write the expected direction down before shipping.
- Report results as "descriptive", never as "significant", below about 1,500 visitors per arm.
- A split test needs a randomiser and a variant flag in the event name (`store_click/.../v2`). Build it only when traffic justifies it.
