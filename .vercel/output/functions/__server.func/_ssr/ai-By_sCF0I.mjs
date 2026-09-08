import { n as TSS_SERVER_FUNCTION, t as createServerFn } from "./ssr.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/ai-By_sCF0I.js
var createServerRpc = (serverFnMeta, splitImportFn) => {
	const url = "/_serverFn/" + serverFnMeta.id;
	return Object.assign(splitImportFn, {
		url,
		serverFnMeta,
		[TSS_SERVER_FUNCTION]: true
	});
};
var MAX_RESUME = 8e3;
var MAX_JOB = 4e3;
var MAX_TRANSCRIPT = 4500;
var MAX_QUESTION = 1200;
var MAX_SCREEN = 4e3;
function clip(value, max) {
	return value.length > max ? value.slice(-max) : value;
}
function extractJson(text) {
	const start = text.indexOf("{");
	const end = text.lastIndexOf("}");
	if (start < 0 || end < 0) return null;
	try {
		return JSON.parse(text.slice(start, end + 1));
	} catch {
		return null;
	}
}
async function chat(system, user, maxTokens) {
	const apiKey = process.env.XAI_API_KEY;
	if (!apiKey) return {
		ok: false,
		error: "AI is not available in this environment"
	};
	const res = await fetch("https://api.x.ai/v1/chat/completions", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			Authorization: `Bearer ${apiKey}`
		},
		body: JSON.stringify({
			model: "grok-4.5",
			temperature: .55,
			max_tokens: maxTokens,
			messages: [{
				role: "system",
				content: system
			}, {
				role: "user",
				content: user
			}]
		})
	});
	if (!res.ok) return {
		ok: false,
		error: `xAI API error ${res.status}`
	};
	return {
		ok: true,
		text: (await res.json()).choices?.[0]?.message?.content ?? ""
	};
}
function modeVoice(mode) {
	if (mode === "interview") return "The user is in a live job interview. Speak as them, first person, calm and specific. No filler, no 'great question'.";
	if (mode === "sales") return "The user is on a live sales or customer call. Give concise commercial answers they can say out loud. Be honest about tradeoffs.";
	return "The user is in an internal meeting. Give short status-style answers: owner, status, risk, next step.";
}
var generateAssist_createServerFn_handler = createServerRpc({
	id: "dd12aa1ad34f002e7de23905c12362de06596f34906b15014a03da01f6397e9b",
	name: "generateAssist",
	filename: "src/lib/ai.ts"
}, (opts) => generateAssist.__executeServer(opts));
var generateAssist = createServerFn({ method: "POST" }).validator((input) => input).handler(generateAssist_createServerFn_handler, async ({ data }) => {
	const resume = clip(data.resume ?? "", MAX_RESUME);
	const job = clip(data.job ?? "", MAX_JOB);
	const transcript = clip(data.transcript ?? "", MAX_TRANSCRIPT);
	const question = clip(data.question ?? "", MAX_QUESTION);
	const screenText = clip(data.screenText ?? "", MAX_SCREEN);
	const out = await chat(`You are VEIL, a private meeting copilot. Only the user can see your output.
${modeVoice(data.mode)}
Ground every answer in their resume and the job/context when those are provided. Do not invent employers or metrics that are not in the resume.
If this is a coding prompt, give a speakable approach first, then compact TypeScript.
Return ONLY JSON with keys:
- spoken: string (what they should say, 3–6 sentences, no markdown)
- points: string[] (2–4 short talking points)
- code: string (code only if relevant, else empty string)`, `KIND: ${data.kind === "screen" ? "Solve or explain what is on the shared screen." : "Answer the latest question."}
RESUME:
${resume || "(none)"}

JOB / CONTEXT:
${job || "(none)"}

SHARED SCREEN:
${screenText || "(none)"}

TRANSCRIPT (latest last):
${transcript || "(none)"}

FOCUS QUESTION:
${question || "(use the latest interviewer question in the transcript)"}`, data.kind === "screen" ? 900 : 700);
	if (!out.ok) return out;
	const parsed = extractJson(out.text);
	if (!parsed || typeof parsed.spoken !== "string") return {
		ok: true,
		result: {
			spoken: out.text.trim(),
			points: [],
			code: ""
		}
	};
	return {
		ok: true,
		result: {
			spoken: parsed.spoken,
			points: Array.isArray(parsed.points) ? parsed.points.map(String).slice(0, 6) : [],
			code: typeof parsed.code === "string" ? parsed.code : ""
		}
	};
});
var generateNotes_createServerFn_handler = createServerRpc({
	id: "2b2261cff88357137235722bf39631b75347a2a278a6df81933e4be9c436948b",
	name: "generateNotes",
	filename: "src/lib/ai.ts"
}, (opts) => generateNotes.__executeServer(opts));
var generateNotes = createServerFn({ method: "POST" }).validator((input) => input).handler(generateNotes_createServerFn_handler, async ({ data }) => {
	const transcript = clip(data.transcript ?? "", MAX_TRANSCRIPT);
	if (!transcript.trim()) return {
		ok: true,
		notes: {
			summary: "No transcript was captured in this session.",
			keyPoints: [],
			questions: [],
			actionItems: [],
			followUpEmail: ""
		}
	};
	const out = await chat(`You write private post-call notes for VEIL.
Return ONLY JSON with keys:
- summary: string (1 short paragraph)
- keyPoints: string[] 
- questions: string[] (questions the other person asked)
- actionItems: string[]
- followUpEmail: string (a send-ready email, plain text)`, `MODE: ${data.mode}
RESUME: ${clip(data.resume ?? "", 2e3)}
CONTEXT: ${clip(data.job ?? "", 1500)}
TRANSCRIPT:
${transcript}`, 1100);
	if (!out.ok) return out;
	const parsed = extractJson(out.text);
	if (!parsed || typeof parsed.summary !== "string") return {
		ok: true,
		notes: {
			summary: out.text.trim(),
			keyPoints: [],
			questions: [],
			actionItems: [],
			followUpEmail: ""
		}
	};
	const list = (v) => Array.isArray(v) ? v.map(String).slice(0, 8) : [];
	return {
		ok: true,
		notes: {
			summary: parsed.summary,
			keyPoints: list(parsed.keyPoints),
			questions: list(parsed.questions),
			actionItems: list(parsed.actionItems),
			followUpEmail: typeof parsed.followUpEmail === "string" ? parsed.followUpEmail : ""
		}
	};
});
//#endregion
export { generateAssist_createServerFn_handler, generateNotes_createServerFn_handler };
