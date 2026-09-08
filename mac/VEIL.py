#!/usr/bin/env python3
"""VEIL — macOS overlay copilot.

A titled HUD window excluded from screen capture
(NSWindowSharingNone + content protection). Menu bar extra + floating window.
Does not join Zoom, Meet, or Teams.
"""

from __future__ import annotations

import sys

if sys.platform != "darwin":
    sys.stderr.write("VEIL is a macOS overlay. Open it on a Mac.\n")
    sys.exit(1)

import threading
import time

from AppKit import (
    NSApp,
    NSApplication,
    NSApplicationActivationPolicyRegular,
    NSAppearance,
    NSBackingStoreBuffered,
    NSButton,
    NSColor,
    NSEvent,
    NSFloatingWindowLevel,
    NSFont,
    NSImage,
    NSMakeRect,
    NSMenu,
    NSMenuItem,
    NSScreen,
    NSScrollView,
    NSStatusBar,
    NSTextField,
    NSTextView,
    NSVariableStatusItemLength,
    NSView,
    NSVisualEffectBlendingModeBehindWindow,
    NSVisualEffectMaterialHUDWindow,
    NSVisualEffectStateActive,
    NSVisualEffectView,
    NSWindow,
    NSWindowCollectionBehaviorCanJoinAllSpaces,
    NSWindowCollectionBehaviorFullScreenAuxiliary,
    NSWindowCollectionBehaviorStationary,
    NSWindowSharingNone,
    NSWindowSharingReadOnly,
    NSWindowStyleMaskClosable,
    NSWindowStyleMaskTitled,
)
from Foundation import NSObject
from PyObjCTools import AppHelper

import engine

W, H = 420, 580
CHROME = 44
FOOTER = 52


def rgba(r, g, b, a=1.0):
    return NSColor.colorWithCalibratedRed_green_blue_alpha_(r, g, b, a)


COL_BG = rgba(0.035, 0.035, 0.043, 0.92)
COL_CARD = rgba(0.075, 0.075, 0.086, 0.94)
COL_TEXT = rgba(0.953, 0.949, 0.933)
COL_MUTED = rgba(0.545, 0.545, 0.525)
COL_SAGE = rgba(0.561, 0.686, 0.612)
COL_LINE = rgba(0.953, 0.949, 0.933, 0.10)
COL_RED = rgba(0.816, 0.439, 0.439)


def font(size, medium=False):
    if medium:
        return NSFont.systemFontOfSize_weight_(size, 0.3)
    return NSFont.systemFontOfSize_(size)


def label(text, frame, size=12, muted=False, medium=False):
    f = NSTextField.alloc().initWithFrame_(frame)
    f.setStringValue_(text)
    f.setBezeled_(False)
    f.setDrawsBackground_(False)
    f.setEditable_(False)
    f.setSelectable_(False)
    f.setFont_(font(size, medium=medium))
    f.setTextColor_(COL_MUTED if muted else COL_TEXT)
    f.setBackgroundColor_(NSColor.clearColor())
    return f


def field(frame, placeholder=""):
    f = NSTextField.alloc().initWithFrame_(frame)
    f.setPlaceholderString_(placeholder)
    f.setBezeled_(True)
    f.setBezelStyle_(1)
    f.setDrawsBackground_(True)
    f.setBackgroundColor_(COL_CARD)
    f.setTextColor_(COL_TEXT)
    f.setFont_(font(13))
    f.setFocusRingType_(1)
    return f


def pill(title, frame, target, action, kind="ghost"):
    b = NSButton.alloc().initWithFrame_(frame)
    b.setTitle_(title)
    b.setBordered_(False)
    b.setWantsLayer_(True)
    b.layer().setCornerRadius_(14)
    if kind == "sage":
        b.layer().setBackgroundColor_(rgba(0.561, 0.686, 0.612, 0.18).CGColor())
    elif kind == "danger":
        b.layer().setBackgroundColor_(rgba(0.816, 0.439, 0.439, 0.16).CGColor())
    else:
        b.layer().setBackgroundColor_(COL_CARD.CGColor())
    color = COL_SAGE if kind == "sage" else COL_RED if kind == "danger" else COL_TEXT
    attr = {
        "NSFont": font(12, medium=True),
        "NSColor": color,
    }
    from Foundation import NSAttributedString

    b.setAttributedTitle_(NSAttributedString.alloc().initWithString_attributes_(title, attr))
    b.setTarget_(target)
    b.setAction_(action.decode() if isinstance(action, bytes) else action)
    return b


