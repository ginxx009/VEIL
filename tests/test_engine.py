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
    assert "Do NOT add a personal example" in system
    blob = (system + user).lower()
    assert "draw.io" in blob  # the prohibition mentions it
    assert "no extra example" in user.lower()


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
