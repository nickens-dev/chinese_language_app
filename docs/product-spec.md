# Product Specification

## 1. Product vision

Create a Chinese study app that gives learners unusually precise control over study material and study modes while intelligently adapting to their performance. A learner can combine decks, focus on difficult material, choose an exact number of items, and practice any useful transformation—for example Chinese audio to typed English, characters to spoken Chinese, or English to characters.

The application begins as a local desktop experience for a beginner learner, but its content and mastery model must support intermediate and advanced study and later mobile clients.

## 2. Target user

The initial user is an English-speaking beginner studying Mandarin Chinese who:

- wants to build vocabulary without losing context;
- needs practice across reading, listening, speaking, meaning, pinyin, and characters;
- wants control over session length and content selection;
- prefers meaningful input and feedback over passive card flipping;
- expects the application to grow with them.

## 3. Product principles

- **Learner control:** Decks, subsets, session size, prompt format, and response format are configurable.
- **Skill-specific mastery:** Knowing a meaning is not the same as recognizing audio or producing speech.
- **Active recall:** A review is not completed by merely revealing the answer.
- **Transparent adaptation:** The app explains why items were selected and how an answer was scored.
- **Contextual progression:** Words become phrases and sentences as mastery develops.
- **AI with guardrails:** Generated Chinese is validated, attributed, editable, and never silently treated as ground truth.

## 4. Core concepts

### 4.1 Language item

A language item represents a word, phrase, or sentence. It may contain:

- simplified and traditional characters;
- pinyin with tone marks and a normalized tone-number form;
- one or more English meanings;
- Chinese audio and optional English audio;
- image(s);
- part of speech, classifier, usage notes, tags, and source;
- component words and example contexts.

This is intentionally not a two-sided flashcard. A study card is a configurable view of a language item.

### 4.2 Deck

A deck is an ordered or filtered collection of language items. Items can belong to multiple decks without duplication. Decks may be:

- manually curated;
- imported;
- generated from selected vocabulary;
- dynamically filtered from mastery data;
- generated around a topic, level, or scenario.

### 4.3 Study mode

A study mode pairs a prompt presentation with a required response and evaluation method.

Examples:

| Prompt | Required response | Evaluation |
|---|---|---|
| Chinese audio | Typed English | Semantic similarity against accepted meanings |
| Characters | Spoken Mandarin | Speech recognition plus pronunciation/content scoring |
| English | Typed characters | Character normalization and accepted-answer matching |
| Characters | Typed pinyin | Syllable and tone-aware comparison |
| Image | Spoken Mandarin | Speech recognition and semantic matching |
| Characters + audio | Typed English | Semantic similarity |

The user can save combinations as named study modes.

## 5. MVP scope

### 5.1 Deck and item management

- Create, rename, archive, and combine decks.
- Add, edit, remove, tag, search, and filter items.
- Add an item from partial English, pinyin, or character input using dictionary-backed suggestions.
- Review all machine-suggested fields before saving.
- Support words, phrases, and sentences in the underlying model from day one.
- Prevent accidental duplicate items while allowing alternate senses and pronunciations.

### 5.2 Session builder

The learner can:

- select one or more decks;
- include or exclude tags, item types, or individual items;
- select due items, difficult items, new items, low-confidence items, or all eligible items;
- choose an exact target session size;
- choose or save a study mode;
- optionally set the mix of new and reviewed material;
- preview the resulting session before starting.

If fewer eligible items exist than requested, the app clearly reports the available count and offers to relax filters.

### 5.3 Active study and feedback

- Require typed, spoken, selected, or constructed input before completion.
- Allow skip and “I don’t know,” recorded as evidence rather than hidden failure.
- Show correct answer, differences, accepted alternatives, and a concise explanation.
- Give separate feedback for meaning, characters, pinyin syllables, tones, and pronunciation when relevant.
- Allow the learner to override an incorrect automated judgment; preserve both the original score and override.
- Save attempts, latency, hints, confidence, and scoring details.
- Resume an interrupted local session.

