import { useEffect, useMemo, useState } from "react";

import { fetchProgress } from "../../api/progress";
import { createStudySession } from "../../api/study";
import type { DeckSummary } from "../decks/types";
import type { StudySession } from "../study/types";
import type { ProgressFilters, ProgressReport, ProgressTrendPoint } from "./types";

interface ProgressPageProps { decks: DeckSummary[]; onStudy: () => void; onStart: (session: StudySession) => void; }
const modes = [
  ["characters", "english", "Characters → English"],
  ["english", "characters", "English → Characters"],
  ["characters", "pinyin", "Characters → Pinyin"],
  ["pinyin", "english", "Pinyin → English"],
] as const;
const modeLabel = (prompt: string, response: string) => `${prompt} → ${response}`;
const dateLabel = (value: string) => new Intl.DateTimeFormat("en", { month: "short", day: "numeric" }).format(new Date(value));

function TrendChart({ points }: { points: ProgressTrendPoint[] }) {
  if (!points.length) return <div className="progress-empty-chart">Complete a study session to begin your trend.</div>;
  const width = 760, height = 240, left = 42, top = 18, bottom = 35;
  const innerWidth = width - left - 15, innerHeight = height - top - bottom;
  const maxAttempts = Math.max(...points.map((point) => point.attempts), 1);
  const x = (index: number) => left + (points.length === 1 ? innerWidth / 2 : index * innerWidth / (points.length - 1));
  const accuracyY = (value: number) => top + innerHeight * (1 - value / 100);
  const line = points.map((point, index) => `${x(index)},${accuracyY(point.accuracyPercent)}`).join(" ");
  return <div className="trend-chart-wrap"><svg className="trend-chart" viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Accuracy line and attempt volume by study day">
    {[0, 50, 100].map((value) => <g key={value}><line x1={left} x2={width - 15} y1={accuracyY(value)} y2={accuracyY(value)} className="chart-grid"/><text x="4" y={accuracyY(value) + 4}>{value}%</text></g>)}
    {points.map((point, index) => { const barHeight = innerHeight * point.attempts / maxAttempts; return <rect key={point.date} x={x(index) - 8} y={top + innerHeight - barHeight} width="16" height={barHeight} rx="4" className="attempt-bar"><title>{dateLabel(point.date)}: {point.attempts} attempts</title></rect>; })}
    <polyline points={line} className="accuracy-line"/>
    {points.map((point, index) => <circle key={point.date} cx={x(index)} cy={accuracyY(point.accuracyPercent)} r="4" className="accuracy-dot"><title>{dateLabel(point.date)}: {point.accuracyPercent}% correct</title></circle>)}
    {points.map((point, index) => (points.length <= 8 || index === 0 || index === points.length - 1) && <text key={point.date} x={x(index)} y={height - 7} textAnchor="middle">{dateLabel(point.date)}</text>)}
  </svg><div className="chart-legend"><span><i className="legend-line"/>Reviewed accuracy</span><span><i className="legend-bar"/>Attempts</span></div></div>;
}

