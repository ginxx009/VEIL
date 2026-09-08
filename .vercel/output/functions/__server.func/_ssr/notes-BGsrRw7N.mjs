import { i as __toESM } from "../_runtime.mjs";
import { u as require_react } from "../_libs/@floating-ui/react-dom+[...].mjs";
import { _ as Link } from "../_libs/@tanstack/react-router+[...].mjs";
import { n as require_jsx_runtime } from "../_libs/radix-ui__react-context+react.mjs";
import { r as formatClock } from "./router-BwvKYRlp.mjs";
import { l as VeilWordmark, s as MODE_COPY, t as Button } from "./logo-7oN5QId3.mjs";
import { r as loadSessions, t as NotesBody } from "./storage-B0ii18W5.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/notes-BGsrRw7N.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
function NotesPage() {
	const [sessions, setSessions] = (0, import_react.useState)([]);
	const [openId, setOpenId] = (0, import_react.useState)("");
	(0, import_react.useEffect)(() => {
		const all = loadSessions();
		setSessions(all);
		setOpenId((id) => id || all[0]?.id || "");
	}, []);
	const current = sessions.find((s) => s.id === openId) ?? sessions[0];
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "min-h-dvh bg-background",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("header", {
			className: "mx-auto flex max-w-5xl items-center justify-between px-5 py-5",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Link, {
				to: "/",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(VeilWordmark, {})
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
				size: "sm",
				asChild: true,
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Link, {
					to: "/session",
					children: "New room"
				})
			})]
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("main", {
			className: "mx-auto grid max-w-5xl gap-8 px-5 pb-16 lg:grid-cols-[16rem_1fr]",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("aside", { children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
					className: "font-display text-3xl tracking-tight",
					children: "Notes"
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "mt-2 text-sm text-muted-foreground",
					children: "Stored on this device only."
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("ul", {
					className: "mt-6 space-y-1",
					children: sessions.length === 0 ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("li", {
						className: "text-sm text-muted-foreground",
						children: "No rooms yet."
					}) : sessions.map((s) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("li", { children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("button", {
						type: "button",
						onClick: () => setOpenId(s.id),
						className: `w-full rounded-md px-3 py-2 text-left text-sm ${current?.id === s.id ? "bg-secondary text-foreground" : "text-muted-foreground hover:text-foreground"}`,
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "block truncate",
							children: s.title
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
							className: "text-xs text-muted-foreground",
							children: [
								MODE_COPY[s.mode].label,
								" · ",
								formatClock(s.durationSec)
							]
						})]
					}) }, s.id))
				})
			] }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("section", { children: current?.notes ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_jsx_runtime.Fragment, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "text-xs uppercase tracking-widest text-muted-foreground",
				children: current.title
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(NotesBody, { notes: current.notes })] }) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "text-sm text-muted-foreground",
				children: "Finish a room to generate notes."
			}) })]
		})]
	});
}
//#endregion
export { NotesPage as component };
