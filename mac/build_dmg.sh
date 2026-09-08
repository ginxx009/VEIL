#!/bin/bash
# Build VEIL.app + VEIL.dmg on macOS. Run from anywhere:
#   bash mac/build_dmg.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python3 -m pip install -q pyinstaller pyobjc-core pyobjc-framework-Cocoa \
  pyobjc-framework-Quartz pyobjc-framework-AVFoundation pyobjc-framework-Speech pypdf pillow

ICONSET="$ROOT/build/icon.iconset"
rm -rf "$ICONSET" "$ROOT/build/veil.icns"
mkdir -p "$ICONSET" "$ROOT/dist"
for s in 16 32 64 128 256 512; do
  sips -z $s $s "$ROOT/icons/veil.png" --out "$ICONSET/icon_${s}x${s}.png" >/dev/null
  ds=$((s * 2))
  sips -z $ds $ds "$ROOT/icons/veil.png" --out "$ICONSET/icon_${s}x${s}@2x.png" >/dev/null
done
iconutil -c icns "$ICONSET" -o "$ROOT/build/veil.icns"

pyinstaller --noconfirm --clean --windowed --name VEIL \
  --icon "$ROOT/build/veil.icns" \
  --osx-bundle-identifier ph.joesolutions.veil \
  --add-data "$ROOT/mac/engine.py:." \
  --add-data "$ROOT/mac/listen.py:." \
  --add-data "$ROOT/icons/veil.png:icons" \
  --hidden-import=engine \
  --hidden-import=listen \
  "$ROOT/mac/VEIL.py"

PLIST="$ROOT/dist/VEIL.app/Contents/Info.plist"
if [ -f "$PLIST" ]; then
  /usr/libexec/PlistBuddy -c "Add :NSMicrophoneUsageDescription string VEIL listens to the interviewer so it can write a speakable answer." "$PLIST" 2>/dev/null || true
  /usr/libexec/PlistBuddy -c "Add :NSSpeechRecognitionUsageDescription string VEIL turns spoken questions into text on your Mac." "$PLIST" 2>/dev/null || true
fi

rm -f "$ROOT/dist/VEIL.dmg"
hdiutil create -volname VEIL -srcfolder "$ROOT/dist/VEIL.app" -ov -format UDZO "$ROOT/dist/VEIL.dmg"
echo "Built $ROOT/dist/VEIL.dmg"
