import { i as __toESM } from "../_runtime.mjs";
import { u as require_react } from "../_libs/@floating-ui/react-dom+[...].mjs";
import { _ as Link, v as useNavigate } from "../_libs/@tanstack/react-router+[...].mjs";
import { n as require_jsx_runtime } from "../_libs/radix-ui__react-context+react.mjs";
import { n as TSS_SERVER_FUNCTION, r as getServerFnById, t as createServerFn } from "./ssr.mjs";
import { a as Play, c as PanelLeft, d as Mic, f as MicOff, g as EyeOff, h as Eye, l as Monitor, p as LayoutGrid, s as PhoneOff } from "../_libs/lucide-react.mjs";
import { n as toast } from "../_libs/sonner.mjs";
import { a as sleep, n as cn } from "./router-BwvKYRlp.mjs";
import { l as VeilWordmark, o as MOCK_QUESTIONS, s as MODE_COPY, t as Button } from "./logo-7oN5QId3.mjs";
import { a as upsertSession, i as saveProfile, n as loadProfile, t as NotesBody } from "./storage-B0ii18W5.mjs";
import { a as screenContentText, i as OverlayPanel, n as Input, r as MeetingStage, t as DualView } from "./overlay-panel-CBXOhmZx.mjs";
import { i as Viewport, n as ScrollAreaScrollbar, r as ScrollAreaThumb, t as Root } from "../_libs/radix-ui__react-scroll-area.mjs";
import { t as Root$1 } from "../_libs/radix-ui__react-label.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/session-B0s7f2rX.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
var ScrollArea = import_react.forwardRef(({ className, children, ...props }, ref) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Root, {
	ref,
	className: cn("relative overflow-hidden", className),
	...props,
	children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Viewport, {
		className: "h-full w-full rounded-[inherit]",
		children
	}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ScrollAreaScrollbar, {
		orientation: "vertical",
		className: "flex w-2 touch-none select-none p-0.5",
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ScrollAreaThumb, { className: "relative flex-1 rounded-full bg-border" })
	})]
}));
ScrollArea.displayName = Root.displayName;
function TranscriptRail({ lines, themName, youName }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ScrollArea, {
		className: "h-full",
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "space-y-3 p-1",
			children: lines.length === 0 ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "text-sm text-muted-foreground",
				children: "Transcript is empty. Play a mock question or turn on the mic — VEIL never joins the call as a bot."
			}) : lines.map((line) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "space-y-1",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "text-[0.65rem] font-medium uppercase tracking-[0.16em] text-muted-foreground",
					children: line.speaker === "you" ? youName : line.speaker === "them" ? themName : "Room"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: cn("text-sm leading-relaxed", line.speaker === "them" ? "text-foreground" : "text-muted-foreground"),
					children: line.text
				})]
			}, line.id))
		})
	});
}
var Label = import_react.forwardRef(({ className, ...props }, ref) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Root$1, {
	ref,
	className: cn("text-sm font-medium text-muted-foreground", className),
	...props
}));
Label.displayName = Root$1.displayName;
var Textarea = import_react.forwardRef(({ className, ...props }, ref) => {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("textarea", {
		className: cn("flex min-h-28 w-full rounded-md bg-secondary px-3 py-2.5 text-sm text-foreground shadow-[var(--shadow-border)] outline-none transition-[box-shadow] duration-150 placeholder:text-muted-foreground focus-visible:shadow-[var(--shadow-border-hover)] focus-visible:ring-2 focus-visible:ring-ring/40 disabled:opacity-50", className),
		ref,
		...props
	});
});
Textarea.displayName = "Textarea";
var createSsrRpc = (functionId) => {
	const url = "/_serverFn/" + functionId;
	const serverFnMeta = { id: functionId };
	const fn = async (...args) => {
		return (await getServerFnById(functionId, { origin: "server" }))(...args);
	};
	return Object.assign(fn, {
		url,
		serverFnMeta,
		[TSS_SERVER_FUNCTION]: true
	});
};
var generateAssist = createServerFn({ method: "POST" }).validator((input) => input).handler(createSsrRpc("dd12aa1ad34f002e7de23905c12362de06596f34906b15014a03da01f6397e9b"));
var generateNotes = createServerFn({ method: "POST" }).validator((input) => input).handler(createSsrRpc("2b2261cff88357137235722bf39631b75347a2a278a6df81933e4be9c436948b"));
var MAX_ASSISTS = 12;
function SessionPage() {
	const navigate = useNavigate();
	const [profile, setProfile] = (0, import_react.useState)(loadProfile);
	const [phase, setPhase] = (0, import_react.useState)("setup");
	const [stealthOn, setStealthOn] = (0, import_react.useState)(true);
	const [overlayVisible, setOverlayVisible] = (0, import_react.useState)(true);
	const [view, setView] = (0, import_react.useState)("split");
	const [transcript, setTranscript] = (0, import_react.useState)([]);
	const [prompt, setPrompt] = (0, import_react.useState)("");
	const [status, setStatus] = (0, import_react.useState)("idle");
	const [result, setResult] = (0, import_react.useState)(null);
	const [error, setError] = (0, import_react.useState)(null);
	const [elapsed, setElapsed] = (0, import_react.useState)(0);
	const [listening, setListening] = (0, import_react.useState)(false);
	const [mockIndex, setMockIndex] = (0, import_react.useState)(0);
	const [assistCount, setAssistCount] = (0, import_react.useState)(0);
	const [notes, setNotes] = (0, import_react.useState)(null);
	const [notesBusy, setNotesBusy] = (0, import_react.useState)(false);
	const [sessionId, setSessionId] = (0, import_react.useState)("");
	const [railOpen, setRailOpen] = (0, import_react.useState)(true);
	const recognitionRef = (0, import_react.useRef)(null);
	const startedAtRef = (0, import_react.useRef)(0);
	(0, import_react.useEffect)(() => {
		setProfile(loadProfile());
	}, []);
	(0, import_react.useEffect)(() => {
		if (phase !== "live") return;
		const t = window.setInterval(() => setElapsed((e) => e + 1), 1e3);
		return () => window.clearInterval(t);
	}, [phase]);
	const addLine = (0, import_react.useCallback)((speaker, text) => {
		const line = {
			id: `${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
			speaker,
			text,
			at: Date.now()
		};
		setTranscript((prev) => [...prev, line]);
		return line;
	}, []);
	const runAssist = (0, import_react.useCallback)(async (kind, questionOverride, extraTranscript) => {
		if (status === "thinking") return;
		if (assistCount >= MAX_ASSISTS) {
			toast.error("Assist limit reached for this room");
			return;
		}
		const question = (questionOverride ?? prompt).trim();
		setStatus("thinking");
		setError(null);
		setOverlayVisible(true);
		const packed = [...transcript.map((l) => `${l.speaker}: ${l.text}`), extraTranscript].filter(Boolean).join("\n");
		try {
			const res = await generateAssist({ data: {
				mode: profile.mode,
				kind,
				resume: profile.resume,
				job: profile.jobDescription,
				transcript: packed,
				question,
				screenText: screenContentText(profile.mode)
			} });
			if (!res.ok) {
				setStatus("error");
				setError(res.error);
				return;
			}
			setAssistCount((c) => c + 1);
			setStatus("ready");
			const words = res.result.spoken.split(" ");
			let acc = "";
			for (const w of words) {
				acc += (acc ? " " : "") + w;
				setResult({
					spoken: acc,
					points: [],
					code: ""
				});
				await sleep(18);
			}
			setResult(res.result);
			setPrompt("");
		} catch {
			setStatus("error");
			setError("Could not reach the model.");
		}
	}, [
		assistCount,
		profile,
		prompt,
		status,
		transcript
	]);
	const playMock = (0, import_react.useCallback)(async () => {
		const list = MOCK_QUESTIONS[profile.mode];
		const q = list[mockIndex % list.length];
		setMockIndex((i) => i + 1);
		addLine("them", q);
		await sleep(200);
		await runAssist("answer", q, `them: ${q}`);
	}, [
		addLine,
		mockIndex,
		profile.mode,
		runAssist
	]);
	const toggleMic = (0, import_react.useCallback)(() => {
		const win = window;
		const SR = win.SpeechRecognition || win.webkitSpeechRecognition;
		if (!SR) {
			toast.error("This browser has no speech recognition. Use mock questions.");
			return;
		}
		if (listening) {
			recognitionRef.current?.stop();
			setListening(false);
			return;
		}
		const rec = new SR();
		rec.continuous = true;
		rec.interimResults = false;
		rec.lang = "en-US";
		rec.onresult = (ev) => {
			const text = Array.from(ev.results).slice(ev.resultIndex).map((r) => r[0]?.transcript ?? "").join(" ").trim();
			if (text) addLine("room", text);
		};
		rec.onerror = () => {
			setListening(false);
			toast.error("Microphone unavailable. Use mock questions.");
		};
		rec.onend = () => setListening(false);
		recognitionRef.current = rec;
		try {
			rec.start();
			setListening(true);
		} catch {
			toast.error("Could not start the microphone.");
		}
	}, [addLine, listening]);
	(0, import_react.useEffect)(() => {
		const onKey = (e) => {
			if (phase !== "live") return;
			const mod = e.metaKey || e.ctrlKey;
			if (mod && e.key === "Enter") {
				e.preventDefault();
				runAssist("answer");
			}
			if (mod && e.shiftKey && e.key.toLowerCase() === "e") {
				e.preventDefault();
				setStealthOn((s) => !s);
			}
			if (mod && e.shiftKey && e.key.toLowerCase() === "h") {
				e.preventDefault();
				setOverlayVisible((v) => !v);
			}
			if (mod && e.shiftKey && e.key.toLowerCase() === "s") {
				e.preventDefault();
				runAssist("screen");
			}
		};
		window.addEventListener("keydown", onKey);
		return () => window.removeEventListener("keydown", onKey);
	}, [phase, runAssist]);
	(0, import_react.useEffect)(() => {
		return () => recognitionRef.current?.stop();
	}, []);
	const enterRoom = () => {
		saveProfile(profile);
		setSessionId(`veil-${Date.now()}`);
		startedAtRef.current = Date.now();
		setElapsed(0);
		setTranscript([]);
		setResult(null);
		setStatus("idle");
		setAssistCount(0);
		setMockIndex(0);
		setNotes(null);
		setStealthOn(true);
		setOverlayVisible(true);
		setPhase("live");
		if (window.matchMedia("(max-width: 1023px)").matches) {
			setView("you");
			setRailOpen(false);
		}
	};
	const endRoom = async () => {
		recognitionRef.current?.stop();
		setListening(false);
		setNotesBusy(true);
		setPhase("notes");
		const packed = transcript.map((l) => `${l.speaker}: ${l.text}`).join("\n");
		let nextNotes = null;
		if (packed.trim()) {
			const res = await generateNotes({ data: {
				mode: profile.mode,
				resume: profile.resume,
				job: profile.jobDescription,
				transcript: packed
			} });
			if (res.ok) nextNotes = res.notes;
			else toast.error(res.error);
		} else nextNotes = {
			summary: "No transcript was captured.",
			keyPoints: [],
			questions: [],
			actionItems: [],
			followUpEmail: ""
		};
		setNotes(nextNotes);
		setNotesBusy(false);
		upsertSession({
			id: sessionId || `veil-${Date.now()}`,
			title: MODE_COPY[profile.mode].meeting,
			mode: profile.mode,
			startedAt: startedAtRef.current || Date.now(),
			durationSec: elapsed,
			transcript,
			notes: nextNotes
		});
	};
	const copy = MODE_COPY[profile.mode];
	const overlay = /* @__PURE__ */ (0, import_jsx_runtime.jsx)(OverlayPanel, {
		stealthOn,
		visible: overlayVisible,
		status,
		result,
		error,
		prompt,
		onPrompt: setPrompt,
		onAssist: () => void runAssist("answer"),
		onScreen: () => void runAssist("screen"),
		onToggleStealth: () => setStealthOn((s) => !s),
		onHide: () => setOverlayVisible(false)
	});
	if (phase === "setup") return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "min-h-dvh bg-background",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("header", {
			className: "mx-auto flex max-w-3xl items-center justify-between px-5 py-5",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Link, {
				to: "/",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(VeilWordmark, {})
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
				variant: "ghost",
				size: "sm",
				asChild: true,
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Link, {
					to: "/notes",
					children: "Past notes"
				})
			})]
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("main", {
			className: "mx-auto max-w-3xl px-5 pb-16",
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
					className: "font-display text-4xl tracking-tight",
					children: "Enter a room"
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "mt-2 max-w-lg text-sm text-muted-foreground",
					children: "Context stays on this device. Grok only sees what you send for the next answer."
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "mt-8 grid gap-2 sm:grid-cols-3",
					children: [
						"interview",
						"sales",
						"meeting"
					].map((m) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("button", {
						type: "button",
						onClick: () => setProfile((p) => ({
							...p,
							mode: m
						})),
						className: cn("rounded-xl p-4 text-left shadow-[var(--shadow-border)] transition-[box-shadow,background-color] duration-150", profile.mode === m ? "bg-secondary" : "bg-card hover:shadow-[var(--shadow-border-hover)]"),
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "font-medium",
							children: MODE_COPY[m].label
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "mt-1 text-xs text-muted-foreground",
							children: MODE_COPY[m].hint
						})]
					}, m))
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "mt-8 grid gap-4 sm:grid-cols-2",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Field, {
						label: "Your name",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Input, {
							value: profile.displayName,
							onChange: (e) => setProfile((p) => ({
								...p,
								displayName: e.target.value
							}))
						})
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Field, {
						label: "Role",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Input, {
							value: profile.role,
							onChange: (e) => setProfile((p) => ({
								...p,
								role: e.target.value
							}))
						})
					})]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "mt-4",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Field, {
						label: "Resume / playbook",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Textarea, {
							value: profile.resume,
							onChange: (e) => setProfile((p) => ({
								...p,
								resume: e.target.value
							})),
							className: "min-h-36"
						})
					})
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "mt-4",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Field, {
						label: "Job or meeting context",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Textarea, {
							value: profile.jobDescription,
							onChange: (e) => setProfile((p) => ({
								...p,
								jobDescription: e.target.value
							}))
						})
					})
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "mt-8 flex flex-wrap gap-3",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
						size: "lg",
						onClick: enterRoom,
						children: ["Enter ", copy.label.toLowerCase()]
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
						size: "lg",
						variant: "outline",
						asChild: true,
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Link, {
							to: "/",
							children: "Back"
						})
					})]
				})
			]
		})]
	});
	if (phase === "notes") return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "min-h-dvh bg-background",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("header", {
			className: "mx-auto flex max-w-3xl items-center justify-between px-5 py-5",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Link, {
				to: "/",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(VeilWordmark, {})
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
				size: "sm",
				variant: "outline",
				onClick: () => setPhase("setup"),
				children: "New room"
			})]
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("main", {
			className: "mx-auto max-w-3xl px-5 pb-16",
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "text-xs uppercase tracking-widest text-muted-foreground",
					children: copy.meeting
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
					className: "mt-2 font-display text-4xl tracking-tight",
					children: "Notes"
				}),
				notesBusy ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "veil-shimmer mt-8 bg-clip-text text-muted-foreground",
					children: "Writing the recap…"
				}) : notes ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(NotesBody, { notes }) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "mt-8 text-sm text-muted-foreground",
					children: "No notes for this room."
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "mt-10 flex gap-3",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
						onClick: () => navigate({ to: "/notes" }),
						children: "All notes"
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
						variant: "outline",
						onClick: () => setPhase("setup"),
						children: "Another room"
					})]
				})
			]
		})]
	});
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "flex h-dvh flex-col bg-background",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("header", {
			className: "flex shrink-0 items-center gap-2 border-b border-border px-3 py-2 md:px-4",
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Link, {
					to: "/",
					className: "hidden sm:block",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(VeilWordmark, {})
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
					className: "truncate text-xs text-muted-foreground sm:ml-3",
					children: copy.meeting
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "ml-auto flex items-center gap-1",
					children: [
						[
							"split",
							"you",
							"them"
						].map((v) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
							type: "button",
							onClick: () => setView(v),
							className: cn("hidden h-9 rounded-full px-3 text-xs font-medium md:inline", view === v ? "bg-secondary text-foreground" : "text-muted-foreground hover:text-foreground"),
							children: v === "split" ? "Split" : v === "you" ? "You" : "Them"
						}, v)),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
							variant: stealthOn ? "sage" : "outline",
							size: "sm",
							onClick: () => setStealthOn((s) => !s),
							className: "rounded-full",
							children: [stealthOn ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(EyeOff, { className: "size-3.5" }) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Eye, { className: "size-3.5" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
								className: "hidden sm:inline",
								children: stealthOn ? "Stealth" : "Visible"
							})]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
							variant: "destructive",
							size: "sm",
							className: "rounded-full",
							onClick: () => void endRoom(),
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(PhoneOff, { className: "size-3.5" }), "End"]
						})
					]
				})
			]
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "flex min-h-0 flex-1",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex min-w-0 flex-1 flex-col p-3 md:p-4",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(DualView, {
						view,
						stealthOn,
						overlayVisible,
						you: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(MeetingStage, {
							mode: profile.mode,
							youName: profile.displayName,
							elapsed
						}),
						them: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(MeetingStage, {
							mode: profile.mode,
							youName: profile.displayName,
							elapsed
						}),
						overlay
					}),
					!overlayVisible ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
						type: "button",
						className: "mt-2 self-start text-xs text-muted-foreground hover:text-foreground",
						onClick: () => setOverlayVisible(true),
						children: "Show overlay"
					}) : null,
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "mt-3 flex flex-wrap items-center gap-2",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
								size: "sm",
								onClick: () => void playMock(),
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Play, { className: "size-3.5" }), "Next question"]
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
								size: "sm",
								variant: listening ? "sage" : "outline",
								onClick: toggleMic,
								children: [listening ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Mic, { className: "size-3.5" }) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(MicOff, { className: "size-3.5" }), listening ? "Listening" : "Mic"]
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
								size: "sm",
								variant: "outline",
								onClick: () => void runAssist("screen"),
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Monitor, { className: "size-3.5" }), "Solve screen"]
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
								size: "icon-sm",
								variant: "ghost",
								className: "ml-auto md:hidden",
								onClick: () => setView((v) => v === "you" ? "them" : "you"),
								"aria-label": "Swap view",
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(LayoutGrid, { className: "size-4" })
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
								size: "icon-sm",
								variant: "ghost",
								className: "lg:hidden",
								onClick: () => setRailOpen((o) => !o),
								"aria-label": "Transcript",
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(PanelLeft, { className: "size-4" })
							})
						]
					})
				]
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("aside", {
				className: cn("w-72 shrink-0 flex-col border-l border-border p-4", railOpen ? "flex" : "hidden lg:flex"),
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "mb-3 text-xs font-medium uppercase tracking-widest text-muted-foreground",
					children: "Transcript"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "min-h-0 flex-1",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(TranscriptRail, {
						lines: transcript,
						themName: copy.interviewer,
						youName: profile.displayName
					})
				})]
			})]
		})]
	});
}
function Field({ label, children }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
		className: "block space-y-2",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Label, { children: label }), children]
	});
}
//#endregion
export { SessionPage as component };
