import { useMemo, useState, type FormEvent } from "react";

import { createStudySession } from "../../api/study";
import type { DeckSummary } from "../decks/types";
import type { StudyChannel, StudySession } from "./types";

interface StudySetupProps { decks: DeckSummary[]; initialDeckIds: string[]; onBack: () => void; onStart: (session: StudySession) => void; }
const labels: Record<StudyChannel, string> = { characters: "Chinese characters", english: "English text", pinyin: "Pinyin" };
const validResponses: Record<StudyChannel, StudyChannel[]> = { characters: ["english", "pinyin"], english: ["characters"], pinyin: ["english"] };

export function StudySetup({ decks, initialDeckIds, onBack, onStart }: StudySetupProps) {
  const [selected, setSelected] = useState(new Set(initialDeckIds));
  const [count, setCount] = useState(30);
  const [prompt, setPrompt] = useState<StudyChannel>("characters");
  const [response, setResponse] = useState<StudyChannel>("english");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const available = useMemo(() => decks.filter((deck) => selected.has(deck.id)).reduce((sum, deck) => sum + deck.itemCount, 0), [decks, selected]);

  function changePrompt(next: StudyChannel) { setPrompt(next); setResponse(validResponses[next][0]); }
  async function start(event: FormEvent) {
    event.preventDefault(); setBusy(true); setError(null);
    try { onStart(await createStudySession({ deckIds: [...selected], requestedCount: count, promptChannel: prompt, responseChannel: response })); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "The session could not be started."); setBusy(false); }
  }

  return <section className="page study-setup">
    <button className="back-button" type="button" onClick={onBack}>← Back to decks</button>
    <div className="page-heading"><div><p className="kicker">Design your practice</p><h1>Build a study session</h1><p>Choose the content, session size, and independent question and answer formats.</p></div></div>
    <form className="study-setup-grid" onSubmit={start}>
      <div className="study-panel"><span className="step-number">1</span><h2>Choose decks</h2><div className="study-deck-options">{decks.map((deck) => <label key={deck.id}><input type="checkbox" checked={selected.has(deck.id)} onChange={() => setSelected((current) => { const next = new Set(current); if (next.has(deck.id)) next.delete(deck.id); else next.add(deck.id); return next; })}/><span><strong>{deck.name}</strong><small>{deck.itemCount} cards</small></span></label>)}</div></div>
      <div className="study-panel"><span className="step-number">2</span><h2>Choose the formats</h2><div className="format-controls"><label><span>Show me</span><select value={prompt} onChange={(event) => changePrompt(event.target.value as StudyChannel)}>{Object.entries(labels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label><span className="format-arrow">→</span><label><span>I will type</span><select value={response} onChange={(event) => setResponse(event.target.value as StudyChannel)}>{validResponses[prompt].map((value) => <option key={value} value={value}>{labels[value]}</option>)}</select></label></div></div>
      <div className="study-panel session-length"><span className="step-number">3</span><h2>Set session length</h2><label><span>Number of cards</span><input type="number" min="1" max="500" value={count} onChange={(event) => setCount(Number(event.target.value))}/></label><p>{available} card{available === 1 ? "" : "s"} available; shared cards are only shown once.</p></div>
      <div className="study-start">{error && <p className="form-error" role="alert">{error}</p>}<button className="primary-button" disabled={busy || selected.size === 0 || available === 0 || count < 1}>{busy ? "Building session…" : `Start ${Math.min(count, available)}-card session →`}</button></div>
    </form>
  </section>;
}