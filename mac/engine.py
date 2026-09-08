"""VEIL copilot brain — xAI or the VEIL HTTP API. No UI."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path

SUPPORT = Path.home() / "Library" / "Application Support" / "VEIL"
CONFIG = SUPPORT / "config.json"
PROFILE = SUPPORT / "profile.json"
SESSIONS = SUPPORT / "sessions.json"

MODES = ("interview", "sales", "meeting")

DEFAULT_PROFILE = {
    "displayName": "Alex Rivera",
    "role": "Staff Engineer",
    "company": "Northwind",
    "resume": (
        "Alex Rivera — Staff Software Engineer\n"
        "8 years shipping product and platform systems.\n"
        "TypeScript, React, Node, Postgres, AWS.\n"
        "Led a billing rewrite that cut failed payments 22%.\n"
        "Comfortable with system design, on-call, and mentoring."
    ),
    "jobDescription": (
        "Staff Engineer, Platform\n"
        "Own the payments and identity services. Mentorship is part of the job.\n"
        "Interviews include a coding round and a system-design conversation."
    ),
    "mode": "interview",
}

MODE_COPY = {
    "interview": "Staff Engineer · first round",
    "sales": "Product walkthrough · Northwind",
    "meeting": "Q3 launch standup",
}

MOCK_QUESTIONS = {
    "interview": [
        "Tell me about yourself — the short version.",
        "Walk me through a production incident you owned end to end.",
        "How would you design a URL shortener that handles 10 million writes a day?",
        "Looking at the Two Sum prompt on the shared screen — how would you approach it?",
        "What's the time and space complexity of your solution, and where does it break?",
    ],
    "sales": [
        "Can you walk us through pricing for a 40-person team?",
        "How do you compare to the tool we already pay for?",
        "What's the implementation timeline if we started next month?",
        "Who actually owns this after the contract is signed?",
        "What happens if we need to be off the platform in 90 days?",
    ],
    "meeting": [
        "What's the status on the Q3 launch?",
        "Who owns the identity migration, and is it still this sprint?",
        "Any blockers we should escalate today?",
        "What slipped since Monday, and why?",
        "What does done look like before Friday?",
    ],
}

SCREEN_FALLBACK = (
    "Given an array of integers nums and an integer target, return the indices "
    "of the two numbers that add up to target. You may assume each input has "
    "exactly one solution, and you may not use the same element twice.\n"
    "function twoSum(nums: number[], target: number): number[]\n"
    "nums = [2, 7, 11, 15], target = 9  →  [0, 1]"
)


def _read_json(path: Path, fallback):
    try:
        return json.loads(path.read_text())
    except Exception:
        return fallback


def load_profile() -> dict:
    SUPPORT.mkdir(parents=True, exist_ok=True)
    data = _read_json(PROFILE, {})
    return {**DEFAULT_PROFILE, **data}


def save_profile(profile: dict) -> None:
    SUPPORT.mkdir(parents=True, exist_ok=True)
    PROFILE.write_text(json.dumps(profile, indent=2))


def load_config() -> dict:
    env_url = os.environ.get("VEIL_API_URL", "")
    env_key = os.environ.get("XAI_API_KEY", "")
    file_cfg = _read_json(CONFIG, {})
    return {
        "api_url": env_url or file_cfg.get("api_url", ""),
        "api_key": env_key or file_cfg.get("api_key", ""),
    }


def save_config(cfg: dict) -> None:
    SUPPORT.mkdir(parents=True, exist_ok=True)
    CONFIG.write_text(json.dumps(cfg, indent=2))


def save_session(session: dict) -> None:
    SUPPORT.mkdir(parents=True, exist_ok=True)
    all_s = _read_json(SESSIONS, [])
    if not isinstance(all_s, list):
        all_s = []
    all_s.insert(0, session)
    SESSIONS.write_text(json.dumps(all_s[:24], indent=2))


def _post_json(url: str, payload: dict, headers: dict | None = None) -> dict:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json", **(headers or {})},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as res:
        return json.loads(res.read().decode("utf-8"))


def _clip(value: str, n: int) -> str:
    return value[-n:] if len(value) > n else value


def _extract_json(text: str):
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end < 0:
        return None
    try:
        return json.loads(text[start : end + 1])
    except Exception:
        return None


def _voice(mode: str) -> str:
    if mode == "interview":
        return "The user is in a live job interview. Speak as them, first person, calm and specific. No filler, no 'great question'."
    if mode == "sales":
        return "The user is on a live sales or customer call. Give concise commercial answers they can say out loud. Be honest about tradeoffs."
    return "The user is in an internal meeting. Give short status-style answers: owner, status, risk, next step."


def _xai_chat(api_key: str, system: str, user: str, max_tokens: int) -> dict:
    data = _post_json(
        "https://api.x.ai/v1/chat/completions",
        {
            "model": "grok-4.5",
            "temperature": 0.55,
            "max_tokens": max_tokens,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        },
        {"Authorization": f"Bearer {api_key}"},
    )
    return {"ok": True, "text": data.get("choices", [{}])[0].get("message", {}).get("content", "")}


def assist(profile: dict, transcript: str, question: str, kind: str, screen_text: str) -> dict:
    cfg = load_config()
    payload = {
        "mode": profile.get("mode", "interview"),
        "kind": kind,
        "resume": profile.get("resume", ""),
        "job": profile.get("jobDescription", ""),
        "transcript": transcript,
        "question": question,
        "screenText": screen_text,
    }
    url = (cfg.get("api_url") or "").rstrip("/")
    if url:
        try:
            return _post_json(f"{url}/api/assist", payload)
        except urllib.error.URLError as e:
            return {"ok": False, "error": f"Could not reach VEIL API ({e.reason})"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    key = cfg.get("api_key") or ""
    if not key:
        return {
            "ok": False,
            "error": "Add an xAI API key in VEIL → Settings, or set XAI_API_KEY.",
        }

    system = f"""You are VEIL, a private meeting copilot. Only the user can see your output.
{_voice(payload["mode"])}
Ground every answer in their resume and the job/context when those are provided. Do not invent employers or metrics that are not in the resume.
If this is a coding prompt, give a speakable approach first, then compact TypeScript.
Return ONLY JSON with keys:
- spoken: string (what they should say, 3–6 sentences, no markdown)
- points: string[] (2–4 short talking points)
- code: string (code only if relevant, else empty string)"""
    user = f"""KIND: {"Solve or explain what is on the shared screen." if kind == "screen" else "Answer the latest question."}
