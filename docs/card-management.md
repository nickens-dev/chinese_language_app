# Card Management

Card management is the first persistent content workflow inside a deck. A learner can add, review, edit, and remove Chinese words, phrases, and sentences while keeping the content model ready for shared cards and dictionary assistance.

## Card fields

| Field | Required | Purpose |
|---|---|---|
| Type | Yes | Classifies an item as a word, phrase, or sentence. |
| Simplified Chinese | Yes | The default written form used by the application. |
| Traditional Chinese | No | Preserves the corresponding traditional form when useful. |
| Pinyin | No | Stores tone-marked pronunciation; dictionary assistance will fill this later. |
| English meaning | Yes | Stores one or more learner-facing glosses. |
| Notes | No | Stores usage, classifiers, context, or memory aids. |

Text is trimmed at the API boundary. Simplified Chinese and English meaning cannot be blank.

## Membership behavior

Language items and deck memberships are separate records. This allows a card to belong to multiple decks later without copying its content.

- Creating a card also creates its first deck membership.
- Cards are returned in stable deck order.
- Removing a card removes only the requested membership.
- A card with no remaining memberships is archived rather than destroyed.
- Deck item counts are synchronized in the same SQLite transaction as membership changes.

## API contract

| Method | Path | Purpose | Success |
|---|---|---|---|
| GET | `/api/decks/{deck_id}/cards` | List active cards in deck order | 200 |
| POST | `/api/decks/{deck_id}/cards` | Create a card in a deck | 201 |
| PATCH | `/api/cards/{card_id}` | Update supplied card fields | 200 |
| DELETE | `/api/decks/{deck_id}/cards/{card_id}` | Remove a card from a deck | 204 |

## Current boundary

Manual and dictionary-assisted entry share the same reviewed card form. Dictionary search accepts English, pinyin, and characters, then populates sourced candidates without saving automatically. See [Dictionary-assisted entry](dictionary-assistance.md).