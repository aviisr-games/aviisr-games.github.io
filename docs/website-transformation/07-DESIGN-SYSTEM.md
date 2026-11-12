# 07 - Design system

Implementation target: one new stylesheet, `assets/site.css`, plain CSS custom properties, no framework, no preprocessor. `style.css` stays for legal and support pages until they are migrated.

## 1. Colour tokens

### Studio frame

| Token | Value | Use | Contrast |
|---|---|---|---|
| `--studio-bg` | `#15171C` | Header, hero, footer | |
| `--studio-text` | `#F5F2EA` | Text on studio background | 16.0:1 |
| `--studio-dim` | `#A7AFBD` | Secondary text | 8.1:1 |
| `--studio-ring` | `#FFB547` | Logo, highlight word | 10.2:1 |
| `--focus` | `currentColor` | Focus ring, 3 px, 3 px offset | Inherits text contrast |

### Game worlds

Each band or game page sets five variables on its root element.

| World | `--w-bg` | `--w-text` | `--w-accent` (button) | `--w-on-accent` | Text contrast | Button contrast |
|---|---|---|---|---|---|---|
| Ninely | `#2F6FED` | `#FFFFFF` | `#FFFFFF` | `#1746B0` | 4.55:1 | 8.3:1 |
| Middle East 2030 | `#F3EDE0` | `#1B1A17` | `#1B1A17` | `#F3EDE0` | 14.9:1 | 14.9:1 |
| Baylight | `#101A33` | `#EAF0FF` | `#FFD23F` | `#101A33` | 15.1:1 | 11.9:1 |
| Morning Paper Route | `#FF9A3D` to `#F4743B` | `#1E2433` | `#1E2433` | `#FFFFFF` | 5.5:1 to 7.3:1 | 15.5:1 |
| Mila | `#F7F2FF` | `#3B1E7A` | `#6D3BDB` | `#FFFFFF` | 11.6:1 | 6.4:1 |

Notes:
- Ninely white on `#2F6FED` passes AA for body text by a hair (4.55:1). Darken the blue to about `#2A63D9` at build time, or keep body text at 18 px and above.
- Middle East 2030 red `#B3261E`: 5.6:1 on newsprint, 6.5:1 under white text.
- Concept A's amber label `#B86A00` on paper is 3.7:1 and would fail for small text. It is not used in the chosen design.
- All ratios were computed with the WCAG 2 formula from the hex values above.

No light or dark switch. The studio frame is dark and each world fixes its own background, so `prefers-color-scheme` is not used. Legal and support pages keep one readable theme.

## 2. Typography

System stacks only. No web fonts: the content security policy allows only same-origin files, and a font file would be the largest asset on the page.

| Token | Stack |
|---|---|
| `--font-sans` | `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif` |
| `--font-round` | `ui-rounded, "SF Pro Rounded", var(--font-sans)` |
| `--font-serif` | `"Iowan Old Style", "Palatino Linotype", Georgia, serif` |

Hebrew and Arabic fall back to the platform fonts through the same stacks. Rounded display type is an Apple-only enhancement; other platforms show the regular sans at the same weight.

| Step | Size | Line height | Weight | Use |
|---|---|---|---|---|
| `--t-hero` | `clamp(2.6rem, 8vw, 5rem)` | 1.0 | 900 | Home headline |
| `--t-h1` | `clamp(2.2rem, 6vw, 4rem)` | 1.05 | 800 or 700 serif | Game page headline |
| `--t-h2` | `clamp(2rem, 5vw, 3.2rem)` | 1.05 | 900 | Band headline |
| `--t-h3` | `1.3rem` | 1.25 | 700 | Fact titles |
| `--t-lead` | `1.15rem` | 1.5 | 400 | Band copy |
| `--t-body` | `1rem` | 1.6 | 400 | Text |
| `--t-small` | `0.9rem` | 1.4 | 400 | Notes |
| `--t-tag` | `0.78rem`, tracking 0.1em, upper case | 1 | 800 | Genre tags |

Hebrew and Arabic: no upper case, no letter spacing. Set `letter-spacing: 0` and `text-transform: none` under `:lang(he), :lang(ar)`.

## 3. Spacing, radius, elevation

| Scale | Values |
|---|---|
| Spacing | 4, 8, 12, 16, 24, 32, 44, 64, 88 px (`--s-1` to `--s-9`) |
| Radius | 8 (inputs), 14 (buttons), 22 (panels), 28 (phone frame), 999 (tags) |
| Elevation | `--e-1: 0 4px 0 rgba(0,0,0,.25)` (button), `--e-2: 0 18px 40px rgba(0,0,0,.28)` (phone) |
| Page column | max 1120 px, 20 px side padding |
| Band padding | 64 px desktop, 44 px mobile |

## 4. Grid and breakpoints

