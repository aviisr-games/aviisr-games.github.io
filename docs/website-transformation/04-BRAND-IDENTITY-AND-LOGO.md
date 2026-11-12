# 04 - Brand identity and logo

## 1. Audit of the current identity

| Element | Today | Assessment |
|---|---|---|
| Name | "Aviisr Games" on the site, "Aviisr" as the Play developer name, "aviisr-games" on the share image | Three spellings in public. Fix the share image. [E] |
| Mark | Amber ring on charcoal, used only as the favicon | A usable mark that the site itself never shows. [E] |
| Palette | Dark green and gold, tokens named `--felt` and `--gold` | Inherited from the casino pages. It says "card table", which fits none of the five products. [E] |
| Type | System sans everywhere, Georgia in the Middle East 2030 playable | Fast and free. No character. [E] |
| Imagery | App icons at 56 px | The games have strong art that the studio pages do not use. [E] |
| Voice | Plain, honest, short | A real strength. Keep it. [J] |
| Motion | None on studio pages | Nothing to fix, nothing to keep. [E] |

Personality as it reads from the products and copy: careful, plain-spoken, a little dry. One maker who finishes things. [J]

## 2. Does the identity need to change?

A refinement, not a rebrand. The studio has almost no brand recognition to protect or to lose, the favicon ring already exists, and the games carry the visual interest. [J]

Recommendation: promote the ring to the studio mark, retire the green and gold, and let each game bring its own colour. Do not redesign any app icon.

## 3. Three logo directions

Drawn in `mockups/logo-directions.svg`.

| | 1. Ring | 2. Five worlds | 3. Wordmark |
|---|---|---|---|
| Concept | The existing amber ring with the name set beside it | The ring split into five arcs, one per product colour | Lower-case "aviisr" with the ring as a full stop |
| Meaning | A token, a target, a full circle: finished work | A studio made of distinct worlds | The name itself is the brand |
| Memorability | Medium. Simple shapes are common | Higher | Medium |
| Scales to 16 px | Yes | No. Five colours blur under 24 px | The ring alone does |
| App ecosystem fit | Neutral beside any icon | Competes with the icons | Neutral |
| Social avatar | Works | Works at large sizes only | Needs the ring-only version |
| Dark and light | One colour swap | Needs two tuned palettes | One colour swap |
| Accessibility | Amber on charcoal 10.2:1 | Arc contrast varies | Text contrast is fine |
| Production | Already exists | Redraw when a product is added or removed | Custom lettering work |

**Choice: direction 1.** It is already in use, it works at favicon size, and it costs nothing. Direction 2 can appear once, as a hero or loading animation, without becoming the logo. [J]

The owner's notes mention a "logo Route C" test that waits on the 28-day data gate. This audit could not see what Route C is. Nothing here should override that test; fold direction 1 in as the baseline.

## 4. Brand architecture: one studio, five products

Rule: **the studio is the frame, the game is the picture.**

Studio owns (identical everywhere):
- The header bar with the ring and name, charcoal `#15171C`.
- The footer.
- Button shapes, spacing scale, focus ring, the store badge treatment.
- The interaction rules: one primary action per block, play and store actions always in the same order.
- Tone of voice.

Each game owns (inside its block or page):
- Background colour and one accent, taken from its store art.
- Its display typeface choice from the system stacks (sans or serif).
- Its screenshots and, later, its video loop.

| Product | Background | Accent | Display type | Source of the colours |
|---|---|---|---|---|
| Ninely | `#2F6FED` blue | white | sans, heavy | App icon |
| Middle East 2030 | `#F3EDE0` newsprint | `#B3261E` red | serif | Store screenshots |
| Baylight | `#101A33` night navy | `#FFD23F` yellow | sans, heavy | Store screenshots |
| Morning Paper Route | `#FF9A3D` to `#F4743B` sunrise | `#1E2433` ink | sans, heavy | Store screenshots |
| Mila | `#F7F2FF` lilac | `#6D3BDB` purple | sans, rounded | Existing Mila pages |

Hex values were picked by eye from the artwork for the mockups. Sample the final values from the source art files before build.

## 5. Tone of voice

- Say what the game is in one line a player would repeat.
- State limits plainly: "Not on iPhone yet."
- No superlatives, no invented numbers, no "award-winning".
- Middle East 2030 always carries the fiction line in the first screen.
- Mila copy speaks to parents, in Hebrew first.

## 6. Assets to produce

1. Ring logo as SVG (mark, mark plus name, light and dark). 
2. `favicon.ico` and a 180 px touch icon (the `.ico` request currently returns 404).
3. New `assets/og/studio.jpg` with the correct name and five icons.
4. A 512 px raster logo for the Organization structured data (it points at the SVG favicon today).
