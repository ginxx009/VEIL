#!/usr/bin/env python3
"""VEIL — macOS overlay copilot.

HUD window excluded from screen capture (NSWindowSharingNone).
PyObjC 12 only allows ObjC-style methods on NSObject, so UI lives on a
plain Python class and buttons target a thin action object.
"""

from __future__ import annotations

import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    sys.path.insert(0, sys._MEIPASS)

if sys.platform != "darwin":
    sys.stderr.write("This is the macOS overlay. On Windows run windows/VEIL.py\n")
    sys.exit(1)

import signal
import threading
import time
import traceback

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
    NSOpenPanel,
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
from Foundation import NSAttributedString, NSObject
from PyObjCTools import AppHelper

import engine
import listen

W, H = 420, 680
CHROME = 44
FOOTER = 52


def rgba(r, g, b, a=1.0):
    return NSColor.colorWithCalibratedRed_green_blue_alpha_(r, g, b, a)


COL_CARD = rgba(0.075, 0.075, 0.086, 0.94)
COL_TEXT = rgba(0.953, 0.949, 0.933)
COL_MUTED = rgba(0.545, 0.545, 0.525)
COL_SAGE = rgba(0.561, 0.686, 0.612)
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
    b.setAttributedTitle_(
        NSAttributedString.alloc().initWithString_attributes_(
            title, {"NSFont": font(12, medium=True), "NSColor": color}
        )
    )
    b.setTarget_(target)
    b.setAction_(action)
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


def multiline(frame, text):
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


class OverlayPanel(NSWindow):
    def canBecomeKeyWindow(self):
        return True

    def canBecomeMainWindow(self):
        return True


class Actions(NSObject):
    """ObjC target only. Every method is a selector ending in _."""

    hud = None

    def pickMode_(self, sender):
        self.hud.pick_mode(int(sender.tag()))

    def launch_(self, sender):
        self.hud.launch()

    def showSettings_(self, sender):
        self.hud.show_settings()

    def saveSettings_(self, sender):
        self.hud.save_settings()

    def backSettings_(self, sender):
        self.hud.show_setup()

    def showOverlay_(self, sender):
        self.hud.show_overlay()

    def hideOverlay_(self, sender):
        self.hud.hide_overlay()

    def toggleStealth_(self, sender):
        self.hud.toggle_stealth()

    def quit_(self, sender):
        NSApp.terminate_(None)

    def assist_(self, sender):
        self.hud.assist()

    def screen_(self, sender):
        self.hud.screen()

    def nextQuestion_(self, sender):
        self.hud.next_question()

    def endRoom_(self, sender):
        self.hud.end_room()

    def toggleMic_(self, sender):
        self.hud.toggle_mic()

    def importResume_(self, sender):
        self.hud.import_resume()

    def loadBriefing_(self, sender):
        self.hud.load_briefing()


