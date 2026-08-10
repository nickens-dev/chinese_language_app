# Study sessions

The first study implementation is a persistent, typed-response learning loop. It intentionally establishes reliable practice history before adaptive selection, audio, or ML-assisted evaluation are added.

## Learner workflow

1. Start from one deck, several selected decks, or the Study navigation item.
2. Select one or more non-empty decks.
3. Choose the exact requested number of cards. If fewer unique cards are available, the session uses all available cards.
4. Choose independent prompt and response channels. The first supported modes are:
   - Chinese characters → English text
   - English text → Chinese characters
   - Chinese characters → pinyin
   - Pinyin → English text
5. Type a non-blank answer and select **Check answer**.
6. Review the verdict, similarity score, expected answer, and feedback.
7. Select **Continue**. The final card completes the session and updates each selected deck's last-studied time.

## Persistence model

- `study_sessions` stores configuration, progress, status, and timestamps.
- `study_session_decks` records the decks included in a session.
- `study_prompts` stores an ordered snapshot of each card. Editing a card later cannot change an existing session.
- `study_attempts` stores the raw and normalized response, score, verdict, feedback, evaluator version, and timestamp.

Only one attempt is accepted for each prompt in this version. Expected answers are not returned until the learner submits an answer.

### Learner review and accepted alternatives

A learner can disagree with a `mostly_correct` or `incorrect` result in two ways:

- **Mark correct** changes the final judgment for that attempt only.
- **Mark correct + save answer** also stores the response as a format-specific accepted answer on the underlying card.

The original evaluator verdict, score, and evaluator version remain unchanged. The attempt separately records its final verdict, override reason, and review time. Future evaluations include saved alternatives for the matching response channel, so an English synonym cannot affect character or pinyin evaluation.

## Selection and evaluation

Selection policy `deck-order-v1` is deterministic. It follows deck membership order, deduplicates cards shared by selected decks, and takes up to the requested count. The stored policy name makes future mastery-based selection auditable.

Evaluator `typed-v1` applies format-specific normalization:

- English ignores capitalization and punctuation, accepts semicolon- or slash-separated definitions, and uses text similarity.
- Characters ignore whitespace and accept either the stored simplified or traditional form.
- Pinyin accepts tone marks or tone numbers. Matching syllables with missing or differing tones receive partial credit.

Scores of at least 90% are `correct`; at least 70% are `mostly_correct`; lower scores are `incorrect`. These thresholds are versioned and can evolve without losing the meaning of old attempts.

## API

- `POST /api/study/sessions` creates a session.
- `GET /api/study/sessions/{session_id}` restores its current state.
- `POST /api/study/sessions/{session_id}/attempts` evaluates and saves the current answer.
- `POST /api/study/sessions/{session_id}/advance` advances only after an answer is saved.

## Completion and progress summary

Completing a session returns a persisted summary rather than calculating results only in the browser. The completion screen shows:

- the percentage of final reviewed judgments that were correct;
- the average automatic similarity score;
- correct, mostly-correct, incorrect, and learner-override counts;
- each card's Chinese, pinyin, English, submitted answer, final result, and match score;
- historical correct attempts, total attempts, and percentage correct for that card.

Historical card accuracy is scoped to the exact prompt and response channels. For example, `characters → english` and `english → characters` accumulate separate histories. Correctness uses the final reviewed verdict, while average match continues to expose the evaluator's original numerical score.
## Next learning layers

Attempt history now provides the foundation for per-mode mastery, weak-card prioritization, spaced repetition, richer correction explanations, and audio prompt/response channels. Those features should consume this history rather than altering completed attempts.