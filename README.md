# VEIL

Private overlay for live interviews, sales calls, and meetings. Hidden from screen capture.

MIT licensed. PRs welcome — they cannot land on `main` until **@ginxx009** approves. See [CONTRIBUTING.md](CONTRIBUTING.md).

| Platform | Hide from share | Run | Installer |
|---|---|---|---|
| **macOS** | `NSWindowSharingNone` | [mac/README.md](mac/README.md) | `VEIL.dmg` |
| **Windows** | `WDA_EXCLUDEFROMCAPTURE` | [windows/README.md](windows/README.md) | `VEIL.exe` |

## Mac

```bash
cd mac
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 VEIL.py
```

Build a DMG (on a Mac): `bash mac/build_dmg.sh` → `dist/VEIL.dmg`.

## Windows

```bat
cd windows
Launch.bat
```

Build an EXE (on Windows): `windows\build.bat` → `dist\VEIL.exe`.

## Download

GitHub → **Actions** → **Release installers** → Run workflow (or push a `v*` tag). Artifacts:

- `VEIL-mac` → `VEIL.dmg`
- `VEIL-windows` → `VEIL.exe`

Icon is in [icons/](icons/).