### 5.4 Adaptive selection and mastery

- Track mastery per language item and skill direction, not as one global number.
- Prioritize overdue, weak, slow, and repeatedly confused items.
- Use spaced-repetition scheduling as the stable baseline.
- Let the user explicitly request difficult items or a random/representative sample.
- Explain selection with labels such as “due,” “weak listening,” or “frequently confused.”

### 5.5 Context builder

- Suggest common phrases and sentences containing selected or mastered vocabulary.
- Show which target words each suggestion practices.
- Provide translation, pinyin, audio, difficulty estimate, and source/provenance.
- Let the user edit, reject, or accept suggestions into a new or existing deck.
- Prefer common, natural language and constrain suggestions to a chosen proficiency band.

## 6. Post-MVP capabilities

- Mobile client with offline study and synchronization.
- Rich pronunciation coaching and tone-contour feedback.
- Camera/OCR capture of Chinese in the environment.
- Role-play, mysteries, matching, and arcade-style games constrained by mastered vocabulary.
- Unlockable activities tied to mastery milestones.
- Conversation practice and scenario-based generated decks.
- Handwriting input and stroke-order evaluation.
- Multi-device accounts and sharing.

## 7. Intelligent features

### Search and item completion

Use a trusted Chinese dictionary as the factual base. Search may use fuzzy matching, pinyin normalization, segmentation, and semantic ranking. A language model can improve ranking and explain distinctions, but should not invent dictionary facts.

### Phrase and sentence suggestions

Use retrieval before generation: find attested examples where possible, then optionally generate targeted examples. Generated content must be labeled, checked for required vocabulary and level, and editable before it enters a deck.

### Session selection

Begin with an explainable scoring formula using due date, skill mastery, recent errors, response latency, recency, and user filters. More advanced models can be tested later against learning outcomes.

### Answer evaluation

Use the narrowest reliable evaluator:

- normalization and exact/variant matching for characters;
- syllable- and tone-aware comparison for pinyin;
- accepted translations plus semantic similarity for English meaning;
- speech-to-text plus content and pronunciation signals for spoken Chinese.

Uncertain judgments should be surfaced as uncertain and allow self-assessment.

## 8. Key user journeys

### Focused listening session

1. Select several decks.
2. Filter to weak listening items.
3. Request exactly 30 prompts.
4. Select Chinese audio → typed English.
5. Complete each prompt and review structured feedback.
6. See a session summary and updated listening mastery.

### Build a vocabulary item

1. Type partial English, pinyin, or characters.
2. Choose a dictionary suggestion.
3. Review characters, pinyin, meanings, audio, and metadata.
4. Add it to one or more decks.

### Grow vocabulary into context

1. Select a vocabulary deck or mastery range.
2. Request common phrases or sentences at a chosen difficulty.
3. Inspect provenance and target-word coverage.
4. Edit and accept useful suggestions into a context deck.
5. Practice that deck using reading, listening, or speaking modes.

## 9. Success measures

- A learner can create a 30-item multi-deck session in under one minute.
- Every completed review records verifiable learner input or an explicit skip.
- Mastery and due state are tracked independently for at least meaning recognition, character recognition, listening, pinyin production, and speaking.
- At least 90% of accepted context suggestions are retained after human review during early testing.
- A learner can understand why every adaptive item appeared.
- No generated content is added to a deck without explicit acceptance.

## 10. MVP exclusions

- Social network, public deck marketplace, and competitive leaderboards.
- Fully autonomous chat tutor.
- Training a foundation language model.
- Cloud accounts and cross-device sync.
- Game modes and camera capture.
- Claims of objective pronunciation accuracy without validated evidence.

## 11. Open product decisions

- Preferred Chinese variant at launch: simplified-first is assumed, with traditional stored alongside it.
- Whether handwriting should enter the MVP after basic typed and spoken modes are proven.
- Which dictionary/example corpora can be redistributed under acceptable licenses.
- Whether initial speech recognition runs locally or uses an optional cloud provider.
- How much manual control the learner wants over spaced-repetition parameters.
