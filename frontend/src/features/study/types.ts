export type StudyChannel = "characters" | "english" | "pinyin";
export type StudyVerdict = "correct" | "mostly_correct" | "incorrect";

export interface StudyPrompt {
  id: string;
  position: number;
  total: number;
  promptText: string;
  promptChannel: StudyChannel;
  responseChannel: StudyChannel;
  answered: boolean;
}

export interface StudySession {
  id: string;
  status: "active" | "completed";
  requestedCount: number;
  actualCount: number;
  currentIndex: number;
  promptChannel: StudyChannel;
  responseChannel: StudyChannel;
  createdAt: string;
  completedAt: string | null;
  currentPrompt: StudyPrompt | null;
}

export interface StudySessionInput {
  deckIds: string[];
  requestedCount: number;
  promptChannel: StudyChannel;
  responseChannel: StudyChannel;
}

export interface StudyAttemptResult {
  attemptId: string;
  score: number;
  verdict: StudyVerdict;
  finalVerdict: StudyVerdict;
  overridden: boolean;
  acceptedAnswerAdded: boolean;
  expectedAnswers: string[];
  feedback: string;
  evaluatorVersion: string;
}