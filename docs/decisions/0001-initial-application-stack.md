# ADR 0001: Initial Application Stack

- **Status:** Accepted
- **Date:** 2026-07-31

## Context

The application starts on one local machine, must remain approachable to its owner, and should later support a phone client. Its core differentiator is a configurable learning engine, with future dictionary, text, audio, and machine-learning integrations.

## Decision

- Use React with TypeScript for the user interface.
- Use Python with FastAPI for the application API and learning engine.
- Use SQLite as the initial local system of record.
- Make simplified Chinese the default presentation while retaining traditional forms in the domain model.
- Implement dictionary-assisted content entry before generative features.
- Keep frontend, backend, and provider integrations behind explicit interfaces.

## Consequences

- The browser interface can be responsive and later installed as a progressive web app.
- TypeScript catches many frontend data-shape errors during development.
- Python provides a direct path to language-processing and ML libraries.
- FastAPI supplies validation and an OpenAPI contract from which frontend types can be generated.
- SQLite avoids account and database-server setup, but eventual multi-device synchronization will require an additional service.
- The frontend and backend require two development toolchains, so unified setup scripts and clear documentation are important.

## Reconsider when

- local installation proves too complex for the intended audience;
- required offline phone behavior cannot be delivered well by the selected client approach;
- profiling shows a demonstrated performance limit rather than a hypothetical concern;
- a chosen dictionary or speech capability imposes incompatible deployment constraints.
