import { useState, type FormEvent } from "react";

import { searchDictionary } from "../../api/dictionary";
import type { DictionaryCandidate } from "./dictionaryTypes";

import type { CardInput, CardType, LanguageCard } from "./types";

interface CardEditorDialogProps {
  card?: LanguageCard;
  onClose: () => void;
  onSave: (values: CardInput) => Promise<void>;
  onRemove?: () => Promise<void>;
}

export function CardEditorDialog({ card, onClose, onSave, onRemove }: CardEditorDialogProps) {
  const [itemType, setItemType] = useState<CardType>(card?.itemType ?? "word");
  const [simplified, setSimplified] = useState(card?.simplified ?? "");
  const [traditional, setTraditional] = useState(card?.traditional ?? "");
  const [pinyin, setPinyin] = useState(card?.pinyin ?? "");
  const [english, setEnglish] = useState(card?.english ?? "");
  const [notes, setNotes] = useState(card?.notes ?? "");
  const [sourceName, setSourceName] = useState(card?.sourceName ?? "user");
  const [sourceEntryId, setSourceEntryId] = useState<string | null>(card?.sourceEntryId ?? null);
  const [saving, setSaving] = useState(false);
  const [removePending, setRemovePending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lookupQuery, setLookupQuery] = useState("");
  const [candidates, setCandidates] = useState<DictionaryCandidate[]>([]);
  const [searching, setSearching] = useState(false);
  const [lookupError, setLookupError] = useState<string | null>(null);

  async function handleLookup(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const query = lookupQuery.trim();
    if (!query) return;
    setSearching(true);
    setLookupError(null);
    try {
      setCandidates(await searchDictionary(query));
    } catch (reason: unknown) {
      setLookupError(reason instanceof Error ? reason.message : "Dictionary search failed.");
    } finally {
      setSearching(false);
    }
  }

  function applyCandidate(candidate: DictionaryCandidate) {
    setSimplified(candidate.simplified);
    setTraditional(candidate.traditional);
    setPinyin(candidate.pinyin);
    setEnglish(candidate.definitions.join("; "));
    setSourceName(candidate.sourceName);
    setSourceEntryId(candidate.sourceEntryId);
    setCandidates([]);
  }
  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setError(null);
    try {
      await onSave({ itemType, simplified, traditional, pinyin, english, notes, sourceName, sourceEntryId });
    } catch (reason: unknown) {
      setError(reason instanceof Error ? reason.message : "The card could not be saved.");
      setSaving(false);
    }
  }

  async function handleRemove() {
    if (!onRemove) return;
    setSaving(true);
    setError(null);
    try {
      await onRemove();
    } catch (reason: unknown) {
      setError(reason instanceof Error ? reason.message : "The card could not be removed.");
      setSaving(false);
    }
  }

  return (
    <div className="modal-backdrop" role="presentation" onMouseDown={(event) => {
      if (event.target === event.currentTarget && !saving) onClose();
    }}>
      <section className="modal-card card-editor" role="dialog" aria-modal="true" aria-labelledby="card-editor-title">
        <div className="modal-heading">
          <div>
            <p className="kicker">{card ? "Edit content" : sourceName !== "user" ? "Sourced entry" : "Manual entry"}</p>
            <h2 id="card-editor-title">{card ? "Edit card" : "Add a card"}</h2>
          </div>
          <button className="icon-button" type="button" aria-label="Close" onClick={onClose} disabled={saving}>×</button>
        </div>
        {!card && (
          <section className="dictionary-assist" aria-labelledby="dictionary-assist-title">
            <div>
              <h3 id="dictionary-assist-title">Find dictionary content</h3>
              <p>Search English, characters, numbered pinyin, or tone-marked pinyin.</p>
            </div>
            <form className="dictionary-search" onSubmit={handleLookup}>
              <label className="sr-only" htmlFor="dictionary-query">Dictionary search</label>
              <input id="dictionary-query" value={lookupQuery} onChange={(event) => setLookupQuery(event.target.value)} placeholder="hello, 你好, or ni3 hao3" />
              <button className="small-primary" type="submit" disabled={searching || !lookupQuery.trim()}>{searching ? "Searching…" : "Search"}</button>
            </form>
            {lookupError && <p className="form-error" role="alert">{lookupError}</p>}
            {!searching && candidates.length === 0 && lookupQuery.trim() && !lookupError && sourceName === "user" && <p className="lookup-hint">Search to see sourced candidates. You can still enter the card manually below.</p>}
            {sourceName !== "user" && candidates.length === 0 && <p className="lookup-success">Candidate applied below. Review every field before saving.</p>}
            {candidates.length > 0 && (
              <div className="candidate-list" aria-label="Dictionary candidates">
                {candidates.map((candidate) => (
                  <button className="dictionary-candidate" type="button" key={`${candidate.sourceEntryId ?? "fallback"}-${candidate.simplified}-${candidate.pinyin}`} onClick={() => applyCandidate(candidate)}>
                    <span className="candidate-characters" lang="zh-Hans">{candidate.simplified}</span>
                    {candidate.traditional !== candidate.simplified && <span lang="zh-Hant">{candidate.traditional}</span>}
                    <span className="candidate-pinyin">{candidate.pinyin}</span>
                    <span className="candidate-definition">{candidate.definitions.length ? candidate.definitions.slice(0, 3).join("; ") : "No dictionary definition—complete the English field manually."}</span>
                    <span className="candidate-source">{candidate.sourceName}</span>
                  </button>
                ))}
              </div>
            )}
          </section>
        )}
        <form className="deck-form" onSubmit={handleSubmit}>
          <label>
            <span>Card type</span>
            <select aria-label="Card type" value={itemType} onChange={(event) => setItemType(event.target.value as CardType)}>
              <option value="word">Word</option>
              <option value="phrase">Phrase</option>
              <option value="sentence">Sentence</option>
            </select>
          </label>
          <label>
            <span>Simplified Chinese</span>
            <input lang="zh-Hans" required maxLength={120} autoFocus value={simplified} onChange={(event) => setSimplified(event.target.value)} placeholder="你好" />
          </label>
          <label>
            <span>Traditional Chinese <small>optional</small></span>
            <input lang="zh-Hant" maxLength={120} value={traditional} onChange={(event) => setTraditional(event.target.value)} placeholder="你好" />
          </label>
          <label>
            <span>Pinyin <small>optional for now</small></span>
            <input lang="zh-Latn-pinyin" maxLength={240} value={pinyin} onChange={(event) => setPinyin(event.target.value)} placeholder="nǐ hǎo" />
          </label>
          <label>
            <span>English meaning</span>
            <input required maxLength={300} value={english} onChange={(event) => setEnglish(event.target.value)} placeholder="hello; how are you" />
          </label>
          <label>
            <span>Notes <small>optional</small></span>
            <textarea rows={3} maxLength={1000} value={notes} onChange={(event) => setNotes(event.target.value)} placeholder="Usage, classifier, or memory aid" />
          </label>
          {sourceName !== "user" && <p className="source-note">Source: {sourceName}. Review and edit before saving.</p>}
          {error && <p className="form-error" role="alert">{error}</p>}
          {removePending && (
            <div className="remove-confirm" role="alert">
              <p>Remove this card from the deck?</p>
              <button className="text-button" type="button" onClick={() => setRemovePending(false)}>Cancel</button>
              <button className="danger-button" type="button" onClick={handleRemove} disabled={saving}>Remove</button>
            </div>
          )}
          <div className="form-actions card-form-actions">
            {card && onRemove && !removePending && <button className="danger-button outline" type="button" onClick={() => setRemovePending(true)} disabled={saving}>Remove card</button>}
            <span className="form-spacer" />
            <button className="text-button" type="button" onClick={onClose} disabled={saving}>Cancel</button>
            <button className="primary-button" type="submit" disabled={saving}>{saving ? "Saving…" : card ? "Save card" : "Add card"}</button>
          </div>
        </form>
      </section>
    </div>
  );
}