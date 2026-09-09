# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

# SPECPATH is the directory that contains this spec (mac/), not the file.
SPECDIR = Path(SPECPATH).resolve()
ROOT = SPECDIR.parent

a = Analysis(
    [str(SPECDIR / "VEIL.py")],
    pathex=[str(SPECDIR)],
    binaries=[],
    datas=[
        (str(SPECDIR / "engine.py"), "."),
        (str(SPECDIR / "listen.py"), "."),
        (str(ROOT / "icons" / "veil.png"), "icons"),
        (str(SPECDIR / "playbooks"), "playbooks"),
    ],
    hiddenimports=[
        "engine",
        "listen",
        "objc",
        "AppKit",
        "Foundation",
        "AVFoundation",
        "Speech",
        "Quartz",
        "CoreFoundation",
        "CoreMedia",
        "pypdf",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="VEIL",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=str(SPECDIR / "entitlements.plist"),
    icon=str(ROOT / "build" / "veil.icns"),
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="VEIL",
)
app = BUNDLE(
    coll,
    name="VEIL.app",
    icon=str(ROOT / "build" / "veil.icns"),
    bundle_identifier="ph.joesolutions.veil",
    info_plist={
        "CFBundleName": "VEIL",
        "CFBundleDisplayName": "VEIL",
        "CFBundleIdentifier": "ph.joesolutions.veil",
        "CFBundleVersion": "1.0.0",
        "CFBundleShortVersionString": "1.0.0",
        "CFBundlePackageType": "APPL",
        "LSMinimumSystemVersion": "13.0",
        "LSApplicationCategoryType": "public.app-category.productivity",
        "NSHighResolutionCapable": True,
        "NSMicrophoneUsageDescription": "VEIL listens to the interviewer so it can write a speakable answer.",
        "NSSpeechRecognitionUsageDescription": "VEIL turns spoken questions into text on this Mac.",
        "NSAppleEventsUsageDescription": "VEIL stays as a floating overlay above your interview.",
        "NSPrincipalClass": "NSApplication",
    },
)
