"""Windows listener — record until a pause, then transcribe."""

from __future__ import annotations

import io
import threading
import time
import wave

UTTERANCE_PAUSE = 1.15


def _main(fn):
    fn()


class Listener:
    def __init__(self, on_partial, on_final, on_error):
        self.on_partial = on_partial
        self.on_final = on_final
        self.on_error = on_error
        self.running = False
        self._thread = None
        self._lock = threading.Lock()
        self._chunks: list[bytes] = []
        self._last_voice = 0.0
        self._voiced = False
        self._last_final = ""

    def start(self):
        if self.running:
            return
        self.running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.running = False

    def flush_now(self):
        self._emit_from_buffer(force=True)

    def _loop(self):
        try:
            import sounddevice as sd
        except Exception as e:
            self.on_error(f"Could not open the microphone ({e}). pip install sounddevice")
            return
        samplerate = 16000
        print("VEIL: listening (Windows).", flush=True)
        self.on_partial("Listening…")

        def callback(indata, frames, time_info, status):
            if not self.running:
                return
            pcm = bytes(indata)
            rms = _rms(indata)
            now = time.time()
            with self._lock:
                if rms > 0.012:
                    self._chunks.append(pcm)
                    self._last_voice = now
                    self._voiced = True
                elif self._voiced:
                    self._chunks.append(pcm)

        try:
            with sd.RawInputStream(
                samplerate=samplerate,
                channels=1,
                dtype="int16",
                blocksize=1600,
                callback=callback,
            ):
                while self.running:
                    time.sleep(0.15)
                    if self._voiced and (time.time() - self._last_voice) >= UTTERANCE_PAUSE:
                        self._emit_from_buffer()
        except Exception as e:
            self.on_error(f"Mic failed: {e}")

    def _emit_from_buffer(self, force=False):
        with self._lock:
            chunks = self._chunks
            self._chunks = []
            self._voiced = False
        if not chunks:
            return
        wav = _to_wav(b"".join(chunks), 16000)
        self.on_partial("Transcribing…")
        try:
            text = _transcribe(wav)
        except Exception as e:
            print(f"VEIL stt: {e}", flush=True)
            self.on_error(str(e))
            return
        text = (text or "").strip()
        if len(text) < 4:
            return
        if text == self._last_final:
            return
        self._last_final = text
        print(f"VEIL question: {text}", flush=True)
        self.on_final(text)


def _rms(indata) -> float:
    try:
        import numpy as np

        x = np.frombuffer(bytes(indata), dtype=np.int16).astype(np.float32)
        if x.size == 0:
            return 0.0
        return float((x * x).mean() ** 0.5) / 32768.0
    except Exception:
        return 0.02


def _to_wav(pcm: bytes, rate: int) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(pcm)
    return buf.getvalue()


def _transcribe(wav: bytes) -> str:
    import engine

    cfg = engine.load_config()
    key = (cfg.get("api_key") or "").strip()
    if key.startswith("sk-"):
        return _whisper(key, wav)
    return _google(wav)


def _whisper(api_key: str, wav: bytes) -> str:
    import json
    import uuid

    import urllib.request

    boundary = "----VEIL" + uuid.uuid4().hex
    filename = "clip.wav"
    parts = []
    parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"model\"\r\n\r\nwhisper-1\r\n".encode())
    parts.append(
        (
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{filename}\"\r\n"
            "Content-Type: audio/wav\r\n\r\n"
        ).encode()
        + wav
        + b"\r\n"
    )
    parts.append(f"--{boundary}--\r\n".encode())
    body = b"".join(parts)
    req = urllib.request.Request(
        "https://api.openai.com/v1/audio/transcriptions",
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=45) as res:
        data = json.loads(res.read().decode("utf-8"))
    return str(data.get("text") or "")


def _google(wav: bytes) -> str:
    try:
        import speech_recognition as sr
    except Exception:
        raise RuntimeError("Add an OpenAI sk- key for Windows listening, or pip install SpeechRecognition.")
    r = sr.Recognizer()
    audio = sr.AudioData(wav[44:], 16000, 2)
    return r.recognize_google(audio)
