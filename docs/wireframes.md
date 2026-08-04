# Low-Fidelity Wireframes

These wireframes define information hierarchy and workflow, not visual styling. Desktop layouts are shown first. On narrow screens, the left navigation becomes a bottom bar or menu, multi-column areas stack, and the primary action remains reachable without horizontal scrolling.

## Shared application shell

```text
┌──────────────────────────────────────────────────────────────────────────┐
│ 中文 Study                                              Local • Settings │
├──────────────┬───────────────────────────────────────────────────────────┤
│ Home         │                                                           │
│ Decks        │                  Current screen                           │
│ Study        │                                                           │
│ Progress     │                                                           │
│ Suggestions  │                                                           │
│              │                                                           │
├──────────────┴───────────────────────────────────────────────────────────┤
│ Data stays on this device                              Sync: not enabled │
└──────────────────────────────────────────────────────────────────────────┘
```

The persistent shell makes Decks and Study the strongest destinations. “Local” communicates the storage model rather than behaving like an account control.

## 1. Deck library

```text
┌──────────────────────────────────────────────────────────────────────────┐
│ Decks                                      [Search decks…]  [+ New deck] │
│ Build vocabulary and reuse it in any study mode.                         │
├──────────────────────────────────────────────────────────────────────────┤
│ [All 6] [Recently studied] [Needs attention] [Archived]   Sort: Recent  │
├──────────────────────┬──────────────────────┬────────────────────────────┤
│ HSK 1 Core           │ Food & Restaurants   │ Introductions              │
│ 148 items            │ 42 items             │ 25 items                   │
│ 18 due • 12 weak     │ 6 due • 4 weak       │ 3 due • 2 weak             │
│ Last studied today   │ Last studied Tue     │ Not studied yet            │
│ [Study] [Open]       │ [Study] [Open]       │ [Study] [Open]             │
├──────────────────────┴──────────────────────┴────────────────────────────┤
│ Selected: 0                          [Combine selected] [Start session]  │
└──────────────────────────────────────────────────────────────────────────┘
```

Key behavior:

- selecting multiple decks enables combined study without merging their contents;
- `Study` opens the session builder with that deck preselected;
- deck cards expose due and weak counts without reducing mastery to one percentage.
- the initial library uses visual cards; a dense table view is not part of the first interface.

## 2. Deck detail and item editor

```text
┌──────────────────────────────────────────────────────────────────────────┐
│ ‹ Decks   Food & Restaurants             [Study deck] [Deck options ⋯]  │
│ 42 items • 6 due • 4 weak                                            │
├──────────────────────────────────┬───────────────────────────────────────┤
│ [Search English, pinyin, 汉字…]  │ Add language item                     │
│ Filters: [All] [Words] [Phrases] │ Search dictionary                     │
│          [Sentences] [Weak]      │ [ chi fan________________________ ]   │
│                                  │                                      │
│ □ 吃饭  chīfàn   eat a meal     │ Suggestions                          │
│ □ 菜单  càidān   menu            │ ○ 吃饭  chīfàn  eat/have a meal      │
│ □ 买单  mǎidān   pay the bill    │ ○ 吃  chī  eat                       │
│ □ 好吃  hǎochī  delicious        │ ○ 午饭  wǔfàn  lunch                  │
│                                  │                                      │
│ [Add manually]                   │ [Review selected suggestion →]       │
├──────────────────────────────────┴───────────────────────────────────────┤
│ Selected: 0                  [Move/Add to deck] [Tag] [Remove from deck] │
└──────────────────────────────────────────────────────────────────────────┘
```

After choosing a suggestion, a review form shows simplified and traditional characters, pinyin, meanings, classifiers, tags, source, and audio availability. Nothing suggested by a provider is saved until the learner confirms it.

## 3. Session builder

```text
┌──────────────────────────────────────────────────────────────────────────┐
│ Build a study session                                      Step 1 of 1 │
├────────────────────────────────┬─────────────────────────────────────────┤
│ CONTENT                        │ LIVE PREVIEW                            │
│ Decks (2 selected)             │ 30 prompts available                   │
│ ☑ HSK 1 Core                  │                                         │
│ ☑ Food & Restaurants          │ 18 due     8 weak     4 new             │
│ ☐ Introductions               │                                         │
│                                │ Selection reasons:                     │
│ Focus                          │ Due listening, weak meanings, new mix  │
│ ○ Due and difficult            │                                         │
│ ○ Difficult only               │ If filters become too narrow, this     │
│ ○ New only                     │ panel explains what must be relaxed.   │
│ ○ All eligible                 │                                         │
│                                │                                         │
│ SESSION                        │                                         │
│ Number of prompts [ 30 ]       │                                         │
│ Study mode                     │                                         │
│ [Chinese audio ▾] → [English typed ▾]                                  │
│ New/review mix [ 15% new ━●━━ ]                                         │
│                                │                         [Start session] │
└────────────────────────────────┴─────────────────────────────────────────┘
```

