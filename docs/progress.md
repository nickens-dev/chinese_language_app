# Progress dashboard

The Progress page is a read-only view over persisted study attempts. It does not maintain separate mastery totals, so learner-reviewed verdicts remain the source of truth.

## Filters

The report supports 7-day, 30-day, 90-day, and all-time ranges plus optional deck and study-direction filters. Every section uses the same filters. The browser sends its local timezone offset so study days and streak boundaries follow the learner's calendar rather than UTC.

## Metrics

- **Reviewed accuracy** is the percentage of attempts whose final verdict is correct.
- **Average match** is the average original evaluator score and is not changed by overrides.
- **Attempts** counts submitted answers.
- **Unique cards** counts distinct language items.
- **Sessions** counts completed sessions represented in the filtered attempts.
- **Study days** counts calendar dates containing attempts.
- **Current streak** remains active when the most recent study day is today or yesterday.
- **Longest streak** is the longest run of consecutive study dates.
- **Cards per session** divides attempts by represented completed sessions.

Active elapsed time is intentionally excluded because creation and completion timestamps include breaks and abandoned browser time.

## Sections

The overview is followed by an accuracy line with attempt-volume bars, a study-direction comparison, weakest-first card-direction records, and the ten most recent matching completed sessions. Word records remain separated by prompt and response channels.

## API

`GET /api/progress` accepts `days`, `deckId`, `promptChannel`, and `responseChannel`, and `timezoneOffset`. Aggregates are calculated from attempts at request time and returned as one consistent report.