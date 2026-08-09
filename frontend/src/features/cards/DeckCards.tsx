import { useEffect, useState } from "react";

import { createCard, fetchCards, removeCard, updateCard } from "../../api/cards";
import { CardEditorDialog } from "./CardEditorDialog";
import type { CardInput, LanguageCard } from "./types";

interface DeckCardsProps {
  deckId: string;
  onCountChange: (deckId: string, count: number) => void;
}

export function DeckCards({ deckId, onCountChange }: DeckCardsProps) {
  const [cards, setCards] = useState<LanguageCard[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editorOpen, setEditorOpen] = useState(false);
  const [editingCard, setEditingCard] = useState<LanguageCard | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    fetchCards(deckId, controller.signal)
      .then((loadedCards) => {
        setCards(loadedCards);
        onCountChange(deckId, loadedCards.length);
        setError(null);
      })
      .catch((reason: unknown) => {
        if (reason instanceof DOMException && reason.name === "AbortError") return;
        setError(reason instanceof Error ? reason.message : "Cards could not be loaded.");
      })
      .finally(() => setLoading(false));
    return () => controller.abort();
  }, [deckId, onCountChange]);

  function openCreate() {
    setEditingCard(null);
    setEditorOpen(true);
  }

  function openEdit(card: LanguageCard) {
    setEditingCard(card);
    setEditorOpen(true);
  }

  async function handleSave(values: CardInput) {
    if (editingCard) {
      const saved = await updateCard(editingCard.id, values);
      setCards((current) => current.map((card) => card.id === saved.id ? saved : card));
    } else {
      const saved = await createCard(deckId, values);
      setCards((current) => {
        const next = [...current, saved];
        onCountChange(deckId, next.length);
        return next;
      });
    }
    setEditorOpen(false);
    setEditingCard(null);
  }

  async function handleRemove() {
    if (!editingCard) return;
    await removeCard(deckId, editingCard.id);
    setCards((current) => {
      const next = current.filter((card) => card.id !== editingCard.id);
      onCountChange(deckId, next.length);
      return next;
    });
    setEditorOpen(false);
    setEditingCard(null);
  }

  return (
    <section className="items-panel">
      <div className="panel-heading">
        <div>
          <p className="kicker">Contents</p>
          <h2>Language items</h2>
        </div>
        <button className="primary-button" type="button" onClick={openCreate}>＋ Add card</button>
      </div>

      {loading ? (
        <p className="notice card-notice">Loading cards…</p>
      ) : error ? (
        <p className="notice error card-notice" role="alert">{error}</p>
      ) : cards.length === 0 ? (
        <div className="empty-state">
          <span lang="zh-Hans">词</span>
          <h3>This deck is ready for vocabulary</h3>
          <p>Add a word, phrase, or sentence manually. Dictionary-assisted entry comes next.</p>
          <button className="text-button" type="button" onClick={openCreate}>Add the first card</button>
        </div>
      ) : (
        <div className="card-list">
          {cards.map((card) => (
            <button className="language-card" type="button" key={card.id} onClick={() => openEdit(card)} aria-label={`Edit ${card.simplified}`}>
              <span className="card-type">{card.itemType}</span>
              <span className="card-chinese" lang="zh-Hans">{card.simplified}</span>
              {card.traditional && card.traditional !== card.simplified && <span className="card-traditional" lang="zh-Hant">{card.traditional}</span>}
              {card.pinyin && <span className="card-pinyin" lang="zh-Latn-pinyin">{card.pinyin}</span>}
              <span className="card-english">{card.english}</span>
              {card.notes && <span className="card-notes">{card.notes}</span>}
              <span className="edit-hint">Edit</span>
            </button>
          ))}
        </div>
      )}

      {editorOpen && (
        <CardEditorDialog
          card={editingCard ?? undefined}
          onClose={() => { setEditorOpen(false); setEditingCard(null); }}
          onSave={handleSave}
          onRemove={editingCard ? handleRemove : undefined}
        />
      )}
    </section>
  );
}