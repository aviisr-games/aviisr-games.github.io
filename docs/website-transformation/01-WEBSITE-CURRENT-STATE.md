# 01 - Website current state

Audit date: 2026-11-12. Source: `origin/main` at `41529cf`, the live site, and public store data.
Labels used in all documents: **[E]** evidence (measured or read), **[J]** professional judgment, **[S]** speculative.

## 1. What the site is

- Static HTML, CSS and vanilla JavaScript at the repository root. No framework, no bundler, no npm. [E]
- Hosted on GitHub Pages from `main` (`.nojekyll`, `CNAME` = `aviisrgames.com`). [E]
- 41 HTML pages, 137 tracked files, 14 MB working tree. [E]
- One shared stylesheet (`style.css`, 6.5 KB), one i18n engine (`assets/i18n.js`, 41 KB, 19 language dictionaries), a Play badge helper and a cookieless visit counter (`assets/count.js`, GoatCounter). [E]
- Python generators and tests in `tools/` (sitemap, Mila packs, Ninely daily pack). 51 tests pass. Two CI workflows, actions pinned by SHA, Dependabot on. [E]

## 2. Page inventory

| Area | Pages | Notes |
|---|---|---|
| Studio | `/`, `/support/`, `/privacy/`, `404.html` | Home is a 5-card list plus contact |
| Ninely | hub, `/play/` (daily Sudoku), `/duel/` (app link landing), `/strategy/` hub + 8 technique guides, privacy | Richest section; guides carry TechArticle markup |
| Middle East 2030 | hub, `/briefing/` (3-month playable), `/guide/`, support, privacy | Hub has English and Hebrew sections on one URL |
| Baylight | hub, `/dock/` (playable), privacy | English only |
| Morning Paper Route | `/paper-route/` hub, `/morning-route/preview/` (playable), privacy at both paths | Two folders for one game |
| Mila | hub, support, privacy, worksheets, answer key | Hebrew first, no counter, no external scripts |
| Legacy, not on the allowlist | `/casino/`, `/casino/trainer/`, `/privacy.html`, `/support.html` | Live and return 200, not linked from the home page, not in the sitemap, no canonical |
| Kept on purpose | `/redline-2030/`, `/redline-2030/privacy/` | Canonicalise to `/middle-east-2030/` by owner decision; the privacy path is the URL registered in the Play Console for Middle East 2030. Do not remove |

Internal link check: 639 references, 0 missing targets, 0 broken fragments. [E]

## 3. Store availability (verified 2026-11-12)

| App | Google Play (US and IL) | App Store | Install bucket shown on Play |
|---|---|---|---|
| Ninely: Sudoku & Logic Puzzle | Live | Not found | 1+ |
| Middle East 2030: Politics Sim | Live | Not found | 50+ |
| Baylight: Truck Sort Puzzle | Live | Not found | 10+ |
| Morning Paper Route: Bike Game | Live | Not found | 5+ |
| Mila | Not listed | Not found | n/a |

The home page statement "Four games on Google Play now; Mila and iPhone versions are coming" matches the stores today. [E]
App Store status comes from the iTunes lookup API (bundle id, name and seller searches returned nothing). An absent API result is strong but not absolute proof. [E]

## 4. Visual baseline

- Studio pages: dark green radial background, gold headings and links, translucent dark cards, system font. The colour tokens are named `--felt`, `--dark`, `--gold`: a casino-table palette inherited from the earlier casino pages. [E]
- The favicon is an amber ring on charcoal (`#FFB547` on `#15171C`), which does not match the green and gold site. [E]
- The share image `assets/og/studio.jpg` shows the old name "aviisr-games" and four icons, without Mila. [E]
- Each playable has its own unrelated look: cream newspaper (Middle East 2030 briefing), navy (Baylight dock), light blue (Morning Paper Route preview), green (Ninely). [E]
- The home page shows no gameplay image at all. Game art appears only as 56 px icons. [E]

## 5. Performance baseline (Lighthouse 12 lab runs, 2026-11-12)

| Page | Mobile perf / a11y / best practice / SEO | Mobile LCP | Transfer size |
|---|---|---|---|
| Home | 100 / 100 / 100 / 100 | 1.0 s | 47 KB |
| Ninely hub | 100 / 100 / 100 / 100 | 1.2 s | 82 KB |
| Ninely play | 100 / 100 / 96 / 100 | 1.2 s | 58 KB |
| Middle East 2030 hub | 100 / 100 / 100 / 100 | 1.0 s | 117 KB |
| Baylight dock | 100 / 100 / 100 / 100 | 0.8 s | 19 KB |
| Mila hub | 100 / 100 / 100 / 100 | 1.5 s | 144 KB |

These are lab numbers on a simulated mid-range phone. There is no field (real user) data: traffic is too low for the Chrome UX Report. [E]
Open items from the runs: cache lifetime is 10 minutes (a GitHub Pages limit), the first hub screenshot is lazy-loaded although it is the LCP element, `favicon.ico` returns 404 on `/ninely/play/`. [E]

## 6. What already works and must be kept

1. Speed and weight: 100 in every Lighthouse category on five of six pages, 96 for best practice on one because of a missing `favicon.ico`. Any redesign that drops these scores is a regression. [E]
2. Honest availability copy and the test that blocks App Store links until an app is live. [E]
3. Official Google Play badges, localised, with app names in the alt text. [E]
4. Privacy posture: no cookies, no third-party scripts, strict rules for Mila, a privacy page that matches the counter. [E]
5. The allowlist, sitemap generator, store-link checks and the weekly CI run. [E]
6. Real content with search value: eight Sudoku technique guides and a daily puzzle. [J]
7. Desktop QR handoff on hubs. [E]

## 7. Main weaknesses

1. The home page reads as a list of links, with no picture of any game. [E]
2. The browser playables are built from emoji and plain boxes, and two call themselves a "prototype" or carry a "Development Notice". They do not look like the games they promote. [E]
3. No studio identity: the palette is a leftover, the favicon and share image disagree with the site. [E]
4. No shared header or navigation. Each section has its own link row. [E]
5. Languages switch in place on one URL, so Hebrew and Arabic text cannot be indexed separately and there is no `hreflang`. [E]
6. Legacy casino pages are still served and indexable, and the store-link test does not scan them. [E]
7. Traffic and installs are very small, so the site cannot yet prove what converts. [E]

## 8. Constraints already decided by the owner (from `.agent/`)

- Mila pages: no analytics, no ads, no cross-promotion, no script from outside `/mila/`.
- Website ads deferred until 50,000 eligible pageviews a month for two months, with a certified consent platform.
- Hub redesign, more Ninely guides and a logo change are gated on 28 days of counter data (around 2026-12-08).
- No App Store link until an app is public there.
