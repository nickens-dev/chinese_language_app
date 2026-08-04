import type { DeckSummary } from "./types";

interface DeckCardProps {
  deck: DeckSummary;
  selected: boolean;
  onToggle: (deckId: string) => void;
}

function studyLabel(value: string | null): string {
  if (!value) return "Not studied yet";
  return `Last studied ${new Intl.DateTimeFormat("en", { dateStyle: "medium" }).format(new Date(value))}`;
}

export function DeckCard({ deck, selected, onToggle }: DeckCardProps) {
  return (
    <article className={`deck-card accent-${deck.accent} ${selected ? "selected" : ""}`}>
      <div className="deck-card-topline">
        <span className="deck-glyph" aria-hidden="true">{deck.name.slice(0, 1)}</span>
        <label className="select-deck">
          <input
            type="checkbox"
            checked={selected}
            onChange={() => onToggle(deck.id)}
          />
          <span>Select</span>
        </label>
      </div>
      <div className="deck-copy">
        <h2>{deck.name}</h2>
        <p>{deck.description}</p>
      </div>
      <dl className="deck-stats">
        <div><dt>Items</dt><dd>{deck.itemCount}</dd></div>
        <div><dt>Due</dt><dd>{deck.dueCount}</dd></div>
        <div><dt>Weak</dt><dd>{deck.weakCount}</dd></div>
      </dl>
      <footer className="deck-card-footer">
        <span>{studyLabel(deck.lastStudiedAt)}</span>
        <div>
          <button className="text-button" type="button">Open</button>
          <button className="small-primary" type="button">Study</button>
        </div>
      </footer>
    </article>
  );
}