- Mobile first. One column under 760 px.
- From 760 px: band is two columns (1.1fr and 0.9fr); copy and phones alternate sides.
- From 1120 px: the column stops growing.
- Tablet portrait (768 to 1023 px) uses the two-column band with phones at 44% width each.
- Use logical properties (`margin-inline`, `padding-inline`, `inset-inline`) everywhere so right-to-left needs no overrides.

## 5. Components

### Buttons

| Variant | Look | States |
|---|---|---|
| Play (primary) | 54 px high, 22 px side padding, radius 14, `--w-accent` background, `--e-1` shadow, weight 800 | Hover: lift 1 px. Active: shadow removed, move down 2 px. Focus: 3 px ring. Disabled: not used |
| Store badge | Official artwork, 54 px high, unaltered, clear space kept | Focus ring on the link |
| Text link | Underlined, weight 600 | Hover: thicker underline |
| Tag | Pill, not interactive | |

Minimum touch target 44 by 44 px for buttons, 24 px height for inline links, 8 px between adjacent targets.

### Header

Charcoal bar, 56 px. Left: ring and name, linking home. Right: Games, Play now, Support, language. Under 760 px: ring, name and language only; the other links move to the footer. No hamburger menu.

### Language control

A button labelled with a globe icon and the current language name, opening a list of links. On pages with one language it is absent. Visible text label, never an icon alone.

### World band

`<section class="world" data-world="ninely">` containing tag, `h2`, lead, actions, phones. Actions always in the order play, store, then note. Device script may swap play and store for Android.

### Phone frame

Image inside a 6 px dark border, radius 28. Two phones per band from 760 px, one below. Text never uses `opacity` to dim; use the dim colour token. Fixed `width` and `height` attributes. First band's images load eagerly with `fetchpriority="high"` on the first; all others `loading="lazy"`.

### Game card (for "More from Aviisr Games")

Icon 56 px, title, one line, whole card is one link. Two cards per row on mobile.

### End-of-play card

Shown inside a playable when a round ends. One sentence about what the app adds, the store badge (or the iPhone note), and "Play again". Not a modal; it replaces the board area and receives focus.

### Modals

None. Nothing in the design needs one.

### Availability note

Small text under the actions: "Not on iPhone yet." or "Coming to the App Store and Google Play." Driven by the data file.

## 6. Motion tokens

| Token | Value |
|---|---|
| `--m-fast` | 120 ms |
| `--m-base` | 180 ms |
| `--m-slow` | 320 ms |
| `--ease-out` | `cubic-bezier(.2,.8,.2,1)` |

| Motion | Class | Trigger | Spec | Reduced motion |
|---|---|---|---|---|
| Button press | Functional feedback | Pointer down | Move 2 px, `--m-fast` | Kept (no travel, colour only) |
| Icon lift in rail | Brand personality | Hover or focus | Up 6 px, rotate 3 degrees, `--m-base` | Off |
| Band reveal (optional, lowest priority) | Decoration | First time 20% visible | Phones rise 16 px, `--m-slow`, once. No opacity change, so content can never be hidden by a failed script | Off |
| Smooth scroll to band | Navigation | Rail link | Native `scroll-behavior` | Off |

Only `transform` and `opacity` are animated. No scroll-linked effects, no parallax, no autoplay video, no background animation. Content is visible without JavaScript; the reveal class is added by script, never the hidden state by CSS alone.

## 7. Accessibility rules

1. Every text and button pair meets 4.5:1; large display text 3:1.
2. Focus ring always visible, 3 px, on every interactive element.
3. One `h1` per page; bands use `h2`.
4. Screenshots carry alt text that describes the screen; decorative duplicates use empty alt.
5. Emoji are never used as game graphics. Where one remains as an icon it is hidden from assistive technology and paired with text.
6. Nothing essential depends on hover.
7. Language changes are marked with `lang` and `dir` on the element.
8. Playables are fully keyboard operable and announce results through a live region.
9. Reflow at 320 px with no horizontal scroll.

## 8. Right-to-left

- The Mila band and Hebrew or Arabic pages set `dir="rtl"`.
- Layout uses logical properties and flex or grid, so order mirrors automatically.
- Phone fan rotation is mirrored with a `[dir="rtl"]` rule.
- Latin names and store names inside Hebrew text are wrapped in `<bdi>`.
- The email address stays left-to-right.

## 9. Performance budget

| Item | Budget |
|---|---|
| Home transfer size, first load | 250 KB (today 47 KB) |
| Images above the fold | 2 screenshots, under 40 KB together |
| New CSS | 8 KB uncompressed |
| New JavaScript on home | 3 KB, deferred |
| Third-party requests | 0, except the existing counter pixel |
| Lab LCP on mobile | under 1.8 s |
| CLS | under 0.05 |
| Lighthouse | 100 accessibility, 95 or more performance |

A change that breaks a budget does not ship.
