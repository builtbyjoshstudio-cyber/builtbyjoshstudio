#!/usr/bin/env python3
"""
bundle_release.py — assemble a zero-dependency standalone Windows buyer release.

Produces:
    dist/inkpress-studio-win64/          self-contained folder (bundles Python + Tkinter)
    dist/inkpress-studio-win64.zip       ready-to-sell buyer download archive
    dist/inkpress-studio-win64/installer/inkpress-setup.iss   Inno Setup installer script

Usage:
    python bundle_release.py               # full standalone bundle + ZIP
    python bundle_release.py --app-only    # lightweight app bundle without copying Python stdlib
"""
import argparse
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import build_exe
from inkpress_lib import __version__

HERE = Path(__file__).resolve().parent
DIST_ROOT = HERE / "dist"
BUNDLE_NAME = "inkpress-studio-win64"

_EXCLUDED_STDLIB_DIRS = frozenset(
    {
        "site-packages",
        "test",
        "tests",
        "idlelib",
        "turtledemo",
        "ensurepip",
        "venv",
        "lib2to3",
        "pydoc_data",
        "distutils",
        "__pycache__",
    }
)


def _inno_setup_script(version):
    return f"""; Inno Setup 6 Installer Script for Inkpress Studio {version}
; Compile with: ISCC.exe installer\\inkpress-setup.iss
; Optional code signing: pass /S"signtool=signtool.exe sign /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 $f"

[Setup]
AppId={{{{8F2D6B4A-4C71-4E2B-9A15-7D9C0E1B3A42}}}}
AppName=Inkpress Formatting Studio
AppVersion={version}
AppPublisher=Built By Josh Studio
AppPublisherURL=https://builtbyjoshstudio.com
DefaultDirName={{autopf}}\\Inkpress Studio
DefaultGroupName=Inkpress Studio
SetupIconFile=..\\inkpress.ico
UninstallDisplayIcon={{app}}\\inkpress.exe
Compression=lzma2/ultra64
SolidCompression=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
WizardStyle=modern
PrivilegesRequired=lowest
OutputDir=..\\..
OutputBaseFilename=Inkpress-Studio-{version}-Setup

[Tasks]
Name: "desktopicon"; Description: "Create a &Desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Files]
Source: "..\\*"; DestDir: "{{app}}"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "installer\\*"

[Icons]
Name: "{{group}}\\Inkpress Formatting Studio"; Filename: "{{app}}\\inkpress.exe"
Name: "{{autodesktop}}\\Inkpress Formatting Studio"; Filename: "{{app}}\\inkpress.exe"; Tasks: desktopicon

[Run]
Filename: "{{app}}\\inkpress.exe"; Description: "Launch Inkpress Formatting Studio"; Flags: nowait postinstall skipifsilent
"""


def _buyer_readme(version):
    return f"""Inkpress Formatting Studio {version} — Quick Start Guide
=======================================================

Thank you for downloading Inkpress Formatting Studio by Built By Josh Studio!

1. LAUNCHING THE STUDIO
   Double-click `inkpress.exe` to start the desktop studio. No Python or extra
   runtime installation is required.

2. FORMATTING YOUR BOOK
   - Drag and drop a Word (.docx), Markdown (.md), or plain text (.txt)
     manuscript directly onto the studio window (or click "Load Sample").
   - Fill in Book & Cover details, optional Front & Back Matter (Dedication,
     Epigraph, Copyright, Also By, About the Author, Reader Magnet CTA), and
     choose your Typography Tier, Font Pairing, Drop Letter, and Colored Border.
   - Press `Ctrl+S` ("Save Project") at any time to save per-book settings next
     to your manuscript (`<book>.inkpress.json`).
   - Click `Format Book` (`F5`) to generate your EPUB 3 ebook, KDP-ready Print
     Interior (HTML & PDF), and standalone Web Reader page.

3. UNLOCKING STUDIO PRO
   Click the `FREE STARTER · Unlock Pro` badge in the top header bar and paste
   your `INKP-XXXX-XXXX-XXXX-XXXX` license key. Verification is 100% offline.
"""


