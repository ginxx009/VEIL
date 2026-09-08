# VEIL for Windows

Overlay for live interviews. Topmost HUD, hidden from screen share via `SetWindowDisplayAffinity` (`WDA_EXCLUDEFROMCAPTURE`) — Zoom / Teams / Meet should not capture it. Windows 10 2004+ required for that flag.

## Run from source

```bat
cd VEIL\windows
Launch.bat
```

Or:

```bat
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python VEIL.py
```

Paste an OpenAI `sk-…` key in Settings (Whisper + answers). Same resume / role / Mic flow as Mac.

## Installer

You cannot build a real `.exe` on a Mac. PyInstaller does not cross-compile Windows GUIs.

**From your Mac:** GitHub → **Actions** → **Release installers** → **Run workflow** → wait → download artifact **VEIL-windows** (`VEIL.exe`).

Or, if `gh` is installed:

```bash
gh workflow run "Release installers" --ref main
```

On a Windows PC:

```bat
windows\build.bat
```

writes `dist\VEIL.exe`.
