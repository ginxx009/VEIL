"""Windows listener helpers — no sound device required."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "windows"))

import listen  # noqa: E402


def test_wav_header_and_payload():
    pcm = b"\x00\x00" * 16
    wav = listen._to_wav(pcm, 16000)
    assert wav[:4] == b"RIFF"
    assert b"WAVE" in wav[:12]
    assert wav.endswith(pcm)
    assert len(wav) > len(pcm)
