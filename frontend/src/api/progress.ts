import type { ProgressFilters, ProgressReport } from "../features/progress/types";

export async function fetchProgress(filters: ProgressFilters, signal?: AbortSignal): Promise<ProgressReport> {
  const parameters = new URLSearchParams({ days: String(filters.days), timezoneOffset: String(filters.timezoneOffset ?? new Date().getTimezoneOffset()) });
  if (filters.deckId) parameters.set("deckId", filters.deckId);
  if (filters.promptChannel) parameters.set("promptChannel", filters.promptChannel);
  if (filters.responseChannel) parameters.set("responseChannel", filters.responseChannel);
  const response = await fetch(`/api/progress?${parameters}`, { signal });
  if (!response.ok) {
    let message = "Progress could not be loaded.";
    try { const body = await response.json() as { detail?: string }; if (body.detail) message = body.detail; } catch { /* use fallback */ }
    throw new Error(message);
  }
  return response.json() as Promise<ProgressReport>;
}