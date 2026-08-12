import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { expect, test, vi } from "vitest";

import * as studyApi from "../../api/study";
import type { DeckSummary } from "../decks/types";
import { StudySetup } from "./StudySetup";

vi.mock("../../api/study");

const decks: DeckSummary[] = ["Core", "Travel"].map((name, index) => ({
  id: `deck-${index + 1}`, name, description: "", itemCount: 2,
  dueCount: 0, weakCount: 0, lastStudiedAt: null, accent: "jade",
  createdAt: "2026-08-01", updatedAt: "2026-08-01",
}));

test("selects every deck and submits new cards in mixed mode", async () => {
  vi.mocked(studyApi.createStudySession).mockRejectedValue(new Error("stop after request"));
  render(<StudySetup decks={decks} initialDeckIds={[]} onBack={vi.fn()} onStart={vi.fn()}/>);

  fireEvent.click(screen.getByRole("button", { name: "Select all" }));
  expect(screen.getByRole("button", { name: "Clear all" })).toBeInTheDocument();
  fireEvent.click(screen.getByRole("checkbox", { name: /Mixed mode/ }));
  fireEvent.change(screen.getByLabelText("Selection focus"), { target: { value: "new" } });
  fireEvent.click(screen.getByRole("button", { name: /Start 4-card session/ }));

  await waitFor(() => expect(studyApi.createStudySession).toHaveBeenCalledWith({
    deckIds: ["deck-1", "deck-2"], requestedCount: 30,
    promptChannel: "characters", responseChannel: "english",
    selectionPolicy: "new", mixedMode: true,
  }));
});
