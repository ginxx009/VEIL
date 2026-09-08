import { i as __toESM } from "../_runtime.mjs";
import { u as require_react } from "../_libs/@floating-ui/react-dom+[...].mjs";
import { n as require_jsx_runtime } from "../_libs/radix-ui__react-context+react.mjs";
import { i as Slot } from "../_libs/@radix-ui/react-dismissable-layer+[...].mjs";
import { t as cva } from "../_libs/class-variance-authority+clsx.mjs";
import { n as cn } from "./router-BwvKYRlp.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/logo-7oN5QId3.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
var DEFAULT_PROFILE = {
	displayName: "Alex Rivera",
	role: "Staff Engineer",
	company: "Northwind",
	resume: `Alex Rivera — Staff Software Engineer
8 years shipping product and platform systems.
TypeScript, React, Node, Postgres, AWS.
Led a billing rewrite that cut failed payments 22%.
Comfortable with system design, on-call, and mentoring.`,
	jobDescription: `Staff Engineer, Platform
Own the payments and identity services. Mentorship is part of the job.
Interviews include a coding round and a system-design conversation.`,
	mode: "interview"
};
var MODE_COPY = {
	interview: {
		label: "Interview",
		meeting: "Staff Engineer · first round",
		interviewer: "Jordan Hale",
		hint: "Coding + behavioral. Answers stay first-person and speakable."
	},
	sales: {
		label: "Sales call",
		meeting: "Product walkthrough · Northwind",
		interviewer: "Sam Okonkwo",
		hint: "Pricing, timeline, and competitor objections."
	},
	meeting: {
		label: "Internal meeting",
		meeting: "Q3 launch standup",
		interviewer: "Priya Shah",
		hint: "Status, owners, blockers — keep answers short."
	}
};
var MOCK_QUESTIONS = {
	interview: [
		"Tell me about yourself — the short version.",
		"Walk me through a production incident you owned end to end.",
		"How would you design a URL shortener that handles 10 million writes a day?",
		"Looking at the Two Sum prompt on the shared screen — how would you approach it?",
		"What's the time and space complexity of your solution, and where does it break?"
	],
	sales: [
		"Can you walk us through pricing for a 40-person team?",
		"How do you compare to the tool we already pay for?",
		"What's the implementation timeline if we started next month?",
		"Who actually owns this after the contract is signed?",
		"What happens if we need to be off the platform in 90 days?"
	],
	meeting: [
		"What's the status on the Q3 launch?",
		"Who owns the identity migration, and is it still this sprint?",
		"Any blockers we should escalate today?",
		"What slipped since Monday, and why?",
		"What does done look like before Friday?"
	]
};
var CODE_PROBLEM = {
	title: "1. Two Sum",
	prompt: "Given an array of integers nums and an integer target, return the indices of the two numbers that add up to target. You may assume each input has exactly one solution, and you may not use the same element twice.",
	signature: `function twoSum(nums: number[], target: number): number[] {
  // your code
}`,
	tests: "nums = [2, 7, 11, 15], target = 9  →  [0, 1]"
};
var SALES_SLIDE = {
	kicker: "Northwind Platform",
	title: "Pricing that scales with seats, not surprises",
	bullets: [
		"Team — $24 / seat / month, up to 50",
		"Scale — $18 / seat, SSO + audit log",
		"Pilot — 21 days, production data, no card"
	]
};
var MEETING_DOC = {
	title: "Q3 launch — working notes",
	lines: [
		"Identity migration: Priya · in progress · risk: token TTL",
		"Payments cutover: Alex · blocked on fraud-review queue",
		"Docs site: unowned · needs a name today",
		"Friday demo: must ship the empty state, not the polish"
	]
};
var LANDING_SAMPLE_ANSWER = {
	spoken: "I'd use a hash map so we stay O(n). Walk the array once, store value to index, and for each n check whether target minus n is already in the map. Return those two indices as soon as we hit a match.",
	points: [
		"One pass, hash map of value → index",
		"Watch the same-element rule",
		"O(n) time, O(n) space"
	],
	code: `const seen = new Map<number, number>();
for (let i = 0; i < nums.length; i++) {
  const need = target - nums[i];
  if (seen.has(need)) return [seen.get(need)!, i];
  seen.set(nums[i], i);
}`
};
var buttonVariants = cva("inline-flex items-center justify-center gap-2 whitespace-nowrap text-sm font-medium transition-[opacity,transform,background-color,box-shadow,color] duration-150 ease-out focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/60 disabled:pointer-events-none disabled:opacity-40 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0 active:not-disabled:scale-[0.96]", {
	variants: {
		variant: {
			default: "bg-primary text-primary-foreground hover:opacity-90",
			secondary: "bg-secondary text-secondary-foreground hover:bg-accent",
			outline: "bg-transparent shadow-[var(--shadow-border)] hover:shadow-[var(--shadow-border-hover)]",
			ghost: "hover:bg-accent hover:text-accent-foreground",
			sage: "bg-sage-dim text-sage hover:opacity-90",
			destructive: "bg-destructive/15 text-destructive hover:bg-destructive/25"
		},
		size: {
			default: "h-11 rounded-md px-4",
			sm: "h-9 rounded-sm px-3 text-sm",
			lg: "h-12 rounded-lg px-5",
			icon: "size-11 rounded-md",
			"icon-sm": "size-9 rounded-sm"
		}
	},
	defaultVariants: {
		variant: "default",
		size: "default"
	}
});
var Button = import_react.forwardRef(({ className, variant, size, asChild = false, ...props }, ref) => {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(asChild ? Slot : "button", {
		className: cn(buttonVariants({
			variant,
			size,
			className
		})),
		ref,
		...props
	});
});
Button.displayName = "Button";
function VeilMark({ className }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("svg", {
		viewBox: "0 0 32 32",
		className: cn("size-7", className),
		"aria-hidden": true,
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("rect", {
			x: "3.5",
			y: "7.5",
			width: "17",
			height: "17",
			rx: "4",
			fill: "none",
			stroke: "currentColor",
			strokeWidth: "1.6"
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("rect", {
			x: "11.5",
			y: "7.5",
			width: "17",
			height: "17",
			rx: "4",
			fill: "none",
			stroke: "currentColor",
			strokeWidth: "1.6",
			strokeDasharray: "2.4 2.2",
			opacity: "0.45"
		})]
	});
}
function VeilWordmark({ className }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
		className: cn("inline-flex items-center gap-2 text-foreground", className),
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(VeilMark, { className: "size-6" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
			className: "font-display text-xl tracking-tight",
			children: "VEIL"
		})]
	});
}
//#endregion
export { MEETING_DOC as a, SALES_SLIDE as c, LANDING_SAMPLE_ANSWER as i, VeilWordmark as l, CODE_PROBLEM as n, MOCK_QUESTIONS as o, DEFAULT_PROFILE as r, MODE_COPY as s, Button as t };
