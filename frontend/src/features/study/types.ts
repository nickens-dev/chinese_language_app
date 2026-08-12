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
  selectionReason: string;
  selectionBucket: string;
}

export interface StudyCardResult {
  promptId: string;
  simplified: string;
  pinyin: string;
  english: string;
  answer: string;
  score: number;
  evaluatorVerdict: StudyVerdict;
  finalVerdict: StudyVerdict;
  overridden: boolean;
  selectionReason: string;
  historicalCorrect: number;
  historicalAttempts: number;
  historicalPercent: number;
}

export interface StudySessionSummary {
  correctCount: number;
  mostlyCorrectCount: number;
  incorrectCount: number;
  overriddenCount: number;
  correctPercent: number;
  averageScore: number;
  results: StudyCardResult[];
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
  summary: StudySessionSummary | null;
}

export interface StudySessionInput {
  deckIds: string[];
  requestedCount: number;
  promptChannel: StudyChannel;
  responseChannel: StudyChannel;
  selectionPolicy?: "balanced" | "due" | "weak" | "new";
  itemIds?: string[];
  mixedMode?: boolean;
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
