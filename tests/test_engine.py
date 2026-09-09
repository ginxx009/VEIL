"""Unit tests for VEIL's copilot brain. No Mac UI, no network."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "mac"))

import engine  # noqa: E402


@pytest.fixture
def tmp_support(tmp_path, monkeypatch):
    monkeypatch.setattr(engine, "SUPPORT", tmp_path)
    monkeypatch.setattr(engine, "CONFIG", tmp_path / "config.json")
    monkeypatch.setattr(engine, "PROFILE", tmp_path / "profile.json")
    monkeypatch.setattr(engine, "SESSIONS", tmp_path / "sessions.json")
    return tmp_path


def test_provider_openai():
    assert engine._provider("sk-abc") == "openai"


def test_provider_gemini():
    assert engine._provider("AIzaSyDummy") == "gemini"


def test_provider_xai():
    assert engine._provider("xai-abc") == "xai"


def test_clip_keeps_short():
    assert engine._clip("hello", 10) == "hello"


def test_clip_tail():
    assert engine._clip("abcdefghij", 4) == "ghij"


@pytest.mark.parametrize(
    "q,expect",
    [
        ("please open draw.io and sketch the flow", True),
        ("put this on the whiteboard", True),
        ("use the whiteboard for this", True),
        ("draw this on the canvas", True),
        ("how would you design a Salesforce integration?", False),
        ("walk me through a system design", False),
        ("draw a distinction between sync and async", False),
        ("tell me about yourself", False),
        ("", False),
    ],
)
def test_draw_detection(q, expect):
    assert engine._is_draw_question(q) is expect


def test_prompt_does_not_coach_draw_by_default():
    profile = {
        "displayName": "Alex",
        "role": "Senior Salesforce Engineer",
        "resume": "Apex, LWC, named credentials.",
        "jobDescription": "Staff SFDC",
        "mode": "interview",
    }
    system, user = engine._assist_prompts(
        profile, "", "How would you design a billing integration?", "answer", ""
    )
    assert "They did not ask you to draw" in system
    assert "They asked you to DRAW" not in system
    assert "Do NOT invent a personal example" in system
    blob = (system + user).lower()
    assert "draw.io" in blob  # the prohibition mentions it
    assert "match the question" in user.lower()


def test_prompt_does_coach_draw_when_asked():
    profile = {"displayName": "Alex", "role": "Engineer", "resume": "", "mode": "interview"}
    system, _ = engine._assist_prompts(
        profile, "", "Can you sketch this on the whiteboard?", "answer", ""
    )
    assert "They asked you to DRAW" in system


def test_salesforce_voice_when_resume_has_apex():
    profile = {
        "displayName": "Alex",
        "role": "Engineer",
        "resume": "5 years Apex and LWC on Sales Cloud.",
        "mode": "interview",
    }
    voice = engine._voice("interview", profile)
    assert "Salesforce" in voice
    assert "governor limits" in voice


def test_generic_senior_voice_without_sfdc():
    profile = {
        "displayName": "Alex",
        "role": "Staff Engineer",
        "resume": "TypeScript and Postgres.",
        "mode": "interview",
    }
    voice = engine._voice("interview", profile)
    assert "Salesforce" not in voice
    assert "war story" in voice


def test_load_resume_txt(tmp_path):
    p = tmp_path / "cv.txt"
    p.write_text("Jane Doe\nApex developer", encoding="utf-8")
    assert "Jane Doe" in engine.load_resume_file(str(p))


def test_load_resume_truncates(tmp_path):
    p = tmp_path / "cv.md"
    p.write_text("x" * 30000, encoding="utf-8")
    assert len(engine.load_resume_file(str(p))) == 24000


def test_profile_roundtrip(tmp_support):
    engine.save_profile({"displayName": "Pat", "role": "SE", "resume": "Apex"})
    loaded = engine.load_profile()
    assert loaded["displayName"] == "Pat"
    assert loaded["role"] == "SE"
    assert loaded["mode"] == "interview"  # default fill


def test_config_prefers_env(tmp_support, monkeypatch):
    engine.save_config({"api_key": "sk-file", "api_url": ""})
    monkeypatch.setenv("OPENAI_API_KEY", "sk-env")
    cfg = engine.load_config()
    assert cfg["api_key"] == "sk-env"


def test_extract_json():
    data = engine._extract_json('noise {"spoken": "hi"} trailing')
    assert data == {"spoken": "hi"}


def test_extract_json_none():
    assert engine._extract_json("no json here") is None


def test_followup_prompt_does_not_restart():
    profile = {
        "displayName": "Alex",
        "role": "Principal Engineer",
        "resume": "Shipped agentic review loops on Cursor.",
        "jobDescription": "Principal Engineer hiring manager. Agentic coding.",
        "mode": "interview",
    }
    prior = "them: how would you scale checkout?\nyou: I'd split read and write paths first."
    system, user = engine._assist_prompts(profile, prior, "why?", "followup", "")
    assert "FOLLOW-UP" in system
    assert "Do not repeat" in system
    assert "why?" in user
    assert "you: I'd split" in user


def test_principal_voice_from_job_brief():
    profile = {
        "displayName": "Alex",
        "role": "Engineer",
        "resume": "TypeScript.",
        "jobDescription": "Principal Engineer hiring manager interview. Agentic coding is the highest priority.",
        "mode": "interview",
    }
    voice = engine._voice("interview", profile)
    assert "Principal" in voice
    assert "agentic" in voice.lower()


def test_load_briefing_principal():
    text = engine.load_briefing("principal-engineer")
    assert "agentic coding" in text.lower()
    assert "Principal Engineer" in text


def test_speech_hints_include_agentic():
    hints = engine.speech_hints(
        {
            "resume": "Used Cursor and Claude Code for agentic loops.",
            "jobDescription": "Principal Engineer hiring manager",
            "role": "Principal Engineer",
        }
    )
    joined = " ".join(hints).lower()
    assert "agentic" in joined
    assert "cursor" in joined


def test_looks_like_utterance():
    assert engine.looks_like_utterance("me too") is False
    assert engine.looks_like_utterance("ok") is False
    assert (
        engine.looks_like_utterance(
            "how you introduced agentic coding practices across your team"
        )
        is True
    )


def test_prompt_forbids_invented_metrics():
    profile = {
        "displayName": "Alex",
        "role": "Principal Engineer",
        "resume": "Cursor workflows.",
        "jobDescription": "Principal Engineer. Agentic coding.",
        "mode": "interview",
    }
    system, _ = engine._assist_prompts(profile, "", "how did you scale agentic coding", "answer", "")
    assert "NEVER invent a percent" in system
    assert "speech-to-text" in system
    assert "Agentic coding" in system
    assert "boilerplate" in system.lower()


def test_repair_asr_agentic_and_cursor():
    raw = (
        "hands on experience with agency coding specifically how many years "
        "have you been working with Sue's like hers are Claude Code or GitHub Copilot"
    )
    fixed = engine.repair_asr(raw)
    low = fixed.lower()
    assert "agentic coding" in low
    assert "cursor" in low
    assert "claude code" in low


def test_repair_asr_agents_including_and_older_cars():
    raw = (
        "hands on experience with agents including specifically how many years "
        "have you been working with older cars are Claude Code a GitHub Copilot"
    )
    low = engine.repair_asr(raw).lower()
    assert "agentic coding" in low
    assert "cursor" in low


def test_agentic_facts_override_resume():
    profile = {
        "displayName": "Dexter",
        "role": "Principal Engineer",
        "resume": "TypeScript, AWS.",
        "agenticFacts": "5 years agentic. Cursor CLI, Claude Code, Dynaskills personas. Not Copilot-only.",
        "jobDescription": "Principal Engineer. Agentic coding.",
        "mode": "interview",
    }
    system, user = engine._assist_prompts(
        profile, "", "how many years with Cursor and Claude Code", "answer", ""
    )
    assert "HARD FACTS" in user
    assert "Dynaskills" in user
    assert "Never say you have not used a tool that is in HARD FACTS" in system
    assert "shipped product" in system.lower() or "not a production product" in system.lower()


def test_architecture_prompt_forbids_dynaskills_as_product():
    profile = {
        "displayName": "Dexter",
        "role": "Principal Engineer",
        "resume": "Designed a multi-AZ payments API on AWS.",
        "agenticFacts": "Cursor CLI, Claude Code, Dynaskills personas.",
        "projects": "Payments API on AWS, multi-AZ, SQS over a cron. Alternative was a bigger RDS.",
        "jobDescription": "Principal Engineer",
        "mode": "interview",
    }
    system, user = engine._assist_prompts(
        profile,
        "",
        "tell me about a time you independently owned an architectural decision for a product",
        "answer",
        "",
    )
    assert "PRODUCTS / PROJECTS" in user
    assert "Payments API" in user
    assert "PRODUCTS / PROJECTS first" in system or "pick ONE system from PRODUCTS" in system
    assert "6 to 9" in system
    assert "do not say you 'integrated the tools'" in system.lower() or "integrated the tools" in system


def test_repair_asr_architecture_question():
    raw = (
        "independently owned and architectural decision for prodded "
        "how you insured with scalable and maintainable in a long run"
    )
    low = engine.repair_asr(raw).lower()
    assert "a product" in low
    assert "owned an architectural" in low
    assert "ensured it was scalable" in low


def test_repair_asr_tsekmo():
    assert "tsekmo" in engine.repair_asr("walk me through Checkmo").lower()


def test_repair_asr_etl_not_eto():
    raw = "experience with designing data pipelines handling ETO processes or processing large data sets"
    low = engine.repair_asr(raw).lower()
    assert "etl" in low
    assert "eto processes" not in low


def test_data_pipeline_prompt_does_not_disqualify():
    profile = {
        "displayName": "Dexter",
        "role": "Principal Engineer",
        "resume": "Node RDS.",
        "projects": "TSEKMO EventBridge S3 RDS Lambda. No Spark warehouse.",
        "jobDescription": "Principal Engineer",
        "mode": "interview",
    }
    system, _ = engine._assist_prompts(profile, "", "tell me about ETL pipelines", "answer", "")
    assert "Do NOT open with" in system
    assert "ETO" in system
    assert "PHP-to-Node" in system


def test_leadership_facts_in_prompt():
    profile = {
        "displayName": "Dexter",
        "role": "Principal Engineer",
        "resume": "AWS.",
        "agenticFacts": "Cursor CLI.",
        "projects": "TSEKMO Lambda plus EC2 sockets. Dropped one-box EC2.",
        "leadership": "Paired juniors on Dynaskills so the same PR gate stuck.",
        "jobDescription": "Principal Engineer",
        "mode": "interview",
    }
    system, user = engine._assist_prompts(profile, "", "how do you mentor engineers", "answer", "")
    assert "LEADERSHIP" in user
    assert "Dynaskills so the same PR gate stuck" in user
    assert "mentoring" in system.lower()
