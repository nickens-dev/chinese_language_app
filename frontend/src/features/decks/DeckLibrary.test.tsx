import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { DeckLibrary } from "./DeckLibrary";
import type { DeckSummary } from "./types";

const decks: DeckSummary[] = [
  {
    id: "one",
    name: "Travel Basics",
    description: "Trains and hotels",
    itemCount: 0,
    dueCount: 0,
    weakCount: 0,
    lastStudiedAt: null,
    accent: "jade",
    createdAt: "2026-08-06T00:00:00Z",
    updatedAt: "2026-08-06T00:00:00Z",
  },
  {
    id: "two",
    name: "Food",
    description: "Restaurants and meals",
    itemCount: 4,
    dueCount: 1,
    weakCount: 0,
    lastStudiedAt: null,
    accent: "coral",
    createdAt: "2026-08-06T00:01:00Z",
    updatedAt: "2026-08-06T00:01:00Z",
  },
];

describe("DeckLibrary", () => {
  it("filters visual cards by name and description", () => {
    render(
      <DeckLibrary
        state={{ status: "ready", decks }}
        onOpen={vi.fn()}
        onCreate={vi.fn()}
      />,
    );

    fireEvent.change(screen.getByRole("searchbox", { name: "Search decks" }), {
      target: { value: "restaurant" },
    });

    expect(screen.getByRole("heading", { name: "Food" })).toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: "Travel Basics" })).not.toBeInTheDocument();
  });

  it("collects new deck fields and submits them", async () => {
    const onCreate = vi.fn().mockResolvedValue(undefined);
    render(
      <DeckLibrary
        state={{ status: "ready", decks }}
        onOpen={vi.fn()}
        onCreate={onCreate}
      />,
    );

    fireEvent.click(screen.getByRole("button", { name: "＋ New deck" }));
    fireEvent.change(screen.getByLabelText("Deck name"), {
      target: { value: "Daily Life" },
    });
    fireEvent.change(screen.getByLabelText("Description optional"), {
      target: { value: "Useful routines" },
    });
    fireEvent.click(screen.getByLabelText("Gold"));
    fireEvent.click(screen.getByRole("button", { name: "Create deck" }));

    await waitFor(() =>
      expect(onCreate).toHaveBeenCalledWith({
        name: "Daily Life",
        description: "Useful routines",
        accent: "gold",
      }),
    );
  });

  it("starts a session builder from a non-empty deck card", () => {
    const onStudy = vi.fn();
    render(
      <DeckLibrary
        state={{ status: "ready", decks }}
        onOpen={vi.fn()}
        onCreate={vi.fn()}
        onStudy={onStudy}
      />,
    );

    const studyButtons = screen.getAllByRole("button", { name: "Study" });
    expect(studyButtons[0]).toBeDisabled();
    fireEvent.click(studyButtons[1]);
    expect(onStudy).toHaveBeenCalledWith(["two"]);
  });});
