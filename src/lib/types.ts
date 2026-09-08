export type MeetingMode = "interview" | "sales" | "meeting";

export type Speaker = "them" | "you" | "room";

export type SessionPhase = "setup" | "live" | "notes";

export type ViewMode = "split" | "you" | "them";

export type AssistStatus = "idle" | "thinking" | "ready" | "error";

export interface TranscriptLine {
  id: string;
  speaker: Speaker;
  text: string;
  at: number;
}

export interface AssistResult {
  spoken: string;
  points: string[];
  code: string;
}

export interface SessionNotes {
  summary: string;
  keyPoints: string[];
  questions: string[];
  actionItems: string[];
  followUpEmail: string;
}

export interface Profile {
  displayName: string;
  role: string;
  company: string;
  resume: string;
  jobDescription: string;
  mode: MeetingMode;
}

export interface SavedSession {
  id: string;
  title: string;
  mode: MeetingMode;
  startedAt: number;
  durationSec: number;
  transcript: TranscriptLine[];
  notes: SessionNotes | null;
}
