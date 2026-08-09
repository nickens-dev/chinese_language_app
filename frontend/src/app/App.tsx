import { useCallback, useEffect, useState } from "react";

import { archiveDeck, createDeck, fetchDecks, updateDeck } from "../api/decks";
import { DeckDetail } from "../features/decks/DeckDetail";
import { DeckLibrary } from "../features/decks/DeckLibrary";
import type { DeckInput, DeckSummary } from "../features/decks/types";
import { StudyRunner } from "../features/study/StudyRunner";
import { StudySetup } from "../features/study/StudySetup";
import type { StudySession } from "../features/study/types";

export type LoadState =
  | { status: "loading"; decks: DeckSummary[] }
  | { status: "ready"; decks: DeckSummary[] }
  | { status: "error"; decks: DeckSummary[]; message: string };
type View = { name: "library" } | { name: "deck"; deckId: string } | { name: "setup"; deckIds: string[] } | { name: "study"; session: StudySession };

export function App() {
  const [loadState, setLoadState] = useState<LoadState>({ status: "loading", decks: [] });
  const [view, setView] = useState<View>({ name: "library" });

  useEffect(() => { const controller = new AbortController(); fetchDecks(controller.signal).then((decks) => setLoadState({ status: "ready", decks })).catch((error: unknown) => { if (error instanceof DOMException && error.name === "AbortError") return; setLoadState({ status: "error", decks: [], message: error instanceof Error ? error.message : "Unknown error" }); }); return () => controller.abort(); }, []);
  const selectedDeck = view.name === "deck" ? loadState.decks.find((deck) => deck.id === view.deckId) ?? null : null;
  async function handleCreate(values: DeckInput) { const deck = await createDeck(values); setLoadState((current) => ({ status: "ready", decks: [...current.decks, deck] })); setView({ name: "deck", deckId: deck.id }); }
  async function handleUpdate(deckId: string, values: Partial<DeckInput>) { const deck = await updateDeck(deckId, values); setLoadState((current) => ({ status: "ready", decks: current.decks.map((item) => item.id === deck.id ? deck : item) })); }
  const handleItemCountChange = useCallback((deckId: string, count: number) => { setLoadState((current) => ({ ...current, decks: current.decks.map((deck) => deck.id === deckId && deck.itemCount !== count ? { ...deck, itemCount: count } : deck) })); }, []);
  async function handleArchive(deckId: string) { await archiveDeck(deckId); setLoadState((current) => ({ status: "ready", decks: current.decks.filter((deck) => deck.id !== deckId) })); setView({ name: "library" }); }
  const goHome = () => setView({ name: "library" });
  const beginSetup = (deckIds: string[]) => setView({ name: "setup", deckIds });

  let content;
  if (view.name === "setup") content = <StudySetup decks={loadState.decks} initialDeckIds={view.deckIds} onBack={goHome} onStart={(session) => setView({ name: "study", session })}/>;
  else if (view.name === "study") content = <StudyRunner initialSession={view.session} onExit={goHome}/>;
  else if (selectedDeck) content = <DeckDetail deck={selectedDeck} onBack={goHome} onUpdate={handleUpdate} onArchive={handleArchive} onItemCountChange={handleItemCountChange} onStudy={beginSetup}/>;
  else content = <DeckLibrary state={loadState} onOpen={(deckId) => setView({ name: "deck", deckId })} onCreate={handleCreate} onStudy={beginSetup}/>;

  return <div className="app-shell">
    <aside className="sidebar"><button className="brand brand-button" type="button" onClick={goHome} aria-label="Chinese Study home"><span className="brand-mark" lang="zh-Hans">中文</span><span>Study</span></button><nav aria-label="Main navigation"><a href="#home">Home</a><button className={view.name === "library" || view.name === "deck" ? "active" : ""} type="button" onClick={goHome}>Decks</button><button className={view.name === "setup" || view.name === "study" ? "active" : ""} type="button" onClick={() => beginSetup([])}>Study</button><a href="#progress">Progress</a><a href="#suggestions">Suggestions</a></nav><div className="local-note"><span className="status-dot" aria-hidden="true"/><div><strong>Local mode</strong><small>Data stays on this device</small></div></div></aside>
    <main id="top"><header className="topbar"><div><span className="eyebrow">{view.name === "study" ? "Focused practice" : view.name === "setup" ? "Session builder" : "Your library"}</span></div><button className="icon-button" type="button" aria-label="Open settings">⚙</button></header>{content}</main>
  </div>;
}