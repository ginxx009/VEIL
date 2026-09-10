"""Live interview listening via macOS Speech + AVAudioEngine."""

from __future__ import annotations

import threading
import time

from Foundation import NSLocale
from PyObjCTools import AppHelper

try:
    from AVFoundation import AVAudioEngine, AVCaptureDevice, AVMediaTypeAudio
    from Speech import SFSpeechAudioBufferRecognitionRequest, SFSpeechRecognizer
except ImportError as e:  # pragma: no cover
    AVAudioEngine = None
    _IMPORT_ERROR = e
else:
    _IMPORT_ERROR = None

# Pause after the last partial before we treat it as a finished question.
UTTERANCE_PAUSE = 1.55


def _host():
    import sys

    return "VEIL" if getattr(sys, "frozen", False) else "Terminal / VEIL"


def prime_permissions():
    """Pop the macOS Mic + Speech dialogs on first launch (required for a shipped .app)."""
    if _IMPORT_ERROR is not None:
        print(f"VEIL: cannot prime permissions ({_IMPORT_ERROR})", flush=True)
        return
    print("VEIL: requesting Speech + Microphone permission…", flush=True)

    def after_speech(status):
        print(f"VEIL: speech auth status={status!r}", flush=True)
        media = AVMediaTypeAudio if AVMediaTypeAudio else "soun"
        AVCaptureDevice.requestAccessForMediaType_completionHandler_(
            media, lambda ok: print(f"VEIL: mic auth ok={ok!r}", flush=True)
        )

    try:
        SFSpeechRecognizer.requestAuthorization_(after_speech)
    except Exception as e:
        print(f"VEIL: permission request failed: {e}", flush=True)


def _main(fn):
    AppHelper.callAfter(fn)


