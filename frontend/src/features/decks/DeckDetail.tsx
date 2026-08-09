import { useState, type FormEvent } from "react";

import { DeckCards } from "../cards/DeckCards";
import type { DeckAccent, DeckInput, DeckSummary } from "./types";

interface DeckDetailProps {
  deck: DeckSummary;
  onBack: () => void;
  onUpdate: (deckId: string, values: Partial<DeckInput>) => Promise<void>;
  onArchive: (deckId: string) => Promise<void>;
  onItemCountChange: (deckId: string, count: number) => void;
  onStudy?: (deckIds: string[]) => void;
}

export function DeckDetail({ deck, onBack, onUpdate, onArchive, onItemCountChange, onStudy }: DeckDetailProps) {
  const [name, setName] = useState(deck.name);
  const [description, setDescription] = useState(deck.description);
  const [accent, setAccent] = useState<DeckAccent>(deck.accent);
  const [saving, setSaving] = useState(false);
  const [archivePending, setArchivePending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);


  async function handleSave(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setSaved(false);
    setError(null);
    try {
      await onUpdate(deck.id, { name, description, accent });
      setSaved(true);
    } catch (reason: unknown) {
      setError(reason instanceof Error ? reason.message : "The deck could not be updated.");
    } finally {
      setSaving(false);
    }
  }

  async function handleArchive() {
    setSaving(true);
    setError(null);
    try {
      await onArchive(deck.id);
    } catch (reason: unknown) {
      setError(reason instanceof Error ? reason.message : "The deck could not be archived.");
      setSaving(false);
    }
  }

  return (
    <section className="page deck-detail">
      <button className="back-button" type="button" onClick={onBack}>← All decks</button>
      <div className="detail-heading">
        <div>
          <p className="kicker">Deck details</p>
          <h1>{deck.name}</h1>
          <p>{deck.itemCount} items • {deck.dueCount} due • {deck.weakCount} weak</p>
        </div>
        <button className="primary-button" type="button" disabled={deck.itemCount === 0} onClick={() => onStudy?.([deck.id])}>Study deck</button>
      </div>

      <div className="detail-grid">
        <DeckCards deckId={deck.id} onCountChange={onItemCountChange} />

        <aside className="settings-panel">
          <p className="kicker">Settings</p>
          <h2>Deck information</h2>
          <form className="deck-form" onSubmit={handleSave}>
            <label>
              <span>Deck name</span>
              <input required maxLength={80} value={name} onChange={(event) => { setName(event.target.value); setSaved(false); }} />
            </label>
            <label>
              <span>Description</span>
              <textarea rows={4} maxLength={500} value={description} onChange={(event) => { setDescription(event.target.value); setSaved(false); }} />
            </label>
            <label>
              <span>Card color</span>
              <select value={accent} onChange={(event) => { setAccent(event.target.value as DeckAccent); setSaved(false); }}>
                <option value="jade">Jade</option>
                <option value="coral">Coral</option>
                <option value="gold">Gold</option>
                <option value="ink">Ink</option>
              </select>
            </label>
            {error && <p className="form-error" role="alert">{error}</p>}
            {saved && <p className="form-success" role="status">Changes saved locally.</p>}
            <button className="primary-button" type="submit" disabled={saving}>{saving ? "Saving…" : "Save changes"}</button>
          </form>

          <div className="danger-zone">
            <h3>Archive deck</h3>
            <p>Archiving removes this deck from the library without deleting its history.</p>
            {archivePending ? (
              <div className="archive-confirm">
                <p>Archive “{deck.name}”?</p>
                <button className="text-button" type="button" onClick={() => setArchivePending(false)}>Cancel</button>
                <button className="danger-button" type="button" onClick={handleArchive} disabled={saving}>Archive</button>
              </div>
            ) : (
              <button className="danger-button outline" type="button" onClick={() => setArchivePending(true)}>Archive deck</button>
            )}
          </div>
        </aside>
      </div>
    </section>
  );
}
