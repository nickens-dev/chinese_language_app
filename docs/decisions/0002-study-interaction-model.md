# ADR 0002: Study Interaction Model

- **Status:** Accepted
- **Date:** 2026-07-31

## Context

The application must support many transformations between English meaning, simplified and traditional characters, pinyin, images, Chinese audio, and learner speech. Treating each transformation as an unrelated named mode would create a growing list and make multimodal combinations difficult to reason about.

The learner also needs deliberate feedback review and flexibility after making mistakes.

## Decision

- Present decks as visual cards in the initial library.
- Configure study sessions with independent prompt and response controls.
- Describe each channel by representation and modality.
- Derive the evaluator and mastery evidence from the selected combination.
- Require an explicit Continue action after feedback.
- Support immediate mistake-review sessions without replacing normal spaced-repetition scheduling.

## Consequences

- The system can grow to audio-to-speech, image-to-speech, and other combinations without introducing a new card entity for every pair.
- The interface must prevent or explain combinations that cannot be evaluated.
- Named presets may improve convenience later, but remain shortcuts over the composable model.
- Learners control how long they inspect feedback.
- Retry attempts must reference earlier mistakes without overwriting their history or due dates.

## Reconsider when

- independent controls consistently confuse learners during usability testing;
- the number of supported channels makes the controls difficult to scan;
- evidence shows automatic advancement materially improves study flow without harming feedback comprehension.
