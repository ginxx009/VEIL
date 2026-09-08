# VEIL for Mac

Native overlay for live interviews, sales calls, and meetings. It floats above the call and is **excluded from screen capture**, so Zoom / Meet / Teams do not show it.

Python + AppKit (`NSWindowSharingNone`). Not a browser.

## Run

Homebrew Python will refuse a system-wide `pip install`. Use a venv, or double-click **Launch.command** (it creates one).

```bash
cd VEIL/mac
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 VEIL.py
```

Already cloned:

```bash
git pull origin main
cd mac
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 VEIL.py
```

A **VEIL** extra appears in the menu bar. The HUD sits top-right.

## First launch

1. **Settings** — paste an API key.
   - OpenAI `sk-…` (default, [platform.openai.com/api-keys](https://platform.openai.com/api-keys))
   - xAI `xai-…` or Gemini `AIza…` still work if you paste those
2. Set **your name**, **role** (e.g. Senior Salesforce Cloud Engineer), and paste **resume / playbook**. That is who VEIL answers as. Empty resume = generic answers.
3. **Import file** accepts `.txt`, `.md`, or `.pdf` (needs `pypdf` from `requirements.txt`). You can also paste.
4. Pick mode: Interview / Sales / Meeting → **Launch overlay**.
5. Share **Meet / Zoom / your editor** — never the VEIL window.

## Live

| Control | What it does |
|---|---|
| **Mic** | Listens to the interviewer. Answers when they pause. Click again to turn the mic off — the last question still gets an answer. |
| **Assist** / **Go** | Answer whatever is in the prompt (or ⌘↩). |
| **Screen** | Looks at your display and coaches what to say or draw next. Use this for draw.io / a whiteboard. |
| **Next Q** | Practice question. |
| **Hide overlay** | HUD goes away; menu bar extra stays. |

Leave **Mic** on for the whole call if you want. You do not have to toggle it every question.

Play **their** audio on **speakers**, not headphones, or the Mac mic cannot hear them. Headphones are fine for *you* so VEIL does not hear you reading the answer.

### Hotkeys

| Shortcut | Action |
|---|---|
| ⌘↩ | Assist |
| ⌘⇧M | Toggle mic |
| ⌘⇧S | Screen |
| ⌘⇧E | Toggle stealth |
| ⌘⇧H | Hide overlay |

**Stealth on** (default) = not in their screen share. **Stealth off** = visible, for rehearsal.

## Permissions

First Mic click, macOS will ask for:

- **Microphone**
- **Speech Recognition**

If it never hears them: System Settings → Privacy & Security → enable both for **Terminal** (or **VEIL**, if you launched via Launch.command).

## How answers work

- Answers the **question they asked**. No extra war story unless they asked for experience.
- Does **not** coach draw.io unless they actually asked to draw, or you hit **Screen**.
- Grounds facts in your resume. Fill it.

Keys, profile, and sessions: `~/Library/Application Support/VEIL/`.

## Installer (DMG)

On a Mac:

```bash
bash mac/build_dmg.sh
```

Writes `dist/VEIL.dmg`. Or run **Actions → Release installers** on GitHub and download the Mac artifact.

## Files

| File | Role |
|---|---|
| `VEIL.py` | Overlay, menu bar, hotkeys |
| `engine.py` | OpenAI / xAI / Gemini, resume, screen |
| `listen.py` | Live speech → questions |
| `Launch.command` | Double-click runner |
| `requirements.txt` | PyObjC, Speech, pypdf |

Quit with Ctrl+C in the terminal, or Quit from the menu bar extra.
