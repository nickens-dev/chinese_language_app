import { useState, type FormEvent } from "react";

import { advanceStudySession, submitStudyAttempt } from "../../api/study";
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
  async function next() { setBusy(true); setError(null); try { const updated = await advanceStudySession(session.id); setSession(updated); setAnswer(""); setResult(null); } catch (reason) { setError(reason instanceof Error ? reason.message : "The session could not continue."); } finally { setBusy(false); } }

  if (session.status === "completed") return <section className="page study-complete"><div className="completion-card"><span>✓</span><p className="kicker">Session complete</p><h1>You studied {session.actualCount} card{session.actualCount === 1 ? "" : "s"}.</h1><p>Every answer was saved locally. Mastery-based review and detailed progress summaries will build on this history.</p><button className="primary-button" type="button" onClick={onExit}>Return to decks</button></div></section>;
  if (!prompt) return null;
  const percent = Math.round((prompt.position / prompt.total) * 100);
  return <section className="page study-runner">
    <div className="runner-top"><button className="back-button" type="button" onClick={onExit}>× End session</button><span>Card {prompt.position + 1} of {prompt.total}</span></div>
    <div className="progress-track"><span style={{ width: `${percent}%` }}/></div>
    <div className="prompt-card"><p className="kicker">{prompt.promptChannel} → {prompt.responseChannel}</p><div className={`study-prompt prompt-${prompt.promptChannel}`} lang={prompt.promptChannel === "characters" ? "zh-Hans" : undefined}>{prompt.promptText}</div>
      <form onSubmit={check}><label htmlFor="study-answer">{responseHints[prompt.responseChannel]}</label><input id="study-answer" autoFocus autoComplete="off" disabled={Boolean(result)} value={answer} onChange={(event) => setAnswer(event.target.value)}/>{error && <p className="form-error" role="alert">{error}</p>}
        {!result ? <button className="primary-button" disabled={busy || !answer.trim()}>{busy ? "Checking…" : "Check answer"}</button> : <div className={`answer-feedback verdict-${result.verdict}`} role="status"><div><strong>{result.verdict.replace("_", " ")}</strong><span>{Math.round(result.score * 100)}% match</span></div><p>{result.feedback}</p><p><small>Expected answer</small>{result.expectedAnswers.join(" · ")}</p><button className="primary-button" type="button" disabled={busy} onClick={next}>{busy ? "Loading…" : prompt.position + 1 === prompt.total ? "Finish session" : "Continue →"}</button></div>}
      </form>
    </div>
  </section>;
}