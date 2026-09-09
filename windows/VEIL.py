#!/usr/bin/env python3
"""VEIL — Windows overlay copilot.

Topmost HUD excluded from screen capture via SetWindowDisplayAffinity
(WDA_EXCLUDEFROMCAPTURE). Same flow as the Mac app.
"""

from __future__ import annotations

import ctypes
import os
import sys
import threading
import time
from pathlib import Path

if getattr(sys, "frozen", False):
    BASE = Path(sys._MEIPASS)
    ROOT = Path(sys.executable).resolve().parent
else:
    BASE = Path(__file__).resolve().parent
    ROOT = BASE.parent

sys.path.insert(0, str(BASE))
sys.path.insert(0, str(ROOT / "mac"))
sys.path.insert(0, str(BASE.parent / "mac"))

import tkinter as tk
from tkinter import filedialog, ttk

import engine
import listen

WDA_NONE = 0x00000000
WDA_EXCLUDEFROMCAPTURE = 0x00000011
GWL_EXSTYLE = -20
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_APPWINDOW = 0x00040000

BG = "#131316"
CARD = "#1c1c22"
TEXT = "#f3f2ee"
MUTED = "#8b8b86"
SAGE = "#8fb09c"
RED = "#d07070"


def _hwnd(win: tk.Tk) -> int:
    win.update_idletasks()
    wid = win.winfo_id()
    parent = ctypes.windll.user32.GetParent(wid)
    return parent or wid


def set_stealth(win: tk.Tk, stealth: bool):
    hwnd = _hwnd(win)
    ctypes.windll.user32.SetWindowDisplayAffinity(
        hwnd, WDA_EXCLUDEFROMCAPTURE if stealth else WDA_NONE
    )
    style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    style |= WS_EX_TOOLWINDOW
    style &= ~WS_EX_APPWINDOW
    ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)


