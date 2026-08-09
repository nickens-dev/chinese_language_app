import { useCallback, useEffect, useState } from "react";

import {
  archiveDeck,
  createDeck,
  fetchDecks,
  updateDeck,
} from "../api/decks";
import { DeckDetail } from "../features/decks/DeckDetail";
import { DeckLibrary } from "../features/decks/DeckLibrary";
import type { DeckInput, DeckSummary } from "../features/decks/types";

export type LoadState =
  | { status: "loading"; decks: DeckSummary[] }
  | { status: "ready"; decks: DeckSummary[] }
  | { status: "error"; decks: DeckSummary[]; message: string };

export function App() {
  const [loadState, setLoadState] = useState<LoadState>({
    status: "loading",
    decks: [],
  });
  const [selectedDeckId, setSelectedDeckId] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();

    fetchDecks(controller.signal)
      .then((decks) => setLoadState({ status: "ready", decks }))
      .catch((error: unknown) => {
        if (error instanceof DOMException && error.name === "AbortError") return;
        const message = error instanceof Error ? error.message : "Unknown error";
        setLoadState({ status: "error", decks: [], message });
      });

    return () => controller.abort();
  }, []);

  const selectedDeck =
    loadState.decks.find((deck) => deck.id === selectedDeckId) ?? null;

  async function handleCreate(values: DeckInput) {
    const deck = await createDeck(values);
    setLoadState((current) => ({
      status: "ready",
      decks: [...current.decks, deck],
    }));
    setSelectedDeckId(deck.id);
  }

  async function handleUpdate(deckId: string, values: Partial<DeckInput>) {
    const deck = await updateDeck(deckId, values);
    setLoadState((current) => ({
      status: "ready",
      decks: current.decks.map((item) => (item.id === deck.id ? deck : item)),
    }));
  }

  const handleItemCountChange = useCallback((deckId: string, count: number) => {
    setLoadState((current) => ({
      ...current,
      decks: current.decks.map((deck) =>
        deck.id === deckId && deck.itemCount !== count
          ? { ...deck, itemCount: count }
          : deck,
      ),
    }));
  }, []);
  async function handleArchive(deckId: string) {
    await archiveDeck(deckId);
    setLoadState((current) => ({
      status: "ready",
      decks: current.decks.filter((deck) => deck.id !== deckId),
    }));
    setSelectedDeckId(null);
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <button
          className="brand brand-button"
          type="button"
          onClick={() => setSelectedDeckId(null)}
          aria-label="Chinese Study home"
        >
          <span className="brand-mark" lang="zh-Hans">中文</span>
          <span>Study</span>
        </button>
        <nav aria-label="Main navigation">
          <a href="#home">Home</a>
          <button
            className="active"
            type="button"
            aria-current="page"
            onClick={() => setSelectedDeckId(null)}
          >
            Decks
          </button>
          <a href="#study">Study</a>
          <a href="#progress">Progress</a>
          <a href="#suggestions">Suggestions</a>
        </nav>
        <div className="local-note">
          <span className="status-dot" aria-hidden="true" />
          <div><strong>Local mode</strong><small>Data stays on this device</small></div>
        </div>
      </aside>

      <main id="top">
        <header className="topbar">
          <div><span className="eyebrow">Your library</span></div>
          <button className="icon-button" type="button" aria-label="Open settings">⚙</button>
        </header>
        {selectedDeck ? (
          <DeckDetail
            deck={selectedDeck}
            onBack={() => setSelectedDeckId(null)}
            onUpdate={handleUpdate}
            onArchive={handleArchive}
            onItemCountChange={handleItemCountChange}
          />
        ) : (
          <DeckLibrary
            state={loadState}
            onOpen={setSelectedDeckId}
            onCreate={handleCreate}
          />
        )}
      </main>
    </div>
  );
}
