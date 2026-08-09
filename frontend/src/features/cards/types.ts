export type CardType = "word" | "phrase" | "sentence";

export interface LanguageCard {
  id: string;
  itemType: CardType;
  simplified: string;
  traditional: string;
  pinyin: string;
  english: string;
  notes: string;
  sourceName: string;
  sourceEntryId: string | null;
  createdAt: string;
  updatedAt: string;
}

export interface CardInput {
  itemType: CardType;
  simplified: string;
  traditional: string;
  pinyin: string;
  english: string;
  notes: string;
  sourceName: string;
  sourceEntryId: string | null;
}