class HUD:
    def __init__(self, root: tk.Tk):
        self.root = root
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
        self._build_shell()
        self.show_setup()
        self.root.after(400, lambda: set_stealth(self.root, True))

    def _build_shell(self):
        r = self.root
        r.title("VEIL")
        r.configure(bg=BG)
        r.geometry("420x580+80+80")
        r.minsize(380, 520)
        r.attributes("-topmost", True)
        r.resizable(False, True)
        icon = ROOT / "icons" / "veil.ico"
        if not icon.exists():
            icon = BASE / "icons" / "veil.ico"
        if icon.exists():
            try:
                r.iconbitmap(str(icon))
            except Exception:
                pass
        self.header = tk.Frame(r, bg=BG, height=44)
        self.header.pack(fill="x")
        tk.Label(self.header, text="VEIL", fg=SAGE, bg=BG, font=("Segoe UI Semibold", 12)).pack(
            side="left", padx=16, pady=10
        )
        self.stealth_lbl = tk.Label(self.header, text="stealth on", fg=MUTED, bg=BG, font=("Segoe UI", 9))
        self.stealth_lbl.pack(side="right", padx=16)
        self.body = tk.Frame(r, bg=BG)
        self.body.pack(fill="both", expand=True)

    def _clear(self):
        for w in self.body.winfo_children():
            w.destroy()

    def _btn(self, parent, title, cmd, kind="ghost"):
        fg = SAGE if kind == "sage" else RED if kind == "danger" else TEXT
        bg = "#24332c" if kind == "sage" else "#3a2222" if kind == "danger" else CARD
        b = tk.Button(
            parent,
            text=title,
            command=cmd,
            fg=fg,
            bg=bg,
            activeforeground=fg,
            activebackground=bg,
            relief="flat",
            font=("Segoe UI Semibold", 9),
            padx=12,
            pady=6,
            cursor="hand2",
            bd=0,
        )
        return b

    def _entry(self, parent, value, show=None):
        e = tk.Entry(
            parent,
            fg=TEXT,
            bg=CARD,
            insertbackground=TEXT,
            relief="flat",
            font=("Segoe UI", 10),
            show=show or "",
        )
        e.insert(0, value)
        e.pack(fill="x", padx=20, ipady=6)
        return e

    def _text(self, parent, value, height=6):
        t = tk.Text(
            parent,
            fg=TEXT,
            bg=CARD,
            insertbackground=TEXT,
            relief="flat",
            font=("Segoe UI", 10),
            height=height,
            wrap="word",
        )
        t.insert("1.0", value)
        t.pack(fill="both", expand=True, padx=20)
        return t

    def _label(self, text):
        tk.Label(self.body, text=text, fg=MUTED, bg=BG, font=("Segoe UI", 9), anchor="w").pack(
            fill="x", padx=20, pady=(12, 4)
        )

    def show_setup(self):
        self.phase = "setup"
        self._clear()
        self._label("Your name")
        self.name_field = self._entry(self.body, self.profile.get("displayName", ""))
        self._label("Role")
        self.role_field = self._entry(self.body, self.profile.get("role", ""))
        row = tk.Frame(self.body, bg=BG)
        row.pack(fill="x", padx=20, pady=8)
        for m, title in (("interview", "Interview"), ("sales", "Sales"), ("meeting", "Meeting")):
            kind = "sage" if self.profile.get("mode") == m else "ghost"

            def pick(mode=m):
                self.profile["mode"] = mode
                self.show_setup()

            self._btn(row, title, pick, kind).pack(side="left", padx=(0, 8))
        head = tk.Frame(self.body, bg=BG)
        head.pack(fill="x", padx=20, pady=(8, 0))
        tk.Label(head, text="Resume / playbook", fg=MUTED, bg=BG, font=("Segoe UI", 9)).pack(side="left")
        self._btn(head, "Import file", self.import_resume).pack(side="right")
        self.resume_field = self._text(self.body, self.profile.get("resume", ""), height=7)
        self._label("Job or meeting context")
        self.job_field = self._text(self.body, self.profile.get("jobDescription", ""), height=3)
        self._label("Agentic facts — years, Cursor CLI, Claude Code, Dynaskills, impact")
        self.agentic_field = self._text(self.body, self.profile.get("agenticFacts", ""), height=3)
        self._label("Products / projects — name, architecture, alternative, how it scales")
        self.projects_field = self._text(self.body, self.profile.get("projects", ""), height=3)
        self._label("Leadership — culture change, mentoring, how a standard got adopted")
        self.leadership_field = self._text(self.body, self.profile.get("leadership", ""), height=2)
        self._label("Data / ETL — EventBridge, S3, RDS, PHP→Node. ETO means ETL")
        self.data_field = self._text(self.body, self.profile.get("dataFacts", ""), height=3)
        foot = tk.Frame(self.body, bg=BG)
        foot.pack(fill="x", padx=20, pady=16)
        self._btn(foot, "Launch overlay", self.launch, "sage").pack(side="left")
        self._btn(foot, "Load briefing", self.load_briefing).pack(side="left", padx=8)
        self._btn(foot, "Settings", self.show_settings).pack(side="left", padx=8)

    def show_settings(self):
        self.phase = "settings"
        self._clear()
        cfg = engine.load_config()
        self._label("API key (OpenAI sk-…, or xAI / Gemini)")
        self.key_field = self._entry(self.body, cfg.get("api_key", ""), show="*")
        self._label("Optional API URL")
        self.url_field = self._entry(self.body, cfg.get("api_url", ""))
        tk.Label(
            self.body,
            text="Windows stealth uses WDA_EXCLUDEFROMCAPTURE so Zoom / Teams / Meet cannot see this window.",
            fg=MUTED,
            bg=BG,
            wraplength=360,
            justify="left",
            font=("Segoe UI", 9),
        ).pack(fill="x", padx=20, pady=12)
        foot = tk.Frame(self.body, bg=BG)
        foot.pack(fill="x", padx=20, pady=16)
        self._btn(foot, "Save", self.save_settings, "sage").pack(side="left")
        self._btn(foot, "Back", self.show_setup).pack(side="left", padx=8)

    def show_live(self):
        self.phase = "live"
        self._clear()
        mic = "Listening" if self.listening else "Mic"
        row = tk.Frame(self.body, bg=BG)
        row.pack(fill="x", padx=16, pady=8)
        self._btn(row, mic, self.toggle_mic, "sage" if self.listening else "ghost").pack(side="left")
        self._btn(row, "Assist", self.assist, "sage").pack(side="left", padx=6)
        self._btn(row, "Screen", self.screen).pack(side="left")
        stealth = "Stealth on" if self.stealth else "Stealth off"
        self._btn(row, stealth, self.toggle_stealth).pack(side="left", padx=6)
        self.prompt = self._entry(self.body, "")
        self.answer = tk.Text(
            self.body,
            fg=TEXT,
            bg=CARD,
            relief="flat",
            font=("Segoe UI", 11),
            wrap="word",
            height=16,
            state="disabled",
        )
        self.answer.pack(fill="both", expand=True, padx=20, pady=10)
        foot = tk.Frame(self.body, bg=BG)
        foot.pack(fill="x", padx=16, pady=8)
        self._btn(foot, "Next Q", self.next_question).pack(side="left")
        self._btn(foot, "New room", self.show_setup).pack(side="left", padx=6)
        self._btn(foot, "Hide", self.hide_overlay).pack(side="left")
        self._btn(foot, "Quit", self.root.destroy, "danger").pack(side="right")
        self._paint_answer()
        self.stealth_lbl.config(text="stealth on" if self.stealth else "visible")

    def _paint_answer(self):
        if self.phase != "live":
            return
        spoken = ""
        if self.result:
            spoken = self.result.get("spoken") or ""
        if spoken:
            body, color = spoken, TEXT
        elif self.status == "error":
            body, color = self.error or "Could not generate an answer.", RED
        elif self.status == "thinking":
            held = self._compose_board()
            if held:
                body, color = held + "\n\nAdding…", TEXT
            else:
                body, color = "Writing a speakable answer…", MUTED
        elif self.listening and self.hearing:
            body, color = "Hearing…\n" + self.hearing, MUTED
        elif self.listening:
            body, color = "Listening. Leave Mic on. Click Mic only to stop.", MUTED
        else:
            body, color = "Mic stays on across questions. Stealth hides this window from screen share.", MUTED
        self.answer.config(state="normal", fg=color)
        self.answer.delete("1.0", "end")
        self.answer.insert("1.0", body)
        self.answer.config(state="disabled")
        self.answer.see("end")

    def ui(self, fn):
        self.root.after(0, fn)

    def launch(self):
        self.profile["displayName"] = self.name_field.get().strip()
        self.profile["role"] = self.role_field.get().strip()
        self.profile["resume"] = self.resume_field.get("1.0", "end").strip()
        self.profile["jobDescription"] = self.job_field.get("1.0", "end").strip()
        self.profile["agenticFacts"] = self.agentic_field.get("1.0", "end").strip()
        self.profile["projects"] = self.projects_field.get("1.0", "end").strip()
        self.profile["leadership"] = self.leadership_field.get("1.0", "end").strip()
        self.profile["dataFacts"] = self.data_field.get("1.0", "end").strip()
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

    def save_settings(self):
        engine.save_config(
            {
                "api_key": self.key_field.get().strip(),
                "api_url": self.url_field.get().strip(),
            }
        )
        self.show_setup()

    def import_resume(self):
        path = filedialog.askopenfilename(
            title="Import resume",
            filetypes=[("Resume", "*.pdf *.txt *.md *.rtf"), ("All", "*.*")],
        )
        if not path:
            return
        try:
            text = engine.load_resume_file(path)
        except Exception as e:
            print(f"VEIL resume: {e}", flush=True)
            return
        self.profile["resume"] = text
        engine.save_profile(self.profile)
        if self.phase == "setup":
            self.show_setup()

    def toggle_mic(self):
        if self.phase != "live":
            return
        if self.listening:
            self._stop_mic(flush=True)
            self.show_live()
            return
        self.listening = True
        self.hearing = ""
        self.listener = listen.Listener(self._heard_partial, self._heard_final, self._heard_error)
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
        def go():
            self.hearing = text
            if self.phase == "live" and self.status != "thinking":
                self._paint_answer()

        self.ui(go)

    def _heard_final(self, text: str):
        def go():
            cleaned = engine.repair_asr(text.strip())
            self.hearing = ""
            if not engine.looks_like_utterance(cleaned):
                print(f"VEIL skip (too short / filler): {cleaned}", flush=True)
                if hasattr(self, "prompt"):
                    self.prompt.delete(0, "end")
                    self.prompt.insert(0, cleaned)
                return
            print(f"VEIL assist on: {cleaned}", flush=True)
            self.transcript.append(f"them: {cleaned}")
            if hasattr(self, "prompt"):
                self.prompt.delete(0, "end")
                self.prompt.insert(0, cleaned)
            if self.status == "thinking":
                self.pending_q = cleaned
                self.pending_kind = "answer"
                return
            self._run("answer", cleaned, "")

        self.ui(go)

    def _heard_error(self, msg: str):
        def go():
            print(f"VEIL listen: {msg}", flush=True)
            self.error = msg
            if self.phase == "live":
                self._paint_answer()

        self.ui(go)

    def _compose_board(self) -> str:
        parts = []
        if self.anchor_q:
            parts.append(self.anchor_q)
        if self.anchor_a:
            parts.append(self.anchor_a)
        for fq, fa in self.followups:
            parts.append(f"— {fq}\n{fa}")
        if self.draft_follow:
            parts.append(f"— {self.follow_q or 'follow-up'}\n{self.draft_follow}")
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
            self.result = {"spoken": "", "points": [], "code": ""}
        else:
            self.follow_q = question
            self.draft_follow = ""
        self.status = "thinking"
        self.error = None
        self._paint_answer()
        packed = "\n".join(self.transcript)
        profile = dict(self.profile)

        def work():
            acc = []
            try:
                for chunk in engine.stream_assist(profile, packed, question, kind, screen_text):
                    acc.append(chunk)
                    text = "".join(acc)
                    self.ui(lambda t=text, f=follow: self._stream_paint(t, f))

                def done():
                    if follow:
                        if self.draft_follow.strip():
                            self.followups.append((self.follow_q, self.draft_follow.strip()))
                            self.transcript.append(f"you: {self.draft_follow.strip()}")
                        self.draft_follow = ""
                    elif self.anchor_a.strip():
                        self.transcript.append(f"you: {self.anchor_a.strip()}")
                    self.result = {"spoken": self._compose_board(), "points": [], "code": ""}
                    self.status = "ready"
                    nxt = self.pending_q
                    nxt_kind = self.pending_kind or "answer"
                    self.pending_q = None
                    self.pending_kind = None
                    if nxt:
                        self._run(nxt_kind, nxt, "")

                self.ui(done)
            except Exception as e:
                msg = str(e)

                def fail(m=msg):
                    self.status = "error"
                    self.error = m
                    self._paint_answer()

                self.ui(fail)

        threading.Thread(target=work, daemon=True).start()

    def _stream_paint(self, text: str, follow=False):
        if follow:
            self.draft_follow = text
        else:
            self.anchor_a = text
        self.result = {"spoken": self._compose_board(), "points": [], "code": ""}
        self._paint_answer()

    def assist(self):
        if self.phase != "live":
            return
        q = self.prompt.get().strip()
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

    def screen(self):
        if self.phase != "live":
            return
        q = self.prompt.get() or "Look at my screen. If I'm on a whiteboard, tell me what to draw next."
        self._run("screen", q, "")

    def next_question(self):
        if self.phase != "live":
            return
        mode = self.profile.get("mode", "interview")
        qs = engine.MOCK_QUESTIONS[mode]
        q = qs[self.mock_i % len(qs)]
        self.mock_i += 1
        self.transcript.append(f"them: {q}")
        self.prompt.delete(0, "end")
        self.prompt.insert(0, q)
        self._run("answer", q, "")

    def toggle_stealth(self):
        self.stealth = not self.stealth
        set_stealth(self.root, self.stealth)
        if self.phase == "live":
            self.show_live()

    def hide_overlay(self):
        self.root.withdraw()
        self.root.after(50, self._tray_hint)

    def _tray_hint(self):
        self.root.deiconify()
        self.root.iconify()


def main():
    if sys.platform != "win32":
        print("This is the Windows overlay. On a Mac run mac/VEIL.py")
        sys.exit(1)
    print("Starting VEIL…", flush=True)
    root = tk.Tk()
    HUD(root)
    root.mainloop()


if __name__ == "__main__":
    main()
