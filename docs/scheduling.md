# Review scheduling and mastery

The first scheduler is deliberately transparent. It gives useful spaced-review behavior now while keeping the review history needed to adopt FSRS later without losing learner progress.

## What is being learned

Mastery belongs to a card and a study direction, not to a word by itself. For example, `你: characters → English` and `你: audio → characters` have independent schedules because recognition, listening, recall, and production are different skills.

The stored skill state includes its learning state, next due time, interval, stability, difficulty, review count, lapse count, and scheduler version.

## Review ratings and intervals

The evaluator's final verdict becomes a scheduler rating:

- incorrect → **Again**: review after 10 minutes; reduce stability and increase difficulty;
- mostly correct → **Hard**: review after at least 1 day; increase the interval slowly;
- correct → **Good**: review after 1 day initially, then grow the interval by about 2.5×;
- **Easy** is reserved for a future explicit learner rating: 4 days initially, then about 3.2×.

These rules are versioned as `transparent-v1`. They are product rules rather than a claim to reproduce FSRS.

## Due and weak mean different things

A studied card-direction is **due** when its stored `dueAt` is now or earlier. New card-directions remain available for balanced sessions but are described as new rather than counted as due.

A card-direction is **weak** after at least two reviews when one or more of these explainable conditions applies:

- reviewed accuracy is below 70%;
- the latest scheduler rating is Again;
- it has lapsed at least twice;
- scheduler difficulty is 6.5 or higher.

The API and Progress screen expose the concrete reason, such as “Accuracy is 50% (below 70%)” or “Incorrect last time.” This avoids reducing mastery to an unexplained badge.

## How cards are selected

Balanced sessions rank eligible cards in this order:

1. overdue and weak;
2. other due cards;
3. weak cards not yet due;
4. new card-directions;
5. early cards used only to fill the learner's requested session size.

Ordering within a group is stable. Every prompt stores a snapshot of its selection bucket and a readable explanation, so the learner can see why it appeared even if its mastery changes later.

Weak-only sessions, including those launched from Progress, include only card-directions that currently satisfy the weak rules. Deck, prompt, response, and explicit item filters still apply.

## Review history and corrections

Every answered attempt has an immutable-by-identity review event containing the final learner-approved verdict and scheduler version. If the learner disagrees with an evaluation, the override updates that event and the skill state is rebuilt by replaying all events in order. Existing attempts are backfilled into events at application startup.

## Path to FSRS

FSRS can later replace the interval calculation while preserving the surrounding design:

- retain timestamped review events and their Again/Hard/Good/Easy ratings;
- add an FSRS scheduler version and FSRS-specific state fields or a versioned payload;
- replay history to calculate FSRS state;
- compare scheduling versions with tests and, eventually, learner-level parameter training;
- keep selection explanations independent from the scheduling engine.

No migration should manufacture historical review timing. The event log is the durable source; calculated skill state can always be rebuilt.
