import { createServerFn } from "@tanstack/react-start";
import type { AssistResult, MeetingMode, SessionNotes } from "./types";

const MAX_RESUME = 8000;
const MAX_JOB = 4000;
const MAX_TRANSCRIPT = 4500;
const MAX_QUESTION = 1200;
const MAX_SCREEN = 4000;

export type AssistKind = "answer" | "screen";

export interface AssistInput {
  mode: MeetingMode;
  kind: AssistKind;
  resume: string;
  job: string;
  transcript: string;
  question: string;
  screenText: string;
}

export interface NotesInput {
  mode: MeetingMode;
  resume: string;
  job: string;
  transcript: string;
}

function clip(value: string, max: number) {
  return value.length > max ? value.slice(-max) : value;
}

function extractJson(text: string): unknown | null {
  const start = text.indexOf("{");
  const end = text.lastIndexOf("}");
  if (start < 0 || end < 0) return null;
  try {
    return JSON.parse(text.slice(start, end + 1));
  } catch {
    return null;
  }
}

async function chat(system: string, user: string, maxTokens: number) {
  const apiKey = process.env.XAI_API_KEY;
  if (!apiKey) return { ok: false as const, error: "AI is not available in this environment" };

  const res = await fetch("https://api.x.ai/v1/chat/completions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${apiKey}`,
    },
    body: JSON.stringify({
      model: "grok-4.5",
      temperature: 0.55,
      max_tokens: maxTokens,
      messages: [
        { role: "system", content: system },
        { role: "user", content: user },
      ],
    }),
  });

  if (!res.ok) {
    return { ok: false as const, error: `xAI API error ${res.status}` };
  }

  const body = (await res.json()) as {
    choices?: { message?: { content?: string } }[];
  };
  const text = body.choices?.[0]?.message?.content ?? "";
  return { ok: true as const, text };
}

function modeVoice(mode: MeetingMode) {
  if (mode === "interview") {
    return "The user is in a live job interview. Speak as them, first person, calm and specific. No filler, no 'great question'.";
  }
  if (mode === "sales") {
    return "The user is on a live sales or customer call. Give concise commercial answers they can say out loud. Be honest about tradeoffs.";
  }
  return "The user is in an internal meeting. Give short status-style answers: owner, status, risk, next step.";
}

export async function runAssist(
  data: AssistInput,
): Promise<{ ok: true; result: AssistResult } | { ok: false; error: string }> {
  const resume = clip(data.resume ?? "", MAX_RESUME);
  const job = clip(data.job ?? "", MAX_JOB);
  const transcript = clip(data.transcript ?? "", MAX_TRANSCRIPT);
  const question = clip(data.question ?? "", MAX_QUESTION);
  const screenText = clip(data.screenText ?? "", MAX_SCREEN);

  const system = `You are VEIL, a private meeting copilot. Only the user can see your output.
${modeVoice(data.mode)}
Ground every answer in their resume and the job/context when those are provided. Do not invent employers or metrics that are not in the resume.
If this is a coding prompt, give a speakable approach first, then compact TypeScript.
Return ONLY JSON with keys:
- spoken: string (what they should say, 3–6 sentences, no markdown)
- points: string[] (2–4 short talking points)
- code: string (code only if relevant, else empty string)`;

  const user = `KIND: ${data.kind === "screen" ? "Solve or explain what is on the shared screen." : "Answer the latest question."}
RESUME:
${resume || "(none)"}

JOB / CONTEXT:
${job || "(none)"}

SHARED SCREEN:
${screenText || "(none)"}

TRANSCRIPT (latest last):
${transcript || "(none)"}

FOCUS QUESTION:
${question || "(use the latest interviewer question in the transcript)"}`;

  const out = await chat(system, user, data.kind === "screen" ? 900 : 700);
  if (!out.ok) return out;

  const parsed = extractJson(out.text) as Partial<AssistResult> | null;
  if (!parsed || typeof parsed.spoken !== "string") {
    return {
      ok: true,
      result: { spoken: out.text.trim(), points: [], code: "" },
    };
  }
  return {
    ok: true,
    result: {
      spoken: parsed.spoken,
      points: Array.isArray(parsed.points) ? parsed.points.map(String).slice(0, 6) : [],
      code: typeof parsed.code === "string" ? parsed.code : "",
    },
  };
}

export async function runNotes(
  data: NotesInput,
): Promise<{ ok: true; notes: SessionNotes } | { ok: false; error: string }> {
  const transcript = clip(data.transcript ?? "", MAX_TRANSCRIPT);
  if (!transcript.trim()) {
    return {
      ok: true,
      notes: {
        summary: "No transcript was captured in this session.",
        keyPoints: [],
        questions: [],
        actionItems: [],
        followUpEmail: "",
      },
    };
  }

  const system = `You write private post-call notes for VEIL.
Return ONLY JSON with keys:
- summary: string (1 short paragraph)
- keyPoints: string[]
- questions: string[] (questions the other person asked)
- actionItems: string[]
- followUpEmail: string (a send-ready email, plain text)`;

  const user = `MODE: ${data.mode}
RESUME: ${clip(data.resume ?? "", 2000)}
CONTEXT: ${clip(data.job ?? "", 1500)}
TRANSCRIPT:
${transcript}`;

  const out = await chat(system, user, 1100);
  if (!out.ok) return out;
  const parsed = extractJson(out.text) as Partial<SessionNotes> | null;
  if (!parsed || typeof parsed.summary !== "string") {
    return {
      ok: true,
      notes: {
        summary: out.text.trim(),
        keyPoints: [],
        questions: [],
        actionItems: [],
        followUpEmail: "",
      },
    };
  }
  const list = (v: unknown) => (Array.isArray(v) ? v.map(String).slice(0, 8) : []);
  return {
    ok: true,
    notes: {
      summary: parsed.summary,
      keyPoints: list(parsed.keyPoints),
      questions: list(parsed.questions),
      actionItems: list(parsed.actionItems),
      followUpEmail: typeof parsed.followUpEmail === "string" ? parsed.followUpEmail : "",
    },
  };
}

export const generateAssist = createServerFn({ method: "POST" })
  .validator((input: AssistInput) => input)
  .handler(async ({ data }) => runAssist(data));

export const generateNotes = createServerFn({ method: "POST" })
  .validator((input: NotesInput) => input)
  .handler(async ({ data }) => runNotes(data));