RESUME:
{_clip(payload["resume"], 8000) or "(none)"}

JOB / CONTEXT:
{_clip(payload["job"], 4000) or "(none)"}

SHARED SCREEN:
{_clip(screen_text, 4000) or "(none)"}

TRANSCRIPT (latest last):
{_clip(transcript, 4500) or "(none)"}

FOCUS QUESTION:
{_clip(question, 1200) or "(use the latest interviewer question in the transcript)"}"""
    try:
        out = _xai_chat(key, system, user, 900 if kind == "screen" else 700)
    except Exception as e:
        return {"ok": False, "error": str(e)}
    parsed = _extract_json(out["text"]) or {}
    if not isinstance(parsed, dict) or not parsed.get("spoken"):
        return {"ok": True, "result": {"spoken": out["text"].strip(), "points": [], "code": ""}}
    return {
        "ok": True,
        "result": {
            "spoken": str(parsed.get("spoken", "")),
            "points": [str(p) for p in parsed.get("points", [])][:6] if isinstance(parsed.get("points"), list) else [],
            "code": str(parsed.get("code", "") or ""),
        },
    }


def notes(profile: dict, transcript: str) -> dict:
    cfg = load_config()
    payload = {
        "mode": profile.get("mode", "interview"),
        "resume": profile.get("resume", ""),
        "job": profile.get("jobDescription", ""),
        "transcript": transcript,
    }
    url = (cfg.get("api_url") or "").rstrip("/")
    if url:
        try:
            return _post_json(f"{url}/api/notes", payload)
        except Exception as e:
            return {"ok": False, "error": str(e)}
    key = cfg.get("api_key") or ""
    if not key:
        return {"ok": False, "error": "Add an xAI API key in VEIL → Settings."}
    if not transcript.strip():
        return {
            "ok": True,
            "notes": {
                "summary": "No transcript was captured in this session.",
                "keyPoints": [],
                "questions": [],
                "actionItems": [],
                "followUpEmail": "",
            },
        }
    system = """You write private post-call notes for VEIL.
Return ONLY JSON with keys:
- summary: string (1 short paragraph)
- keyPoints: string[]
- questions: string[] (questions the other person asked)
- actionItems: string[]
- followUpEmail: string (a send-ready email, plain text)"""
    user = f"MODE: {payload['mode']}\nRESUME: {payload['resume'][:2000]}\nCONTEXT: {payload['job'][:1500]}\nTRANSCRIPT:\n{_clip(transcript, 4500)}"
    try:
        out = _xai_chat(key, system, user, 1100)
    except Exception as e:
        return {"ok": False, "error": str(e)}
    parsed = _extract_json(out["text"]) or {}
    if not isinstance(parsed, dict) or not parsed.get("summary"):
        return {
            "ok": True,
            "notes": {
                "summary": out["text"].strip(),
                "keyPoints": [],
                "questions": [],
                "actionItems": [],
                "followUpEmail": "",
            },
        }

    def lst(v):
        return [str(x) for x in v][:8] if isinstance(v, list) else []

    return {
        "ok": True,
        "notes": {
            "summary": str(parsed.get("summary", "")),
            "keyPoints": lst(parsed.get("keyPoints")),
            "questions": lst(parsed.get("questions")),
            "actionItems": lst(parsed.get("actionItems")),
            "followUpEmail": str(parsed.get("followUpEmail", "") or ""),
        },
    }
