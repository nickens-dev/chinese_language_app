import { fireEvent, render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";

import type { DeckSummary } from "../decks/types";
import { SummaryPage } from "./SummaryPage";

const decks: DeckSummary[] = [{ id:"deck-1", name:"Core", description:"", itemCount:12, dueCount:4, weakCount:2, lastStudiedAt:null, accent:"jade", createdAt:"2026-08-01", updatedAt:"2026-08-01" }];

test("summarizes deck workload and links to detailed progress", () => {
  const onProgress = vi.fn();
  render(<SummaryPage decks={decks} onProgress={onProgress} onStudy={vi.fn()}/>);
  expect(screen.getByText("4 due")).toBeInTheDocument();
  expect(screen.getByText("2 weak")).toBeInTheDocument();
  expect(screen.getByText("Core")).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name:"View detailed progress →" }));
  expect(onProgress).toHaveBeenCalledOnce();
});
