import { useEffect, useState } from "react";

import { fetchDecks } from "../api/decks";
import { DeckLibrary } from "../features/decks/DeckLibrary";
import type { DeckSummary } from "../features/decks/types";

type LoadState =
  | { status: "loading"; decks: DeckSummary[] }
  | { status: "ready"; decks: DeckSummary[] }
  | { status: "error"; decks: DeckSummary[]; message: string };

export function App() {
  const [loadState, setLoadState] = useState<LoadState>({
    status: "loading",
    decks: [],
  });

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

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="#top" aria-label="Chinese Study home">
          <span className="brand-mark" lang="zh-Hans">中文</span>
          <span>Study</span>
        </a>
        <nav aria-label="Main navigation">
          <a href="#home">Home</a>
          <a className="active" href="#decks" aria-current="page">Decks</a>
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
        <DeckLibrary state={loadState} />
      </main>
    </div>
  );
}
