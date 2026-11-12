# 05 - Three creative directions

Each direction has a working HTML mockup of the home page and of the Middle East 2030 page, built with the real store screenshots, icons, names and published copy. Open the HTML files from a checkout, or see the captures in `mockups/screens/`.

| | Home | Game page |
|---|---|---|
| A. Quiet Shelf | `mockups/a-quiet-shelf/home.html` | `mockups/a-quiet-shelf/game.html` |
| B. Five Worlds | `mockups/b-five-worlds/home.html` | `mockups/b-five-worlds/game.html` |
| C. Play First | `mockups/c-play-first/home.html` | `mockups/c-play-first/game.html` |

The mockups are static sketches. Links go nowhere, there is no device detection, and nothing in them is deployed.

Strategy context (see document 06): the site's job is to turn the visitors the studio earns into store visits and browser plays. All three directions serve that; they differ in how.

---

## A. Quiet Shelf (premium minimal)

**Concept.** A bookshop shelf. Warm paper background, one serif headline, one game per row with a single phone.

| Aspect | Specification |
|---|---|
| Palette | Paper `#F6F3EC`, ink `#15171C`, grey `#5B5F68`, rule `#DDD7C9`, amber `#B86A00` for small labels, ring `#FFB547` |
| Type | System serif for headings (Iowan Old Style, Palatino, Georgia), system sans for text |
| Layout | 1120 px column, large vertical rhythm, hairline rules between games |
| Header | Ring and name on the left, three links and the language on the right |
| Hero | The existing tagline as a large serif line and two sentences. No image |
| Game rows | Label, serif title, two lines, badge plus one text link, one phone on the right |
| Game page | Kicker, headline, one paragraph, badge and text link, three facts, three screenshots |
| Footer | One line |
| Motion | None beyond link underline and a 150 ms fade on images |
| Mobile | Rows stack, phone under text |
| Conversion | Badge is the primary action in every row; browser play is a text link |
| Accessibility | Highest of the three: high contrast, no motion, simple reading order |
| Technical | CSS only. About 2 KB of new CSS |
| Estimate | 4 to 5 working days for home plus five pages |

Strengths: calm, credible, cheapest, fastest, flatters Middle East 2030 and Mila.
Weaknesses: does not feel like games. Baylight and Paper Route look out of place on cream. The hero shows no game.
Risks: reads as a portfolio site; lowest curiosity for a first-time visitor.

---

## B. Five Worlds (playful, game-led)

**Concept.** The studio is a dark, quiet frame. Scrolling moves through five full-width worlds, each in its game's own colours and type.

| Aspect | Specification |
|---|---|
| Palette | Studio charcoal `#15171C`, ring `#FFB547`, text `#F5F2EA`; per-game colours from document 04 |
| Type | System rounded sans, weight 800 to 900, for studio and three games; system serif for Middle East 2030 |
| Layout | Full-bleed bands, 1120 px inner column, copy and phones alternate sides |
| Header | Ring, name, Games, Play now, Support, language |
| Hero | "Pick a world." with a five-icon rail that jumps to each band. No image to download beyond the icons |
| Game bands | Genre tag, one-line headline, one line of copy, a play button in the game's accent, the store badge, two fanned phones |
| Game page | Borrows the game's look. Middle East 2030 becomes a newspaper front page with masthead, fiction banner, columns |
| Footer | Charcoal, one line |
| Motion | Icon lift on hover, bands reveal once on scroll, phones settle 4 degrees. All off under reduced motion |
| Mobile | Bands stack, actions above the phones |
| Conversion | Play button first, badge second, both above the screenshots |
| Accessibility | Each band needs its own contrast check; right-to-left Mila band inside a left-to-right page |
| Technical | CSS custom properties per band. About 5 KB CSS, under 1 KB JS for reveal |
| Estimate | 7 to 9 working days for home plus five pages |

Strengths: each game looks like itself; the page has energy without stock decoration; real art does the work; clear difference from the current site.
Weaknesses: a long home page; five colour systems to keep accessible; more CSS to maintain.
Risks: could look like five unrelated sites if the frame (header, buttons, spacing) is not strictly shared.

---

## C. Play First (conversion platform)

**Concept.** A product page. The first screen is a featured game with a play button; below it, tiles that each offer "play" and "Google Play".

| Aspect | Specification |
|---|---|
| Palette | Near-black `#0F1115`, panel `#191C23`, line `#2A2F3A`, text `#F2F4F8`, grey `#A7AFBD`, action green `#35D07F`, ring `#FFB547` |
| Type | System sans, weight 800 headings |
| Layout | Featured panel, then a four-tile grid, then a Mila strip |
| Header | Ring, name, Play now, Games, Support, language |
| Hero | Featured game (Ninely daily puzzle) with a green "Play in your browser" button, the badge, and an iPhone note |
| Game tiles | Square crop of a screenshot, title, one line, two equal buttons |
| Game page | Pitch panel on the left, the live playable on the right, screenshots below |
| Footer | One line, plus a sticky store bar on phones |
| Motion | Button press feedback only |
| Mobile | Two-column tiles, sticky bottom bar with the store badge for the page's game |
| Conversion | Strongest: every tile has both actions, the store action never leaves the screen |
| Accessibility | Sticky bar must not cover focus; green on black passes |
| Technical | Device detection script for the sticky bar; playable embedded in the game page |
| Estimate | 8 to 10 working days, mostly embedding the playables |

Strengths: shortest path to a play or a store visit; easy to measure; compact.
Weaknesses: generic app-store look; one featured game hides the others; the sticky bar is the pattern users dislike most; no studio character.
Risks: featuring the two weak previews (Baylight, Paper Route) beside the pitch exposes them more.

---

## Comparison

Scores 1 to 5, judgment of this audit. [J]

| Criterion | A | B | C |
|---|---|---|---|
| Visual quality | 4 | 5 | 3 |
| Brand memorability | 3 | 5 | 2 |
| Player appeal | 2 | 5 | 4 |
| Clarity | 5 | 4 | 4 |
| Conversion potential | 3 | 4 | 5 |
| Mobile usability | 4 | 4 | 4 |
| Accessibility | 5 | 3 | 4 |
| SEO suitability | 4 | 4 | 4 |
| Performance | 5 | 4 | 4 |
| Development cost (5 = cheap) | 5 | 3 | 3 |
| Maintenance (5 = light) | 5 | 3 | 3 |
| **Total** | **45** | **44** | **40** |

The totals are close on purpose: A wins on cost and safety, B on appeal, C on conversion mechanics. The decision is in document 06.
