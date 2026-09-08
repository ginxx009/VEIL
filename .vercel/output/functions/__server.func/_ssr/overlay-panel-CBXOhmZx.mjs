import { i as __toESM } from "../_runtime.mjs";
import { u as require_react } from "../_libs/@floating-ui/react-dom+[...].mjs";
import { n as require_jsx_runtime } from "../_libs/radix-ui__react-context+react.mjs";
import { _ as CornerDownLeft, d as Mic, f as MicOff, g as EyeOff, h as Eye, l as Monitor, m as Keyboard, n as Video, o as Phone, t as X, u as MonitorUp, v as Copy } from "../_libs/lucide-react.mjs";
import { t as cva } from "../_libs/class-variance-authority+clsx.mjs";
import { n as toast } from "../_libs/sonner.mjs";
import { i as modKeyLabel, n as cn, r as formatClock } from "./router-BwvKYRlp.mjs";
import { a as MEETING_DOC, c as SALES_SLIDE, n as CODE_PROBLEM, s as MODE_COPY, t as Button } from "./logo-7oN5QId3.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/overlay-panel-CBXOhmZx.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
function DualView({ view, stealthOn, overlayVisible, you, them, overlay }) {
	const showThemOverlay = overlayVisible && !stealthOn;
	const split = view === "split";
	const showYou = view !== "them";
	const showThem = view !== "you";
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: cn("grid min-h-0 flex-1 gap-3", split ? "lg:grid-cols-2" : "grid-cols-1"),
		children: [showYou ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(ScreenFrame, {
			kicker: "Your display",
			caption: overlayVisible ? "VEIL is on this machine only" : "Overlay hidden",
			tone: "you",
			children: [you, overlayVisible ? overlay : null]
		}) : null, showThem ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(ScreenFrame, {
			kicker: "Their screen share",
			caption: stealthOn ? "Capture compositor skipped the overlay" : overlayVisible ? "Stealth off — they can see VEIL" : "Overlay hidden",
			tone: stealthOn || !overlayVisible ? "clean" : "exposed",
			children: [them, showThemOverlay ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "pointer-events-none opacity-90",
				children: overlay
			}) : null]
		}) : null]
	});
}
function ScreenFrame({ kicker, caption, tone, children }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
		className: "flex min-h-0 flex-col",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "mb-2 flex items-end justify-between gap-3 px-1",
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "text-[0.65rem] font-medium uppercase tracking-[0.2em] text-muted-foreground",
				children: kicker
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: cn("text-xs", tone === "exposed" ? "text-warn" : tone === "clean" ? "text-sage" : "text-muted-foreground"),
				children: caption
			})] })
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "relative min-h-64 flex-1 overflow-hidden rounded-xl bg-card shadow-[var(--shadow-border)]",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "pointer-events-none absolute inset-x-0 top-0 z-10 flex justify-center",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { className: "h-4 w-24 rounded-b-md bg-secondary" })
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "absolute inset-0 pt-3",
				children
			})]
		})]
	});
}
function Tile({ initials, name, you, compact }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: cn("relative overflow-hidden rounded-md bg-secondary", compact ? "h-16 w-24" : "aspect-video min-h-24"),
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "flex h-full items-center justify-center",
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
				className: cn("flex items-center justify-center rounded-full bg-accent font-medium text-foreground", compact ? "size-8 text-xs" : "size-12 text-sm"),
				children: initials
			})
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "absolute inset-x-0 bottom-0 flex items-center justify-between px-2 py-1.5",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
				className: "text-xs text-foreground/90",
				children: name
			}), you ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Mic, { className: "size-3 text-sage" }) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(MicOff, { className: "size-3 text-muted-foreground" })]
		})]
	});
}
function SharedScreen({ mode }) {
	if (mode === "sales") return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "flex h-full flex-col justify-between rounded-md bg-background p-5 shadow-[var(--shadow-border)]",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "text-xs uppercase tracking-widest text-muted-foreground",
				children: SALES_SLIDE.kicker
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h3", {
				className: "font-display text-2xl leading-snug text-foreground md:text-3xl",
				children: SALES_SLIDE.title
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("ul", {
				className: "space-y-2 text-sm text-muted-foreground",
				children: SALES_SLIDE.bullets.map((b) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", {
					className: "flex gap-2",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { className: "mt-2 size-1 shrink-0 rounded-full bg-sage" }), b]
				}, b))
			})
		]
	});
	if (mode === "meeting") return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "h-full rounded-md bg-background p-5 shadow-[var(--shadow-border)]",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "text-xs uppercase tracking-widest text-muted-foreground",
				children: "Shared doc"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h3", {
				className: "mt-2 font-display text-xl text-foreground",
				children: MEETING_DOC.title
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("ul", {
				className: "mt-4 space-y-2.5 text-sm text-muted-foreground",
				children: MEETING_DOC.lines.map((line) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("li", {
					className: "rounded-sm bg-secondary px-3 py-2 text-foreground/90",
					children: line
				}, line))
			})
		]
	});
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "flex h-full flex-col overflow-hidden rounded-md bg-background shadow-[var(--shadow-border)]",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "flex items-center justify-between border-b border-border px-3 py-2",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
				className: "text-xs text-muted-foreground",
				children: CODE_PROBLEM.title
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
				className: "font-mono text-xs text-muted-foreground",
				children: "pad · typescript"
			})]
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "min-h-0 flex-1 overflow-auto p-3 font-mono text-xs leading-relaxed",
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "text-muted-foreground",
					children: CODE_PROBLEM.prompt
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("pre", {
					className: "mt-3 whitespace-pre-wrap text-foreground/90",
					children: CODE_PROBLEM.signature
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "mt-3 text-sage",
					children: CODE_PROBLEM.tests
				})
			]
		})]
	});
}
function screenContentText(mode) {
	if (mode === "sales") return `${SALES_SLIDE.kicker}\n${SALES_SLIDE.title}\n${SALES_SLIDE.bullets.join("\n")}`;
	if (mode === "meeting") return `${MEETING_DOC.title}\n${MEETING_DOC.lines.join("\n")}`;
	return `${CODE_PROBLEM.title}\n${CODE_PROBLEM.prompt}\n${CODE_PROBLEM.signature}\n${CODE_PROBLEM.tests}`;
}
function MeetingStage({ mode, youName, elapsed, className }) {
	const copy = MODE_COPY[mode];
	const youInitials = youName.split(" ").map((p) => p[0]).join("").slice(0, 2).toUpperCase();
	const themInitials = copy.interviewer.split(" ").map((p) => p[0]).join("").slice(0, 2).toUpperCase();
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: cn("flex h-full min-h-0 flex-col bg-background text-foreground", className),
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex items-center justify-between px-3 py-2 text-xs text-muted-foreground",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
					className: "truncate",
					children: copy.meeting
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
					className: "tabular-nums",
					children: formatClock(elapsed)
				})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "grid min-h-0 flex-1 grid-cols-1 gap-2 px-2 sm:grid-cols-[1fr_auto]",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SharedScreen, { mode }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "flex w-auto flex-row gap-2 sm:w-28 sm:flex-col",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Tile, {
						initials: themInitials,
						name: copy.interviewer,
						compact: true
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Tile, {
						initials: youInitials || "YO",
						name: youName.split(" ")[0] || "You",
						you: true,
						compact: true
					})]
				})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex items-center justify-center gap-2 py-3",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
						className: "flex size-9 items-center justify-center rounded-full bg-secondary text-foreground",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Mic, { className: "size-4" })
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
						className: "flex size-9 items-center justify-center rounded-full bg-secondary text-foreground",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Video, { className: "size-4" })
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
						className: "flex size-9 items-center justify-center rounded-full bg-sage-dim text-sage",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(MonitorUp, { className: "size-4" })
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
						className: "flex size-9 items-center justify-center rounded-full bg-destructive text-destructive-foreground",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Phone, { className: "size-4 rotate-hang" })
					})
				]
			})
		]
	});
}
var badgeVariants = cva("inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium tracking-wide", {
	variants: { variant: {
		default: "bg-secondary text-muted-foreground",
		sage: "bg-sage-dim text-sage",
		outline: "shadow-[var(--shadow-border)] text-muted-foreground",
		warn: "bg-warn/15 text-warn"
	} },
	defaultVariants: { variant: "default" }
});
function Badge({ className, variant, ...props }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
		className: cn(badgeVariants({ variant }), className),
		...props
	});
}
var Input = import_react.forwardRef(({ className, type, ...props }, ref) => {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
		type,
		className: cn("flex h-11 w-full rounded-md bg-secondary px-3 text-sm text-foreground shadow-[var(--shadow-border)] outline-none transition-[box-shadow] duration-150 placeholder:text-muted-foreground focus-visible:shadow-[var(--shadow-border-hover)] focus-visible:ring-2 focus-visible:ring-ring/40 disabled:opacity-50", className),
		ref,
		...props
	});
});
Input.displayName = "Input";
function OverlayPanel({ stealthOn, visible, status, result, error, prompt, onPrompt, onAssist, onScreen, onToggleStealth, onHide, compact }) {
	if (!visible) return null;
	const mod = modKeyLabel();
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: cn("pointer-events-auto absolute inset-x-3 top-3 z-20 flex max-h-[calc(100%-0.75rem)] flex-col gap-2 overflow-y-auto", compact ? "max-w-full" : "mx-auto max-w-lg"),
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex items-center gap-1 rounded-full bg-card/92 px-1.5 py-1 shadow-[var(--shadow-border),var(--shadow-float)] backdrop-blur-md",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Badge, {
						variant: stealthOn ? "sage" : "warn",
						className: "ml-1 shrink-0",
						children: stealthOn ? "Stealth on" : "Visible"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
						type: "button",
						onClick: onAssist,
						className: "rounded-full px-3 py-1.5 text-xs font-medium text-foreground hover:bg-accent",
						children: "Assist"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
						type: "button",
						onClick: onScreen,
						className: "hidden rounded-full px-3 py-1.5 text-xs font-medium text-muted-foreground hover:bg-accent hover:text-foreground sm:inline",
						children: "Screen"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "ml-auto flex items-center",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(IconBtn, {
							label: stealthOn ? "Show on share" : "Hide from share",
							onClick: onToggleStealth,
							children: stealthOn ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(EyeOff, { className: "size-3.5" }) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Eye, { className: "size-3.5" })
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(IconBtn, {
							label: "Hide overlay",
							onClick: onHide,
							children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(X, { className: "size-3.5" })
						})]
					})
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("form", {
				className: "flex gap-2 rounded-xl bg-card/92 p-2 shadow-[var(--shadow-border)] backdrop-blur-md",
				onSubmit: (e) => {
					e.preventDefault();
					onAssist();
				},
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Input, {
					value: prompt,
					onChange: (e) => onPrompt(e.target.value),
					placeholder: `Ask, or ${mod}+Enter for Assist`,
					className: "h-10 rounded-lg bg-transparent shadow-none focus-visible:ring-0"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
					type: "submit",
					size: "sm",
					className: "h-10 rounded-lg px-3",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CornerDownLeft, { className: "size-3.5" }), "Go"]
				})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "rounded-xl bg-card/92 p-3.5 shadow-[var(--shadow-border)] backdrop-blur-md",
				children: status === "thinking" ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "veil-shimmer bg-clip-text text-sm text-muted-foreground",
					children: "Writing a speakable answer…"
				}) : status === "error" ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "text-sm text-destructive",
					children: error ?? "Could not generate an answer."
				}) : result ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "space-y-3",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "flex items-center justify-between gap-2",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "text-xs font-medium uppercase tracking-widest text-muted-foreground",
								children: "Answer"
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
								type: "button",
								variant: "ghost",
								size: "icon-sm",
								className: "size-8 shrink-0",
								onClick: () => {
									navigator.clipboard.writeText([
										result.spoken,
										result.points.map((p) => `• ${p}`).join("\n"),
										result.code
									].filter(Boolean).join("\n\n"));
									toast.success("Copied");
								},
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Copy, { className: "size-3.5" })
							})]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "text-sm leading-relaxed text-foreground",
							children: result.spoken
						}),
						result.points.length > 0 ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("ul", {
							className: "space-y-1",
							children: result.points.map((p) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", {
								className: "flex gap-2 text-xs text-muted-foreground",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { className: "mt-1 size-1 shrink-0 rounded-full bg-sage" }), p]
							}, p))
						}) : null,
						result.code ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("pre", {
							className: "overflow-x-auto rounded-md bg-background p-2.5 font-mono text-xs leading-relaxed text-sage",
							children: result.code
						}) : null
					]
				}) : /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "space-y-2 text-xs text-muted-foreground",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
						className: "flex items-center gap-2",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Keyboard, { className: "size-3.5" }),
							mod,
							"+Enter assist · ",
							mod,
							"+Shift+E stealth · ",
							mod,
							"+Shift+H hide"
						]
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
						className: "flex items-center gap-2",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Monitor, { className: "size-3.5" }), stealthOn ? "Excluded from the shared frame. Their share stays clean." : "Stealth is off — the overlay will appear on their screen share."]
					})]
				})
			})
		]
	});
}
function IconBtn({ children, label, onClick }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
		type: "button",
		"aria-label": label,
		title: label,
		onClick,
		className: "flex size-9 items-center justify-center rounded-full text-muted-foreground hover:bg-accent hover:text-foreground",
		children
	});
}
//#endregion
export { screenContentText as a, OverlayPanel as i, Input as n, MeetingStage as r, DualView as t };
