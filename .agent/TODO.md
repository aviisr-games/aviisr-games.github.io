# Founder TODOs (website)

Opened 2026-11-08. These need the founder's accounts or people. Agents handle code tickets in PRs.

## Verified status (2026-11-10)

An earlier report said every item was done. A check on 2026-11-10 found only the counter and the studio name done. Tick an item only with evidence.

| Item | Status | Evidence (2026-11-10) |
|---|---|---|
| Visit counter | Done | live since PR #15 |
| Studio name | Done | `d9c6cd0` "Aviisr Games" (pushed to `main` without a PR) |
| Protect `main` | Done 2026-11-10 | branch protection on, Dependabot for GitHub Actions configured |
| "Advertisements" boxes | Done 2026-11-10 | removed from 9 Ninely guides; test now fails if one returns |
| Unused Mila PNGs | Done 2026-11-10 | 5 unreferenced PNGs (5.9 MB) deleted; `og-mila.png` is used and kept; all remain in git history |
| Middle East 2030 | Partly done | owner decided 2026-11-10: no TestFlight link for now; term is 6 to 8 months (README fixed); Play rating Everyone 10+ vs adult positioning still needs an owner check in Play Console |
| Daily pack | Open, not due | ends 2027-02-05; regenerate before 2027-01-06 |
| GoatCounter settings | Unverifiable from outside | dashboard needs login |
| Play Console privacy URLs | Done 2026-11-10 | read in Play Console: ME2030 `/redline-2030/privacy/`, Baylight `/baylight/privacy.html`, Mila `/mila/privacy/`, Paper Route `/paper-route/privacy/`, Ninely `/ninely/privacy.html`. None uses root `/privacy.html`; all return 200 |
| Play Console campaign check, native he/ar read, traffic posts | Unverifiable from outside | no public trace |
| Search Console export, 5-person test | Deferred by founder | |
| 28-day gate | Not due | around 2026-12-08 |

- [x] **Turn on the visit counter.** Done 2026-11-09 (site `aviisrgames`).
  - Create a free GoatCounter site (cookieless).
  - Put its count URL in `assets/count.js` (`var ENDPOINT = 'https://<code>.goatcounter.com/count';`), or send the code to an agent.
  - It never runs on `/mila/**` or on privacy and support pages.
- [ ] **Export Search Console** performance data: Deferred (site has been live under 3 months; export once 3 months accumulate). Keep the CSV private (not in this public repo).
- [ ] **Play Console check.** Under Store listing acquisition, confirm that visits from links tagged `utm_source=aviisrgames&utm_campaign=<app>-<surface>` appear as a campaign or source once traffic accumulates.
- [ ] **Book 5 people** for a 15-minute remote test: Deferred by founder (not relevant currently).
- [ ] **GoatCounter settings.** Signed in, turn off optional data collection (screen size, region, language, sessions) so the dashboard matches the privacy page (pages, referring sites, Google Play clicks).
- [x] **Play Console privacy URLs.** Done 2026-11-10 (all app-specific; studio canonicals now `/privacy/` and `/support/`). Check that each game's listing links to its own privacy page (`/ninely/privacy.html`, `/middle-east-2030/privacy/`, `/baylight/privacy.html`, `/paper-route/privacy/`), not the root `/privacy.html`. Then make `/privacy/` and `/support/` the studio canonicals in `AGENTS.md` and `.agent/context.md`.
- [x] **Protect `main`.** Done 2026-11-10. Repository settings: require a pull request with passing checks, block force-push and deletion; turn on Dependabot for GitHub Actions.
- [x] **Decide: empty "Advertisements" boxes** Done 2026-11-10 (removed). on the 9 Ninely guide pages. Recommendation: remove them (they earn nothing). This would reverse the 2026-11-08 decision.
- [x] **Decide: public studio name:** Decided as "Aviisr Games" and standardized across the site, schema.org, footers, and app projects.
- [ ] **Middle East 2030.** Decide whether iPhone visitors see the TestFlight beta link; confirm term length (site says 6 to 8 months, README says 6 to 10); review the Play content rating (Everyone 10+) against the adult positioning.
- [x] **Confirm the 6.2 MB of unreferenced PNGs in `mila/assets/`** are unused (store tooling?) so an agent can delete them.
- [ ] **Native read** of the Hebrew and Arabic copy added on 2026-11-09 (homepage hero, Ninely benefits and post-solve card, Middle East 2030 card).
- [ ] **Traffic.** Two genuinely useful posts a week (for example a technique guide where a community allows it), each link tagged `?utm_source=<channel>&utm_campaign=<app>-<post>`.
- [ ] **Regenerate the Ninely daily pack before 2027-01-06** (it ends 2027-02-05). The weekly `store-links-and-names` workflow fails from that date as a reminder. Command under "Generators" in `.agent/HANDOFF.md`.
- [ ] **After 28 days of counter data (around 2026-12-08)**, run the Phase 2 gate. Write down hub pageviews, Play listing visitors and conversion per app, Search Console impressions on `/ninely/strategy/*`, and the logo test result.

## Decisions already made (2026-11-08)

- **Public studio name:** "Aviisr Games" (standardized across the site, schema.org, footers, and app projects).

- **Baylight public name:** "Baylight: Truck Sort Puzzle", matching the store.
- **Mila pages:** no analytics, no ads, no cross-promotion, ever.
- **No 14-day baseline before the badge release (T2).** The founder chose speed. The before/after read of T2 is therefore descriptive only.
- **Visit counter:** on since 2026-11-09 (GoatCounter, cookieless; never on Mila, privacy or support pages).
- **Website ads:** deferred. Revisit only at 50,000 or more eligible pageviews a month for 2 months, with a certified CMP in place.