def _copy_python_runtime(dest_runtime):
    """Copy a minimal, self-contained Python + Tkinter runtime into dest_runtime."""
    base_prefix = Path(sys.base_prefix).resolve()
    dest_runtime = Path(dest_runtime)
    dest_runtime.mkdir(parents=True, exist_ok=True)

    # Copy top-level executables and runtime DLLs (python.exe, pythonw.exe, python3*.dll, vcruntime*.dll)
    for item in base_prefix.iterdir():
        if not item.is_file():
            continue
        lower = item.name.lower()
        if lower in ("python.exe", "pythonw.exe") or lower.endswith(".dll"):
            shutil.copy2(item, dest_runtime / item.name)

    # Copy extension modules & Tcl/Tk DLLs (DLLs/)
    dlls_src = base_prefix / "DLLs"
    if dlls_src.is_dir():
        shutil.copytree(
            dlls_src,
            dest_runtime / "DLLs",
            ignore=shutil.ignore_patterns("*.pdb", "__pycache__", "_test*"),
            dirs_exist_ok=True,
        )

    # Copy Tcl/Tk script libraries (tcl/) required by Tkinter
    tcl_src = base_prefix / "tcl"
    if tcl_src.is_dir():
        shutil.copytree(
            tcl_src,
            dest_runtime / "tcl",
            ignore=shutil.ignore_patterns("tzdata", "demos", "*.lib"),
            dirs_exist_ok=True,
        )

    # Copy standard library (Lib/), excluding site-packages and heavy test suites
    lib_src = base_prefix / "Lib"
    lib_dst = dest_runtime / "Lib"
    if lib_src.is_dir():
        def _ignore_lib(directory, contents):
            rel = Path(directory).resolve()
            ignored = []
            for name in contents:
                if name in ("__pycache__",) or name.endswith((".pyc", ".pyo", ".pdb")):
                    ignored.append(name)
                elif rel == lib_src.resolve() and name in _EXCLUDED_STDLIB_DIRS:
                    ignored.append(name)
            return ignored

        shutil.copytree(lib_src, lib_dst, ignore=_ignore_lib, dirs_exist_ok=True)


def _maybe_codesign(exe_path):
    """Sign exe_path with signtool.exe if INKPRESS_SIGN_CERT_SHA1 is configured."""
    thumbprint = os.environ.get("INKPRESS_SIGN_CERT_SHA1", "").strip()
    if not thumbprint:
        return False
    signtool = shutil.which("signtool") or shutil.which("signtool.exe")
    if not signtool:
        return False
    cmd = [
        signtool,
        "sign",
        "/sha1",
        thumbprint,
        "/fd",
        "SHA256",
        "/tr",
        "http://timestamp.digicert.com",
        "/td",
        "SHA256",
        str(exe_path),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return proc.returncode == 0


def build_bundle(out_root=DIST_ROOT, include_runtime=True, create_zip=True):
    """Assemble dist/inkpress-studio-win64/ and optional .zip archive."""
    out_root = Path(out_root)
    bundle_dir = out_root / BUNDLE_NAME
    if bundle_dir.exists():
        shutil.rmtree(bundle_dir)
    bundle_dir.mkdir(parents=True, exist_ok=True)

    # 1. Portable icon + launcher executable (no local developer paths baked in)
    ico_path = build_exe.write_icon(bundle_dir / "inkpress.ico")
    exe_path = build_exe.build_exe(
        exe_path=bundle_dir / "inkpress.exe",
        ico_path=ico_path,
        portable=True,
    )
    _maybe_codesign(exe_path)

    # 2. Core studio application & library
    for filename in ("inkpress_app.py", "inkpress.py"):
        shutil.copy2(HERE / filename, bundle_dir / filename)

    shutil.copytree(
        HERE / "inkpress_lib",
        bundle_dir / "inkpress_lib",
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        dirs_exist_ok=True,
    )

    # 3. Sample manuscript
    ms_dir = bundle_dir / "manuscripts"
    ms_dir.mkdir(parents=True, exist_ok=True)
    sample = HERE / "manuscripts" / "sample-manuscript.md"
    if sample.is_file():
        shutil.copy2(sample, ms_dir / sample.name)

    # 4. Buyer README + Inno Setup script
    (bundle_dir / "README.txt").write_text(_buyer_readme(__version__), encoding="utf-8")
    inst_dir = bundle_dir / "installer"
    inst_dir.mkdir(parents=True, exist_ok=True)
    (inst_dir / "inkpress-setup.iss").write_text(
        _inno_setup_script(__version__), encoding="utf-8"
    )

    # 5. Embedded standalone Python + Tkinter runtime
    if include_runtime:
        _copy_python_runtime(bundle_dir / "runtime")

    zip_path = None
    if create_zip:
        zip_path = out_root / f"{BUNDLE_NAME}.zip"
        if zip_path.exists():
            zip_path.unlink()
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for file_path in sorted(bundle_dir.rglob("*")):
                if file_path.is_file():
                    arcname = f"{BUNDLE_NAME}/{file_path.relative_to(bundle_dir).as_posix()}"
                    zf.write(file_path, arcname)

    return bundle_dir, zip_path


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Build a zero-dependency Windows distribution of Inkpress Studio."
    )
    parser.add_argument(
        "--app-only",
        action="store_true",
        help="skip copying the embedded Python stdlib/Tkinter runtime (lightweight test bundle)",
    )
    parser.add_argument(
        "--no-zip",
        action="store_true",
        help="only build the folder without compressing a .zip archive",
    )
    parser.add_argument(
        "--out",
        default=str(DIST_ROOT),
        help="destination directory (default: dist/)",
    )
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])
    bundle_dir, zip_path = build_bundle(
        out_root=args.out,
        include_runtime=not args.app_only,
        create_zip=not args.no_zip,
    )
    print(f"Built standalone bundle: {bundle_dir}")
    if zip_path and zip_path.is_file():
        mb = zip_path.stat().st_size / (1024 * 1024)
        print(f"Built buyer ZIP archive: {zip_path} ({mb:.1f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
