# 09 - SEO and growth strategy

## 1. Technical SEO audit

Source: a scripted scan of all 41 HTML pages on `origin/main`, plus live checks.

| Area | State | Finding |
|---|---|---|
| Indexability | `robots.txt` allows all, sitemap listed | Good |
| Sitemap | 33 URLs, all resolve, generated and checked in CI | Good |
| Canonicals | Present on 36 of 41 pages | Missing on `404.html`, `casino/*`, `privacy.html`, `support.html` (SEO-01) |
| Redirects | http and www go to https apex with 301; the github.io host redirects | Good |
| Titles | All present | 13 over 60 characters, mostly the Ninely guides (SEO-02) |
| Descriptions | Present except `404.html`, `privacy.html` | 4 over 160 characters, 3 under 70 |
| Headings | Every page has an `h1` | 9 pages have 2 or 3 because languages are stacked on one URL (SEO-03) |
| Image alt and size | No image lacks alt, width or height | Good |
| Open Graph | On 16 pages | Missing on the playables for Middle East 2030 and Paper Route, and on guides for those games; `studio.jpg` shows an old name (SEO-04) |
| Structured data | Organization on home; VideoGame with Offer on three hubs; SoftwareApplication on Mila; TechArticle on guides | Organization logo is an SVG favicon; Google asks for a raster image (SEO-05) |
| Languages | 3 to 18 languages switched in the browser on one URL | Translated text is not separately indexable and there is no `hreflang` (SEO-06) |
| Duplicates | `casino/index.html` and `support.html` share a title and description; `morning-route` and `paper-route` share descriptions | SEO-07 |
| Legacy pages | `/casino/` and `/casino/trainer/` return 200 with no canonical and can be indexed. `/redline-2030/` is a deliberate canonical stub and stays | SEO-08 |
| Mobile rendering | Reflows at 390 px, Lighthouse SEO 100 | Good |
| Speed | See document 01 | Good |
| Cache | 10 minutes on everything | Host limit; acceptable |

## 2. Should every game have its own indexable page?

Yes, and they already do. Keep one hub per game as the canonical landing page, with the playable and guides beneath it. Do not create extra thin pages per feature or per keyword.

## 3. Language strategy for search

The current engine swaps text in place, which is fine for interface strings and wrong for content that should rank. Practical plan:

1. English is the default at the existing URLs.
2. Hebrew gets real URLs only where there is a Hebrew market and Hebrew body copy: Mila (already Hebrew), Middle East 2030 (`/middle-east-2030/he/`), and the home page (`/he/`).
3. Arabic stays as an in-place interface option until someone can maintain Arabic body copy. No Arabic landing pages yet.
4. Add `hreflang` pairs only between pages that exist as separate URLs.
5. The 19-language dictionary stays for legal pages, where it mirrors the apps' languages.

Do not machine-translate landing pages to fill out a language list.

## 4. Where visitors can realistically come from

| Source | Potential | Evidence and limits |
|---|---|---|
| Search for Sudoku techniques | Best organic chance | Eight guides exist with real worked boards. The terms are competitive and owned by large sites, so expect long-tail traffic only [J] |
| Search for the game names | Small but certain | Names are distinctive; the hubs should rank first for them [J] |
| Founder's posts in communities | Highest short-term | Already planned in the owner's notes: two useful posts a week with tagged links |
| Hebrew parents searching for English practice sheets | Good niche | The Mila worksheets are free, printable and real. Hebrew competition is lighter [J] |
| QR and offline | Small | Already instrumented |
| Paid | Out of scope | Gated by the owner |

The site has been live under three months and Search Console data has not been exported, so there is no ranking evidence yet. Every traffic estimate here is judgment.

## 5. Content worth making

Only content that a player would thank you for:

1. More Ninely technique guides, in the order players meet the techniques in the app. Already gated on the 28-day data.
2. A "how hints are graded" page for Ninely: which technique belongs to which level. The data exists in the engine.
3. Middle East 2030: the existing chair guide, plus short release notes when a version ships.
4. Mila: worksheet packs by grade (present) and a short page for parents on how to use ten minutes a day.
5. One studio page: who makes the games, contact, press kit.

Not recommended: a blog, daily puzzle archive pages, generated "answers" pages, keyword landing pages, AI-written articles.

## 6. Prioritised roadmap

| Priority | Item | Effort |
|---|---|---|
| 1 | Replace `studio.jpg` and add a raster logo for structured data | 1 hour |
| 2 | Decide and act on the casino pages and root `privacy.html` and `support.html`: `noindex` or removal. Leave `/redline-2030/` alone | 1 hour after the owner's decision |
| 3 | Shorten 13 titles, fix 2 missing and 7 weak descriptions | 2 hours |
| 4 | Add Open Graph tags to the playables and remaining guides | 1 hour |
| 5 | One `h1` per page; split Hebrew into its own URLs with `hreflang` | 1 day, with the redesign |
| 6 | Consolidate Paper Route URLs | 2 hours, with the redesign |
| 7 | Export Search Console once three months of data exist; pick the next guides from real queries | Owner |

## 7. Rules

- No ratings, review counts or install numbers in structured data or copy.
- No other company's game or brand names as keywords.
- Structured data only for facts visible on the page.