export function ProgressPage({ decks, onStudy, onStart }: ProgressPageProps) {
  const [filters, setFilters] = useState<ProgressFilters>({ days: 30 });
  const [report, setReport] = useState<ProgressReport | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [weakBusy, setWeakBusy] = useState(false);
  const [weakError, setWeakError] = useState<string | null>(null);
  useEffect(() => { const controller = new AbortController(); fetchProgress(filters, controller.signal).then((value) => { setReport(value); setError(null); }).catch((reason: unknown) => { if (reason instanceof DOMException && reason.name === "AbortError") return; setError(reason instanceof Error ? reason.message : "Progress could not be loaded."); }).finally(() => { if (!controller.signal.aborted) setLoading(false); }); return () => controller.abort(); }, [filters]);
  const selectedMode = filters.promptChannel ? `${filters.promptChannel}:${filters.responseChannel}` : "all";
  const overview = report?.overview;
  const cards = useMemo(() => report?.cards ?? [], [report]);
  async function studyWeak() {
    if (!filters.promptChannel || !filters.responseChannel) return;
    const deckIds = filters.deckId ? [filters.deckId] : decks.filter((deck) => deck.itemCount > 0).map((deck) => deck.id);
    setWeakBusy(true); setWeakError(null);
    try {
      onStart(await createStudySession({ deckIds, requestedCount: 30, promptChannel: filters.promptChannel, responseChannel: filters.responseChannel, selectionPolicy: "weak" }));
    } catch (reason) {
      setWeakError(reason instanceof Error ? reason.message : "A weak-card session could not be started.");
      setWeakBusy(false);
    }
  }

  return <section className="page progress-page">
    <div className="page-heading"><div><p className="kicker">Learning history</p><h1>Progress</h1><p>See where practice is working and which words or study directions need attention.</p></div><div className="progress-actions"><button className="text-button" type="button" disabled={!filters.promptChannel || weakBusy} onClick={studyWeak}>{weakBusy ? "Building…" : "Study weak cards"}</button><button className="primary-button" type="button" onClick={onStudy}>Start study session</button></div></div>{!filters.promptChannel && <p className="progress-action-hint">Choose a study direction to build a weak-card session.</p>}{weakError && <p className="form-error" role="alert">{weakError}</p>}
    <div className="progress-filters" aria-label="Progress filters">
      <label><span>Time range</span><select value={filters.days} onChange={(event) => setFilters((current) => ({ ...current, days: Number(event.target.value) as ProgressFilters["days"] }))}><option value="7">7 days</option><option value="30">30 days</option><option value="90">90 days</option><option value="0">All time</option></select></label>
      <label><span>Deck</span><select value={filters.deckId ?? ""} onChange={(event) => setFilters((current) => ({ ...current, deckId: event.target.value || undefined }))}><option value="">All decks</option>{decks.map((deck) => <option key={deck.id} value={deck.id}>{deck.name}</option>)}</select></label>
      <label><span>Study direction</span><select value={selectedMode} onChange={(event) => { const [promptChannel, responseChannel] = event.target.value.split(":"); setFilters((current) => ({ ...current, promptChannel: promptChannel === "all" ? undefined : promptChannel as ProgressFilters["promptChannel"], responseChannel: promptChannel === "all" ? undefined : responseChannel as ProgressFilters["responseChannel"] })); }}><option value="all">All directions</option>{modes.map(([prompt, response, label]) => <option key={`${prompt}:${response}`} value={`${prompt}:${response}`}>{label}</option>)}</select></label>
    </div>
    {loading && <p className="notice">Loading progress…</p>}{error && <p className="notice error" role="alert">{error}</p>}
    {!loading && report && <>
      <div className="progress-overview" aria-label="Progress overview">
        <article><strong>{overview?.accuracyPercent}%</strong><span>Reviewed accuracy</span></article><article><strong>{overview?.attempts}</strong><span>Attempts</span></article><article><strong>{overview?.uniqueCards}</strong><span>Unique cards</span></article><article><strong>{overview?.completedSessions}</strong><span>Sessions</span></article><article><strong>{overview?.studyDays}</strong><span>Study days</span></article><article><strong>{overview?.currentStreak}</strong><span>Day streak</span></article>
      </div>
      <div className="progress-main-grid"><article className="progress-panel trend-panel"><div className="progress-panel-heading"><div><p className="kicker">Performance over time</p><h2>Accuracy and practice volume</h2></div><span>{overview?.averageScore}% average match</span></div><TrendChart points={report.trend}/></article>
        <aside className="progress-panel direction-panel"><p className="kicker">Study directions</p><h2>Skills stay separate</h2>{report.directions.length ? <div className="direction-list">{report.directions.map((direction) => <div key={`${direction.promptChannel}:${direction.responseChannel}`}><span>{modeLabel(direction.promptChannel, direction.responseChannel)}</span><strong>{direction.accuracyPercent}%</strong><small>{direction.attempts} attempts</small><div><i style={{ width: `${direction.accuracyPercent}%` }}/></div></div>)}</div> : <p className="muted-copy">No direction history in this range.</p>}</aside>
      </div>
      <article className="progress-panel word-progress"><div className="progress-panel-heading"><div><p className="kicker">Word performance</p><h2>Cards needing attention first</h2></div><span>{cards.length} card-direction records</span></div>{cards.length ? <div className="results-table-wrap"><table className="results-table"><thead><tr><th>Card</th><th>Direction</th><th>Accuracy</th><th>Attempts</th><th>Status and reason</th><th>Average match</th><th>Last studied</th></tr></thead><tbody>{cards.map((card) => <tr key={`${card.itemId}:${card.promptChannel}:${card.responseChannel}`}><td><strong lang="zh-Hans">{card.simplified}</strong><span>{card.pinyin}</span><small>{card.english}</small></td><td>{modeLabel(card.promptChannel, card.responseChannel)}</td><td><strong>{card.accuracyPercent}%</strong><small>{card.correct} of {card.attempts} correct</small></td><td>{card.attempts}</td><td><div className="schedule-status">{card.isDue && <span className="result-badge verdict-mostly_correct">Due</span>}{card.weakReason && <><span className="result-badge verdict-incorrect">Weak</span><small>{card.weakReason}</small></>}</div></td><td>{card.averageScore}%</td><td>{dateLabel(card.lastStudiedAt)}</td></tr>)}</tbody></table></div> : <div className="progress-empty-chart">No card history matches these filters.</div>}</article>
      <article className="progress-panel recent-sessions"><div className="progress-panel-heading"><div><p className="kicker">Recent activity</p><h2>Completed sessions</h2></div><span>{overview?.averageCardsPerSession} cards per session</span></div>{report.recentSessions.length ? <div className="session-list">{report.recentSessions.map((item) => <div key={item.id}><time>{dateLabel(item.completedAt)}</time><span><strong>{item.deckNames.join(", ")}</strong><small>{modeLabel(item.promptChannel, item.responseChannel)} · {item.cardCount} cards{item.overriddenCount ? ` · ${item.overriddenCount} reviewed` : ""}</small></span><strong>{item.accuracyPercent}%</strong></div>)}</div> : <p className="muted-copy">No completed sessions match these filters.</p>}</article>
    </>}
  </section>;
}