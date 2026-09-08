"""Live interview listening via macOS Speech + AVAudioEngine."""

from __future__ import annotations

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


def _main(fn):
    AppHelper.callAfter(fn)


class Listener:
    def __init__(self, on_partial, on_final, on_error):
        self.on_partial = on_partial
        self.on_final = on_final
        self.on_error = on_error
        self.running = False
        self._engine = None
        self._request = None
        self._task = None
        self._recognizer = None
        self._tap = None
        self._last_final = ""

    def start(self):
        if _IMPORT_ERROR is not None:
            self.on_error(
                "Speech frameworks missing. In the venv run: pip install pyobjc-framework-Speech pyobjc-framework-AVFoundation"
            )
            return
        if self.running:
            return

        def after_speech(status):
            if int(status) != 3:  # authorized
                _main(
                    lambda: self.on_error(
                        "Allow Speech Recognition for Terminal / Python in System Settings → Privacy & Security."
                    )
                )
                return

            def after_mic(ok):
                if not ok:
                    _main(
                        lambda: self.on_error(
                            "Allow Microphone for Terminal / Python in System Settings → Privacy & Security."
                        )
                    )
                    return
                _main(self._begin)

            media = AVMediaTypeAudio if AVMediaTypeAudio else "soun"
            AVCaptureDevice.requestAccessForMediaType_completionHandler_(media, after_mic)

        SFSpeechRecognizer.requestAuthorization_(after_speech)

    def stop(self):
        self.running = False
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
        fmt = node.outputFormatForBus_(0)

        def tap(buffer, when):
            req = self._request
            if req is not None and self.running:
                req.appendAudioPCMBuffer_(buffer)

        self._tap = tap
        try:
            node.removeTapOnBus_(0)
        except Exception:
            pass
        node.installTapOnBus_bufferSize_format_block_(0, 1024, fmt, tap)
        started = engine.startAndReturnError_(None)
        if started is False:
            self.on_error("Could not start the microphone.")
            self.stop()
            return
        self.running = True
        self._start_task()

    def _start_task(self):
        if not self.running or self._recognizer is None:
            return
        request = SFSpeechAudioBufferRecognitionRequest.alloc().init()
        request.setShouldReportPartialResults_(True)
        try:
            if self._recognizer.supportsOnDeviceRecognition():
                request.setRequiresOnDeviceRecognition_(True)
        except Exception:
            pass
        self._request = request

        def handler(result, error):
            if not self.running:
                return
            if error is not None:
                # Apple caps a request around a minute — just roll a new one.
                _main(self._start_task)
                return
            if result is None:
                return
            text = str(result.bestTranscription().formattedString() or "").strip()
            if not text:
                return
            if result.isFinal():
                _main(lambda t=text: self._emit_final(t))
                _main(self._start_task)
            else:
                _main(lambda t=text: self.on_partial(t))

        self._task = self._recognizer.recognitionTaskWithRequest_resultHandler_(request, handler)

    def _emit_final(self, text: str):
        if text == self._last_final:
            return
        self._last_final = text
        self.on_final(text)