This screen is the product’s central control surface. Prompt and response are separate controls so future combinations do not require separate hard-coded modes. Presets can later provide friendly names for common combinations.

Each control describes both representation and modality—for example, `Chinese meaning + audio` as a prompt or `Mandarin + microphone` as a response. Unsupported combinations remain visible only when useful for discovery and explain why they cannot yet be evaluated.

## 4. Active study

```text
┌──────────────────────────────────────────────────────────────────────────┐
│ Food + HSK 1       Chinese audio → English typed          7 / 30  [Exit]│
│ Progress ━━━━━━━━━━━━━━━━╺━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│                              [▶ Play audio]                              │
│                              [↻ 0.75× speed]                             │
│                                                                          │
│ What does this mean?                                                     │
│ ┌──────────────────────────────────────────────────────────────────────┐ │
│ │ Type an English meaning…                                            │ │
│ └──────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│ [I don't know]                                             [Check answer]│
│                                                                          │
│ Reason selected: due • weak listening                                   │
└──────────────────────────────────────────────────────────────────────────┘
```

The prompt hides characters and pinyin because they would answer this listening question. Keyboard focus begins in the answer field. Replay does not count as a hint initially, but playback count is recorded.

## 5. Answer feedback

```text
┌──────────────────────────────────────────────────────────────────────────┐
│ 7 / 30                                                   Mostly correct │
├──────────────────────────────────────────────────────────────────────────┤
│ 吃饭        chīfàn        [▶ audio]                                     │
│                                                                          │
│ Your answer:  eat                                                        │
│ Accepted:     eat a meal; have a meal                                   │
│                                                                          │
│ Meaning      86%   Your answer has the core meaning but misses “meal.”   │
│ Listening    Evidence recorded from this audio prompt.                   │
│                                                                          │
│ Source: dictionary entry                                                 │
│ Was this judgment fair? [Yes] [No—mark correct] [No—mark incorrect]      │
│                                                                          │
│                                                   [Continue →]           │
└──────────────────────────────────────────────────────────────────────────┘
```

Feedback separates the evaluated answer from mastery evidence. Overrides preserve the automated result and the learner’s correction. A later semantic evaluator must expose uncertainty rather than manufacture precision.

## 6. Session summary

```text
┌──────────────────────────────────────────────────────────────────────────┐
│ Session complete                                             12 minutes │
├──────────────────────┬───────────────────────────────────────────────────┤
│ 30 prompts           │ SKILL EVIDENCE                                    │
│ 23 correct           │ Listening meaning     23 strong / 7 review       │
│  5 mostly correct    │ Characters            not tested                 │
│  2 incorrect         │ Pinyin & tones         not tested                 │
│                      │ Speaking               not tested                 │
├──────────────────────┴───────────────────────────────────────────────────┤
│ NEEDS REVIEW                                                            │
│ 买单 mǎidān      confused with 菜单      [Review now] [Open item]        │
│ 还是 háishi      slow response           [Review now] [Open item]        │
│                                                                          │
│ [Study these 7 again] [Return to decks]             [Build new session] │
└──────────────────────────────────────────────────────────────────────────┘
```

The summary avoids a single mastery score. It reports evidence only for skills exercised in the session and makes immediate targeted review optional.

Choosing `Study these 7 again` creates an immediate retry session while the original attempts and their normal spaced-repetition schedules remain intact.

## Mobile adaptation

```text
┌──────────────────────┐
│ Study          7/30  │
│ ━━━━━━━━━╺━━━━━━━━━━ │
│                      │
│    [▶ Play audio]    │
│                      │
│ What does this mean? │
│ [English answer…   ] │
│                      │
│ [I don't know]       │
│ [Check answer]       │
├──────────────────────┤
│ Home Decks Study You │
└──────────────────────┘
```

Study content uses the full narrow screen. Configuration sections stack vertically, summaries become cards, and destructive or secondary actions move into menus. The response control stays above the on-screen keyboard when it opens.

## Confirmed interaction decisions

1. The deck library uses visual cards.
2. Prompt and response are configured with two independent controls; multimodal combinations are modeled explicitly.
3. Feedback waits for an explicit Continue action.
4. The learner can review mistakes immediately, while spaced repetition still schedules future reviews.
