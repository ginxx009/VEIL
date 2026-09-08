import { n as require_jsx_runtime } from "../_libs/radix-ui__react-context+react.mjs";
import { r as DEFAULT_PROFILE } from "./logo-7oN5QId3.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/storage-B0ii18W5.js
var import_jsx_runtime = require_jsx_runtime();
function NotesBody({ notes }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "mt-8 space-y-8",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
				className: "text-xs font-medium uppercase tracking-widest text-muted-foreground",
				children: "Summary"
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "mt-2 text-sm leading-relaxed text-foreground",
				children: notes.summary
			})] }),
			notes.keyPoints.length ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(List, {
				title: "Key points",
				items: notes.keyPoints
			}) : null,
			notes.questions.length ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(List, {
				title: "Questions asked",
				items: notes.questions
			}) : null,
			notes.actionItems.length ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(List, {
				title: "Action items",
				items: notes.actionItems
			}) : null,
			notes.followUpEmail ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
				className: "text-xs font-medium uppercase tracking-widest text-muted-foreground",
				children: "Follow-up"
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("pre", {
				className: "mt-2 whitespace-pre-wrap rounded-xl bg-card p-4 text-sm leading-relaxed text-foreground shadow-[var(--shadow-border)]",
				children: notes.followUpEmail
			})] }) : null
		]
	});
}
function List({ title, items }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
		className: "text-xs font-medium uppercase tracking-widest text-muted-foreground",
		children: title
	}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("ul", {
		className: "mt-2 space-y-2",
		children: items.map((item) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", {
			className: "flex gap-2 text-sm text-foreground",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { className: "mt-2 size-1 shrink-0 rounded-full bg-sage" }), item]
		}, item))
	})] });
}
var PROFILE_KEY = "veil-profile-v1";
var SESSIONS_KEY = "veil-sessions-v1";
function loadProfile() {
	if (typeof window === "undefined") return DEFAULT_PROFILE;
	try {
		const raw = localStorage.getItem(PROFILE_KEY);
		if (!raw) return DEFAULT_PROFILE;
		return {
			...DEFAULT_PROFILE,
			...JSON.parse(raw)
		};
	} catch {
		return DEFAULT_PROFILE;
	}
}
function saveProfile(profile) {
	if (typeof window === "undefined") return;
	localStorage.setItem(PROFILE_KEY, JSON.stringify(profile));
}
function loadSessions() {
	if (typeof window === "undefined") return [];
	try {
		const raw = localStorage.getItem(SESSIONS_KEY);
		if (!raw) return [];
		const parsed = JSON.parse(raw);
		return Array.isArray(parsed) ? parsed : [];
	} catch {
		return [];
	}
}
function saveSessions(sessions) {
	if (typeof window === "undefined") return;
	localStorage.setItem(SESSIONS_KEY, JSON.stringify(sessions.slice(0, 24)));
}
function upsertSession(session) {
	const all = loadSessions().filter((s) => s.id !== session.id);
	all.unshift(session);
	saveSessions(all);
}
//#endregion
export { upsertSession as a, saveProfile as i, loadProfile as n, loadSessions as r, NotesBody as t };
