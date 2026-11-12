# 11 - Security, privacy and accessibility

Testing was passive only: reading the repository, fetching public URLs, DNS and TLS lookups. Nothing was probed or changed.
Status labels: **Confirmed** (observed), **Potential** (plausible, not demonstrated).

## 1. Security

### What is already right (confirmed)

- HTTPS enforced; http and www redirect to the apex with 301.
- Certificate from Let's Encrypt, valid to 2027-02-06, renewed by GitHub Pages.
- DNSSEC delegation present; CAA limits issuance to Let's Encrypt and Google.
- SPF and DMARC (`p=quarantine`) on the mail domain.
- A content security policy on every page, limited to same-origin plus the counter image host; `object-src 'none'`, `base-uri 'self'`.
- No third-party scripts, fonts, frames or embeds anywhere.
- The shared i18n engine contains no `innerHTML` call and validates the language parameter against an allowlist.
- `security.txt` present and unexpired.
- CI actions pinned to commit hashes, read-only workflow permissions, Dependabot for actions, branch protection on `main`.
- Every link that opens a new tab carries `rel="noopener"` (17 of 17).

### Findings

| Id | Severity | Status | Finding | Recommendation |
|---|---|---|---|---|
| SEC-01 | Medium | Confirmed exposure, limited impact | `baylight/flags.json` is served publicly and contains an `all_clear_hook` URL for a Google Apps Script endpoint with a token in the query string. The Baylight source reads this field and calls the hook when a player clears every bay; the script emails the developer. Because the app must be able to call it, the token cannot be secret, so anyone can trigger those emails. A site commit also removed the hook from the Baylight privacy policy | Owner: confirm the endpoint can only send that one fixed email and is rate-limited, so abuse costs nothing but noise. Check whether the current build still calls it; if it does, the privacy policy should still mention the anonymous ping, and if it does not, empty the field |
| SEC-02 | Medium | Confirmed | `/casino/` and `/casino/trainer/` are live, indexable and outside the allowlist. The trainer links to an App Store id that returns no listing and to a Play package (`com.aviisrgames.blackjack`) that returns 404. The store-link test scans allowlisted pages only, so all tests pass while these dead links are live | Owner decision: remove, or add `noindex` and fix the dead links. Check first whether any store listing or app still points at `/privacy.html` or `/support.html`. Do not touch `/redline-2030/`: its privacy page is the URL registered in the Play Console for Middle East 2030 |
| SEC-03 | Low | Confirmed | Internal working files are served from the production domain: `/.agent/HANDOFF.md`, `/AGENTS.md`, `/tools/*.py`, test fixtures. The repository is public, so nothing secret is added, but it publishes process notes on the brand's domain | Later: deploy with a Pages workflow that uploads only site files. Not urgent |
| SEC-04 | Low | Confirmed, host limit | No HSTS, `X-Frame-Options`, `X-Content-Type-Options` or `Permissions-Policy` headers. GitHub Pages cannot set them, and `frame-ancestors` does not work in a meta policy | Accept. The pages hold no accounts or forms, so clickjacking has little to gain. A proxy in front would fix it at the cost of a new dependency; not recommended now |
| SEC-05 | Low | Confirmed | Policies allow `'unsafe-inline'` for scripts and styles on all pages except two, and twelve pages (guides, playables, worksheets) build some markup with `innerHTML`. The inputs appear to be the page's own data, which was not traced line by line | With the redesign, move inline scripts into files so `script-src 'self'` can be used on new pages, and keep user-supplied values out of `innerHTML` |
| SEC-06 | Low | Confirmed | Six different policy strings across pages | Reduce to two: one with the counter host, one without |
| SEC-07 | Info | Confirmed | `favicon.ico` returns 404 | Add the file |
| SEC-08 | Info | Potential | The domain is registered through a Squarespace-run registrar; registrar lock and two-factor sign-in could not be verified from outside | Owner: confirm both |
| SEC-09 | Info | Confirmed | The home page carries a `google-adsense-account` tag and `ads.txt` although website ads are deferred | Harmless. Remove the meta tag if ads stay off, to avoid implying otherwise |

No critical issue was found. No cross-site scripting path was found by reading the code; this was not a penetration test.

`app-ads.txt` (52 KB) and `ads.txt` are served with status 200 and were not changed. `app-ads.txt` is maintained by the app release process; the redesign must not move or rewrite it.

## 2. Privacy

| Topic | State | Note |
|---|---|---|
| Cookies | None | Confirmed in code |
| Local storage | Language choice only | Disclosed on the privacy page |
| Analytics | Counter as described in document 10 | Matches the privacy page except for one live event, `qr_land`, which the page does not list (PRIV-03) |
| New events | Would exceed what the privacy page lists | Update the page text first; owner approval needed |
| Consent banner | Not required for the current setup | Cookieless, aggregate, no identifiers. If a tool that sets cookies is ever added, this changes |
| Third parties | Counter image host only | Named on the privacy page |
| Retention | 400 days | Stated |
| Contact | Email link, no forms | Nothing is collected by the site |
| Children | Mila pages load nothing external and no counter | Enforced by tests. Keep it absolute |
| App privacy pages | One per game, listing ad partners | Maintained with each release. The owner has decided to remove four ad networks and add one in future versions; the policy pages must change in the same release, not before |
| Regional rules | No personal data processed by the site itself | GDPR, Israeli privacy law and COPPA obligations sit mainly with the apps |

Children's content: do not add ads, analytics, cross-promotion, social links or reward mechanics to anything a child might use. The home page's Mila band speaks to parents.

This is an engineering review, not legal advice.

## 3. Accessibility

Lighthouse reports 100 on all six tested pages. Automated checks catch only part of WCAG, so the manual findings matter more.

| Id | WCAG 2.2 | Finding | Fix |
|---|---|---|---|
| A11Y-01 | 2.5.8 Target size (passes through the spacing and inline exceptions; Lighthouse audit passes) | Hub links on cards are 23 px high, footer links 17 px. Polish, not a failure | Minimum 24 px height with padding |
| A11Y-02 | 3.3.2, 1.3.1 | Language `<select>` has no visible label | Label or labelled button |
| A11Y-03 | 1.1.1, 1.3.1 | Playables use emoji as game pieces; screen readers announce "package", "truck" and so on, in sequence | Real images with alt text, or hidden emoji with text equivalents |
| A11Y-04 | 2.4.6 | Several pages have more than one `h1` | One per page |
| A11Y-05 | 3.1.2 | Mixed-language sections are marked with `lang`; keep this in the redesign | Keep |
| A11Y-06 | 2.1.1 | Playables accept keyboard input (number keys, space); not fully verified for every control | Test each one during the reskin |
| A11Y-07 | Process | No real VoiceOver or TalkBack session has been run (noted in the owner's handoff) | Run one before launch |
| A11Y-08 | 1.4.3 | New world colours: all pairs pass, Ninely blue is at the limit | See document 07 |
| A11Y-09 | 2.3.3, 2.2.2 | New motion must stop under reduced motion; no autoplay video | Built into document 07 |

Already good: skip link, visible focus ring, reflow at 320 px, alt text and dimensions on every image, app names inside badge alt text.
