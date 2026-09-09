"""VEIL copilot brain — xAI or the VEIL HTTP API. No UI."""

from __future__ import annotations

import base64
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

if sys.platform == "darwin":
    SUPPORT = Path.home() / "Library" / "Application Support" / "VEIL"
elif sys.platform == "win32":
    SUPPORT = Path(os.environ.get("APPDATA", str(Path.home()))) / "VEIL"
else:
    SUPPORT = Path.home() / ".local" / "share" / "VEIL"
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
    "agenticFacts": "",
    "projects": "",
    "leadership": "",
    "dataFacts": "",
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


def capture_screen() -> str | None:
    """JPEG of the main display as base64. VEIL is capture-excluded."""
    if sys.platform == "win32":
        try:
            from io import BytesIO

            from PIL import ImageGrab

            img = ImageGrab.grab()
            img.thumbnail((1280, 800))
            buf = BytesIO()
            img.convert("RGB").save(buf, format="JPEG", quality=55)
            return base64.b64encode(buf.getvalue()).decode("ascii")
        except Exception as e:
            print(f"VEIL capture: {e}", flush=True)
            return None
    try:
        import Quartz
        from AppKit import NSBitmapImageRep

        img = Quartz.CGWindowListCreateImage(
            Quartz.CGRectInfinite,
            Quartz.kCGWindowListOptionOnScreenOnly,
            Quartz.kCGNullWindowID,
            Quartz.kCGWindowImageBoundsIgnoreFraming,
        )
        if img is None:
            return None
        rep = NSBitmapImageRep.alloc().initWithCGImage_(img)
        data = rep.representationUsingType_properties_(3, {"NSImageCompressionFactor": 0.4})
        if data is None:
            return None
        return base64.b64encode(bytes(data)).decode("ascii")
    except Exception as e:
        print(f"VEIL capture: {e}", flush=True)
        return None


def load_resume_file(path: str) -> str:
    p = Path(path)
    suffix = p.suffix.lower()
    if suffix == ".pdf":
        try:
            from pypdf import PdfReader

            reader = PdfReader(str(p))
            text = "\n".join((page.extract_text() or "") for page in reader.pages)
            text = text.strip()
            if text:
                return text[:24000]
        except Exception as e:
            print(f"VEIL pdf: {e}", flush=True)
        raise RuntimeError("Could not read that PDF. Paste the text into Resume instead.")
    return p.read_text(encoding="utf-8", errors="replace")[:24000]


def load_briefing(name: str = "principal-engineer") -> str:
    """Bundled interview brief for the Job field."""
    if getattr(sys, "frozen", False):
        root = Path(sys._MEIPASS)
    else:
        root = Path(__file__).resolve().parent
    p = root / "playbooks" / f"{name}.md"
    if not p.exists():
        raise RuntimeError(f"No briefing named {name}.")
    return p.read_text(encoding="utf-8", errors="replace")[:24000]


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


def _voice(mode: str, profile: dict) -> str:
    role = (profile.get("role") or "").strip()
    blob = f"{role}\n{profile.get('resume') or ''}\n{profile.get('jobDescription') or ''}\n{profile.get('agenticFacts') or ''}\n{profile.get('projects') or ''}\n{profile.get('leadership') or ''}\n{profile.get('dataFacts') or ''}".lower()
    salesforce = any(
        k in blob
        for k in (
            "salesforce",
            "sfdc",
            "apex",
            "lwc",
            "lightning",
            "sales cloud",
            "service cloud",
            "experience cloud",
            "marketing cloud",
            "npsp",
            "cpq",
            "soql",
        )
    )
    if mode == "sales":
        return "Live sales call. Senior. Straight commercial talk, honest tradeoffs, no brochure."
    if mode == "meeting":
        return "Internal meeting. Owner, what's stuck, blast radius, next step. No theater."
    extra = (
        " This is a senior Salesforce / cloud engineer: talk org shape, data model, "
        "sharing (OWD, roles, sharing rules), governor limits, integration pattern "
        "(platform events, named credentials, middleware), what you'd actually ship "
        "in an enterprise org. Not Trailhead. Not admin click-path. Not junior reciting objects."
        if salesforce
        else (
            " Senior engineer: answer the question they asked. Decision and constraint. "
            "Do not volunteer a war story unless they asked for experience."
        )
    )
    blob_job = f"{blob}\n{profile.get('jobDescription') or ''}".lower()
    if any(k in blob_job for k in ("principal engineer", "agentic coding", "hiring manager")):
        extra += (
            " Principal / hiring-manager bar: they want what YOU built. "
            "If they asked experience, architecture you owned, agentic coding, migration, "
            "or leadership, use one resume-backed example (context, what you owned, why, outcome). "
            "If they asked a design-only question, answer the design first. "
            "Agentic coding means workflows and review loops, not 'I prompt Cursor'."
        )
    return (
        f"You are this person in a live interview, role: {role or 'senior engineer'}.{extra} "
        "Sound like you talking, not like generated text."
    )


