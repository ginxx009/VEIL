@echo off
REM Build VEIL.exe on Windows. Run from repo root or this folder.
set ROOT=%~dp0..
cd /d "%ROOT%"
python -m pip install -q pyinstaller sounddevice numpy pypdf pillow
python -m PyInstaller --noconfirm --clean --windowed --onefile --name VEIL ^
  --icon "%ROOT%\icons\veil.ico" ^
  --add-data "%ROOT%\mac\engine.py;." ^
  --add-data "%ROOT%\windows\listen.py;." ^
  --add-data "%ROOT%\icons\veil.ico;icons" ^
  --hidden-import=engine --hidden-import=listen --hidden-import=sounddevice --hidden-import=numpy ^
  "%ROOT%\windows\VEIL.py"
echo Built dist\VEIL.exe
