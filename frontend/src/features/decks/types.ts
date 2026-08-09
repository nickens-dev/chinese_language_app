export type DeckAccent = "jade" | "coral" | "gold" | "ink";

export interface DeckSummary {
  id: string;
  name: string;
  description: string;
  itemCount: number;
  dueCount: number;
  weakCount: number;
  lastStudiedAt: string | null;
  accent: DeckAccent;
  createdAt: string;
  updatedAt: string;
}

export interface DeckInput {
  name: string;
  description: string;
  accent: DeckAccent;
}
