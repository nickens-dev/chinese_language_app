export const deckAccents = [
  { value: "jade", label: "Jade" },
  { value: "coral", label: "Coral" },
  { value: "gold", label: "Gold" },
  { value: "ink", label: "Ink" },
  { value: "sky", label: "Sky" },
  { value: "plum", label: "Plum" },
  { value: "rose", label: "Rose" },
  { value: "tangerine", label: "Tangerine" },
  { value: "moss", label: "Moss" },
  { value: "slate", label: "Slate" },
] as const;

export type DeckAccent = (typeof deckAccents)[number]["value"];

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
