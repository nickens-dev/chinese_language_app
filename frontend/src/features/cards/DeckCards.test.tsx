import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { CardEditorDialog } from "./CardEditorDialog";
import { DeckCards } from "./DeckCards";

const savedCard = {
  id: "card-one",
  itemType: "word" as const,
  simplified: "你好",
  traditional: "",
  pinyin: "nǐ hǎo",
  english: "hello",
  notes: "A greeting",
  sourceName: "user",
  sourceEntryId: null,
  createdAt: "2026-08-08T00:00:00Z",
  updatedAt: "2026-08-08T00:00:00Z",
};

afterEach(() => vi.unstubAllGlobals());

describe("card management", () => {
  it("collects the complete manual-entry card shape", async () => {
    const onSave = vi.fn().mockResolvedValue(undefined);
    render(<CardEditorDialog onClose={vi.fn()} onSave={onSave} />);

    fireEvent.change(screen.getByLabelText("Card type"), { target: { value: "phrase" } });
    fireEvent.change(screen.getByLabelText("Simplified Chinese"), { target: { value: "多少钱？" } });
    fireEvent.change(screen.getByLabelText(/Pinyin/), { target: { value: "duōshao qián?" } });
    fireEvent.change(screen.getByLabelText("English meaning"), { target: { value: "How much?" } });
    fireEvent.change(screen.getByLabelText(/Notes/), { target: { value: "Shopping" } });
    fireEvent.click(screen.getByRole("button", { name: "Add card" }));

    await waitFor(() => expect(onSave).toHaveBeenCalledWith({
      itemType: "phrase",
      simplified: "多少钱？",
      traditional: "",
      pinyin: "duōshao qián?",
      english: "How much?",
      notes: "Shopping",
      sourceName: "user",
      sourceEntryId: null,
    }));
  });

  it("loads a deck and adds its first card", async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(new Response(JSON.stringify([]), { status: 200 }))
      .mockResolvedValueOnce(new Response(JSON.stringify(savedCard), { status: 201 }));
    vi.stubGlobal("fetch", fetchMock);
    const onCountChange = vi.fn();
    render(<DeckCards deckId="deck-one" onCountChange={onCountChange} />);

    await screen.findByText("This deck is ready for vocabulary");
    fireEvent.click(screen.getByRole("button", { name: "Add the first card" }));
    fireEvent.change(screen.getByLabelText("Simplified Chinese"), { target: { value: "你好" } });
    fireEvent.change(screen.getByLabelText(/Pinyin/), { target: { value: "nǐ hǎo" } });
    fireEvent.change(screen.getByLabelText("English meaning"), { target: { value: "hello" } });
    fireEvent.change(screen.getByLabelText(/Notes/), { target: { value: "A greeting" } });
    fireEvent.click(screen.getByRole("button", { name: "Add card" }));

    expect(await screen.findByText("你好")).toBeInTheDocument();
    expect(screen.getByText("nǐ hǎo")).toBeInTheDocument();
    expect(onCountChange).toHaveBeenLastCalledWith("deck-one", 1);
    const request = fetchMock.mock.calls[1];
    expect(request[0]).toBe("/api/decks/deck-one/cards");
    expect(request[1]).toMatchObject({ method: "POST" });
  });
  it("applies a sourced dictionary candidate before saving", async () => {
    const candidate = {
      simplified: "你好",
      traditional: "你好",
      pinyin: "nǐ hǎo",
      definitions: ["hello", "hi"],
      sourceName: "CC-CEDICT",
      sourceEntryId: "cedict-hello",
    };
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(new Response(JSON.stringify([candidate]), { status: 200 })),
    );
    const onSave = vi.fn().mockResolvedValue(undefined);
    render(<CardEditorDialog onClose={vi.fn()} onSave={onSave} />);

    fireEvent.change(screen.getByLabelText("Dictionary search"), {
      target: { value: "hello" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Search" }));
    fireEvent.click(await screen.findByText("你好"));

    expect(screen.getByLabelText("Simplified Chinese")).toHaveValue("你好");
    expect(screen.getByLabelText(/Pinyin/)).toHaveValue("nǐ hǎo");
    expect(screen.getByLabelText("English meaning")).toHaveValue("hello; hi");
    expect(screen.getByText(/Source: CC-CEDICT/)).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Add card" }));
    await waitFor(() => expect(onSave).toHaveBeenCalledWith(expect.objectContaining({
      simplified: "你好",
      pinyin: "nǐ hǎo",
      sourceName: "CC-CEDICT",
      sourceEntryId: "cedict-hello",
    })));
  });
});