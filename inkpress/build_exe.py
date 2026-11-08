#!/usr/bin/env python3
"""
build_exe.py — generate inkpress.ico and compile the native Windows inkpress.exe launcher.

Uses the built-in Windows .NET compiler (csc.exe) with /target:winexe so
double-clicking inkpress.exe opens the desktop app directly with no console
window flash, a custom icon, taskbar pinning, and drag-and-drop file support.
"""
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ICO_PATH = HERE / "inkpress.ico"
EXE_PATH = HERE / "inkpress.exe"

_CSC_CANDIDATES = (
    r"C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe",
    r"C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe",
    "csc",
)


def _render_icon_frame(size):
    """Render one size x size 32-bit BGRA DIB frame for a Windows .ico file."""
    pixels = bytearray(size * size * 4)

    def set_px(x, y, r, g, b, a=255):
        if 0 <= x < size and 0 <= y < size:
            # DIB rows are stored bottom-up.
            row = (size - 1 - y) * size + x
            idx = row * 4
            pixels[idx] = b
            pixels[idx + 1] = g
            pixels[idx + 2] = r
            pixels[idx + 3] = a

    pad = max(1, size // 16)
    corner = max(2, size // 8)

    # Rounded dark charcoal tile (#191817)
    for y in range(pad, size - pad):
        for x in range(pad, size - pad):
            dx = min(x - pad, (size - 1 - pad) - x)
            dy = min(y - pad, (size - 1 - pad) - y)
            if dx < corner and dy < corner:
                if (corner - dx) ** 2 + (corner - dy) ** 2 > corner ** 2:
                    continue
            set_px(x, y, 0x19, 0x18, 0x17, 255)

    # Inner ember frame (#8a4b26)
    fpad = max(3, size // 7)
    for x in range(fpad, size - fpad):
        set_px(x, fpad, 0x8A, 0x4B, 0x26)
        set_px(x, size - 1 - fpad, 0x8A, 0x4B, 0x26)
    for y in range(fpad, size - fpad):
        set_px(fpad, y, 0x8A, 0x4B, 0x26)
        set_px(size - 1 - fpad, y, 0x8A, 0x4B, 0x26)

    # Cream page sheet (#fdfbf7)
    px0, px1 = size // 4, size - (size // 4)
    py0, py1 = size // 5, size - (size // 5)
    for y in range(py0, py1):
        for x in range(px0, px1):
            set_px(x, y, 0xFD, 0xFB, 0xF7)

    # Ember chapter header bar (#8a4b26) inside the sheet
    lx0, lx1 = px0 + max(2, size // 14), px1 - max(2, size // 14)
    hy0 = py0 + max(3, size // 10)
    hy1 = hy0 + max(2, size // 16)
    for y in range(hy0, min(hy1, py1 - 2)):
        for x in range(lx0, lx1):
            set_px(x, y, 0x8A, 0x4B, 0x26)

    # Typographic body lines (#191817)
    step = max(3, size // 10)
    thickness = max(1, size // 32)
    y = hy1 + step
    while y + thickness < py1 - max(2, size // 12):
        end_x = lx1 if (y // step) % 3 != 0 else lx1 - max(2, (lx1 - lx0) // 4)
        for ty in range(y, y + thickness):
            for x in range(lx0, end_x):
                set_px(x, ty, 0x19, 0x18, 0x17)
        y += step

    and_row_bytes = ((size + 31) // 32) * 4
    and_mask = bytes(and_row_bytes * size)

    header = struct.pack(
        "<IIIHHIIIIII",
        40,
        size,
        size * 2,
        1,
        32,
        0,
        len(pixels) + len(and_mask),
        0,
        0,
        0,
        0,
    )
    return header + bytes(pixels) + and_mask


def write_icon(path=ICO_PATH):
    """Write a multi-resolution Windows .ico file (16x16, 32x32, 48x48, 64x64)."""
    path = Path(path)
    sizes = (16, 32, 48, 64)
    frames = [_render_icon_frame(s) for s in sizes]

    out = bytearray(struct.pack("<HHH", 0, 1, len(sizes)))
    offset = 6 + 16 * len(sizes)
    for size, frame in zip(sizes, frames):
        out.extend(
            struct.pack(
                "<BBBBHHII",
                size if size < 256 else 0,
                size if size < 256 else 0,
                0,
                0,
                1,
                32,
                len(frame),
                offset,
            )
        )
        offset += len(frame)

    for frame in frames:
        out.extend(frame)

    path.write_bytes(bytes(out))
    return path


def find_csc():
    for candidate in _CSC_CANDIDATES:
        found = shutil.which(candidate)
        if found:
            return found
        if Path(candidate).is_file():
            return str(Path(candidate))
    return None


def _csharp_source(fallback_dir, preferred_pythonw):
    esc_dir = str(fallback_dir).replace("\\", "\\\\").replace('"', '\\"')
    esc_pyw = str(preferred_pythonw).replace("\\", "\\\\").replace('"', '\\"')
    return f"""using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Reflection;
using System.Text;
using System.Windows.Forms;

[assembly: AssemblyTitle("inkpress")]
[assembly: AssemblyProduct("inkpress")]
[assembly: AssemblyVersion("1.0.0.0")]

internal static class Program
{{
    private static string QuoteArg(string arg)
    {{
        if (string.IsNullOrEmpty(arg)) return "\\"\\"";
        if (arg.IndexOfAny(new char[] {{ ' ', '\\t', '\\"' }}) < 0) return arg;
        return "\\"" + arg.Replace("\\"", "\\\\\\"") + "\\"";
    }}

    private static string FindScript()
    {{
        string baseDir = AppDomain.CurrentDomain.BaseDirectory;
        string local = Path.Combine(baseDir, "inkpress_app.py");
        if (File.Exists(local)) return local;

        string fallback = Path.Combine("{esc_dir}", "inkpress_app.py");
        if (File.Exists(fallback)) return fallback;
        return null;
    }}

    private static string FindPython()
    {{
        string preferred = "{esc_pyw}";
        if (!string.IsNullOrEmpty(preferred) && File.Exists(preferred)) return preferred;
        return "pythonw.exe";
    }}

    [STAThread]
    private static int Main(string[] args)
    {{
        string script = FindScript();
        if (script == null)
        {{
            MessageBox.Show(
                "Could not find inkpress_app.py next to inkpress.exe.",
                "inkpress",
                MessageBoxButtons.OK,
                MessageBoxIcon.Error
            );
            return 1;
        }}

        StringBuilder sb = new StringBuilder();
        sb.Append(QuoteArg(script));
        foreach (string a in args)
        {{
            sb.Append(' ');
            sb.Append(QuoteArg(a));
        }}

        string[] candidates = new string[] {{ FindPython(), "pyw.exe", "pythonw.exe", "python.exe" }};
        foreach (string exe in candidates)
        {{
            try
            {{
                ProcessStartInfo psi = new ProcessStartInfo();
                psi.FileName = exe;
                psi.Arguments = sb.ToString();
                psi.WorkingDirectory = Path.GetDirectoryName(script);
                psi.UseShellExecute = false;
                psi.CreateNoWindow = true;
                Process proc = Process.Start(psi);
                if (proc != null) return 0;
            }}
            catch
            {{
            }}
        }}

        MessageBox.Show(
            "Could not find Python (pythonw.exe) to start inkpress.",
            "inkpress",
            MessageBoxButtons.OK,
            MessageBoxIcon.Error
        );
        return 1;
    }}
}}
"""


def build_exe(exe_path=EXE_PATH, ico_path=ICO_PATH):
    """Generate inkpress.ico and compile inkpress.exe. Returns exe_path."""
    ico_path = write_icon(ico_path)
    exe_path = Path(exe_path)

    csc = find_csc()
    if not csc:
        raise RuntimeError("C# compiler (csc.exe) not found on this machine")

    py_exe = Path(sys.executable).resolve()
    pyw_candidate = py_exe.with_name("pythonw.exe")
    preferred_pyw = str(pyw_candidate if pyw_candidate.is_file() else py_exe)

    with tempfile.TemporaryDirectory() as tmp:
        cs_file = Path(tmp) / "Launcher.cs"
        cs_file.write_text(_csharp_source(HERE, preferred_pyw), encoding="utf-8")
        cmd = [
            csc,
            "/nologo",
            "/optimize+",
            "/target:winexe",
            f"/out:{exe_path}",
            f"/win32icon:{ico_path}",
            "/r:System.Windows.Forms.dll",
            str(cs_file),
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if proc.returncode != 0 or not exe_path.is_file():
            detail = (proc.stderr or proc.stdout or "").strip()
            raise RuntimeError(f"csc.exe failed: {detail}")

    return exe_path


if __name__ == "__main__":
    built = build_exe()
    print(f"Built {built} ({built.stat().st_size:,} bytes)")
