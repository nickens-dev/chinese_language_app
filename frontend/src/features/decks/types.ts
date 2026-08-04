export interface DeckSummary {
  id: string;
  name: string;
  description: string;
  itemCount: number;
  dueCount: number;
  weakCount: number;
  lastStudiedAt: string | null;
  accent: "jade" | "coral" | "gold" | "ink";
}
