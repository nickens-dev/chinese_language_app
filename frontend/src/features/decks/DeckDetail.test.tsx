import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { DeckDetail } from "./DeckDetail";
import type { DeckSummary } from "./types";

const deck: DeckSummary = {
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
};

describe("DeckDetail", () => {
  it("saves editable deck fields", async () => {
    const onUpdate = vi.fn().mockResolvedValue(undefined);
    render(
      <DeckDetail
        deck={deck}
        onBack={vi.fn()}
        onUpdate={onUpdate}
        onArchive={vi.fn()}
        onItemCountChange={vi.fn()}
      />,
    );

    fireEvent.change(screen.getByLabelText("Deck name"), {
      target: { value: "Travel & Transit" },
    });
    fireEvent.change(screen.getByLabelText("Card color"), {
      target: { value: "ink" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Save changes" }));

    await waitFor(() =>
      expect(onUpdate).toHaveBeenCalledWith("one", {
        name: "Travel & Transit",
        description: "Trains and hotels",
        accent: "ink",
      }),
    );
  });

  it("requires confirmation before archiving", async () => {
    const onArchive = vi.fn().mockResolvedValue(undefined);
    render(
      <DeckDetail
        deck={deck}
        onBack={vi.fn()}
        onUpdate={vi.fn()}
        onArchive={onArchive}
        onItemCountChange={vi.fn()}
      />,
    );

    fireEvent.click(screen.getByRole("button", { name: "Archive deck" }));
    expect(onArchive).not.toHaveBeenCalled();

    fireEvent.click(screen.getByRole("button", { name: "Archive" }));
    await waitFor(() => expect(onArchive).toHaveBeenCalledWith("one"));
  });
});
