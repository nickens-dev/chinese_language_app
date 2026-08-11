export type ProgressChannel = "characters" | "english" | "pinyin";
export interface ProgressOverview { accuracyPercent:number; averageScore:number; attempts:number; uniqueCards:number; completedSessions:number; studyDays:number; currentStreak:number; longestStreak:number; averageCardsPerSession:number; lastStudiedAt:string|null; }
export interface ProgressTrendPoint { date:string; attempts:number; accuracyPercent:number; }
export interface DirectionProgress { promptChannel:ProgressChannel; responseChannel:ProgressChannel; attempts:number; accuracyPercent:number; }
export interface CardProgress { itemId:string; simplified:string; pinyin:string; english:string; promptChannel:ProgressChannel; responseChannel:ProgressChannel; correct:number; attempts:number; accuracyPercent:number; averageScore:number; lastStudiedAt:string; }
export interface RecentSession { id:string; completedAt:string; deckNames:string[]; promptChannel:ProgressChannel; responseChannel:ProgressChannel; cardCount:number; accuracyPercent:number; overriddenCount:number; }
export interface ProgressReport { overview:ProgressOverview; trend:ProgressTrendPoint[]; directions:DirectionProgress[]; cards:CardProgress[]; recentSessions:RecentSession[]; }
export interface ProgressFilters { days:0|7|30|90; timezoneOffset?:number; deckId?:string; promptChannel?:ProgressChannel; responseChannel?:ProgressChannel; }