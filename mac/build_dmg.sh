#!/bin/bash
# Build a market-ready VEIL.app + VEIL.dmg on macOS.
#   bash mac/build_dmg.sh
#
# Optional (Apple Developer ID — required to ship outside your own Mac):
#   export VEIL_SIGN_IDENTITY="Developer ID Application: Your Name (TEAMID)"
#   export APPLE_ID="you@example.com"
#   export APPLE_APP_SPECIFIC_PASSWORD="xxxx-xxxx-xxxx-xxxx"
#   export APPLE_TEAM_ID="TEAMID"
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python3 -m pip install -q pyinstaller pyobjc-core pyobjc-framework-Cocoa \
  pyobjc-framework-Quartz pyobjc-framework-AVFoundation pyobjc-framework-Speech pypdf pillow

ICONSET="$ROOT/build/icon.iconset"
rm -rf "$ICONSET" "$ROOT/build/veil.icns" "$ROOT/build/VEIL" "$ROOT/dist/VEIL.app" "$ROOT/dist/dmg"
mkdir -p "$ICONSET" "$ROOT/dist/dmg"
for s in 16 32 64 128 256 512; do
  sips -z $s $s "$ROOT/icons/veil.png" --out "$ICONSET/icon_${s}x${s}.png" >/dev/null
  ds=$((s * 2))
  sips -z $ds $ds "$ROOT/icons/veil.png" --out "$ICONSET/icon_${s}x${s}@2x.png" >/dev/null
done
iconutil -c icns "$ICONSET" -o "$ROOT/build/veil.icns"

pyinstaller --noconfirm --clean --distpath "$ROOT/dist" --workpath "$ROOT/build/pyi" \
  "$ROOT/mac/VEIL.spec"

APP="$ROOT/dist/VEIL.app"
if [ ! -d "$APP" ]; then
  echo "PyInstaller did not produce VEIL.app" >&2
  exit 1
fi

PLIST="$APP/Contents/Info.plist"
/usr/libexec/PlistBuddy -c "Set :NSMicrophoneUsageDescription VEIL listens to the interviewer so it can write a speakable answer." "$PLIST" 2>/dev/null \
  || /usr/libexec/PlistBuddy -c "Add :NSMicrophoneUsageDescription string VEIL listens to the interviewer so it can write a speakable answer." "$PLIST"
/usr/libexec/PlistBuddy -c "Set :NSSpeechRecognitionUsageDescription VEIL turns spoken questions into text on this Mac." "$PLIST" 2>/dev/null \
  || /usr/libexec/PlistBuddy -c "Add :NSSpeechRecognitionUsageDescription string VEIL turns spoken questions into text on this Mac." "$PLIST"

IDENTITY="${VEIL_SIGN_IDENTITY:-}"
if [ -n "$IDENTITY" ]; then
  echo "Signing with $IDENTITY"
  codesign --force --deep --options runtime \
    --entitlements "$ROOT/mac/entitlements.plist" \
    --sign "$IDENTITY" "$APP"
  codesign --verify --verbose=2 "$APP"
else
  echo "No VEIL_SIGN_IDENTITY set — ad-hoc sign so Mic/Speech prompts work on this Mac."
  codesign --force --deep --options runtime \
    --entitlements "$ROOT/mac/entitlements.plist" \
    --sign - "$APP" || true
fi

rm -rf "$ROOT/dist/dmg"
mkdir -p "$ROOT/dist/dmg"
cp -R "$APP" "$ROOT/dist/dmg/VEIL.app"
ln -s /Applications "$ROOT/dist/dmg/Applications"

DMG="$ROOT/dist/VEIL.dmg"
rm -f "$DMG"
hdiutil create -volname "VEIL" -srcfolder "$ROOT/dist/dmg" -ov -format UDZO "$DMG"

if [ -n "$IDENTITY" ]; then
  codesign --force --sign "$IDENTITY" "$DMG" || true
fi

if [ -n "${APPLE_ID:-}" ] && [ -n "${APPLE_APP_SPECIFIC_PASSWORD:-}" ] && [ -n "${APPLE_TEAM_ID:-}" ]; then
  echo "Notarizing (needed so strangers can open it without Gatekeeper warnings)…"
  xcrun notarytool submit "$DMG" \
    --apple-id "$APPLE_ID" \
    --password "$APPLE_APP_SPECIFIC_PASSWORD" \
    --team-id "$APPLE_TEAM_ID" \
    --wait
  xcrun stapler staple "$DMG"
  xcrun stapler staple "$APP" || true
else
  echo "Skip notarize (set APPLE_ID, APPLE_APP_SPECIFIC_PASSWORD, APPLE_TEAM_ID to ship publicly)."
fi

echo ""
echo "Installer: $DMG"
echo "Users: open the DMG → drag VEIL to Applications → open VEIL."
echo "First launch pops Microphone + Speech Recognition. They click Allow once."
