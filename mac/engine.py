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
    file_cfg = _read_json(CONFIG, {})
    env_key = (
        os.environ.get("OPENAI_API_KEY")
        or os.environ.get("XAI_API_KEY")
        or os.environ.get("GEMINI_API_KEY")
        or os.environ.get("GOOGLE_API_KEY")
        or ""
    )
    env_url = os.environ.get("VEIL_API_URL", "")
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
    with urllib.request.urlopen(req, timeout=20) as res:
        return json.loads(res.read().decode("utf-8"))


def _open(url: str, payload: dict, headers: dict | None = None):
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json", **(headers or {})},
        method="POST",
    )
    return urllib.request.urlopen(req, timeout=20)


def _sse_payloads(response):
    for raw in response:
        line = raw.decode("utf-8", "replace").strip()
        if not line.startswith("data:"):
            continue
        data = line[5:].strip()
        if not data or data == "[DONE]":
            continue
        try:
            yield json.loads(data)
        except json.JSONDecodeError:
            continue


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


def _provider(api_key: str) -> str:
    key = (api_key or "").strip()
    if key.startswith("sk-") or os.environ.get("OPENAI_API_KEY") == key:
        return "openai"
    if key.startswith("AIza") or os.environ.get("GEMINI_API_KEY") == key:
        return "gemini"
    return "xai"


def _http_err(e: urllib.error.HTTPError) -> str:
    raw = ""
    try:
        raw = e.read().decode("utf-8", "replace")
    except Exception:
        pass
    msg = str(e.reason)
    try:
        data = json.loads(raw)
        err = data.get("error")
        if isinstance(err, dict):
            msg = err.get("message") or msg
        elif isinstance(err, str):
            msg = err
        elif raw:
            msg = raw[:400]
    except Exception:
        if raw:
            msg = raw[:400]
    return f"HTTP {e.code}: {msg}"


def _openai_stream(url: str, api_key: str, model: str, system: str, user: str, max_tokens: int):
    res = _open(
        url,
        {
            "model": model,
            "temperature": 0.4,
            "max_tokens": max_tokens,
            "stream": True,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        },
        {"Authorization": f"Bearer {api_key}"},
    )
    with res:
        for payload in _sse_payloads(res):
            delta = (payload.get("choices") or [{}])[0].get("delta") or {}
            piece = delta.get("content") or ""
            if piece:
                yield piece


def _gemini_once(api_key: str, model: str, system: str, user: str, max_tokens: int) -> str:
    res = _open(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        {
            "system_instruction": {"parts": [{"text": system}]},
            "contents": [{"parts": [{"text": user}]}],
            "generationConfig": {"temperature": 0.4, "maxOutputTokens": max_tokens},
        },
        {"x-goog-api-key": api_key},
    )
    with res:
        data = json.loads(res.read().decode("utf-8"))
    parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    return "".join(p.get("text", "") for p in parts if isinstance(p, dict))


def _xai_stream(api_key: str, system: str, user: str, max_tokens: int):
    last = None
    for model in ("grok-4.5", "grok-4.3"):
        try:
            yield from _openai_stream(
                "https://api.x.ai/v1/chat/completions",
                api_key,
                model,
                system,
                user,
                max_tokens,
            )
            return
        except urllib.error.HTTPError as e:
            last = _http_err(e)
            continue
    raise RuntimeError(last or "xAI request failed")


def _gemini_stream(api_key: str, system: str, user: str, max_tokens: int):
    last = None
    models = ("gemini-2.0-flash", "gemini-2.5-flash", "gemini-3.8-flash", "gemini-flash-latest")
    for model in models:
        try:
            yield from _openai_stream(
                "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
                api_key,
                model,
                system,
                user,
                max_tokens,
            )
            return
        except urllib.error.HTTPError as e:
            last = _http_err(e)
            continue
    for model in models:
        try:
            text = _gemini_once(api_key, model, system, user, max_tokens)
            if text.strip():
                yield text
                return
        except urllib.error.HTTPError as e:
            last = _http_err(e)
            continue
    hint = last or "Gemini request failed"
    if "free tier" in hint.lower() or "FAILED_PRECONDITION" in hint:
        hint += " Enable billing in Google AI Studio, or use an xAI key."
    raise RuntimeError(hint)