def _is_draw_question(question: str) -> bool:
    q = (question or "").lower()
    needles = (
        "draw.io",
        "drawio",
        "excalidraw",
        "lucidchart",
        "on the whiteboard",
        "on a whiteboard",
        "use the whiteboard",
        "draw this on",
        "draw it on",
        "open a diagram",
        "share the canvas",
    )
    return any(n in q for n in needles)


JARGON = (
    "agentic",
    "agentic coding",
    "Claude Code",
    "Cursor CLI",
    "Dynaskills",
    "dynaskills",
    "Cursor CLI",
    "Dynaskills",
    "Copilot",
    "GitHub Copilot",
    "TypeScript",
    "JavaScript",
    "Next.js",
    "React",
    "Python",
    "PHP",
    "Laravel",
    "AWS",
    "GCP",
    "Azure",
    "CI/CD",
    "high availability",
    "TSEKMO",
    "Checkmo",
    "JOSIE",
    "Dalakuha",
    "AlbumKo",
    "ETL",
    "ELT",
    "data pipeline",
    "EventBridge",
    "Kafka",
    "event sourcing",
    "PostgreSQL",
)
)


def speech_hints(profile: dict | None = None) -> list[str]:
    """Words for macOS Speech so jargon like 'agentic' doesn't become 'agency'."""
    seen = []
    for w in JARGON:
        if w.lower() not in {x.lower() for x in seen}:
            seen.append(w)
    blob = ""
    if profile:
        blob = f"{profile.get('resume') or ''} {profile.get('jobDescription') or ''} {profile.get('role') or ''} {profile.get('agenticFacts') or ''} {profile.get('projects') or ''} {profile.get('leadership') or ''} {profile.get('dataFacts') or ''}"
    for token in blob.replace("/", " ").replace(",", " ").split():
        t = token.strip(".-()[]")
        if len(t) < 4 or not any(c.isalpha() for c in t):
            continue
        if t.lower() not in {x.lower() for x in seen}:
            seen.append(t)
        if len(seen) >= 80:
            break
    return seen


def looks_like_utterance(text: str) -> bool:
    t = (text or "").strip().lower()
    if not t or t in {"me too", "yeah", "yes", "okay", "ok", "right", "uh huh", "mm", "hmm"}:
        return False
    return len(t.split()) >= 5


# Live speech often mangles the words this interview is built on.
_ASR_FIXES = (
    ("agency coding", "agentic coding"),
    ("agency coating", "agentic coding"),
    ("agent see coding", "agentic coding"),
    ("a gentic coding", "agentic coding"),
    ("agents including", "agentic coding"),
    ("agent including", "agentic coding"),
    ("older cars are", "Cursor"),
    ("older cars", "Cursor"),
    ("sue's like hers are", "tools like Cursor"),
    ("sues like hers are", "tools like Cursor"),
    ("tools like hers are", "tools like Cursor"),
    ("hers are claude", "Cursor, Claude"),
    ("git hub copilot", "GitHub Copilot"),
    ("github co pilot", "GitHub Copilot"),
    ("clod code", "Claude Code"),
    ("clawed code", "Claude Code"),
    ("prodded", "a product"),
    ("for prodded", "for a product"),
    ("owned and architectural", "owned an architectural"),
    ("insured with scalable", "ensured it was scalable"),
    ("insured it was", "ensured it was"),
    ("maintainable in a long run", "maintainable in the long run"),
    ("next js", "Next.js"),
    ("type script", "TypeScript"),
    ("checkmo", "TSEKMO"),
    ("check mo", "TSEKMO"),
    ("tsek mo", "TSEKMO"),
    ("czech mo", "TSEKMO"),
    ("eto processes", "ETL processes"),
    ("eto process", "ETL process"),
    ("handling eto", "handling ETL"),
    ("with eto", "with ETL"),
    ("eto or processing", "ETL or processing"),
    ("e t l", "ETL"),
    ("e t o", "ETL"),
)


