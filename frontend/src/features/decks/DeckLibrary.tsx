import { useMemo, useState } from "react";

import { DeckCard } from "./DeckCard";
import { DeckCreateDialog } from "./DeckCreateDialog";
import type { DeckInput, DeckSummary } from "./types";

interface DeckLibraryProps {
  state:
    | { status: "loading"; decks: DeckSummary[] }
    | { status: "ready"; decks: DeckSummary[] }
    | { status: "error"; decks: DeckSummary[]; message: string };
  onOpen: (deckId: string) => void;
  onCreate: (values: DeckInput) => Promise<void>;
  onStudy?: (deckIds: string[]) => void;
}

export function DeckLibrary({ state, onOpen, onCreate, onStudy }: DeckLibraryProps) {
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [creating, setCreating] = useState(false);

  const visibleDecks = useMemo(() => {
    const normalizedQuery = query.trim().toLocaleLowerCase();
    if (!normalizedQuery) return state.decks;
    return state.decks.filter((deck) =>
      (deck.name + " " + deck.description).toLocaleLowerCase().includes(normalizedQuery),
    );
  }, [query, state.decks]);

  function toggleDeck(deckId: string) {
    setSelected((current) => {
      const next = new Set(current);
      if (next.has(deckId)) {
        next.delete(deckId);
      } else {
        next.add(deckId);
      }
      return next;
    });
  }

  async function handleCreate(values: DeckInput) {
    await onCreate(values);
    setCreating(false);
  }

  return (
    <section className="page" id="decks">
      <div className="page-heading">
        <div>
          <p className="kicker">Shape your practice</p>
          <h1>Language decks</h1>
          <p>Build vocabulary, then study it through any prompt and response combination.</p>
        </div>
        <button className="primary-button" type="button" onClick={() => setCreating(true)}>
          <span>＋</span> New deck
        </button>
      </div>

      <div className="library-tools">
        <label className="search-box">
          <span aria-hidden="true">⌕</span>
          <span className="sr-only">Search decks</span>
          <input
            type="search"
            placeholder="Search decks"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
        </label>
        <div className="filter-pills" aria-label="Deck filters">
          <button className="active" type="button">All</button>
          <button type="button">Recently studied</button>
          <button type="button">Needs attention</button>
        </div>
      </div>

      {state.status === "loading" && <p className="notice">Loading your decks…</p>}
      {state.status === "error" && (
        <div className="notice error" role="alert">
          <strong>The local API is unavailable.</strong>
          <span>{state.message} Start the FastAPI backend and refresh this page.</span>
        </div>
      )}
      {state.status === "ready" && visibleDecks.length === 0 && (
        <div className="notice empty-library">
          <strong>{query ? "No decks match your search." : "Your deck library is empty."}</strong>
          <span>{query ? "Try a different search." : "Create a deck to start organizing vocabulary."}</span>
        </div>
      )}

      <div className="deck-grid">
        {visibleDecks.map((deck) => (
          <DeckCard
            key={deck.id}
            deck={deck}
            selected={selected.has(deck.id)}
            onToggle={toggleDeck}
            onOpen={onOpen}
          />
        ))}
      </div>

      {selected.size > 0 && (
        <div className="selection-bar" aria-live="polite">
          <span><strong>{selected.size}</strong> deck{selected.size === 1 ? "" : "s"} selected</span>
          <div>
            <button className="text-button light" type="button" onClick={() => setSelected(new Set())}>Clear</button>
            <button className="primary-button light" type="button" onClick={() => onStudy?.([...selected])}>Build study session →</button>
          </div>
        </div>
      )}

      {creating && <DeckCreateDialog onClose={() => setCreating(false)} onCreate={handleCreate} />}
    </section>
  );
}
