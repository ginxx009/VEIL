# VEIL

Private **macOS overlay** for live interviews, sales calls, and meetings. A menu-bar HUD that is excluded from screen capture (`NSWindowSharingNone` + content protection). Nothing joins Zoom, Meet, or Teams.

This is a native Python + AppKit app. The web page in this repo is the product page, not the overlay.

## Run on a Mac

```bash
git clone https://github.com/ginxx009/VEIL.git
cd VEIL/mac
python3 -m pip install -r requirements.txt
python3 VEIL.py
```

Or unzip `public/veil-mac.zip` and double-click **Launch.command**.

A VEIL extra appears in the menu bar. The HUD floats over the call.

1. Add an [xAI API key](https://console.x.ai/) in **Settings** (or set `XAI_API_KEY`).
2. Launch a room.
3. Share **Meet / Zoom / your editor** — never the overlay window.

### Hotkeys

| Shortcut | Action |
|---|---|
| ⌘↩ | Assist |
| ⌘⇧E | Toggle stealth |
| ⌘⇧H | Hide overlay |
| ⌘⇧S | Solve screen |

Stealth on = the window is not composited into their screen share. Stealth off = visible (for rehearsal).

Profile and sessions live in `~/Library/Application Support/VEIL/`.
