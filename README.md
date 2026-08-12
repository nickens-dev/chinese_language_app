# Yuya Chinese Language Study App

A local-first, mobile-ready Chinese study application built around flexible language decks, configurable study sessions, and evidence-based mastery tracking.

The defining workflow is simple: select one or more decks (or a subset), choose an exact session size, select the prompt and response formats, and receive structured feedback that improves future card selection.

## Project status

The project has executable local deck, card management, dictionary-assisted entry, and persistent typed study workflows backed by SQLite.

- [Product specification](docs/product-spec.md)
- [Technical design](docs/technical-design.md)
- [Domain model](docs/domain-model.md)
- [Low-fidelity wireframes](docs/wireframes.md)
- [Architecture decisions](docs/decisions/README.md)
- [Getting started](docs/getting-started.md)
- [Deck management](docs/deck-management.md)
- [Card management](docs/card-management.md)
- [Dictionary-assisted entry](docs/dictionary-assistance.md)
- [Study sessions](docs/study-sessions.md)
- [Progress dashboard](docs/progress.md)
- [Review scheduling and mastery](docs/scheduling.md)

## Repository structure

```text
frontend/       React and TypeScript user interface
backend/        Python and FastAPI application and learning rules
docs/           Product, interface, architecture, and decision documents
scripts/        Future development and setup automation
```

Each application directory contains a README describing its purpose, source map, commands, and boundaries. The current executable slice is a visual deck manager backed by local FastAPI and SQLite services.

## First development slice

The initial implementation includes:

- a responsive React deck-library screen;
- multi-deck selection as the entry into a future session builder;
- a FastAPI health endpoint and deck-summary endpoint;
- automatic local SQLite schema creation;
- an empty-library starting point with learner-created decks stored locally;
- explicit loading, empty, and backend-unavailable interface states.

See [Getting started](docs/getting-started.md) for prerequisites and commands.

## Product principles

1. The learner controls what and how much to study.
2. Chinese knowledge is multi-modal: meaning, characters, pinyin, listening, and speaking are separate but connected skills.
3. Successful reviews require an answer or other verifiable learner action.
4. AI assists creation and evaluation; it does not hide why an answer or card was selected.
5. Vocabulary should naturally grow into phrases, sentences, and real-world comprehension.
