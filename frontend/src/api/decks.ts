import type { DeckSummary } from "../features/decks/types";

const DECKS_URL = "/api/decks";

export async function fetchDecks(signal?: AbortSignal): Promise<DeckSummary[]> {
  const response = await fetch(DECKS_URL, { signal });

  if (!response.ok) {
    throw new Error(`Deck request failed with status ${response.status}.`);
  }

  return response.json() as Promise<DeckSummary[]>;
}
