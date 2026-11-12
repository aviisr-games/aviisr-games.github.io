# 03 - UX, UI and conversion audit

Labels: **[E]** evidence, **[J]** judgment, **[S]** speculative. Finding ids match `FINDINGS-REGISTER.csv`.

## 1. The first five seconds

Tested at 1440 px and 606 px in Chrome, and at 390 px in a framed capture.

| Question | Answer today |
|---|---|
| Does the visitor understand what is offered? | Yes, in words: "Small mobile games, made with care." [E] |
| Does it look like a game studio? | No. No artwork, only 56 px icons on a dark green page. [E] |
| Is there an emotional hook? | No. The first lines are about availability ("not on the App Store yet"). [E] |
| Is there an obvious next action? | Partly. The first Google Play badge sits at about 490 px on a phone, below the fold on small screens. [E] |
| Is the studio's personality visible? | No. [J] |

The page leads with what is missing (iPhone, Mila) before showing anything that exists. (UX-01)

## 2. Information architecture

- No shared header. The home page has only a language selector; each hub has its own row of text links. (UX-02) [E]
- Morning Paper Route lives in two folders: the hub at `/paper-route/`, the playable at `/morning-route/preview/`. (UX-03) [E]
- The hub link label on the home page is "About, help and privacy", which undersells the page that holds the screenshots. (UX-04) [E]
- Middle East 2030 shows English and Hebrew as two stacked sections on one URL, each with its own H1. (SEO-03) [E]

## 3. The browser playables

| Playable | What it is | Looks like the game? | Store action |
|---|---|---|---|
| Ninely daily (`/ninely/play/`) | Full daily Sudoku with hints | Close: a real board, different colours | Badge on the win card and on the page |
| Middle East 2030 briefing | 3 decisions, 8 endings | Partly: newspaper styling, no illustrations | One badge |
| Baylight dock | Solver-checked sorting puzzle | No: emoji and letter tiles, titled "Interactive Web Prototype", opens with a "Development Notice" | One badge under the board |
| Morning Paper Route preview | Timing bar with emoji rider | No: the game is a 3D street, the preview is a coloured bar; titled "Throw Timing Prototype" | One badge under the board |

The store screenshots prove the games look far better than their web previews. A visitor who tries the Baylight or Paper Route preview sees something weaker than the product. This is the largest conversion risk on the site. (CRO-01) [J, based on E]

## 4. Journey maps

| # | Visitor | Path today | Friction | Fix |
|---|---|---|---|---|
| 1 | First-time visitor | Home, read five cards | Nothing to look at, no reason to pick one | Art-led game blocks |
| 2 | Interested in one game | Home, "About, help and privacy", hub | Vague link label, hub is good | Card and title link to the hub |
| 3 | Android player | Home, badge, Play | Works. Badge below the fold on phones | Badge in the first block |
| 4 | iPhone player | Home, notice, browser version | Honest, but two previews are weak | Reskin previews; keep the notice short and inside each block |
| 5 | Wants to play now | Home, text link, playable | The play link is the least prominent item on the card | A real play button |
| 6 | Returning player | Home | Nothing changes between visits | Daily puzzle date and "what is new" line from release notes |
| 7 | Parent looking at Mila | Home (Hebrew card), Mila hub | Works well. Mila hub is the best page on the site | Keep; add a parent trust block on the home block |
| 8 | Business partner | Home, contact card | No press or about content, old share image | Short studio section and a press kit link |
| 9 | Privacy or support | Footer links | Works. Legacy `/privacy.html` still titled "Casino Games" | Retire legacy pages |

## 5. Usability details

- Small touch targets: the "About, help and privacy" links are 23 px high and footer links 17 px. This is polish, not a WCAG failure: Lighthouse's target-size audit passes and the spacing and inline exceptions of criterion 2.5.8 apply. (A11Y-01) [E]
- The language control is a bare `<select>` with no visible label. (A11Y-02) [E]
- Keyboard focus ring and skip link exist and work. [E]
- No horizontal scroll at 390 px or 606 px. [E]
- The Mila card is right-to-left inside a left-to-right grid, which is correct, but the mixed-language grid looks unplanned. (UX-05) [J]
- Reduced-motion is handled on three pages; the others have no motion to reduce. [E]

## 6. Conversion audit

What exists and is right: official badges, UTM tags per surface (`home`, `hub`, `playable`, `playable-win`), a click counter, a QR handoff on desktop, an honest iPhone note. [E]

What is missing:

1. Proof. No gameplay image on the home page. (CRO-02)
2. Hierarchy. Badge, play link and hub link have similar weight. (CRO-03)
3. Device awareness. An iPhone visitor still sees the Google Play badge first. (CRO-04)
4. End-of-play offers. Only Ninely has a win card with a store action. (CRO-05)
5. Cross-promotion. No "try another game" link after a playable. Never on Mila. (CRO-06)

Trust signals: ratings exist on Play (3.6 to 4.7) but come from very few ratings. Do not show them, and do not show install counts. (CRO-07) [J]

## 7. Platform behaviour to specify

| Device | Primary action | Secondary |
|---|---|---|
| Android | Google Play badge | Play in browser |
| iPhone and iPad | Play in browser | "Not on the App Store yet" text. No badge until a listing is live |
| Desktop | Play in browser | Google Play badge, QR code |
| Unreleased app (Mila) | Parent information, worksheets | "Coming to the App Store and Google Play" text, no badge |
| Unknown or no JavaScript | Both actions as plain links | Works without device detection |

Detection is a progressive enhancement from the user agent. The server-rendered default must be complete and correct on its own.

## 8. Experiments

Traffic is far below what a split test needs. To detect a rise in store click-through from 5.0% to 7.5% at 80% power and 5% significance takes about 1,500 visitors per arm. The Play Console showed 2 Ninely acquisitions in 28 days. [E]

So the plan is sequential before-and-after reads, reported as descriptive only:

| Change | Hypothesis | Primary metric | Guardrail | Decision rule |
|---|---|---|---|---|
| Art-led home blocks | More visitors pick a game | Hub or playable views per home view | Home LCP under 1.8 s lab | Keep unless the metric falls for 4 weeks |

The play and navigation events must be live for four weeks before the first of these changes ships. Otherwise there is no "before" to compare with.

| Change | Hypothesis | Primary metric | Guardrail | Decision rule |
|---|---|---|---|---|
| Play button first | More playable starts | `play_start` per home view | Store clicks per home view do not fall | Keep unless store clicks fall by a third |
| Reskinned Baylight preview | More store clicks from the preview | Store clicks per `play_start` | Completion rate | Compare 4 weeks before and after |
| Device-aware action | Fewer dead ends on iPhone | Playable starts per home view on iOS | None | Keep if not worse |

Run a real split test only when a single page reaches about 3,000 visitors a month.
