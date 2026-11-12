# 12 - Technical architecture

## 1. Is a rebuild needed?

No. The current stack (static files on GitHub Pages, no build chain) scores 100 in every Lighthouse category, costs nothing, has no dependencies to patch, and is already guarded by 51 tests. The weaknesses found are in design and content, not in technology.

What the stack does lack is a single source of truth: game names, store links, availability and navigation are repeated by hand across 41 pages, and tests exist mainly to catch the resulting drift.

## 2. Options

| Option | What it means | For | Against |
|---|---|---|---|
| 1. Hand-authored HTML plus shared CSS | Rewrite home and hubs by hand against `assets/site.css` | Zero new tooling | Header, footer, store links and status repeated on every page; a launch means editing many files |
| **2. Small Python generator (recommended)** | `site/games.json` plus templates; `tools/build_pages.py` writes the home page and the five hubs into the repository, like `build_sitemap.py` does today | One place for names, links, status, order; fits the existing pattern of generators with `--check` in CI; no npm; output is still plain committed HTML | One more script to maintain; contributors must run it |
| 3. Static site generator (Eleventy, Astro, Hugo) | Adopt a framework and a Pages build workflow | Components, layouts, image pipeline | Adds a dependency tree and a build step for six pages; the owner's notes say "do not invent npm commands" |
| 4. Client-side framework | React or similar | None at this size | Slower, heavier, worse for search, more to secure |

**Decision: option 2, in two steps.** Options 3 and 4 solve problems this site does not have.

Step one, now: add `site/games.json` and a drift test that checks the existing hand-written pages and the availability strings in `assets/i18n.js` (for example `iphoneSoon`, in many languages) against it. This gives one place to record status without any templating.

Step two, only if needed: add templates and `build_pages.py`. The trigger is evidence that hand edits are costly, for example the first App Store launch touching more than a handful of files. The generator would cover 6 of 41 pages in English and Hebrew, so its return is unproven. Sections 3 and 4 below describe step two.

## 3. The data file

`site/games.json` (name and place to be confirmed at build time):

```json
{
  "order": ["ninely", "middle-east-2030", "baylight", "paper-route", "mila"],
  "games": {
    "ninely": {
      "title": "Ninely: Sudoku & Logic Puzzle",
      "tag": "Logic puzzle",
      "headline": "Sudoku that explains every move.",
      "lead": "Smart Hints teach the logic step by step. A new daily puzzle every day.",
      "hub": "/ninely/",
      "play": { "url": "/ninely/play/", "label": "Play today's puzzle" },
      "googlePlay": { "status": "live", "package": "com.aviisrgames.ninely" },
      "appStore": { "status": "none", "id": null },
      "screens": ["ninely-1", "ninely-2"],
      "analytics": true,
      "crossPromo": true
    }
  }
}
```

- `status` is `live`, `soon` or `none`. Templates render a badge only for `live`, the "coming" text for `soon`, and the "Not on iPhone yet" note for `none`.
- When an iOS app is approved, the release step is: set the id and `live`, run the generator, and the existing weekly link check confirms the listing responds. This replaces the hand-edited availability sentences.
- Mila has `analytics: false` and `crossPromo: false`; the generator refuses to emit the counter or cross links for it, and a test asserts that.
- Per-language strings stay in the page dictionaries for now; the data file holds English and, for Mila, Hebrew.

## 4. File layout after the change

```
assets/site.css          new: tokens, frame, bands, components
assets/site.js           new: device ordering, reveal, events (deferred, under 3 KB)
assets/count.js          existing, extended with the new events
assets/logo/             new: ring SVGs, favicon.ico, touch icon
assets/screens/          existing 480 px plus new 720 px versions
site/games.json          new: single source of truth
site/templates/          new: home and hub templates (plain text with placeholders)
tools/build_pages.py     new: generator with --check
index.html, */index.html generated and committed
style.css                kept for legal, support and legacy pages
```

Generated pages are committed, so GitHub Pages keeps serving plain files and a failed generator can never break the live site.

## 5. Device-aware actions

- The HTML ships both actions in a safe default order: play first, store second.
- `site.js` reads the user agent once. Android: move the store badge first. iOS: hide the Google Play badge inside bands and show the note. Desktop: default order plus the QR block.
- If the script fails or is blocked, the page is still complete and honest.
- User agent sniffing is acceptable here because it only reorders two visible links; it does not gate content.

## 6. Images and video

- Screenshots: WebP, two widths (480 and 720), `srcset` and `sizes`, explicit dimensions, lazy below the first band.
- First band: first image `fetchpriority="high"`, not lazy. This also fixes the lazy LCP image found on today's hubs.
- Icons: existing 128 px WebP.
- Video, if ever added: self-hosted MP4 (H.264) with a WebP poster, under 600 KB, `preload="none"`, tap to play on phones. The content security policy needs `media-src 'self'`, which `default-src 'self'` already grants.
- No image CDN, no third-party player.

## 7. Content security policy for new pages

```
default-src 'self'; script-src 'self'; style-src 'self';
img-src 'self' data: https://aviisrgames.goatcounter.com;
object-src 'none'; base-uri 'self'; form-action 'none'
```

New pages keep scripts and styles in files so `'unsafe-inline'` can go. Mila pages use the same policy without the counter host.

## 8. Hosting and deployment

- Stay on GitHub Pages from `main`.
- Optional later step: a Pages workflow that publishes only site files, so `.agent/`, `tools/` and `docs/` stop being served (finding SEC-03). Until then, note that this `docs/` folder would itself be served at `aviisrgames.com/docs/...` if merged to `main`. Keep it on a branch, or add the workflow first.
- No proxy or CDN in front. The 10-minute cache lifetime is acceptable at this size.
- Preview: `python3 -m http.server 8000` from the repository root, as today.

## 9. Tests to add

| Test | Asserts |
|---|---|
| Generator freshness | `build_pages.py --check` fails if committed pages differ from the data file |
| Status rules | No store badge for an app whose status is not `live`; no App Store URL unless `appStore.status` is `live` |
| Mila isolation | Generated Mila output has no counter, no cross links, no script outside `/mila/` |
| Budgets | Home HTML plus CSS plus first-band images under the budget in document 07 |
| Contrast | The token pairs in document 07 meet 4.5:1, computed in the test |
| One `h1` | Every generated page has exactly one |
| Existing suites | Allowlist, store names, sitemap, counter rules keep passing |

## 10. Maintenance cost

Recurring cost stays at zero. Routine work after the change: edit one JSON file for a launch, a rename or a reorder; add screenshots when a store listing changes; keep the privacy pages in step with app releases as today.