def _oai_stream(api_key: str, system: str, user: str, max_tokens: int):
    last = None
    for model in ("gpt-4o-mini", "gpt-4.1-mini", "gpt-4o"):
        try:
            yield from _openai_stream(
                "https://api.openai.com/v1/chat/completions",
                api_key,
                model,
                system,
                user,
                max_tokens,
            )
            return
        except urllib.error.HTTPError as e:
            last = _http_err(e)
            continue
    raise RuntimeError(last or "OpenAI request failed")


def _stream(api_key: str, system: str, user: str, max_tokens: int):
    kind = _provider(api_key)
    if kind == "openai":
        yield from _oai_stream(api_key, system, user, max_tokens)
    elif kind == "gemini":
        yield from _gemini_stream(api_key, system, user, max_tokens)
    else:
        yield from _xai_stream(api_key, system, user, max_tokens)


def _chat(api_key: str, system: str, user: str, max_tokens: int) -> dict:
    text = "".join(_stream(api_key, system, user, max_tokens))
    return {"ok": True, "text": text}


def _assist_prompts(profile, transcript, question, kind, screen_text):
    system = f"""VEIL live earpiece. {_voice(profile.get("mode", "interview"))}
Use the resume. Do not invent employers or metrics.
Answer in 2–4 short spoken sentences, first person. No preamble, no markdown, no JSON.
Coding: one-sentence approach, then a tiny snippet."""
    user = f"""Q: {_clip(question, 500) or "(latest in transcript)"}
RESUME:
{_clip(profile.get("resume", ""), 1800) or "(none)"}
ROLE:
{_clip(profile.get("jobDescription", ""), 700) or "(none)"}
HEARD:
{_clip(transcript, 1200) or "(none)"}
SCREEN:
{_clip(screen_text, 800) if kind == "screen" else "(n/a)"}"""
    return system, user


def stream_assist(profile: dict, transcript: str, question: str, kind: str, screen_text: str):
    cfg = load_config()
    url = (cfg.get("api_url") or "").rstrip("/")
    if url:
        res = _post_json(
            f"{url}/api/assist",
            {
                "mode": profile.get("mode", "interview"),
                "kind": kind,
                "resume": profile.get("resume", ""),
                "job": profile.get("jobDescription", ""),
                "transcript": transcript,
                "question": question,
                "screenText": screen_text,
            },
        )
        if not res.get("ok"):
            raise RuntimeError(res.get("error") or "Assist failed")
        spoken = (res.get("result") or {}).get("spoken") or ""
        if spoken:
            yield spoken
        return
    key = cfg.get("api_key") or ""
    if not key:
        raise RuntimeError("Add an OpenAI API key in VEIL → Settings.")
    system, user = _assist_prompts(profile, transcript, question, kind, screen_text)
    yield from _stream(key, system, user, 320 if kind == "screen" else 180)


def assist(profile: dict, transcript: str, question: str, kind: str, screen_text: str) -> dict:
    try:
        text = "".join(stream_assist(profile, transcript, question, kind, screen_text)).strip()
    except Exception as e:
        return {"ok": False, "error": str(e)}
    parsed = _extract_json(text) or {}
    if isinstance(parsed, dict) and parsed.get("spoken"):
        return {
            "ok": True,
            "result": {
                "spoken": str(parsed.get("spoken", "")),
                "points": [str(p) for p in parsed.get("points", [])][:6] if isinstance(parsed.get("points"), list) else [],
                "code": str(parsed.get("code", "") or ""),
            },
        }
    return {"ok": True, "result": {"spoken": text, "points": [], "code": ""}}


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
        return {"ok": False, "error": "Add an OpenAI API key in VEIL → Settings."}
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
        out = _chat(key, system, user, 1100)
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
