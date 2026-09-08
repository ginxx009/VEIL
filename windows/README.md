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

On a Windows machine (or via GitHub Actions):

```bat
windows\build.bat
```

That writes `dist\VEIL.exe`.

A tagged push (`v1.0.0`) or **Actions → Release installers → Run workflow** uploads `VEIL.exe`.