class HUD:
    def __init__(self, actions: Actions):
        self.actions = actions
        self.profile = engine.load_profile()
        self.stealth = True
        self.phase = "setup"
        self.transcript = []
        self.mock_i = 0
        self.status = "idle"
        self.result = None
        self.error = None
        self.started = time.time()
        self.listening = False
        self.hearing = ""
        self.listener = None
        self.pending_q = None
        self.pending_kind = None
        self.anchor_q = ""
        self.anchor_a = ""
        self.followups = []
        self.follow_q = ""
        self.draft_follow = ""

    def boot(self):
        self._build_panel()
        self._build_status_item()
        self._bind_keys()
        self.show_setup()
        self.panel.makeKeyAndOrderFront_(None)
        self.panel.orderFrontRegardless()
        NSApp.activateIgnoringOtherApps_(True)
        self.apply_stealth()
        try:
            listen.prime_permissions()
        except Exception as e:
            print(f"VEIL: permission prime failed: {e}", flush=True)
        print("VEIL window is open (top-right). Menu bar extra reads VEIL.", flush=True)

    def _build_panel(self):
        screen = NSScreen.mainScreen().visibleFrame()
        x = screen.origin.x + screen.size.width - W - 24
        y = screen.origin.y + screen.size.height - H - 24
        panel = OverlayPanel.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(x, y, W, H),
            NSWindowStyleMaskTitled | NSWindowStyleMaskClosable,
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
        self.body = NSView.alloc().initWithFrame_(NSMakeRect(0, 0, W, H))
        fx.addSubview_(self.body)

    def _clear_body(self):
        for v in list(self.body.subviews()):
            v.removeFromSuperview()

    def _chrome(self, title):
        bar = NSView.alloc().initWithFrame_(NSMakeRect(0, H - CHROME, W, CHROME))
        bar.setWantsLayer_(True)
        bar.layer().setBackgroundColor_(rgba(0.07, 0.07, 0.08, 0.5).CGColor())
        self.body.addSubview_(bar)
        self.body.addSubview_(label(title, NSMakeRect(14, H - 34, 210, 20), 12, muted=True, medium=True))
        a = self.actions
        self.body.addSubview_(
            pill(
                "Stealth" if self.stealth else "Visible",
                NSMakeRect(W - 188, H - 36, 78, 28),
                a,
                "toggleStealth:",
                "sage" if self.stealth else "ghost",
            )
        )
        self.body.addSubview_(pill("Hide", NSMakeRect(W - 102, H - 36, 44, 28), a, "hideOverlay:", "ghost"))
        self.body.addSubview_(pill("End", NSMakeRect(W - 52, H - 36, 38, 28), a, "endRoom:", "danger"))

    def show_setup(self):
        self.phase = "setup"
        self._clear_body()
        a = self.actions
        self.body.addSubview_(label("VEIL", NSMakeRect(20, H - 56, 200, 28), 22, medium=True))
        self.body.addSubview_(
            label("Mac overlay. Excluded from their screen share.", NSMakeRect(20, H - 82, 380, 20), 12, muted=True)
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
        x = 20
        for m, title in (("interview", "Interview"), ("sales", "Sales"), ("meeting", "Meeting")):
            kind = "sage" if self.profile.get("mode") == m else "ghost"
            b = pill(title, NSMakeRect(x, y - 32, 118, 28), a, "pickMode:", kind)
            b.setTag_({"interview": 1, "sales": 2, "meeting": 3}[m])
            self.body.addSubview_(b)
            x += 126

        y -= 78
        self.body.addSubview_(label("Resume / playbook", NSMakeRect(20, y, 240, 16), 11, muted=True))
        self.body.addSubview_(pill("Import file", NSMakeRect(268, y - 4, 112, 24), a, "importResume:", "ghost"))
        self.resume_field = multiline(NSMakeRect(20, 268, 380, y - 20 - 268), self.profile.get("resume", ""))
        self.body.addSubview_(self.resume_field["scroll"])
        self.body.addSubview_(label("Job or meeting context", NSMakeRect(20, 248, 380, 16), 11, muted=True))
        self.job_field = multiline(NSMakeRect(20, 210, 380, 36), self.profile.get("jobDescription", ""))
        self.body.addSubview_(self.job_field["scroll"])
        self.body.addSubview_(
            label(
                "Agentic facts — years, Cursor CLI, Claude Code, Dynaskills. Not a product.",
                NSMakeRect(20, 190, 380, 16),
                11,
                muted=True,
            )
        )
        self.agentic_field = multiline(NSMakeRect(20, 136, 380, 52), self.profile.get("agenticFacts", ""))
        self.body.addSubview_(self.agentic_field["scroll"])
        self.body.addSubview_(
            label(
                "Products / projects — name, what it is, architecture, alternative, how it scales.",
                NSMakeRect(20, 116, 380, 16),
                11,
                muted=True,
            )
        )
        self.projects_field = multiline(NSMakeRect(20, 54, 380, 60), self.profile.get("projects", ""))
        self.body.addSubview_(self.projects_field["scroll"])
        self.body.addSubview_(pill("Launch overlay", NSMakeRect(20, 18, 160, 32), a, "launch:", "sage"))
        self.body.addSubview_(pill("Load briefing", NSMakeRect(190, 18, 120, 32), a, "loadBriefing:", "ghost"))
        self.body.addSubview_(pill("Settings", NSMakeRect(320, 18, 80, 32), a, "showSettings:", "ghost"))

    def show_live(self):
        self.phase = "live"
        self._clear_body()
        a = self.actions
        title = engine.MODE_COPY.get(self.profile.get("mode", "interview"), "VEIL")
        self._chrome(title)
        self.body.addSubview_(pill("Assist", NSMakeRect(14, H - CHROME - 40, 64, 28), a, "assist:", "ghost"))
        self.body.addSubview_(pill("Screen", NSMakeRect(84, H - CHROME - 40, 64, 28), a, "screen:", "ghost"))
        self.body.addSubview_(pill("Next Q", NSMakeRect(154, H - CHROME - 40, 64, 28), a, "nextQuestion:", "ghost"))
        self.body.addSubview_(
            pill(
                "Listening" if self.listening else "Mic",
                NSMakeRect(224, H - CHROME - 40, 88, 28),
                a,
                "toggleMic:",
                "sage" if self.listening else "ghost",
            )
        )
        self.prompt = field(NSMakeRect(14, H - CHROME - 84, 310, 32), "Ask, or ⌘↩")
        self.prompt.setTarget_(a)
        self.prompt.setAction_("assist:")
        self.body.addSubview_(self.prompt)
        self.body.addSubview_(pill("Go", NSMakeRect(332, H - CHROME - 84, 74, 32), a, "assist:", "sage"))

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
        self.answer_scroll.setDocumentView_(self.answer_view)
        self.body.addSubview_(self.answer_scroll)

        bar = NSView.alloc().initWithFrame_(NSMakeRect(0, 0, W, FOOTER))
        bar.setWantsLayer_(True)
        bar.layer().setBackgroundColor_(rgba(0.07, 0.07, 0.08, 0.45).CGColor())
        self.body.addSubview_(bar)
        self.body.addSubview_(pill("Hide overlay", NSMakeRect(14, 12, 110, 28), a, "hideOverlay:", "ghost"))
        self.body.addSubview_(
            label(
                "Speakers on — headphones hide their voice from the mic" if self.listening else "Share Meet / Zoom / editor — not this window",
                NSMakeRect(136, 16, 260, 20),
                11,
                muted=True,
            )
        )
        self._paint_answer()

    def show_settings(self):
        self.phase = "settings"
        self._clear_body()
        a = self.actions
        cfg = engine.load_config()
        self.body.addSubview_(label("Settings", NSMakeRect(20, H - 56, 200, 28), 22, medium=True))
        self.body.addSubview_(
            label("API key — OpenAI (sk-…). Stored on this Mac only.", NSMakeRect(20, H - 100, 380, 16), 11, muted=True)
        )
        self.key_field = field(NSMakeRect(20, H - 136, 380, 32), "sk-…")
        self.key_field.setStringValue_(cfg.get("api_key", ""))
        self.body.addSubview_(self.key_field)
        self.body.addSubview_(
            label("Or VEIL API URL if you host the backend", NSMakeRect(20, H - 180, 380, 16), 11, muted=True)
        )
        self.url_field = field(NSMakeRect(20, H - 216, 380, 32), "https://…")
        self.url_field.setStringValue_(cfg.get("api_url", ""))
        self.body.addSubview_(self.url_field)
        self.body.addSubview_(pill("Save", NSMakeRect(20, H - 268, 90, 32), a, "saveSettings:", "sage"))
        self.body.addSubview_(pill("Back", NSMakeRect(120, H - 268, 90, 32), a, "backSettings:", "ghost"))
        self.body.addSubview_(
            label(
                "The overlay uses macOS capture exclusion. Zoom, Meet, and Teams will not composite it when stealth is on.",
                NSMakeRect(20, 80, 380, 80),
                12,
                muted=True,
            )
        )

    def show_notes(self, notes: dict):
        self.phase = "notes"
        self._clear_body()
        a = self.actions
        self.body.addSubview_(label("Notes", NSMakeRect(20, H - 56, 200, 28), 22, medium=True))
        parts = [notes.get("summary", "")]
        if notes.get("keyPoints"):
            parts.append("Key points\n" + "\n".join(f"• {p}" for p in notes["keyPoints"]))
        if notes.get("actionItems"):
            parts.append("Actions\n" + "\n".join(f"• {p}" for p in notes["actionItems"]))
        if notes.get("followUpEmail"):
            parts.append("Follow-up\n" + notes["followUpEmail"])
        box = multiline(NSMakeRect(16, 64, 388, H - 140), "\n\n".join(p for p in parts if p))
        box["tv"].setEditable_(False)
        self.body.addSubview_(box["scroll"])
        self.body.addSubview_(pill("New room", NSMakeRect(20, 18, 110, 32), a, "backSettings:", "sage"))
        self.body.addSubview_(pill("Hide", NSMakeRect(140, 18, 70, 32), a, "hideOverlay:", "ghost"))

    def _paint_answer(self):
        if self.phase != "live":
            return
        spoken = ""
        if self.result:
            spoken = self.result.get("spoken") or ""
            points = self.result.get("points") or []
            code = self.result.get("code") or ""
            if points:
                spoken = spoken + "\n\n" + "\n".join(f"• {p}" for p in points)
            if code:
                spoken = spoken + "\n\n" + code
        if spoken:
            self.answer_view.setString_(spoken)
            self.answer_view.setTextColor_(COL_TEXT)
            return
        if self.status == "error":
            self.answer_view.setString_(self.error or "Could not generate an answer.")
            self.answer_view.setTextColor_(COL_RED)
            return
        if self.status == "thinking":
            held = self._compose_board()
            msg = (held + "\n\nAdding…") if held else "Writing a speakable answer…"
            self.answer_view.setString_(msg)
            self.answer_view.setTextColor_(COL_MUTED if not held else COL_TEXT)
            return
        if self.listening and self.hearing:
            self.answer_view.setTextColor_(COL_MUTED)
            self.answer_view.setString_("Hearing…\n" + self.hearing)
            return
        if self.listening:
            self.answer_view.setTextColor_(COL_MUTED)
            self.answer_view.setString_(
                "Listening continuously. Leave Mic on.\nPlay them on speakers. Click Mic only to stop."
            )
            return
        self.answer_view.setTextColor_(COL_MUTED)
        self.answer_view.setString_(
            "Mic stays on across questions. ⌘⇧M to start/stop · ⌘↩ assist"
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
        if hasattr(self, "status_item"):
            self.status_item.setToolTip_("VEIL · stealth on" if self.stealth else "VEIL · visible on share")

    def _build_status_item(self):
        item = NSStatusBar.systemStatusBar().statusItemWithLength_(NSVariableStatusItemLength)
        item.setTitle_("VEIL")
        img = veil_status_image()
        if img is not None:
            item.setImage_(img)
        item.setHighlightMode_(True)
        item.setToolTip_("VEIL overlay")
        menu = NSMenu.alloc().init()
        menu.setAutoenablesItems_(False)
        a = self.actions
        pairs = [
            ("Show overlay", "showOverlay:"),
            ("Hide overlay", "hideOverlay:"),
            (None, None),
            ("Toggle stealth", "toggleStealth:"),
            ("Toggle mic", "toggleMic:"),
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
            it.setTarget_(a)
            menu.addItem_(it)
        item.setMenu_(menu)
        self.status_item = item

    def _bind_keys(self):
        mask = 1 << 10

        def local_handler(event):
            self._handle_key(event)
            return event

        NSEvent.addLocalMonitorForEventsMatchingMask_handler_(mask, local_handler)

    def _handle_key(self, event):
        flags = int(event.modifierFlags())
        cmd = bool(flags & (1 << 20))
        shift = bool(flags & (1 << 17))
        chars = event.charactersIgnoringModifiers() or ""
        if not cmd:
            return
        if chars == "\r" and self.phase == "live":
            self.assist()
        if shift and chars.lower() == "e":
            self.toggle_stealth()
        if shift and chars.lower() == "h":
            self.hide_overlay()
        if shift and chars.lower() == "s" and self.phase == "live":
            self.screen()
        if shift and chars.lower() == "m" and self.phase == "live":
            self.toggle_mic()

    def pick_mode(self, tag: int):
        self.profile["mode"] = {1: "interview", 2: "sales", 3: "meeting"}.get(tag, "interview")
        self.show_setup()

    def launch(self):
        self.profile["displayName"] = str(self.name_field.stringValue())
        self.profile["role"] = str(self.role_field.stringValue())
        self.profile["resume"] = str(self.resume_field["tv"].string())
        self.profile["jobDescription"] = str(self.job_field["tv"].string())
        self.profile["agenticFacts"] = str(self.agentic_field["tv"].string())
        self.profile["projects"] = str(self.projects_field["tv"].string())
        engine.save_profile(self.profile)
        self.transcript = []
        self.mock_i = 0
        self.status = "idle"
        self.result = None
        self.error = None
        self.started = time.time()
        self.anchor_q = ""
        self.anchor_a = ""
        self.followups = []
        self.follow_q = ""
        self.draft_follow = ""
        self._stop_mic()
        self.show_live()

    def toggle_mic(self):
        if self.phase != "live":
            return
        if self.listening:
            self._stop_mic(flush=True)
            self.show_live()
            return
        self.listening = True
        self.hearing = ""
        self.listener = listen.Listener(
            self._heard_partial,
            self._heard_final,
            self._heard_error,
            hints=engine.speech_hints(self.profile),
        )
        self.show_live()
        self.listener.start()

    def _stop_mic(self, flush=False):
        if flush and self.listener is not None:
            try:
                self.listener.flush_now()
            except Exception:
                pass
        self.listening = False
        self.hearing = ""
        if self.listener is not None:
            self.listener.stop()
            self.listener = None

    def _heard_partial(self, text: str):
        self.hearing = text
        if self.phase == "live" and hasattr(self, "prompt"):
            self.prompt.setStringValue_(text)
        if self.phase == "live" and self.status != "thinking":
            self._paint_answer()

    def _heard_final(self, text: str):
        cleaned = engine.repair_asr(text.strip())
        self.hearing = ""
        if not engine.looks_like_utterance(cleaned):
            print(f"VEIL skip (too short / filler): {cleaned}", flush=True)
            if hasattr(self, "prompt"):
                self.prompt.setStringValue_(cleaned)
            return
        print(f"VEIL assist on: {cleaned}", flush=True)
        self.transcript.append(f"them: {cleaned}")
        if hasattr(self, "prompt"):
            self.prompt.setStringValue_(cleaned)
        if self.status == "thinking":
            self.pending_q = cleaned
            self.pending_kind = "answer"
            return
        self._run("answer", cleaned, "")

    def _heard_error(self, msg: str):
        # Keep the mic on for anything that is not a hard permission failure.
        print(f"VEIL listen: {msg}", flush=True)
        self.error = msg
        if "Allow" in msg or "grant" in msg.lower():
            self._stop_mic()
            self.status = "error"
            if self.phase == "live":
                self.show_live()
            return
        if self.phase == "live":
            self._paint_answer()

    def _compose_board(self) -> str:
        parts = []
        if self.anchor_q:
            parts.append(self.anchor_q)
        if self.anchor_a:
            parts.append(self.anchor_a)
        for fq, fa in self.followups:
            parts.append(f"— {fq}\n{fa}")
        if self.draft_follow:
            label = self.follow_q or "follow-up"
            parts.append(f"— {label}\n{self.draft_follow}")
        return "\n\n".join(p for p in parts if p).strip()

    def _run(self, kind, question, screen_text):
        if self.status == "thinking":
            self.pending_q = question
            self.pending_kind = kind
            return
        follow = kind == "followup"
        if not follow:
            self.anchor_q = question
            self.anchor_a = ""
            self.followups = []
            self.follow_q = ""
            self.draft_follow = ""
        else:
            self.follow_q = question
            self.draft_follow = ""
        self.status = "thinking"
        self.error = None
        if not follow:
            self.result = {"spoken": "", "points": [], "code": ""}
        self._paint_answer()
        packed = "\n".join(self.transcript)
        profile = dict(self.profile)

        def work():
            acc = []
            try:
                for chunk in engine.stream_assist(profile, packed, question, kind, screen_text):
                    acc.append(chunk)
                    text = "".join(acc)

                    def paint(t=text, f=follow):
                        if f:
                            self.draft_follow = t
                        else:
                            self.anchor_a = t
                        self.result = {"spoken": self._compose_board(), "points": [], "code": ""}
                        self._paint_answer()

                    AppHelper.callAfter(paint)

                def done():
                    if follow:
                        if self.draft_follow.strip():
                            self.followups.append((self.follow_q, self.draft_follow.strip()))
                            self.transcript.append(f"you: {self.draft_follow.strip()}")
                        self.draft_follow = ""
                    else:
                        if self.anchor_a.strip():
                            self.transcript.append(f"you: {self.anchor_a.strip()}")
                    self.result = {"spoken": self._compose_board(), "points": [], "code": ""}
                    self.status = "ready"
                    nxt = self.pending_q
                    nxt_kind = getattr(self, "pending_kind", "answer") or "answer"
                    self.pending_q = None
                    self.pending_kind = None
                    if nxt:
                        self._run(nxt_kind, nxt, "")

                AppHelper.callAfter(done)
            except Exception as e:
                msg = str(e)

                def fail(m=msg):
                    self.status = "error"
                    self.error = m
                    self._paint_answer()
                    nxt = self.pending_q
                    nxt_kind = getattr(self, "pending_kind", "answer") or "answer"
                    self.pending_q = None
                    self.pending_kind = None
                    if nxt:
                        self._run(nxt_kind, nxt, "")

                AppHelper.callAfter(fail)

        threading.Thread(target=work, daemon=True).start()

    def save_settings(self):
        engine.save_config(
            {
                "api_key": str(self.key_field.stringValue()).strip(),
                "api_url": str(self.url_field.stringValue()).strip(),
            }
        )
        self.show_setup()

    def show_overlay(self):
        self.panel.orderFrontRegardless()
        NSApp.activateIgnoringOtherApps_(True)

    def hide_overlay(self):
        self.panel.orderOut_(None)

    def toggle_stealth(self):
        self.stealth = not self.stealth
        self.apply_stealth()
        if self.phase == "live":
            self.show_live()

    def assist(self):
        if self.phase != "live":
            return
        q = str(self.prompt.stringValue()).strip()
        if not q:
            return
        kind = "followup" if (self.anchor_a or "").strip() else "answer"
        self._run(kind, q, "")

    def load_briefing(self):
        try:
            text = engine.load_briefing("principal-engineer")
        except Exception as e:
            print(f"VEIL briefing: {e}", flush=True)
            return
        self.profile["jobDescription"] = text
        if not (self.profile.get("role") or "").strip():
            self.profile["role"] = "Principal Engineer"
        engine.save_profile(self.profile)
        if self.phase == "setup":
            self.show_setup()

    def import_resume(self):
        panel = NSOpenPanel.openPanel()
        panel.setAllowsMultipleSelection_(False)
        panel.setCanChooseDirectories_(False)
        panel.setCanChooseFiles_(True)
        panel.setAllowedFileTypes_(["pdf", "txt", "md", "rtf", "text"])
        panel.setTitle_("Import resume")
        if panel.runModal() != 1:
            return
        url = panel.URL()
        if url is None:
            return
        path = str(url.path())
        try:
            text = engine.load_resume_file(path)
        except Exception as e:
            print(f"VEIL resume: {e}", flush=True)
            return
        self.profile["resume"] = text
        engine.save_profile(self.profile)
        if self.phase == "setup":
            self.show_setup()

    def screen(self):
        if self.phase != "live":
            return
        q = str(self.prompt.stringValue()) or "Look at my screen. If I'm on draw.io or a whiteboard, tell me what to draw next."
        self._run("screen", q, "")

    def next_question(self):
        if self.phase != "live":
            return
        mode = self.profile.get("mode", "interview")
        qs = engine.MOCK_QUESTIONS[mode]
        q = qs[self.mock_i % len(qs)]
        self.mock_i += 1
        self.transcript.append(f"them: {q}")
        self.prompt.setStringValue_(q)
        self._run("answer", q, "")

    def end_room(self):
        self._stop_mic()
        if self.phase == "setup":
            self.hide_overlay()
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
    print("Starting VEIL…", flush=True)
    try:
        app = NSApplication.sharedApplication()
        app.setActivationPolicy_(NSApplicationActivationPolicyRegular)
        app.setAppearance_(NSAppearance.appearanceNamed_("NSAppearanceNameDarkAqua"))
        icon_path = Path(__file__).resolve().parent.parent / "icons" / "veil.png"
        if getattr(sys, "frozen", False):
            icon_path = Path(sys._MEIPASS) / "icons" / "veil.png"
        if icon_path.exists():
            img = NSImage.alloc().initWithContentsOfFile_(str(icon_path))
            if img is not None:
                app.setApplicationIconImage_(img)
        actions = Actions.alloc().init()
        hud = HUD(actions)
        actions.hud = hud
        app.setDelegate_(actions)
        hud.boot()
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
