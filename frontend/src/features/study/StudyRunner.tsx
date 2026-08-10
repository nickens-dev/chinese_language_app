import { useState, type FormEvent } from "react";

import { advanceStudySession, reviewStudyAttempt, submitStudyAttempt } from "../../api/study";
import type { StudyAttemptResult, StudySession } from "./types";

interface StudyRunnerProps { initialSession: StudySession; onExit: () => void; }
const responseHints = { characters: "Type simplified or traditional characters", english: "Type the English meaning", pinyin: "Type pinyin with tone marks or numbers" };

export function StudyRunner({ initialSession, onExit }: StudyRunnerProps) {
  const [session, setSession] = useState(initialSession);
  const [answer, setAnswer] = useState("");
  const [result, setResult] = useState<StudyAttemptResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const prompt = session.currentPrompt;

  async function check(event: FormEvent) { event.preventDefault(); if (!answer.trim() || !prompt) return; setBusy(true); setError(null); try { setResult(await submitStudyAttempt(session.id, answer)); } catch (reason) { setError(reason instanceof Error ? reason.message : "The answer could not be checked."); } finally { setBusy(false); } }
  async function override(addToCard: boolean) {
    if (!result) return;
    setBusy(true);
    setError(null);
    try {
      setResult(await reviewStudyAttempt(result.attemptId, addToCard));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "The result could not be updated.");
    } finally {
      setBusy(false);
    }
  }

  async function next() { setBusy(true); setError(null); try { const updated = await advanceStudySession(session.id); setSession(updated); setAnswer(""); setResult(null); } catch (reason) { setError(reason instanceof Error ? reason.message : "The session could not continue."); } finally { setBusy(false); } }

  if (session.status === "completed") {
    const summary = session.summary;
    return <section className="page study-complete">
      <div className="completion-heading">
        <span className="completion-check">✓</span>
        <div><p className="kicker">Session complete</p><h1>You studied {session.actualCount} card{session.actualCount === 1 ? "" : "s"}.</h1><p>Results use your final reviewed judgments. Historical accuracy is specific to {session.promptChannel} → {session.responseChannel}.</p></div>
        <button className="primary-button" type="button" onClick={onExit}>Return to decks</button>
      </div>
      {summary && <>
        <div className="summary-grid" aria-label="Session score summary">
          <article><strong>{summary.correctPercent}%</strong><span>Answered correctly</span></article>
          <article><strong>{summary.averageScore}%</strong><span>Average match score</span></article>
          <article><strong>{summary.correctCount}</strong><span>Correct</span></article>
          <article><strong>{summary.mostlyCorrectCount}</strong><span>Mostly correct</span></article>
          <article><strong>{summary.incorrectCount}</strong><span>Incorrect</span></article>
          <article><strong>{summary.overriddenCount}</strong><span>Learner overrides</span></article>
        </div>
        <div className="results-panel">
          <div className="results-heading"><div><p className="kicker">Card results</p><h2>Performance by word</h2></div><span>{session.promptChannel} → {session.responseChannel}</span></div>
          <div className="results-table-wrap"><table className="results-table"><thead><tr><th>Card</th><th>Your answer</th><th>This session</th><th>Match</th><th>Historical accuracy</th></tr></thead><tbody>{summary.results.map((item) => <tr key={item.promptId}><td><strong lang="zh-Hans">{item.simplified}</strong><span>{item.pinyin}</span><small>{item.english}</small></td><td>{item.answer}</td><td><span className={`result-badge verdict-${item.finalVerdict}`}>{item.finalVerdict.replace("_", " ")}</span>{item.overridden && <small>Reviewed by you</small>}</td><td>{Math.round(item.score * 100)}%</td><td><strong>{item.historicalPercent}%</strong><small>{item.historicalCorrect} of {item.historicalAttempts} correct</small></td></tr>)}</tbody></table></div>
        </div>
      </>}
    </section>;
  }  if (!prompt) return null;
  const percent = Math.round((prompt.position / prompt.total) * 100);
  return <section className="page study-runner">
    <div className="runner-top"><button className="back-button" type="button" onClick={onExit}>× End session</button><span>Card {prompt.position + 1} of {prompt.total}</span></div>
    <div className="progress-track"><span style={{ width: `${percent}%` }}/></div>
    <div className="prompt-card"><p className="kicker">{prompt.promptChannel} → {prompt.responseChannel}</p><div className={`study-prompt prompt-${prompt.promptChannel}`} lang={prompt.promptChannel === "characters" ? "zh-Hans" : undefined}>{prompt.promptText}</div>
      <form onSubmit={check}><label htmlFor="study-answer">{responseHints[prompt.responseChannel]}</label><input id="study-answer" autoFocus autoComplete="off" disabled={Boolean(result)} value={answer} onChange={(event) => setAnswer(event.target.value)}/>{error && <p className="form-error" role="alert">{error}</p>}
        {!result ? <button className="primary-button" disabled={busy || !answer.trim()}>{busy ? "Checking…" : "Check answer"}</button> : <div className={`answer-feedback verdict-${result.verdict}`} role="status"><div><strong>{result.verdict.replace("_", " ")}</strong><span>{Math.round(result.score * 100)}% match</span></div><p>{result.feedback}</p><p><small>Expected answer</small>{result.expectedAnswers.join(" · ")}</p>{result.overridden && <p className="override-confirmation">{result.acceptedAnswerAdded ? "Marked correct and saved as an accepted answer for this card." : "Marked correct for this attempt."}</p>}{result.finalVerdict !== "correct" && <div className="review-actions"><span>Disagree with this result?</span><button className="text-button" type="button" disabled={busy} onClick={() => override(false)}>Mark correct</button><button className="text-button" type="button" disabled={busy} onClick={() => override(true)}>Mark correct + save answer</button></div>}<button className="primary-button" type="button" disabled={busy} onClick={next}>{busy ? "Loading…" : prompt.position + 1 === prompt.total ? "Finish session" : "Continue →"}</button></div>}
      </form>
    </div>
  </section>;
}