def repair_asr(text: str) -> str:
    out = text or ""
    low = out.lower()
    for src, dst in _ASR_FIXES:
        i = low.find(src)
        while i >= 0:
            out = out[:i] + dst + out[i + len(src) :]
            low = out.lower()
            i = low.find(src, i + len(dst))
    return out


def _assist_prompts(profile, transcript, question, kind, screen_text):
    name = profile.get("displayName") or "the candidate"
    role = profile.get("role") or "senior engineer"
    drawing = kind in ("draw", "screen") or _is_draw_question(question)
    follow = kind == "followup"
    draw_rule = (
        "They asked you to DRAW. Talk the next boxes to put on the canvas, in order, as speech. "
        "Name the arrow. One tradeoff. Do not dump a whole architecture essay."
        if drawing
        else (
            "Do NOT describe boxes, arrows, draw.io, or a whiteboard. "
            "They did not ask you to draw. Answer the question out loud like a senior in the room."
        )
    )
    if follow:
        length = (
            "2 to 4 short spoken sentences. Do not repeat the previous answer. "
            "Add only the why / the missing piece they just asked."
        )
        extra_follow = (
            "- This is a FOLLOW-UP on the last answer already on screen. "
            "Do not restart. Do not erase or restate that answer. Extend it.\n"
        )
    else:
        length = "6 to 9 short spoken sentences. Periods, not semicolons. Principal depth: why and how, not a summary."
        extra_follow = ""
        qlow = (question or "").lower()
        if any(k in qlow for k in ("how are you feeling", "how do you feel", "feeling about the interview")):
            length = "One or two honest sentences. This is a check-in, not a tech question. Do not recap the stack."
    system = (
        f"You write spoken lines for {name}, {role}.\n"
        f"{_voice(profile.get('mode', 'interview'), profile)}\n\n"
        "They will say this out loud in the next 15 seconds. Speech, not an essay.\n\n"
        "Hard rules:\n"
        f"- First person only. You are {name}, a {role}.\n"
        f"- {length}\n"
        f"{extra_follow}"
        "- The question is live speech-to-text and will be messy. Infer the intended interview question from the job brief. Common slips: agency→agentic, cursor, copilot, next js, type script, ETO→ETL, Checkmo→TSEKMO.\n"
        "- Contractions. Senior tone: calm, specific, a little blunt.\n"
        "- Answer ONLY what they asked. If they asked how you'd design it, give the design. Stop.\n"
        "- Do NOT invent a personal example. Use the resume only. For Principal / agentic questions about experience or ownership, one resume-backed example is allowed.\n"
        "- Ground facts in the resume. NEVER invent a percent, dollar amount, headcount, or years that are not written in the resume. If there is no number, do not make one up.\n"
        "- Agentic coding: do not say you 'integrated the tools'. Give ONE workflow: the problem, the exact steps (who runs Cursor CLI / Claude Code / Dynaskills, what the agent is allowed to do, where tests and a human gate the diff), why that loop, and impact ONLY if HARD FACTS has a number. No boilerplate story.\n"
        "- HARD FACTS are for agentic / AI-tool questions only (years, Cursor, Claude Code, Dynaskills, team workflow). Dynaskills is skills/personas for agents, not a production product unless PRODUCTS lists it as a shipped product.\n"
        "- If they asked years / which tools / impact: answer those three from HARD FACTS first, then the resume. If HARD FACTS lists Cursor or Claude Code, you have used them. Never say you have not used a tool that is in HARD FACTS.\n"
        "- Architecture / scale / HA / cloud / 'a time you owned a decision': pick ONE system from PRODUCTS / PROJECTS first (TSEKMO if it fits). Always name the alternative you dropped and why. Tie the choice to a business outcome from PRODUCTS or LEADERSHIP only — cost, uptime, shipping speed — never a made-up percent.\n"
        "- Leadership / culture / mentoring / influence: use LEADERSHIP facts. How you got other engineers to adopt a standard, not that you 'communicate well'.\n"
        "- ETL / ELT / data pipelines / large datasets / PHP-to-Node / cutover: ETO in the transcript means ETL. Use DATA / ETL facts first. Kafka / event-sourcing / EventBridge consumers ARE the pipeline — do not say that is 'not ETL'. Do NOT open with 'I don't have experience'. Lead with Kafka at Accenture (zero data loss, decouple monolith) then TSEKMO EventBridge/S3/RDS. PHP-to-Node is allowed when DATA lists that cutover. One clause at the end only if DATA says no Spark/warehouse.\n"
        "- Do not describe agentic coding as generating boilerplate or autocomplete. That is the answer this interviewer is screening out.\n"
        "- Name a real constraint only if it belongs in that design answer (limits, sharing, latency, cost).\n"
        "- If the question is vague, say what you'd need to know — do not pad with an anecdote.\n"
        "- Do not start with Great question, Absolutely, Certainly, As a senior, I would say.\n"
        "- No: furthermore, leverage, utilize, robust, seamless, passionate, circling back.\n"
        "- No markdown, bullets, numbered points, JSON, or labels.\n"
        f"- {draw_rule}\n"
        "- Coding: the approach in one breath, then a tiny snippet, no tutorial."
    )
    user = (
        "HARD FACTS — this is true. Do not contradict it. If empty, do not invent tools or years:\n"
        f"{_clip(profile.get('agenticFacts', ''), 2000) or '(none — then you may not claim Cursor, Claude Code, or Copilot years)'}\n\n"
        "PRODUCTS / PROJECTS you built or are building — architecture and ownership answers MUST come from here. Do not invent a product:\n"
        f"{_clip(profile.get('projects', ''), 4000) or '(none — then use the resume only; do not invent a platform)'}\n\n"
        "LEADERSHIP — culture change, mentoring, how a standard actually spread. Use this when they ask how you lead without a title:\n"
        f"{_clip(profile.get('leadership', ''), 2000) or '(none — do not invent a mentoring program)'}\n\n"
        "DATA / ETL — pipelines, EventBridge, S3, RDS, large sets, PHP→Node cutover. Use this when they ask ETL/ETO/data infrastructure:\n"
        f"{_clip(profile.get('dataFacts', ''), 3000) or '(none — map to PRODUCTS EventBridge/S3/RDS; do not invent Spark)'}\n\n"
        f"They're asking:\n{_clip(question, 700) or '(latest in transcript)'}\n\n"
        "Resume (facts only):\n"
        f"{_clip(profile.get('resume', ''), 5000) or '(none)'}\n\n"
        "Role / job they're interviewing for:\n"
        f"{_clip(profile.get('jobDescription', ''), 8000) or '(none)'}\n\n"
        "Recent conversation (includes your last spoken answer as 'you:'):\n"
        f"{_clip(transcript, 2500) or '(none)'}\n\n"
        + (
            f"Follow-up only. Do not repeat the last 'you:' block. {name} should add the why."
            if follow
            else f"Reply with only the words {name} should say next. Match the question."
        )
    )
    return system, user


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


