import type { DeckInput, DeckSummary } from "../features/decks/types";

const DECKS_URL = "/api/decks";

interface ApiErrorBody {
  detail?: string;
}

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
  }
}

async function readError(response: Response): Promise<ApiError> {
  let message = "The deck request could not be completed.";
  try {
    const body = (await response.json()) as ApiErrorBody;
    if (body.detail) message = body.detail;
  } catch {
    // The status remains useful when a provider returns a non-JSON error.
  }
  return new ApiError(message, response.status);
}

async function readDeck(response: Response): Promise<DeckSummary> {
  if (!response.ok) throw await readError(response);
  return response.json() as Promise<DeckSummary>;
}

export async function fetchDecks(signal?: AbortSignal): Promise<DeckSummary[]> {
  const response = await fetch(DECKS_URL, { signal });
  if (!response.ok) throw await readError(response);
  return response.json() as Promise<DeckSummary[]>;
}

export async function createDeck(values: DeckInput): Promise<DeckSummary> {
  return readDeck(
    await fetch(DECKS_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(values),
    }),
  );
}

export async function updateDeck(
  deckId: string,
  values: Partial<DeckInput>,
): Promise<DeckSummary> {
  return readDeck(
    await fetch(DECKS_URL + "/" + deckId, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(values),
    }),
  );
}

export async function archiveDeck(deckId: string): Promise<void> {
  const response = await fetch(DECKS_URL + "/" + deckId, { method: "DELETE" });
  if (!response.ok) throw await readError(response);
}
