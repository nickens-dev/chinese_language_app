import type { CardInput, LanguageCard } from "../features/cards/types";

interface ApiErrorBody {
  detail?: string;
}

async function readError(response: Response): Promise<Error> {
  let message = "The card request could not be completed.";
  try {
    const body = (await response.json()) as ApiErrorBody;
    if (body.detail) message = body.detail;
  } catch {
    // Preserve the useful fallback when the response is not JSON.
  }
  return new Error(message);
}

async function readCard(response: Response): Promise<LanguageCard> {
  if (!response.ok) throw await readError(response);
  return response.json() as Promise<LanguageCard>;
}

export async function fetchCards(
  deckId: string,
  signal?: AbortSignal,
): Promise<LanguageCard[]> {
  const response = await fetch(`/api/decks/${deckId}/cards`, { signal });
  if (!response.ok) throw await readError(response);
  return response.json() as Promise<LanguageCard[]>;
}

export async function createCard(
  deckId: string,
  values: CardInput,
): Promise<LanguageCard> {
  return readCard(
    await fetch(`/api/decks/${deckId}/cards`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(values),
    }),
  );
}

export async function updateCard(
  cardId: string,
  values: Partial<CardInput>,
): Promise<LanguageCard> {
  return readCard(
    await fetch(`/api/cards/${cardId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(values),
    }),
  );
}

export async function removeCard(deckId: string, cardId: string): Promise<void> {
  const response = await fetch(`/api/decks/${deckId}/cards/${cardId}`, {
    method: "DELETE",
  });
  if (!response.ok) throw await readError(response);
}