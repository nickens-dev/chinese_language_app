import type { DictionaryCandidate } from "../features/cards/dictionaryTypes";

export async function searchDictionary(
  query: string,
  signal?: AbortSignal,
): Promise<DictionaryCandidate[]> {
  const parameters = new URLSearchParams({ q: query, limit: "10" });
  const response = await fetch(`/api/dictionary/search?${parameters}`, { signal });
  if (!response.ok) {
    let message = "Dictionary search could not be completed.";
    try {
      const body = (await response.json()) as { detail?: string };
      if (body.detail) message = body.detail;
    } catch {
      // Keep the stable fallback for non-JSON failures.
    }
    throw new Error(message);
  }
  return response.json() as Promise<DictionaryCandidate[]>;
}