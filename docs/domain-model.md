# Domain Model

## Core entities

| Entity | Purpose |
|---|---|
| `LanguageItem` | Stable identity for a word, phrase, or sentence |
| `WrittenForm` | Simplified/traditional characters and regional variant |
| `Pronunciation` | Pinyin, tones, dialect/region, and audio associations |
| `Sense` | English glosses, part of speech, notes, and classifiers |
| `MediaAsset` | Audio or image with source, license, and local cache state |
| `Deck` | Named manual or dynamic collection |
| `DeckMembership` | Many-to-many item membership with order and metadata |
| `StudyMode` | Independent prompt channels, response channel, and derived evaluator policy |
| `StudySession` | Immutable session configuration plus mutable progress state |
| `SessionPrompt` | Selected item/skill pair, order, and selection reasons |
| `Attempt` | Raw answer, timing, hints, evaluation, and override evidence |
| `MasteryState` | Rebuildable estimate for one item and skill direction |
| `ContentSuggestion` | Retrieved/generated candidate with provenance and review state |
| `SourceRecord` | Dictionary, corpus, user, or model provenance and licensing |

## Important relationships

```text
LanguageItem 1---* WrittenForm
LanguageItem 1---* Pronunciation
LanguageItem 1---* Sense
LanguageItem *---* Deck
LanguageItem 1---* MasteryState (one per skill direction)
StudySession 1---* SessionPrompt 1---* Attempt
LanguageItem *---* LanguageItem (component/context relationships)
ContentSuggestion *---* LanguageItem (target vocabulary)
```

## Skill directions

Mastery keys should describe both stimulus and expected production. Initial keys include:

- audio → English meaning;
- characters → English meaning;
- English meaning → characters;
- characters → pinyin with tones;
- English meaning → spoken Mandarin;
- audio → characters;
- characters → spoken Mandarin.

These can roll up into listening, reading, meaning, character production, pinyin/tone, and speaking summaries without discarding detail.

## Prompt and response channels

A study mode is composed rather than represented by a fixed card type:

```text
StudyMode
  prompt channels: one or more presentation channels
  response channel: one required learner-input channel
  evaluator policy: selected for that prompt/response combination
```

A channel records both modality and representation. `audio + Mandarin speech` is different from `audio + English speech`; likewise, `text + simplified characters` is different from `text + pinyin`. This distinction allows audio-to-audio, image-to-speech, and other future combinations without ambiguous labels.

Not every theoretical combination is valid. The study-mode catalog declares supported combinations and the evidence each contributes to mastery. Friendly named presets may reference these combinations later, but do not replace the underlying independent controls.

## Data rules

- Attempts are append-only; corrections are recorded as overrides.
- Mastery is derived from attempts and may be recalculated.
- Deleting a deck does not delete shared language items by default.
- Generated suggestions are not language items until accepted.
- Original and normalized learner answers are both retained.
- Provider and algorithm versions are stored on generated/scored records.
- IDs should be globally unique from the beginning to simplify future sync.
