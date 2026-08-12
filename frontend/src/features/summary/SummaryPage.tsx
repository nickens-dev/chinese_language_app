import type { DeckSummary } from "../decks/types";

interface SummaryPageProps { decks: DeckSummary[]; onProgress: () => void; onStudy: () => void; }

export function SummaryPage({ decks, onProgress, onStudy }: SummaryPageProps) {
  const totals = decks.reduce((result, deck) => ({ cards: result.cards + deck.itemCount, due: result.due + deck.dueCount, weak: result.weak + deck.weakCount }), { cards: 0, due: 0, weak: 0 });
  const active = decks.filter((deck) => deck.itemCount > 0);

  return <section className="page summary-page">
    <div className="page-heading"><div><p className="kicker">At a glance</p><h1>Study summary</h1><p>A lightweight overview of your current library and review workload. Deeper learning history remains in Progress.</p></div><button className="primary-button" type="button" onClick={onStudy}>Start study session</button></div>
    <div className="summary-grid">
      <article className="summary-score"><p className="kicker">Library coverage</p><strong>{totals.cards}</strong><span>cards in {active.length} active deck{active.length === 1 ? "" : "s"}</span><div><i style={{ width: `${totals.cards ? Math.max(8, 100 - Math.min(100, totals.due / totals.cards * 100)) : 0}%` }}/></div><small>This visual is a structural placeholder for a future mastery measure.</small></article>
      <article className="summary-panel"><span className="summary-icon">◷</span><div><strong>{totals.due} due</strong><p>Scheduled card-directions ready for review.</p></div></article>
      <article className="summary-panel"><span className="summary-icon">△</span><div><strong>{totals.weak} weak</strong><p>Cards with explainable evidence for focused practice.</p></div></article>
      <article className="summary-panel"><span className="summary-icon">冊</span><div><strong>{decks.length} decks</strong><p>{active.length} currently contain study material.</p></div></article>
    </div>
    <div className="summary-section-heading"><div><p className="kicker">Deck workload</p><h2>Where review is waiting</h2></div><button className="text-button" type="button" onClick={onProgress}>View detailed progress →</button></div>
    <div className="summary-decks">{decks.length ? decks.map((deck) => <article key={deck.id}><div><strong>{deck.name}</strong><small>{deck.itemCount} cards</small></div><dl><div><dt>Due</dt><dd>{deck.dueCount}</dd></div><div><dt>Weak</dt><dd>{deck.weakCount}</dd></div></dl></article>) : <p className="notice">Deck summaries will appear here after you create your first deck.</p>}</div>
  </section>;
}
