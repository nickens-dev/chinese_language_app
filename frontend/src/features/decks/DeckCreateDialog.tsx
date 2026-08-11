import { useState, type FormEvent } from "react";

import { deckAccents, type DeckAccent, type DeckInput } from "./types";

interface DeckCreateDialogProps {
  onClose: () => void;
  onCreate: (values: DeckInput) => Promise<void>;
}

export function DeckCreateDialog({ onClose, onCreate }: DeckCreateDialogProps) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [accent, setAccent] = useState<DeckAccent>("jade");
  const [status, setStatus] = useState<"idle" | "saving">("idle");
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setStatus("saving");
    setError(null);
    try {
      await onCreate({ name, description, accent });
    } catch (reason: unknown) {
      setError(reason instanceof Error ? reason.message : "The deck could not be created.");
      setStatus("idle");
    }
  }

  return (
    <div className="modal-backdrop">
      <section className="modal-card" role="dialog" aria-modal="true" aria-labelledby="new-deck-title">
        <div className="modal-heading">
          <div>
            <p className="kicker">New collection</p>
            <h2 id="new-deck-title">Create a deck</h2>
          </div>
          <button className="icon-button" type="button" onClick={onClose} aria-label="Close new deck form">×</button>
        </div>
        <form className="deck-form" onSubmit={handleSubmit}>
          <label>
            <span>Deck name</span>
            <input
              autoFocus
              required
              maxLength={80}
              value={name}
              onChange={(event) => setName(event.target.value)}
              placeholder="For example: Travel Basics"
            />
          </label>
          <label>
            <span>Description <small>optional</small></span>
            <textarea
              maxLength={500}
              value={description}
              onChange={(event) => setDescription(event.target.value)}
              placeholder="What belongs in this deck?"
              rows={3}
            />
          </label>
          <fieldset className="accent-picker">
            <legend>Card color</legend>
            <div>
              {deckAccents.map((option) => (
                <label key={option.value} className={"accent-option accent-" + option.value}>
                  <input
                    type="radio"
                    name="accent"
                    value={option.value}
                    checked={accent === option.value}
                    onChange={() => setAccent(option.value)}
                  />
                  <span aria-hidden="true" />
                  {option.label}
                </label>
              ))}
            </div>
          </fieldset>
          {error && <p className="form-error" role="alert">{error}</p>}
          <div className="form-actions">
            <button className="text-button" type="button" onClick={onClose}>Cancel</button>
            <button className="primary-button" type="submit" disabled={status === "saving"}>
              {status === "saving" ? "Creating…" : "Create deck"}
            </button>
          </div>
        </form>
      </section>
    </div>
  );
}
