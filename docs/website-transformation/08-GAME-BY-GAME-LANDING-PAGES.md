# 08 - Game by game landing pages

Every claim below is taken from the live site or the Google Play listing as read on 2026-11-12. Before build, re-check each fact against the current store listing and the game repository. Do not add features, numbers or praise that are not in those sources.

Shared rules: one template, studio header, play action and store badge in the first screen, availability note from the data file, end-of-play card on the playable, events as in document 10.

---

## Ninely: Sudoku & Logic Puzzle

| | |
|---|---|
| Audience | Adults who play Sudoku and want to get better, including beginners who get stuck |
| Headline | Sudoku that explains every move. |
| Value proposition | Smart Hints name the technique and explain why a digit fits. Short drills for each technique. A new daily puzzle. Five levels from Easy to Master. |
| Verified against | Live hub, win card copy, Play listing |
| World | Blue `#2F6FED`, white, heavy sans |
| Showcase | The daily board itself, embedded at the top of the page on desktop; on phones a "Play today's puzzle" button |
| Band on home | Tag "Logic puzzle", two phones (hint screen, drill screen) |
| Video concept | 8 seconds: tap Hint, the explanation appears, the digit is placed. Only if captured from the real app |
| Primary action | Play today's puzzle (all devices); badge second on Android |
| Browser strategy | Keep the full daily puzzle. It is the strongest playable and the benchmark sites lead with a board. Add "Learn this technique" links (already present) and keep the win card |
| Page URL | `/ninely/` (hub), `/ninely/play/`, `/ninely/strategy/*` |
| Search terms | sudoku hints explained, how to solve sudoku, naked pairs, x-wing sudoku, daily sudoku |
| Events | `play_start/ninely`, `play_complete/ninely`, `hint_used/ninely`, `store_click/...` |

Fixes on the current pages: the hub has three `h1` elements (one per language section); eight guide titles are over 60 characters; first screenshot is lazy-loaded.

---

## Middle East 2030: Politics Sim

| | |
|---|---|
| Audience | Strategy and news readers, rated Everyone 10+ on Play. Hebrew and English today |
| Headline | 2030. Can you hold the region for one term? |
| Value proposition | Pick one of eight capitals. One decision a month is enough. One tap prints the morning paper, and the next front page shows what your choices did. Finished terms build a career with five ranks. |
| Verified against | Live hub (updated for version 3.1.0), store screenshot captions |
| Fiction rule | The line "A work of fiction set in an invented 2030: no event, headline or leader in it is real" appears in the first screen of the band, the page and the playable, in every language. It is never translated by a shared string that could be replaced |
| World | Newsprint `#F3EDE0`, ink, red `#B3261E`, serif. The page is laid out as a front page: masthead, rule lines, three columns |
| Showcase | The engraved illustrations in the store screenshots are the most distinctive art in the catalogue. Use them large |
| Video concept | 10 seconds: choose, tap Print, the paper slides in with the headline. Only from the real app |
| Primary action | Play the 3-month briefing; badge beside it |
| Browser strategy | Keep the briefing as a short, limited preview. Add one illustration per month from the real game and an end card with the result and the badge |
| Page URL | `/middle-east-2030/`. Give Hebrew its own URL (`/middle-east-2030/he/`) so each page has one `h1` and can carry `hreflang` |
| Search terms | political strategy game, politics simulator mobile, government sim, משחק אסטרטגיה פוליטי |
| Events | `play_start/me2030`, `play_complete/me2030/<ending>`, `store_click/...` |

Care point: the game is fiction about a real region. No real leader names, parties, flags or current events anywhere on the page, in alt text, or in search copy.

---

## Baylight: Truck Sort Puzzle

