import type { StudyAttemptResult, StudySession, StudySessionInput } from "../features/study/types";

async function readError(response: Response): Promise<Error> {
  try {
    const body = (await response.json()) as { detail?: string };
    return new Error(body.detail ?? "The study request could not be completed.");
  } catch {
    return new Error("The study request could not be completed.");
  }
}

async function readSession(response: Response): Promise<StudySession> {
  if (!response.ok) throw await readError(response);
  return response.json() as Promise<StudySession>;
}

export async function createStudySession(values: StudySessionInput): Promise<StudySession> {
  return readSession(await fetch("/api/study/sessions", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(values) }));
}

export async function submitStudyAttempt(sessionId: string, answer: string): Promise<StudyAttemptResult> {
  const response = await fetch(`/api/study/sessions/${sessionId}/attempts`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ answer }) });
  if (!response.ok) throw await readError(response);
  return response.json() as Promise<StudyAttemptResult>;
}

export async function advanceStudySession(sessionId: string): Promise<StudySession> {
  return readSession(await fetch(`/api/study/sessions/${sessionId}/advance`, { method: "POST" }));
}
export async function reviewStudyAttempt(
  attemptId: string,
  addToCard: boolean,
): Promise<StudyAttemptResult> {
  const response = await fetch(`/api/study/sessions/attempts/${attemptId}/review`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ addToCard }),
  });
  if (!response.ok) throw await readError(response);
  return response.json() as Promise<StudyAttemptResult>;
}