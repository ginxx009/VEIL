# VEIL

Private **macOS overlay** for live interviews, sales calls, and meetings. A menu-bar HUD that is excluded from screen capture (`NSWindowSharingNone` + content protection). Nothing joins Zoom, Meet, or Teams.

This is a native Python + AppKit app. The web page in this repo is the product page, not the overlay.

## Run on a Mac

Homebrew Python will refuse `pip install` into the system. Use a venv (or just double-click **Launch.command**, which creates one):

```bash
git clone https://github.com/ginxx009/VEIL.git
cd VEIL/mac
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 VEIL.py
```

Already cloned? `git pull origin main` then the `venv` steps from `VEIL/mac`.

A VEIL extra appears in the menu bar. The HUD floats over the call.

1. Add an [xAI](https://console.x.ai/) or [Gemini](https://aistudio.google.com/apikey) API key in **Settings** (or set `XAI_API_KEY` / `GEMINI_API_KEY`).
   Keys starting with `AIza` use Gemini; `xai-` uses xAI.
2. Launch a room.
3. Share **Meet / Zoom / your editor** — never the overlay window.
4. Click **Mic**. Allow Microphone and Speech Recognition when macOS asks. VEIL transcribes the interviewer and writes an answer when they finish the question.

Headphones help so it does not hear you speaking the answer.

### Hotkeys

| Shortcut | Action |
|---|---|
| ⌘↩ | Assist |
| ⌘⇧E | Toggle stealth |
| ⌘⇧H | Hide overlay |
| ⌘⇧S | Solve screen |
| ⌘⇧M | Toggle mic (auto-answer) |

Stealth on = the window is not composited into their screen share. Stealth off = visible (for rehearsal).

Profile and sessions live in `~/Library/Application Support/VEIL/`.
