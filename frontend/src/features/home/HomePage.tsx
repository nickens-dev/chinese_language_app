import type { DeckSummary } from "../decks/types";

interface HomePageProps {
  decks: DeckSummary[];
  onDecks: () => void;
  onStudy: () => void;
  onSummary: () => void;
}

export function HomePage({ decks, onDecks, onStudy, onSummary }: HomePageProps) {
  const cards = decks.reduce((total, deck) => total + deck.itemCount, 0);
  const due = decks.reduce((total, deck) => total + deck.dueCount, 0);
  const weak = decks.reduce((total, deck) => total + deck.weakCount, 0);
  const recent = [...decks].filter((deck) => deck.lastStudiedAt)
    .sort((left, right) => String(right.lastStudiedAt).localeCompare(String(left.lastStudiedAt)))[0];

  return <section className="page home-page">
    <div className="home-hero">
      <div><p className="kicker">Today&apos;s learning space</p><h1>Keep Chinese in motion.</h1><p>Choose a focused review, build your decks, or check the shape of your learning before you begin.</p><div className="home-actions"><button className="primary-button" type="button" onClick={onStudy}>Start studying</button><button className="secondary-button" type="button" onClick={onDecks}>Browse decks</button></div></div>
      <aside className="home-character" aria-label="Chinese study reminder"><span lang="zh-Hans">学</span><strong>Learn through use</strong><small>Study direction by direction.</small></aside>
    </div>
    <div className="home-stat-grid" aria-label="Library snapshot">
      <article><span>Decks</span><strong>{decks.length}</strong><small>Your study collections</small></article>
      <article><span>Cards</span><strong>{cards}</strong><small>Across active decks</small></article>
      <article><span>Due</span><strong>{due}</strong><small>Ready for scheduled review</small></article>
      <article><span>Weak</span><strong>{weak}</strong><small>Need focused practice</small></article>
    </div>
    <div className="home-grid">
      <article className="home-panel"><p className="kicker">Continue</p><h2>{recent ? recent.name : "Your first deck"}</h2><p>{recent ? "Return to the deck you studied most recently." : "Create or open a deck, then begin your first focused session."}</p><button className="text-button" type="button" onClick={onDecks}>Open deck library →</button></article>
      <article className="home-panel"><p className="kicker">Learning overview</p><h2>See the bigger picture</h2><p>Review a compact summary of your content, scheduled workload, and areas needing attention.</p><button className="text-button" type="button" onClick={onSummary}>Open summary →</button></article>
    </div>
  </section>;
}
