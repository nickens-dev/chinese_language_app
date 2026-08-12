import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { expect, test, vi } from "vitest";

import * as progressApi from "../../api/progress";
import * as studyApi from "../../api/study";
import type { DeckSummary } from "../decks/types";
import { ProgressPage } from "./ProgressPage";
import type { ProgressReport } from "./types";

vi.mock("../../api/progress");
vi.mock("../../api/study");
const decks: DeckSummary[] = [{ id:"deck-1", name:"Core", description:"", itemCount:1, dueCount:0, weakCount:0, lastStudiedAt:null, accent:"jade", createdAt:"2026-08-01", updatedAt:"2026-08-01" }];
const report: ProgressReport = {
  overview:{ accuracyPercent:75, averageScore:82, attempts:4, uniqueCards:1, completedSessions:2, studyDays:2, currentStreak:2, longestStreak:3, averageCardsPerSession:2, lastStudiedAt:"2026-08-10T12:00:00Z" },
  trend:[{ date:"2026-08-10", attempts:4, accuracyPercent:75 }],
  directions:[{ promptChannel:"characters", responseChannel:"english", attempts:4, accuracyPercent:75 }],
  cards:[{ itemId:"card-1", simplified:"好", pinyin:"hǎo", english:"good", promptChannel:"characters", responseChannel:"english", correct:3, attempts:4, accuracyPercent:75, averageScore:82, lastStudiedAt:"2026-08-10T12:00:00Z", dueAt:"2026-08-09T12:00:00Z", isDue:true, weakReason:"75% reviewed accuracy" }],
  recentSessions:[{ id:"session-1", completedAt:"2026-08-10T12:00:00Z", deckNames:["Core"], promptChannel:"characters", responseChannel:"english", cardCount:2, accuracyPercent:50, overriddenCount:1 }],
};

test("shows progress aggregates and updates direction filters", async () => {
  vi.mocked(progressApi.fetchProgress).mockResolvedValue(report);
  render(<ProgressPage decks={decks} onStudy={vi.fn()} onStart={vi.fn()}/>);
  expect((await screen.findAllByText("75%")).length).toBeGreaterThan(0);
  expect(screen.getByText("好")).toBeInTheDocument();
  expect(screen.getByText("3 of 4 correct")).toBeInTheDocument();
  fireEvent.change(screen.getByLabelText("Study direction"), { target:{ value:"characters:english" } });
  await waitFor(() => expect(progressApi.fetchProgress).toHaveBeenLastCalledWith(expect.objectContaining({ promptChannel:"characters", responseChannel:"english" }), expect.any(AbortSignal)));
});

test("starts study from progress", async () => {
  vi.mocked(progressApi.fetchProgress).mockResolvedValue(report);
  const onStudy = vi.fn();
  render(<ProgressPage decks={decks} onStudy={onStudy} onStart={vi.fn()}/>);
  await screen.findByText("Learning history");
  fireEvent.click(screen.getByRole("button", { name:"Start study session" }));
  expect(onStudy).toHaveBeenCalledOnce();
});

test("builds a weak-only session from selected progress filters", async () => {
  vi.mocked(progressApi.fetchProgress).mockResolvedValue(report);
  vi.mocked(studyApi.createStudySession).mockRejectedValue(new Error("No weak cards match this deck and study direction."));
  render(<ProgressPage decks={decks} onStudy={vi.fn()} onStart={vi.fn()}/>);
  await screen.findByText("Learning history");
  expect(screen.getByRole("button", { name:"Study weak cards" })).toBeDisabled();
  fireEvent.change(screen.getByLabelText("Study direction"), { target:{ value:"characters:english" } });
  fireEvent.click(screen.getByRole("button", { name:"Study weak cards" }));
  await waitFor(() => expect(studyApi.createStudySession).toHaveBeenCalledWith(expect.objectContaining({ deckIds:["deck-1"], promptChannel:"characters", responseChannel:"english", selectionPolicy:"weak" })));
  expect(await screen.findByRole("alert")).toHaveTextContent("No weak cards match");
});