def _openai_stream(url: str, api_key: str, model: str, system: str, user: str, max_tokens: int, image_b64=None):
    content = user
    if image_b64:
        content = [
            {"type": "text", "text": user},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_b64}", "detail": "low"},
            },
        ]
    res = _open(
        url,
        {
            "model": model,
            "temperature": 0.5,
            "max_tokens": max_tokens,
            "stream": True,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": content},
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
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": max_tokens},
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


def _oai_stream(api_key: str, system: str, user: str, max_tokens: int, image_b64=None):
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
                image_b64=image_b64,
            )
            return
        except urllib.error.HTTPError as e:
            last = _http_err(e)
            continue
    raise RuntimeError(last or "OpenAI request failed")


def _stream(api_key: str, system: str, user: str, max_tokens: int, image_b64=None):
    kind = _provider(api_key)
    if kind == "openai":
        yield from _oai_stream(api_key, system, user, max_tokens, image_b64=image_b64)
    elif kind == "gemini":
        yield from _gemini_stream(api_key, system, user, max_tokens)
    else:
        yield from _xai_stream(api_key, system, user, max_tokens)


def _chat(api_key: str, system: str, user: str, max_tokens: int) -> dict:
    text = "".join(_stream(api_key, system, user, max_tokens))
    return {"ok": True, "text": text}


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
    q = (question or "").lower()
    if kind != "screen" and _is_draw_question(q):
        kind = "draw"
    image = None
    if kind == "screen" or kind == "draw":
        image = capture_screen()
    system, user = _assist_prompts(profile, transcript, question, kind, screen_text)
    yield from _stream(
        key,
        system,
        user,
        520 if kind in ("screen", "draw", "answer") else 360,
        image_b64=image,
    )


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
