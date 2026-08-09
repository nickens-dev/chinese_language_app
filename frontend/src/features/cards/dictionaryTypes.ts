export interface DictionaryCandidate {
  simplified: string;
  traditional: string;
  pinyin: string;
  definitions: string[];
  sourceName: string;
  sourceEntryId: string | null;
}