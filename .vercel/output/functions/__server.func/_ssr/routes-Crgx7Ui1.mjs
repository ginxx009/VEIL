import { i as __toESM } from "../_runtime.mjs";
import { u as require_react } from "../_libs/@floating-ui/react-dom+[...].mjs";
import { _ as Link } from "../_libs/@tanstack/react-router+[...].mjs";
import { n as require_jsx_runtime } from "../_libs/radix-ui__react-context+react.mjs";
import { d as Mic, g as EyeOff, i as StickyNote, y as ArrowRight } from "../_libs/lucide-react.mjs";
import { n as toast } from "../_libs/sonner.mjs";
import { i as LANDING_SAMPLE_ANSWER, l as VeilWordmark, t as Button } from "./logo-7oN5QId3.mjs";
import { i as OverlayPanel, r as MeetingStage, t as DualView } from "./overlay-panel-CBXOhmZx.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/routes-Crgx7Ui1.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
function LandingDemo() {
	const [stealthOn, setStealthOn] = (0, import_react.useState)(true);
	const [overlayVisible, setOverlayVisible] = (0, import_react.useState)(true);
	const [view, setView] = (0, import_react.useState)("split");
	const [prompt, setPrompt] = (0, import_react.useState)("");
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "flex min-h-0 flex-col gap-3",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "flex flex-wrap items-center gap-2",
				children: [
					"split",
					"you",
					"them"
				].map((v) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
					type: "button",
					onClick: () => setView(v),
					className: `h-9 rounded-full px-3 text-xs font-medium ${view === v ? "bg-secondary text-foreground" : "text-muted-foreground hover:text-foreground"}`,
					children: v === "split" ? "Split" : v === "you" ? "You" : "Them"
				}, v))
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "min-h-[22rem] md:min-h-[26rem]",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(DualView, {
					view,
					stealthOn,
					overlayVisible,
					you: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(MeetingStage, {
						mode: "interview",
						youName: "Alex Rivera",
						elapsed: 312
					}),
					them: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(MeetingStage, {
						mode: "interview",
						youName: "Alex Rivera",
						elapsed: 312
					}),
					overlay: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(OverlayPanel, {
						stealthOn,
						visible: true,
						status: "ready",
						result: LANDING_SAMPLE_ANSWER,
						error: null,
						prompt,
						onPrompt: setPrompt,
						onAssist: () => toast.message("Open the copilot to generate live answers."),
						onScreen: () => toast.message("Open the copilot to solve the shared screen."),
						onToggleStealth: () => setStealthOn((s) => !s),
						onHide: () => setOverlayVisible(false)
					})
				})
			}),
			!overlayVisible ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
				type: "button",
				className: "self-start text-xs text-muted-foreground underline-offset-4 hover:text-foreground hover:underline",
				onClick: () => setOverlayVisible(true),
				children: "Show overlay again"
			}) : null
		]
	});
}
function Home() {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "min-h-dvh bg-background text-foreground",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("header", {
			className: "mx-auto flex max-w-6xl items-center justify-between px-5 py-5",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(VeilWordmark, {}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("nav", {
				className: "flex items-center gap-2",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
					variant: "ghost",
					size: "sm",
					asChild: true,
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Link, {
						to: "/notes",
						children: "Notes"
					})
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
					size: "sm",
					asChild: true,
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Link, {
						to: "/session",
						children: ["Open copilot", /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ArrowRight, { className: "size-3.5" })]
					})
				})]
			})]
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("main", {
			className: "mx-auto max-w-6xl px-5 pb-20",
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
					className: "stagger-in max-w-3xl py-6 md:py-8",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "text-xs font-medium uppercase tracking-widest text-sage",
							children: "Private meeting copilot"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("h1", {
							className: "mt-3 font-display text-4xl leading-[1.05] tracking-tight text-foreground md:text-6xl",
							children: [
								"They get the call.",
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("br", {}),
								"You keep the overlay."
							]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "mt-4 max-w-xl text-sm text-muted-foreground md:text-base",
							children: "VEIL listens, drafts speakable answers, and sits on your display. Stealth excludes it from the shared frame — toggle their screen share below and watch it vanish."
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "mt-6 flex flex-wrap gap-3",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
								size: "lg",
								asChild: true,
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Link, {
									to: "/session",
									children: ["Enter a room", /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ArrowRight, { className: "size-4" })]
								})
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
								size: "lg",
								variant: "outline",
								asChild: true,
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("a", {
									href: "#rehearsal",
									children: "Rehearse a share"
								})
							})]
						})
					]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("section", {
					id: "rehearsal",
					className: "scroll-mt-8",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(LandingDemo, {})
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
					className: "mt-16 grid gap-3 md:grid-cols-3",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Fact, {
							icon: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(EyeOff, { className: "size-4" }),
							title: "Excluded from capture",
							body: "The overlay lives on a separate layer. Their screen share compositor never composites it — same idea as a native capture-exclusion flag, rehearsed here in split view."
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Fact, {
							icon: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Mic, { className: "size-4" }),
							title: "No bot in the call",
							body: "Nothing joins Zoom, Meet, or Teams. Mock questions work without a mic. Live assist uses your microphone locally, then Grok writes the answer."
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Fact, {
							icon: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(StickyNote, { className: "size-4" }),
							title: "Notes after, not during",
							body: "When the room ends, VEIL turns the transcript into a recap, action items, and a follow-up email you can send."
						})
					]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "mt-14 max-w-2xl text-xs leading-relaxed text-muted-foreground",
					children: "A browser cannot set OS-level capture exclusion (the API desktop apps use). Share a single meeting tab and keep VEIL in this window — or pop the overlay out — and it stays off the capture. Full-screen share of this tab will include whatever is painted here; use the split rehearsal to confirm stealth is on before you present."
				})
			]
		})]
	});
}
function Fact({ icon, title, body }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("article", {
		className: "rounded-xl bg-card p-5 shadow-[var(--shadow-border)]",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "flex size-9 items-center justify-center rounded-md bg-secondary text-sage",
				children: icon
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
				className: "mt-4 font-medium text-foreground",
				children: title
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "mt-2 text-sm leading-relaxed text-muted-foreground",
				children: body
			})
		]
	});
}
//#endregion
export { Home as component };