| | |
|---|---|
| Audience | Casual puzzle players, short sessions |
| Headline | Stack three. Ship the truck. |
| Value proposition | Tap a bay, stack three of a kind, ship the truck. One thumb. Short rounds. |
| Verified against | Live hub and home card |
| World | Night navy `#101A33`, crate colours yellow, red, blue, heavy sans |
| Showcase | Store screenshots show a clean dock with coloured parcels and trucks |
| Video concept | 6 seconds: three taps, a stack completes, the truck drives off. Second candidate for a video loop after Morning Paper Route |
| Primary action | Load a dock; badge beside it |
| Browser strategy | Keep the solver-checked puzzle logic. Replace the emoji and letter tiles with the game's parcel and truck art, remove "Interactive Web Prototype" and the "Development Notice", and add an end card. If the art cannot be exported, replace the playable with screenshots and a video loop |
| Page URL | `/baylight/`, `/baylight/dock/` |
| Search terms | sorting puzzle game, truck sort, color sort puzzle |
| Events | `play_start/baylight`, `play_complete/baylight`, `store_click/...` |

Security note for this folder: see finding SEC-01 in document 11 about `baylight/flags.json`.

---

## Morning Paper Route: Bike Game

| | |
|---|---|
| Audience | Casual arcade players |
| Headline | Deliver before sunrise. |
| Value proposition | Ride your morning route, throw the paper, deliver before sunrise. One thumb. "No forced ads during rides" is a supporting fact, not the hook. |
| Verified against | Live hub and home card |
| World | Sunrise orange gradient, dark ink, heavy sans |
| Showcase | Store screenshots show a low-poly 3D street with a throw arc. Strong and colourful |
| Video concept | 8 seconds of a real ride with one good throw. The best candidate for a video loop |
| Primary action | Try the throw; badge beside it |
| Browser strategy | The current preview is a timing bar with an emoji rider and does not resemble the game. Either rebuild it as a top-down street with the game's sprites, or retire it and lead with video and screenshots. Recommendation: retire it unless the reskin is cheap, because a weak preview undersells a good-looking game |
| Page URL | Consolidate on `/paper-route/`. Move the preview to `/paper-route/play/` and leave `/morning-route/*` as canonical stubs |
| Search terms | paper delivery game, paperboy style bike game, bike arcade game |
| Events | `play_start/paper-route`, `play_complete/paper-route`, `store_click/...` |

Do not use another game's name in page copy or metadata.

---

## Mila (מילה)

| | |
|---|---|
| Audience | Parents of Hebrew-speaking children in grades 1 to 6. The parent decides and installs |
| Headline | אנגלית לילדים דוברי עברית. |
| Value proposition | Practice at home at the child's pace: vocabulary, sounds, sentences and stories, a few minutes a day. No ads, no account, no data leaves the device. |
| Verified against | Live Mila hub and home card |
| Status | Not in either store. The page says "coming", shows no badge and no store link |
| World | Lilac `#F7F2FF`, purple `#6D3BDB`. The existing Mila page design is good and stays |
| Language | Hebrew first, right to left, with the existing English option |
| Trust block | Three facts, each one already published: no ads, no account, nothing leaves the device. Link to the privacy page. Add who makes it and a contact address |
| Showcase | The three existing screenshots |
| Primary action | Free printable worksheets, then parent information |
| Browser strategy | Worksheets only. No playable aimed at children on the site |
| Hard rules | No counter, no analytics events, no ads, no cross-promotion, no script from outside `/mila/`, no urgency or reward mechanics, nothing addressed to the child |
| Home band | Present, parent-facing, with the trust facts, as the home page already has a Mila card. The home page counter may count the home page view; it never fires an event for Mila links |
| Mila pages | Keep their own header. No studio navigation, no "Games" or "Play now" links, no "More from Aviisr Games": those would be cross-promotion. One "All games" link already exists and is the owner's call |
| Search terms | אנגלית לילדים, לימוד אנגלית לכיתה א, דפי עבודה באנגלית |
| When it launches | Change one status field in the data file; the badge appears and the "coming" text goes. Re-check the children's privacy statements against the shipped build first |

---

## Shared: screenshots and video

- Screenshots on the site are 480 px wide. For the new bands, export 720 px wide WebP versions and serve both with `srcset`.
- Video is optional and comes last. Rules if used: captured from the real build, muted, under 600 KB, with a poster image, `preload="none"`, started by a tap on phones, self-hosted, never autoplaying under reduced motion or data saver.