def veil_status_image():
    try:
        img = NSImage.imageWithSystemSymbolName_accessibilityDescription_("eye.slash", "VEIL")
        if img is not None:
            img.setTemplate_(True)
            return img
    except Exception:
        pass
    return None


class OverlayPanel(NSWindow):
    def canBecomeKeyWindow(self):
        return True

    def canBecomeMainWindow(self):
        return True


class VeilApp(NSObject):
    def start(self):
        self.profile = engine.load_profile()
        self.stealth = True
        self.phase = "setup"
        self.transcript = []
        self.mock_i = 0
        self.status = "idle"
        self.result = None
        self.error = None
        self._build_panel()
        self._build_status_item()
        self._bind_keys()
        self.show_setup()
        self.panel.makeKeyAndOrderFront_(None)
        self.panel.orderFrontRegardless()
        NSApp.activateIgnoringOtherApps_(True)
        self.apply_stealth()
        print("VEIL window is open (top-right). Menu bar extra reads VEIL.", flush=True)

    def _build_panel(self):
        screen = NSScreen.mainScreen().visibleFrame()
        x = screen.origin.x + screen.size.width - W - 24
        y = screen.origin.y + screen.size.height - H - 24
        style = NSWindowStyleMaskTitled | NSWindowStyleMaskClosable
        panel = OverlayPanel.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(x, y, W, H),
            style,
            NSBackingStoreBuffered,
            False,
        )
        panel.setLevel_(NSFloatingWindowLevel)
        panel.setOpaque_(False)
        panel.setBackgroundColor_(NSColor.clearColor())
        panel.setHasShadow_(True)
        panel.setMovableByWindowBackground_(True)
        panel.setHidesOnDeactivate_(False)
        panel.setTitle_("VEIL")
        panel.setReleasedWhenClosed_(False)
        panel.setCollectionBehavior_(
            NSWindowCollectionBehaviorCanJoinAllSpaces
            | NSWindowCollectionBehaviorStationary
            | NSWindowCollectionBehaviorFullScreenAuxiliary
        )
        panel.setAppearance_(NSAppearance.appearanceNamed_("NSAppearanceNameDarkAqua"))

        fx = NSVisualEffectView.alloc().initWithFrame_(NSMakeRect(0, 0, W, H))
        fx.setMaterial_(NSVisualEffectMaterialHUDWindow)
        fx.setBlendingMode_(NSVisualEffectBlendingModeBehindWindow)
        fx.setState_(NSVisualEffectStateActive)
        fx.setWantsLayer_(True)
        panel.setContentView_(fx)

        self.panel = panel
        self.root = fx
        self.body = NSView.alloc().initWithFrame_(NSMakeRect(0, 0, W, H))
        fx.addSubview_(self.body)

    def _clear_body(self):
        for v in list(self.body.subviews()):
            v.removeFromSuperview()

    def _chrome(self, title, stealth_kind):
        bar = NSView.alloc().initWithFrame_(NSMakeRect(0, H - CHROME, W, CHROME))
        bar.setWantsLayer_(True)
        bar.layer().setBackgroundColor_(rgba(0.07, 0.07, 0.08, 0.5).CGColor())
        self.body.addSubview_(bar)
        self.body.addSubview_(label(title, NSMakeRect(14, H - 34, 210, 20), 12, muted=True, medium=True))
        self.stealth_btn = pill(
            "Stealth" if self.stealth else "Visible",
            NSMakeRect(W - 188, H - 36, 78, 28),
            self,
            b"toggleStealth:",
            "sage" if self.stealth else "ghost",
        )
        self.body.addSubview_(self.stealth_btn)
        self.body.addSubview_(
            pill("Hide", NSMakeRect(W - 102, H - 36, 44, 28), self, b"hideOverlay:", "ghost")
        )
        self.body.addSubview_(
            pill("End", NSMakeRect(W - 52, H - 36, 38, 28), self, b"endRoom:", "danger")
        )

    def show_setup(self):
        self.phase = "setup"
        self._clear_body()
        self.body.addSubview_(label("VEIL", NSMakeRect(20, H - 56, 200, 28), 22, medium=True))
        self.body.addSubview_(
            label(
                "Mac overlay. Excluded from their screen share.",
                NSMakeRect(20, H - 82, 380, 20),
                12,
                muted=True,
            )
        )
        y = H - 130
        self.body.addSubview_(label("Your name", NSMakeRect(20, y, 180, 16), 11, muted=True))
        self.name_field = field(NSMakeRect(20, y - 32, 180, 28), "Name")
        self.name_field.setStringValue_(self.profile.get("displayName", ""))
        self.body.addSubview_(self.name_field)
        self.body.addSubview_(label("Role", NSMakeRect(216, y, 180, 16), 11, muted=True))
        self.role_field = field(NSMakeRect(216, y - 32, 184, 28), "Role")
        self.role_field.setStringValue_(self.profile.get("role", ""))
        self.body.addSubview_(self.role_field)

        y -= 78
        self.body.addSubview_(label("Mode", NSMakeRect(20, y, 180, 16), 11, muted=True))
        self.mode_btns = {}
        x = 20
        for m, title in (("interview", "Interview"), ("sales", "Sales"), ("meeting", "Meeting")):
            kind = "sage" if self.profile.get("mode") == m else "ghost"
            b = pill(title, NSMakeRect(x, y - 32, 118, 28), self, b"pickMode:", kind)
            b.setTag_({"interview": 1, "sales": 2, "meeting": 3}[m])
            self.body.addSubview_(b)
            self.mode_btns[m] = b
            x += 126

        y -= 78
        self.body.addSubview_(label("Resume / playbook", NSMakeRect(20, y, 380, 16), 11, muted=True))
        self.resume_field = self._multiline(NSMakeRect(20, 168, 380, y - 20 - 168), self.profile.get("resume", ""))
        self.body.addSubview_(self.resume_field["scroll"])

        self.body.addSubview_(label("Job or meeting context", NSMakeRect(20, 148, 380, 16), 11, muted=True))
        self.job_field = self._multiline(NSMakeRect(20, 64, 380, 80), self.profile.get("jobDescription", ""))
        self.body.addSubview_(self.job_field["scroll"])

        self.body.addSubview_(
            pill("Launch overlay", NSMakeRect(20, 18, 160, 32), self, b"launch:", "sage")
        )
        self.body.addSubview_(
            pill("Settings", NSMakeRect(190, 18, 90, 32), self, b"showSettings:", "ghost")
        )

    def _multiline(self, frame, text):
        scroll = NSScrollView.alloc().initWithFrame_(frame)
        scroll.setHasVerticalScroller_(True)
        scroll.setBorderType_(1)
        scroll.setDrawsBackground_(True)
        scroll.setBackgroundColor_(COL_CARD)
        tv = NSTextView.alloc().initWithFrame_(scroll.contentView().bounds())
        tv.setString_(text)
        tv.setFont_(font(12))
        tv.setTextColor_(COL_TEXT)
        tv.setBackgroundColor_(COL_CARD)
        tv.setAutomaticQuoteSubstitutionEnabled_(False)
        scroll.setDocumentView_(tv)
        return {"scroll": scroll, "tv": tv}

    def show_live(self):
        self.phase = "live"
        self._clear_body()
        title = engine.MODE_COPY.get(self.profile.get("mode", "interview"), "VEIL")
        self._chrome(title, "sage")

        self.body.addSubview_(
            pill("Assist", NSMakeRect(14, H - CHROME - 40, 70, 28), self, b"assist:", "ghost")
        )
        self.body.addSubview_(
            pill("Screen", NSMakeRect(90, H - CHROME - 40, 70, 28), self, b"screen:", "ghost")
        )
        self.body.addSubview_(
            pill("Next Q", NSMakeRect(166, H - CHROME - 40, 70, 28), self, b"nextQuestion:", "ghost")
        )

        self.prompt = field(NSMakeRect(14, H - CHROME - 84, 310, 32), "Ask, or ⌘↩")
        self.prompt.setTarget_(self)
        self.prompt.setAction_(b"assist:")
        self.body.addSubview_(self.prompt)
        self.body.addSubview_(pill("Go", NSMakeRect(332, H - CHROME - 84, 74, 32), self, b"assist:", "sage"))

        self.answer_label = label(
            "Pop this over the call. Share Meet, Zoom, or your editor — never this overlay.",
            NSMakeRect(18, FOOTER + 16, 384, H - CHROME - 120 - FOOTER),
            13,
            muted=True,
        )
        self.answer_label.setSelectable_(True)
        self.answer_scroll = NSScrollView.alloc().initWithFrame_(
            NSMakeRect(14, FOOTER + 12, 392, H - CHROME - 108 - FOOTER)
        )
        self.answer_scroll.setHasVerticalScroller_(True)
        self.answer_scroll.setDrawsBackground_(False)
        self.answer_scroll.setBorderType_(0)
        self.answer_view = NSTextView.alloc().initWithFrame_(self.answer_scroll.contentView().bounds())
        self.answer_view.setEditable_(False)
        self.answer_view.setDrawsBackground_(False)
        self.answer_view.setTextColor_(COL_TEXT)
        self.answer_view.setFont_(font(13))
        self.answer_view.setString_(
            "Overlay is excluded from capture.\n⌘↩ assist · ⌘⇧E stealth · ⌘⇧H hide\n\nShare the meeting window, not VEIL."
        )
        self.answer_scroll.setDocumentView_(self.answer_view)
        self.body.addSubview_(self.answer_scroll)

        bar = NSView.alloc().initWithFrame_(NSMakeRect(0, 0, W, FOOTER))
        bar.setWantsLayer_(True)
        bar.layer().setBackgroundColor_(rgba(0.07, 0.07, 0.08, 0.45).CGColor())
        self.body.addSubview_(bar)
        self.body.addSubview_(
            pill("Hide overlay", NSMakeRect(14, 12, 110, 28), self, b"hideOverlay:", "ghost")
        )
        self.body.addSubview_(
            label("Menu bar extra · no dock icon", NSMakeRect(136, 16, 260, 20), 11, muted=True)
        )
        self._paint_answer()

    def show_settings(self):
        self.phase = "settings"
        self._clear_body()
        self.body.addSubview_(label("Settings", NSMakeRect(20, H - 56, 200, 28), 22, medium=True))
        cfg = engine.load_config()
        self.body.addSubview_(
            label("xAI API key (stored on this Mac only)", NSMakeRect(20, H - 100, 380, 16), 11, muted=True)
        )
        self.key_field = field(NSMakeRect(20, H - 136, 380, 32), "xai-...")
        self.key_field.setStringValue_(cfg.get("api_key", ""))
        self.body.addSubview_(self.key_field)
        self.body.addSubview_(
            label("Or VEIL API URL if you host the backend", NSMakeRect(20, H - 180, 380, 16), 11, muted=True)
        )
        self.url_field = field(NSMakeRect(20, H - 216, 380, 32), "https://…")
        self.url_field.setStringValue_(cfg.get("api_url", ""))
        self.body.addSubview_(self.url_field)
        self.body.addSubview_(
            pill("Save", NSMakeRect(20, H - 268, 90, 32), self, b"saveSettings:", "sage")
        )
        self.body.addSubview_(
            pill("Back", NSMakeRect(120, H - 268, 90, 32), self, b"backSettings:", "ghost")
        )
        self.body.addSubview_(
            label(
                "The overlay window uses macOS capture exclusion. Zoom, Meet, and Teams will not composite it when stealth is on.",
                NSMakeRect(20, 80, 380, 80),
                12,
                muted=True,
            )
        )

    def show_notes(self, notes: dict):
        self.phase = "notes"
        self._clear_body()
        self.body.addSubview_(label("Notes", NSMakeRect(20, H - 56, 200, 28), 22, medium=True))
        parts = [notes.get("summary", "")]
        if notes.get("keyPoints"):
            parts.append("Key points\n" + "\n".join(f"• {p}" for p in notes["keyPoints"]))
        if notes.get("actionItems"):
            parts.append("Actions\n" + "\n".join(f"• {p}" for p in notes["actionItems"]))
        if notes.get("followUpEmail"):
            parts.append("Follow-up\n" + notes["followUpEmail"])
        box = self._multiline(NSMakeRect(16, 64, 388, H - 140), "\n\n".join(p for p in parts if p))
        box["tv"].setEditable_(False)
        self.body.addSubview_(box["scroll"])
        self.body.addSubview_(pill("New room", NSMakeRect(20, 18, 110, 32), self, b"backSettings:", "sage"))
        self.body.addSubview_(pill("Hide", NSMakeRect(140, 18, 70, 32), self, b"hideOverlay:", "ghost"))

    def _paint_answer(self):
        if self.phase != "live":
            return
        if self.status == "thinking":
            self.answer_view.setString_("Writing a speakable answer…")
            self.answer_view.setTextColor_(COL_MUTED)
            return
        if self.status == "error":
            self.answer_view.setString_(self.error or "Could not generate an answer.")
            self.answer_view.setTextColor_(COL_RED)
            return
        if self.result:
            spoken = self.result.get("spoken", "")
            points = self.result.get("points") or []
            code = self.result.get("code") or ""
            text = spoken
            if points:
                text += "\n\n" + "\n".join(f"• {p}" for p in points)
            if code:
                text += "\n\n" + code
            self.answer_view.setString_(text)
            self.answer_view.setTextColor_(COL_TEXT)
            return
        self.answer_view.setTextColor_(COL_MUTED)
        self.answer_view.setString_(
            "Overlay is excluded from capture.\n⌘↩ assist · ⌘⇧E stealth · ⌘⇧H hide\n\nShare the meeting window, not VEIL."
        )

    def apply_stealth(self):
        if self.stealth:
            self.panel.setSharingType_(NSWindowSharingNone)
            try:
                self.panel.setContentProtection_(True)
            except Exception:
                pass
        else:
            try:
                self.panel.setContentProtection_(False)
            except Exception:
                pass
            self.panel.setSharingType_(NSWindowSharingReadOnly)
        self._refresh_status_title()

    def _refresh_status_title(self):
        # Template icon only — tooltip carries state.
        if hasattr(self, "status_item"):
            self.status_item.setToolTip_("VEIL · stealth on" if self.stealth else "VEIL · visible on share")

    def _build_status_item(self):
        bar = NSStatusBar.systemStatusBar()
        item = bar.statusItemWithLength_(NSVariableStatusItemLength)
        item.setTitle_("VEIL")
        img = veil_status_image()
        if img is not None:
            item.setImage_(img)
        item.setHighlightMode_(True)
        item.setToolTip_("VEIL overlay")
        menu = NSMenu.alloc().init()
        menu.setAutoenablesItems_(False)
        pairs = [
            ("Show overlay", "showOverlay:"),
            ("Hide overlay", "hideOverlay:"),
            (None, None),
            ("Toggle stealth", "toggleStealth:"),
            ("Next question", "nextQuestion:"),
            (None, None),
            ("Settings", "showSettings:"),
            ("Quit VEIL", "quit:"),
        ]
        for title, action in pairs:
            if title is None:
                menu.addItem_(NSMenuItem.separatorItem())
                continue
            it = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(title, action, "")
            it.setTarget_(self)
            menu.addItem_(it)
        item.setMenu_(menu)
        self.status_item = item

    def _bind_keys(self):
        # Local only — a global monitor prompts Accessibility and can hang
        # a script with no app bundle.
        mask = 1 << 10  # NSEventMaskKeyDown

        def local_handler(event):
            self._handle_key(event)
            return event

        NSEvent.addLocalMonitorForEventsMatchingMask_handler_(mask, local_handler)

    def _handle_key(self, event):
        flags = int(event.modifierFlags())
        cmd = bool(flags & (1 << 20))  # NSEventModifierFlagCommand
        shift = bool(flags & (1 << 17))
        chars = event.charactersIgnoringModifiers() or ""
        if not cmd:
            return
        if chars == "\r" and self.phase == "live":
            self.assist_(None)
        if shift and chars.lower() == "e":
            self.toggleStealth_(None)
        if shift and chars.lower() == "h":
            self.hideOverlay_(None)
        if shift and chars.lower() == "s" and self.phase == "live":
            self.screen_(None)

    def pickMode_(self, sender):
        tag = int(sender.tag())
        mode = {1: "interview", 2: "sales", 3: "meeting"}.get(tag, "interview")
        self.profile["mode"] = mode
        self.show_setup()

    def launch_(self, sender):
        self.profile["displayName"] = str(self.name_field.stringValue())
        self.profile["role"] = str(self.role_field.stringValue())
        self.profile["resume"] = str(self.resume_field["tv"].string())
        self.profile["jobDescription"] = str(self.job_field["tv"].string())
        engine.save_profile(self.profile)
        self.transcript = []
        self.mock_i = 0
        self.status = "idle"
        self.result = None
        self.error = None
        self.started = time.time()
        self.show_live()

    def showSettings_(self, sender):
        self.show_settings()

    def saveSettings_(self, sender):
        engine.save_config(
            {
                "api_key": str(self.key_field.stringValue()).strip(),
                "api_url": str(self.url_field.stringValue()).strip(),
            }
        )
        self.show_setup()

    def backSettings_(self, sender):
        self.show_setup()

    def showOverlay_(self, sender):
        self.panel.orderFrontRegardless()

    def hideOverlay_(self, sender):
        self.panel.orderOut_(None)

    def toggleStealth_(self, sender):
        self.stealth = not self.stealth
        self.apply_stealth()
        if self.phase == "live":
            self.show_live()

    def quit_(self, sender):
        NSApp.terminate_(None)

    def assist_(self, sender):
        if self.phase != "live":
            return
        q = str(self.prompt.stringValue())
        self._run("answer", q, "")

    def screen_(self, sender):
        if self.phase != "live":
            return
        self._run("screen", str(self.prompt.stringValue()), engine.SCREEN_FALLBACK)

    def nextQuestion_(self, sender):
        if self.phase != "live":
            return
        mode = self.profile.get("mode", "interview")
        qs = engine.MOCK_QUESTIONS[mode]
        q = qs[self.mock_i % len(qs)]
        self.mock_i += 1
        self.transcript.append(f"them: {q}")
        self.prompt.setStringValue_(q)
        self._run("answer", q, "")

    def _run(self, kind, question, screen_text):
        if self.status == "thinking":
            return
        self.status = "thinking"
        self.error = None
        self._paint_answer()
        packed = "\n".join(self.transcript)
        profile = dict(self.profile)

        def work():
            res = engine.assist(profile, packed, question, kind, screen_text)

            def done():
                if res.get("ok"):
                    self.status = "ready"
                    self.result = res.get("result") or {}
                    self.error = None
                    self.prompt.setStringValue_("")
                else:
                    self.status = "error"
                    self.error = res.get("error") or "Could not generate an answer."
                self._paint_answer()

            AppHelper.callAfter(done)

        threading.Thread(target=work, daemon=True).start()

    def endRoom_(self, sender):
        if self.phase == "setup":
            self.hideOverlay_(None)
            return
        packed = "\n".join(self.transcript)
        self.status = "thinking"
        profile = dict(self.profile)

        def work():
            res = engine.notes(profile, packed)

            def done():
                notes = {
                    "summary": "Room ended.",
                    "keyPoints": [],
                    "questions": [],
                    "actionItems": [],
                    "followUpEmail": "",
                }
                if res.get("ok"):
                    notes = res.get("notes") or notes
                engine.save_session(
                    {
                        "title": engine.MODE_COPY.get(profile.get("mode", "interview"), "VEIL"),
                        "mode": profile.get("mode"),
                        "startedAt": int(getattr(self, "started", time.time()) * 1000),
                        "durationSec": int(time.time() - getattr(self, "started", time.time())),
                        "transcript": list(self.transcript),
                        "notes": notes,
                    }
                )
                self.show_notes(notes)

            AppHelper.callAfter(done)

        threading.Thread(target=work, daemon=True).start()


def main():
    import signal
    import traceback

    print("Starting VEIL…", flush=True)
    try:
        app = NSApplication.sharedApplication()
        app.setActivationPolicy_(NSApplicationActivationPolicyRegular)
        app.setAppearance_(NSAppearance.appearanceNamed_("NSAppearanceNameDarkAqua"))
        delegate = VeilApp.alloc().init()
        app.setDelegate_(delegate)
        delegate.start()
        print("This terminal stays busy while VEIL runs. Ctrl+C quits.", flush=True)
        signal.signal(signal.SIGINT, lambda *_: NSApp.terminate_(None))
        AppHelper.runEventLoop()
    except KeyboardInterrupt:
        print("\nQuitting VEIL.", flush=True)
    except Exception:
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