class Listener:
    def __init__(self, on_partial, on_final, on_error, hints=None):
        self.on_partial = on_partial
        self.on_final = on_final
        self.on_error = on_error
        self.hints = [str(h) for h in (hints or []) if str(h).strip()]
        self.running = False
        self._engine = None
        self._request = None
        self._task = None
        self._recognizer = None
        self._tap = None
        self._handler = None
        self._last_final = ""
        self._partial = ""
        self._timer = None
        self._lock = threading.Lock()
        self._got_audio = False
        self._auth_done = False
        self._gen = 0

    def start(self):
        if _IMPORT_ERROR is not None:
            self.on_error(
                "Speech frameworks missing. In the venv run: pip install pyobjc-framework-Speech pyobjc-framework-AVFoundation"
            )
            return
        if self.running:
            return
        print("VEIL: requesting Speech + Microphone permission…", flush=True)

        def watchdog():
            time.sleep(7)
            if not self._auth_done:
                _main(
                    lambda: self.on_error(
                        "macOS did not grant Speech Recognition. System Settings → Privacy & Security → Speech Recognition — enable VEIL."
                    )
                )
                return
            if self.running and not self._got_audio:
                print("VEIL: still listening, but no speech yet. Use speakers.", flush=True)
                _main(
                    lambda: self.on_partial(
                        "Waiting for speech… play them on speakers, not headphones."
                    )
                )

        threading.Thread(target=watchdog, daemon=True).start()

        def after_speech(status):
            self._auth_done = True
            print(f"VEIL: speech auth status={status!r}", flush=True)
            try:
                code = int(status)
            except Exception:
                code = 3 if status else 0
            if code != 3:
                _main(
                    lambda: self.on_error(
                        "Allow Speech Recognition for VEIL in System Settings → Privacy & Security."
                    )
                )
                return

            def after_mic(ok):
                print(f"VEIL: mic auth ok={ok!r}", flush=True)
                if not ok:
                    _main(
                        lambda: self.on_error(
                            "Allow Microphone for VEIL in System Settings → Privacy & Security."
                        )
                    )
                    return
                _main(self._begin)

            media = AVMediaTypeAudio if AVMediaTypeAudio else "soun"
            AVCaptureDevice.requestAccessForMediaType_completionHandler_(media, after_mic)

        SFSpeechRecognizer.requestAuthorization_(after_speech)

    def stop(self):
        self.running = False
        with self._lock:
            if self._timer is not None:
                self._timer.cancel()
                self._timer = None
        try:
            if self._task is not None:
                self._task.cancel()
            if self._request is not None:
                self._request.endAudio()
            if self._engine is not None:
                try:
                    self._engine.inputNode().removeTapOnBus_(0)
                except Exception:
                    pass
                self._engine.stop()
        except Exception:
            pass
        self._task = None
        self._request = None
        self._engine = None

    def _begin(self):
        locale = NSLocale.currentLocale()
        recognizer = SFSpeechRecognizer.alloc().initWithLocale_(locale)
        if recognizer is None:
            recognizer = SFSpeechRecognizer.alloc().init()
        if recognizer is None or not recognizer.isAvailable():
            self.on_error("Speech recognition is not available for this language.")
            return
        self._recognizer = recognizer
        engine = AVAudioEngine.alloc().init()
        self._engine = engine
        node = engine.inputNode()
        engine.prepare()
        fmt = node.inputFormatForBus_(0)
        if fmt is None or getattr(fmt, "sampleRate", lambda: 0)() == 0:
            fmt = node.outputFormatForBus_(0)
        print(f"VEIL: mic format={fmt}", flush=True)

        def tap(buffer, when):
            req = self._request
            if req is not None and self.running:
                req.appendAudioPCMBuffer_(buffer)

        self._tap = tap
        try:
            node.removeTapOnBus_(0)
        except Exception:
            pass
        node.installTapOnBus_bufferSize_format_block_(0, 2048, fmt, tap)
        started = engine.startAndReturnError_(None)
        if started is False:
            self.on_error("Could not start the microphone.")
            self.stop()
            return
        self.running = True
        print("VEIL: listening. Speak a question, or play it on speakers.", flush=True)
        self._start_task()

    def _start_task(self):
        if not self.running or self._recognizer is None:
            return
        self._gen += 1
        gen = self._gen
        if self._task is not None:
            try:
                self._task.cancel()
            except Exception:
                pass
        request = SFSpeechAudioBufferRecognitionRequest.alloc().init()
        request.setShouldReportPartialResults_(True)
        try:
            request.setTaskHint_(1)  # dictation
        except Exception:
            pass
        try:
            request.setAddsPunctuation_(True)
        except Exception:
            pass
        if self.hints:
            try:
                request.setContextualStrings_(self.hints[:80])
            except Exception as e:
                print(f"VEIL: speech hints skipped ({e})", flush=True)
        self._request = request

        def handler(result, error):
            if gen != self._gen or not self.running:
                return
            if error is not None:
                print(f"VEIL: speech cycle ended ({error}) — listening for the next question", flush=True)
                self._restart_soon()
                return
            if result is None:
                return
            text = str(result.bestTranscription().formattedString() or "").strip()
            if not text:
                return
            self._got_audio = True
            print(f"VEIL heard: {text}", flush=True)
            self._arm_flush(text, immediate=bool(result.isFinal()))

        self._handler = handler
        self._task = self._recognizer.recognitionTaskWithRequest_resultHandler_(request, handler)

    def _restart_soon(self):
        if not self.running:
            return

        def go():
            time.sleep(0.2)
            if self.running:
                _main(self._start_task)

        threading.Thread(target=go, daemon=True).start()

    def _arm_flush(self, text: str, immediate: bool):
        with self._lock:
            self._partial = text
            if self._timer is not None:
                self._timer.cancel()
            if immediate:
                self._timer = None
            else:
                self._timer = threading.Timer(UTTERANCE_PAUSE, self._flush)
                self._timer.daemon = True
                self._timer.start()
        _main(lambda t=text: self.on_partial(t))
        if immediate:
            self._flush()

    def _flush(self):
        with self._lock:
            text = (self._partial or "").strip()
            self._partial = ""
            if self._timer is not None:
                self._timer.cancel()
                self._timer = None
        if not text:
            return
        _main(lambda t=text: self._emit_final(t))

    def _emit_final(self, text: str):
        if text == self._last_final:
            return
        self._last_final = text
        print(f"VEIL question: {text}", flush=True)
        self.on_final(text)
        if self.running:
            self._restart_soon()

    def flush_now(self):
        """Treat whatever was just heard as the last question, then the caller can stop."""
        with self._lock:
            text = (self._partial or "").strip()
            self._partial = ""
            if self._timer is not None:
                self._timer.cancel()
                self._timer = None
        if text:
            self._emit_final(text)
