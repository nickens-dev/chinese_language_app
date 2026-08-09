import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { expect, test, vi } from "vitest";

import * as studyApi from "../../api/study";
import { StudyRunner } from "./StudyRunner";
import type { StudySession } from "./types";

vi.mock("../../api/study");
const session: StudySession = { id: "session-1", status: "active", requestedCount: 1, actualCount: 1, currentIndex: 0, promptChannel: "characters", responseChannel: "english", createdAt: "2026-08-09T00:00:00Z", completedAt: null, currentPrompt: { id: "prompt-1", position: 0, total: 1, promptText: "你好", promptChannel: "characters", responseChannel: "english", answered: false } };

test("requires an answer and reveals feedback before continuing", async () => {
  vi.mocked(studyApi.submitStudyAttempt).mockResolvedValue({ score: 1, verdict: "correct", expectedAnswers: ["hello"], feedback: "Correct — nicely done.", evaluatorVersion: "typed-v1" });
  render(<StudyRunner initialSession={session} onExit={vi.fn()}/>);
  const check = screen.getByRole("button", { name: "Check answer" });
  expect(check).toBeDisabled();
  fireEvent.change(screen.getByLabelText("Type the English meaning"), { target: { value: "hello" } });
  fireEvent.click(check);
  await waitFor(() => expect(screen.getByText("Expected answer")).toBeInTheDocument());
  expect(screen.getByText("hello")).toBeInTheDocument();
  expect(screen.getByRole("button", { name: "Finish session" })).toBeInTheDocument();
});