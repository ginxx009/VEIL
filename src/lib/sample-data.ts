import type { MeetingMode, Profile } from "./types";

export const SAMPLE_RESUME = `Alex Rivera — Staff Software Engineer
8 years shipping product and platform systems.
TypeScript, React, Node, Postgres, AWS.
Led a billing rewrite that cut failed payments 22%.
Comfortable with system design, on-call, and mentoring.`;

export const SAMPLE_JOB = `Staff Engineer, Platform
Own the payments and identity services. Mentorship is part of the job.
Interviews include a coding round and a system-design conversation.`;

export const DEFAULT_PROFILE: Profile = {
  displayName: "Alex Rivera",
  role: "Staff Engineer",
  company: "Northwind",
  resume: SAMPLE_RESUME,
  jobDescription: SAMPLE_JOB,
  mode: "interview",
};

export const MODE_COPY: Record<
  MeetingMode,
  { label: string; meeting: string; interviewer: string; hint: string }
> = {
  interview: {
    label: "Interview",
    meeting: "Staff Engineer · first round",
    interviewer: "Jordan Hale",
    hint: "Coding + behavioral. Answers stay first-person and speakable.",
  },
  sales: {
    label: "Sales call",
    meeting: "Product walkthrough · Northwind",
    interviewer: "Sam Okonkwo",
    hint: "Pricing, timeline, and competitor objections.",
  },
  meeting: {
    label: "Internal meeting",
    meeting: "Q3 launch standup",
    interviewer: "Priya Shah",
    hint: "Status, owners, blockers — keep answers short.",
  },
};

export const MOCK_QUESTIONS: Record<MeetingMode, string[]> = {
  interview: [
    "Tell me about yourself — the short version.",
    "Walk me through a production incident you owned end to end.",
    "How would you design a URL shortener that handles 10 million writes a day?",
    "Looking at the Two Sum prompt on the shared screen — how would you approach it?",
    "What's the time and space complexity of your solution, and where does it break?",
  ],
  sales: [
    "Can you walk us through pricing for a 40-person team?",
    "How do you compare to the tool we already pay for?",
    "What's the implementation timeline if we started next month?",
    "Who actually owns this after the contract is signed?",
    "What happens if we need to be off the platform in 90 days?",
  ],
  meeting: [
    "What's the status on the Q3 launch?",
    "Who owns the identity migration, and is it still this sprint?",
    "Any blockers we should escalate today?",
    "What slipped since Monday, and why?",
    "What does done look like before Friday?",
  ],
};

export const CODE_PROBLEM = {
  title: "1. Two Sum",
  prompt:
    "Given an array of integers nums and an integer target, return the indices of the two numbers that add up to target. You may assume each input has exactly one solution, and you may not use the same element twice.",
  signature: `function twoSum(nums: number[], target: number): number[] {
  // your code
}`,
  tests: "nums = [2, 7, 11, 15], target = 9  →  [0, 1]",
};

export const SALES_SLIDE = {
  kicker: "Northwind Platform",
  title: "Pricing that scales with seats, not surprises",
  bullets: [
    "Team — $24 / seat / month, up to 50",
    "Scale — $18 / seat, SSO + audit log",
    "Pilot — 21 days, production data, no card",
  ],
};

export const MEETING_DOC = {
  title: "Q3 launch — working notes",
  lines: [
    "Identity migration: Priya · in progress · risk: token TTL",
    "Payments cutover: Alex · blocked on fraud-review queue",
    "Docs site: unowned · needs a name today",
    "Friday demo: must ship the empty state, not the polish",
  ],
};

export const LANDING_SAMPLE_ANSWER = {
  spoken:
    "I'd use a hash map so we stay O(n). Walk the array once, store value to index, and for each n check whether target minus n is already in the map. Return those two indices as soon as we hit a match.",
  points: [
    "One pass, hash map of value → index",
    "Watch the same-element rule",
    "O(n) time, O(n) space",
  ],
  code: `const seen = new Map<number, number>();
for (let i = 0; i < nums.length; i++) {
  const need = target - nums[i];
  if (seen.has(need)) return [seen.get(need)!, i];
  seen.set(nums[i], i);
}`,
};
