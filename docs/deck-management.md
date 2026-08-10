# Deck Management

Deck management is the first persistent product workflow. A learner can create a deck, open its detail screen, edit its identity, and archive it without deleting future history.

## User workflow

1. Choose **New deck** from the visual library.
2. Enter a unique name, optional description, and card color.
3. Submit the form; the deck is saved to local SQLite and opened immediately.
4. Edit deck information from the detail screen and choose **Save changes**.
5. Archive a deck through the two-step confirmation when it is no longer active.

Archiving is intentionally not deletion. Archived decks disappear from the active library, but their records remain available for later restoration and for preserving future item and attempt relationships.

## API contract

| Method | Path | Purpose | Success |
|---|---|---|---|
| GET | /api/decks | List active decks | 200 |
| POST | /api/decks | Create a deck | 201 |
| GET | /api/decks/{deck_id} | Read one active deck | 200 |
| PATCH | /api/decks/{deck_id} | Update supplied fields | 200 |
| DELETE | /api/decks/{deck_id} | Archive a deck | 204 |

Names are trimmed, required, limited to 80 characters, and unique among active decks without regard to letter case. Descriptions are trimmed and limited to 500 characters. Supported accents are jade, coral, gold, ink, sky, plum, rose, tangerine, moss, and slate. The create and edit interfaces use one shared palette definition.

The API uses camel-case response fields for TypeScript clients while Python and SQLite retain snake-case names internally.

## Persistence and migration

The decks table is the source of truth for deck identity and lifecycle. On startup, the application:

1. creates the current schema and active-name index when needed;
2. migrates the original four-color constraint to the current ten-color palette while preserving every existing deck and relationship;
3. presents the empty-library state when the learner has not created a deck.

The application never inserts demonstration decks. SQLite is the source of truth for the learner's deck library.

## Current boundary

Deck cards and deck-detail screens both provide direct study entry points. Empty decks keep their Study action disabled; non-empty decks open the session builder with that deck preselected. Card management, dictionary-assisted entry, and typed study sessions are documented separately.
