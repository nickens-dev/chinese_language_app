import { fireEvent, render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";

import type { DeckSummary } from "../decks/types";
import { HomePage } from "./HomePage";

const decks: DeckSummary[] = [{ id:"deck-1", name:"Core", description:"", itemCount:12, dueCount:4, weakCount:2, lastStudiedAt:"2026-08-11", accent:"jade", createdAt:"2026-08-01", updatedAt:"2026-08-11" }];

test("shows the library snapshot and routes primary actions", () => {
  const onStudy = vi.fn();
  const onSummary = vi.fn();
  render(<HomePage decks={decks} onDecks={vi.fn()} onStudy={onStudy} onSummary={onSummary}/>);
  expect(screen.getByText("12")).toBeInTheDocument();
  expect(screen.getByText("4")).toBeInTheDocument();
  expect(screen.getByText("Core")).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name:"Start studying" }));
  fireEvent.click(screen.getByRole("button", { name:"Open summary →" }));
  expect(onStudy).toHaveBeenCalledOnce();
  expect(onSummary).toHaveBeenCalledOnce();
});
