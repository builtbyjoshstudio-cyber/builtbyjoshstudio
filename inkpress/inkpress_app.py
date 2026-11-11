#!/usr/bin/env python3
"""
inkpress_app.py — the inkpress Editorial Studio desktop app.

A modern dark-obsidian two-column studio over the same pipeline the CLI uses:
  - Single-instance Win32 mutex so clicking/double-clicking taskbar or desktop
    shortcuts focuses the existing studio window instead of opening duplicates.
  - Left column: interactive drag-and-drop zone + segmented pill navigation
    (Book Details / Style & Borders / Export & Outputs) and live studio telemetry.
  - Right column: hero-sized responsive two-page spread preview (Typographic
    Framed Cover + Chapter 1 Opener with customizable colored borders and Tier 2+
    drop letters) that scales dynamically when maximized, plus a compact bottom
    Chapter & KDP Inspector / Build Console dock.
"""
import json
import os
import platform
import queue
import subprocess
import sys
import threading
import traceback
from datetime import date
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import colorchooser, filedialog, ttk
except ImportError:  # pragma: no cover - only on a Python built without Tk
    sys.stderr.write(
        "This build of Python has no Tkinter, so the desktop app cannot start.\n"
        "Reinstall Python from python.org (the standard installer includes it),\n"
        "or use the command line version instead:  .\\inkpress.ps1 draft.md\n"
    )
    sys.exit(1)

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from inkpress_lib import __version__, editions, inline  # noqa: E402
from inkpress_lib import license as license_mod  # noqa: E402
from inkpress_lib import manuscript as ms  # noqa: E402
from inkpress_lib import (  # noqa: E402
    pipeline,
    project,
    render_print,
    structure,
    validate,
)

SAMPLE_PATH = HERE / "manuscripts" / "sample-manuscript.md"
PREFS_PATH = Path.home() / ".inkpress_prefs.json"

TIER_CHOICES = [editions.TIER_LABELS[key] for key in editions.TIERS]
TIER_BY_LABEL = {editions.TIER_LABELS[key]: key for key in editions.TIERS}

EDITION_CHOICES = [editions.EDITION_LABELS[key] for key in editions.EDITIONS]
EDITION_BY_LABEL = {editions.EDITION_LABELS[key]: key for key in editions.EDITIONS}

BORDER_STYLE_CHOICES = [
    editions.BORDER_STYLE_LABELS[key] for key in editions.BORDER_STYLES
]
BORDER_STYLE_BY_LABEL = {
    editions.BORDER_STYLE_LABELS[key]: key for key in editions.BORDER_STYLES
}

DROP_CAP_STYLE_CHOICES = [
    editions.DROP_CAP_STYLE_LABELS[key] for key in editions.DROP_CAP_STYLES
]
DROP_CAP_STYLE_BY_LABEL = {
    editions.DROP_CAP_STYLE_LABELS[key]: key for key in editions.DROP_CAP_STYLES
}
DROP_LETTER_CHOICES = ["Auto (1st)"] + [
    chr(c) for c in range(ord("A"), ord("Z") + 1)
]

FONT_PAIRING_CHOICES = [
    editions.FONT_PAIRING_LABELS[key] for key in editions.FONT_PAIRINGS
]
FONT_PAIRING_BY_LABEL = {
    editions.FONT_PAIRING_LABELS[key]: key for key in editions.FONT_PAIRINGS
}

TRIM_CHOICES = ("6x9", "5.5x8.5", "5.25x8", "5x8")
_TRIM_ASPECT = {
    "6x9": 6.0 / 9.0,
    "5.5x8.5": 5.5 / 8.5,
    "5.25x8": 5.25 / 8.0,
    "5x8": 5.0 / 8.0,
}

_WORDS_PER_PAGE = {
    "6x9": 320,
    "5.5x8.5": 275,
    "5.25x8": 250,
    "5x8": 235,
}

TARGET_LABELS = (
    ("epub", "Ebook (EPUB 3)", "Kindle, Kobo, Apple Books (with framed cover)"),
    ("print", "Print interior (HTML)", "Paged-media paperback layout"),
    ("site", "Web reader page (HTML)", "Standalone or site-matched article"),
)

OUTPUT_NAMES = {
    "site": "Web page",
    "epub": "Ebook (EPUB)",
    "print": "Print HTML",
    "pdf": "Print PDF",
    "package": "Buyer ZIP",
}

META_FIELDS = (
    ("title", "Title"),
    ("subtitle", "Subtitle"),
    ("author", "Author"),
    ("publisher", "Publisher"),
    ("date", "Date"),
    ("isbn", "ISBN"),
    ("description", "Description"),
    ("dedication", "Dedication"),
    ("epigraph", "Epigraph"),
    ("copyright", "Copyright"),
    ("also_by", "Also By"),
    ("acknowledgments", "Acknowledgments"),
    ("about_author", "About the Author"),
    ("newsletter_cta", "Newsletter CTA"),
    ("newsletter_url", "Newsletter URL"),
)

MATTER_SECTIONS = (
    ("dedication", "Dedication", "Centered italic page after Copyright (supports multiple lines)."),
    ("epigraph", "Epigraph", "Opening quotation page before Chapter 1."),
    ("copyright", "Copyright", "Leave blank for an automatic © page (+ ISBN if entered)."),
    ("also_by", "Also By", "Front-matter list of your other books, one title per line."),
    ("acknowledgments", "Acknowledgments", "Back-matter acknowledgments section."),
    ("about_author", "About Author", "Back-matter author biography."),
    ("newsletter_cta", "Reader CTA", "End-of-book reader magnet / mailing list call-to-action."),
)

# Modern Dark Obsidian Studio Palette
BG_APP = "#0D0F14"
BG_CARD = "#141821"
BG_SUBTLE = "#1C2230"
BG_STAGE = "#0A0C10"
BG_PILL_TROUGH = "#0E1118"
BG_PILL_ACTIVE = "#252E42"
BORDER_CARD = "#232A3B"
BORDER_INPUT = "#2D364B"
INK_DARK = "#F4F6FA"
INK_BODY = "#D0D7E6"
INK_MUTED = "#7E8B9F"
ACCENT_CRIMSON = "#E04F44"
ACCENT_CRIMSON_HOVER = "#F26157"

PAD = 10
_WNDPROC_REFS = []
_SINGLE_INSTANCE_HANDLE = None


def _focus_existing_studio_window():
    """Find an already-open inkpress Studio window and bring it to the foreground."""
    if platform.system() != "Windows":
        return False
    try:
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.windll.user32
        WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        found = [None]

        def _enum_cb(hwnd, _lparam):
            if not user32.IsWindowVisible(hwnd):
                return True
            buf = ctypes.create_unicode_buffer(256)
            if user32.GetWindowTextW(hwnd, buf, 256) > 0:
                title = buf.value
                if (
                    title.lower().startswith("inkpress ")
                    and "formatting studio" in title.lower()
                ):
                    found[0] = hwnd
                    return False
            return True

        cb_ref = WNDENUMPROC(_enum_cb)
        user32.EnumWindows(cb_ref, 0)
        if found[0]:
            if user32.IsIconic(found[0]):
                user32.ShowWindow(found[0], 9)  # SW_RESTORE
            user32.SetForegroundWindow(found[0])
            return True
    except Exception:  # noqa: BLE001
        pass
    return False


def _acquire_single_instance_lock():
    """Acquire a process-wide Win32 named mutex so clicking taskbar links never opens twice."""
    global _SINGLE_INSTANCE_HANDLE
    if platform.system() != "Windows":
        return True
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        kernel32.CreateMutexW.argtypes = [
            ctypes.c_void_p,
            ctypes.c_int,
            ctypes.c_wchar_p,
        ]
        kernel32.CreateMutexW.restype = ctypes.c_void_p
        handle = kernel32.CreateMutexW(
            None, False, "Local\\BuiltByJoshStudio_Inkpress_SingleInstance"
        )
        last_err = kernel32.GetLastError()
        if last_err == 183:  # ERROR_ALREADY_EXISTS
            _focus_existing_studio_window()
            if handle:
                kernel32.CloseHandle(handle)
            return False
        _SINGLE_INSTANCE_HANDLE = handle
        return True
    except Exception:  # noqa: BLE001
        return True


def _apply_windows_dark_titlebar(root):
    """Enable Windows 11/10 immersive dark mode on the native window titlebar."""
    if platform.system() != "Windows":
        return
    try:
        import ctypes

        root.update_idletasks()
        frame_hex = root.wm_frame()
        hwnd = (
            int(frame_hex, 16)
            if frame_hex and frame_hex != "0x0"
            else ctypes.windll.user32.GetParent(root.winfo_id())
        )
        if not hwnd:
            hwnd = root.winfo_id()
        val = ctypes.c_int(1)
        # DWMWA_USE_IMMERSIVE_DARK_MODE = 20 (fallback 19 on older Win10 builds)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, 20, ctypes.byref(val), ctypes.sizeof(val)
        )
    except Exception:  # noqa: BLE001
        pass


def _enable_windows_file_drop(root, on_drop_callback):
    """Enable native Windows Explorer file drag-and-drop onto the Tk window via Win32 WM_DROPFILES."""
    if platform.system() != "Windows":
        return False
    if getattr(root, "_inkpress_drop_enabled", False):
        return True
    try:
        import ctypes
        from ctypes import wintypes

        WM_DROPFILES = 0x0233
        WM_NCDESTROY = 0x0082
        GWL_WNDPROC = -4
        MSGFLT_ALLOW = 1

        LRESULT = ctypes.c_ssize_t
        WNDPROC = ctypes.WINFUNCTYPE(
            LRESULT,
            wintypes.HWND,
            wintypes.UINT,
            wintypes.WPARAM,
            wintypes.LPARAM,
        )

        user32 = ctypes.windll.user32
        shell32 = ctypes.windll.shell32

        user32.SetWindowLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int, WNDPROC]
        user32.SetWindowLongPtrW.restype = ctypes.c_void_p
        user32.CallWindowProcW.argtypes = [
            ctypes.c_void_p,
            wintypes.HWND,
            wintypes.UINT,
            wintypes.WPARAM,
            wintypes.LPARAM,
        ]
        user32.CallWindowProcW.restype = LRESULT
        shell32.DragAcceptFiles.argtypes = [wintypes.HWND, wintypes.BOOL]
        shell32.DragQueryFileW.argtypes = [
            ctypes.c_void_p,
            wintypes.UINT,
            wintypes.LPWSTR,
            wintypes.UINT,
        ]
        shell32.DragQueryFileW.restype = wintypes.UINT
        shell32.DragFinish.argtypes = [ctypes.c_void_p]

        root.update_idletasks()
        frame_hex = root.wm_frame()
        hwnd = (
            int(frame_hex, 16)
            if frame_hex and frame_hex != "0x0"
            else user32.GetParent(root.winfo_id())
        )
        if not hwnd:
            hwnd = root.winfo_id()

        try:
            user32.ChangeWindowMessageFilterEx(hwnd, WM_DROPFILES, MSGFLT_ALLOW, None)
            user32.ChangeWindowMessageFilterEx(hwnd, 0x0049, MSGFLT_ALLOW, None)
        except Exception:  # noqa: BLE001
            pass

        old_wndproc = [None]

        def _wnd_proc(h_wnd, msg, w_param, l_param):
            if msg == WM_DROPFILES:
                hdrop = ctypes.c_void_p(w_param)
                count = shell32.DragQueryFileW(hdrop, 0xFFFFFFFF, None, 0)
                dropped = []
                for idx in range(count):
                    length = shell32.DragQueryFileW(hdrop, idx, None, 0)
                    buf = ctypes.create_unicode_buffer(length + 1)
                    shell32.DragQueryFileW(hdrop, idx, buf, length + 1)
                    if buf.value:
                        dropped.append(buf.value)
                shell32.DragFinish(hdrop)
                for path in dropped:
                    root.after(0, lambda p=path: on_drop_callback(p))
                return 0
            res = user32.CallWindowProcW(old_wndproc[0], h_wnd, msg, w_param, l_param)
            if msg == WM_NCDESTROY and proc_ref in _WNDPROC_REFS:
                _WNDPROC_REFS.remove(proc_ref)
            return res

        proc_ref = WNDPROC(_wnd_proc)
        _WNDPROC_REFS.append(proc_ref)
        old_wndproc[0] = user32.SetWindowLongPtrW(hwnd, GWL_WNDPROC, proc_ref)
        shell32.DragAcceptFiles(hwnd, True)
        root._inkpress_drop_enabled = True
        return True
    except Exception:  # noqa: BLE001
        return False


def estimate_kdp_stats(word_count, chapter_count, trim="6x9"):
    """Estimate paperback page count, KDP inner gutter, and cream spine width."""
    wpp = _WORDS_PER_PAGE.get(str(trim).strip().lower(), 300)
    prose_pages = max(1, round(word_count / float(wpp))) if word_count > 0 else 0
    front_pages = 4 if chapter_count > 1 else 2
    chapter_overhead = max(1, round(chapter_count * 0.6))
    total_pages = prose_pages + front_pages + chapter_overhead if word_count > 0 else 0
    if total_pages % 2 == 1:
        total_pages += 1
    spine_in = round(total_pages * 0.0025, 3)
    gutter = render_print._default_gutter(word_count)
    return {
        "pages": total_pages,
        "spine_in": spine_in,
        "gutter": gutter,
    }


def open_folder(path):
    """Open a folder or file in the system shell."""
    path = Path(path)
    if not path.exists():
        return False
    system = platform.system()
    try:
        if system == "Windows":
            os.startfile(str(path))  # noqa: S606 - intended shell open
        elif system == "Darwin":
            subprocess.run(["open", str(path)], check=False)
        else:
            subprocess.run(["xdg-open", str(path)], check=False)
        return True
    except OSError:
        return False


def _configure_studio_theme(root):
    """Apply a sleek modern dark-obsidian studio theme over ttk."""
    root.configure(bg=BG_APP)
    root.option_add("*TCombobox*Listbox*Background", "#181D29")
    root.option_add("*TCombobox*Listbox*Foreground", INK_DARK)
    root.option_add("*TCombobox*Listbox*selectBackground", ACCENT_CRIMSON)
    root.option_add("*TCombobox*Listbox*selectForeground", "#FFFFFF")
    root.option_add("*TCombobox*Listbox*Font", ("Segoe UI", 9))

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure(
        ".",
        background=BG_APP,
        foreground=INK_BODY,
        borderwidth=0,
        focusthickness=0,
        font=("Segoe UI", 9),
    )
    style.configure("TFrame", background=BG_APP)
    style.configure("Card.TFrame", background=BG_CARD)
    style.configure(
        "TLabel", background=BG_CARD, foreground=INK_BODY, font=("Segoe UI", 9)
    )
    style.configure(
        "Muted.TLabel", background=BG_CARD, foreground=INK_MUTED, font=("Segoe UI", 8)
    )
    style.configure(
        "Section.TLabel",
        background=BG_CARD,
        foreground="#94A3B8",
        font=("Segoe UI", 8, "bold"),
    )
    style.configure(
        "TCheckbutton",
        background=BG_CARD,
        foreground=INK_DARK,
        indicatorbackground=BG_SUBTLE,
        indicatorforeground=ACCENT_CRIMSON,
        indicatorrelief="flat",
        font=("Segoe UI", 9, "bold"),
    )
    style.map(
        "TCheckbutton",
        background=[("active", BG_CARD)],
        indicatorbackground=[
            ("selected", ACCENT_CRIMSON),
            ("active", "#263044"),
            ("!selected", BG_SUBTLE),
        ],
    )

    style.configure(
        "TEntry",
        fieldbackground=BG_SUBTLE,
        foreground=INK_DARK,
        insertcolor=INK_DARK,
        bordercolor=BORDER_INPUT,
        lightcolor=BG_SUBTLE,
        darkcolor=BG_SUBTLE,
        borderwidth=1,
        relief="flat",
        padding=(7, 5),
    )
    style.map(
        "TEntry",
        bordercolor=[("focus", ACCENT_CRIMSON)],
        fieldbackground=[("readonly", BG_SUBTLE), ("disabled", "#12161F")],
    )

    style.configure(
        "TCombobox",
        fieldbackground=BG_SUBTLE,
        background="#252D3F",
        foreground=INK_DARK,
        bordercolor=BORDER_INPUT,
        lightcolor=BG_SUBTLE,
        darkcolor=BG_SUBTLE,
        arrowcolor=INK_BODY,
        arrowsize=12,
        borderwidth=1,
        relief="flat",
        padding=(7, 4),
    )
    style.map(
        "TCombobox",
        fieldbackground=[
            ("readonly", BG_SUBTLE),
            ("disabled", "#11151E"),
        ],
        background=[
            ("readonly", "#252D3F"),
            ("active", "#2E384E"),
            ("disabled", "#141821"),
        ],
        foreground=[
            ("readonly", INK_DARK),
            ("disabled", "#4B5565"),
        ],
        arrowcolor=[
            ("disabled", "#4B5565"),
            ("active", "#FFFFFF"),
        ],
        selectbackground=[("readonly", BG_SUBTLE)],
        selectforeground=[("readonly", INK_DARK)],
    )

    style.configure(
        "TButton",
        background="#22293A",
        foreground=INK_DARK,
        bordercolor="#2F384E",
        lightcolor="#22293A",
        darkcolor="#22293A",
        borderwidth=1,
        relief="flat",
        focusthickness=0,
        padding=(12, 6),
        font=("Segoe UI", 9, "bold"),
    )
    style.map(
        "TButton",
        background=[("active", "#2C354B"), ("disabled", "#151923")],
        foreground=[("disabled", "#4B5565")],
        bordercolor=[("active", "#3D4966"), ("disabled", "#1D2230")],
    )

    style.configure(
        "Primary.TButton",
        background=ACCENT_CRIMSON,
        foreground="#FFFFFF",
        bordercolor=ACCENT_CRIMSON,
        lightcolor=ACCENT_CRIMSON,
        darkcolor=ACCENT_CRIMSON,
        borderwidth=0,
        relief="flat",
        padding=(20, 7),
        font=("Segoe UI", 9, "bold"),
    )
    style.map(
        "Primary.TButton",
        background=[("active", ACCENT_CRIMSON_HOVER), ("disabled", "#4A2624")],
        foreground=[("disabled", "#8E6F6D")],
    )

    # Hide native 1990s protruding notebook tabs; we render modern segmented pill bars
    style.configure(
        "Hidden.TNotebook",
        background=BG_CARD,
        borderwidth=0,
        tabmargins=(0, 0, 0, 0),
    )
    style.layout("Hidden.TNotebook.Tab", [])

    style.layout("Treeview", [("Treeview.treearea", {"sticky": "nswe"})])
    style.configure(
        "Treeview",
        background=BG_CARD,
        fieldbackground=BG_CARD,
        foreground=INK_BODY,
        bordercolor=BG_CARD,
        lightcolor=BG_CARD,
        darkcolor=BG_CARD,
        rowheight=26,
        borderwidth=0,
        relief="flat",
        font=("Segoe UI", 9),
    )
    style.configure(
        "Treeview.Heading",
        background="#1C2230",
        foreground="#94A3B8",
        relief="flat",
        borderwidth=0,
        padding=(8, 5),
        font=("Segoe UI", 8, "bold"),
    )
    style.map(
        "Treeview",
        background=[("selected", "#232B3E")],
        foreground=[("selected", "#FFFFFF")],
    )
    style.map(
        "Treeview.Heading",
        background=[("active", "#232B3E")],
    )

    style.layout(
        "Vertical.TScrollbar",
        [
            (
                "Vertical.Scrollbar.trough",
                {
                    "children": [
                        (
                            "Vertical.Scrollbar.thumb",
                            {"expand": "1", "sticky": "nswe"},
                        )
                    ],
                    "sticky": "ns",
                },
            )
        ],
    )
    style.configure(
        "Vertical.TScrollbar",
        background="#283248",
        troughcolor=BG_CARD,
        bordercolor=BG_CARD,
        lightcolor="#283248",
        darkcolor="#283248",
        relief="flat",
        borderwidth=0,
        width=8,
    )
    style.map(
        "Vertical.TScrollbar",
        background=[("active", "#384664")],
    )

    style.configure(
        "Horizontal.TProgressbar",
        troughcolor="#1A202D",
        background=ACCENT_CRIMSON,
        bordercolor="#1A202D",
        lightcolor=ACCENT_CRIMSON,
        darkcolor=ACCENT_CRIMSON,
        thickness=6,
    )


class _TabDeck(tk.Frame):
    """Borderless modern panel deck with a ttk.Notebook-compatible .select() API."""

    def __init__(self, parent, on_change=None):
        super().__init__(parent, bg=BG_CARD, bd=0, highlightthickness=0)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self._pages = []
        self._active = 0
        self._on_change = on_change

    def add(self, frame, text=""):
        idx = len(self._pages)
        self._pages.append((frame, text))
        frame.grid(row=0, column=0, sticky="nsew")
        if idx == 0:
            frame.tkraise()
        else:
            frame.grid_remove()

    def select(self, idx=None):
        if idx is None:
            return self._active
        idx = int(idx)
        if 0 <= idx < len(self._pages):
            self._active = idx
            for i, (frame, _txt) in enumerate(self._pages):
                if i == idx:
                    frame.grid()
                    frame.tkraise()
                else:
                    frame.grid_remove()
            if self._on_change:
                self._on_change()
        return self._active

    def index(self, item):
        return int(item)


def _make_card(parent, title=None, subtitle=None, pad=12):
    """Create a dark studio panel card with optional header bar."""
    outer = tk.Frame(
        parent,
        bg=BG_CARD,
        highlightthickness=1,
        highlightbackground=BORDER_CARD,
        highlightcolor=BORDER_CARD,
        padx=pad,
        pady=pad,
    )
    if title:
        hdr_row = tk.Frame(outer, bg=BG_CARD)
        hdr_row.grid(row=0, column=0, columnspan=10, sticky="ew", pady=(0, 8))
        tk.Label(
            hdr_row,
            text=title.upper(),
            bg=BG_CARD,
            fg="#94A3B8",
            font=("Segoe UI", 8, "bold"),
            anchor="w",
        ).pack(side="left")
        if subtitle:
            tk.Label(
                hdr_row,
                text=subtitle,
                bg=BG_CARD,
                fg="#5E6B80",
                font=("Segoe UI", 8),
                anchor="e",
            ).pack(side="right")
    return outer


class InkpressApp(ttk.Frame):
    def __init__(self, master, initial_manuscript=None, license_path=None):
        _configure_studio_theme(master)
        super().__init__(master, padding=0)
        self.grid(sticky="nsew")
        master.columnconfigure(0, weight=1)
        master.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.results = queue.Queue()
        self.last_out_dir = None
        self.last_outputs = {}
        self.current_document = None
        self.busy = False
        self._drop_hover = False
        self._preset_buttons = {}
        self._color_swatch_buttons = {}
        self._drop_cap_widgets = []
        self._left_pill_buttons = []
        self._right_pill_buttons = []
        self._matter_pill_buttons = {}
        self._active_matter_key = "dedication"
        self._syncing_matter_text = False

        self.license_path = Path(license_path) if license_path else None
        self.license_info = license_mod.load_saved_license(self.license_path)

        self.manuscript_var = tk.StringVar()
        self.out_var = tk.StringVar(value=str(HERE / "build"))
        self.chrome_var = tk.StringVar()
        self.cover_var = tk.StringVar()
        self.border_color_var = tk.StringVar(value="")
        self.border_style_var = tk.StringVar(
            value=editions.BORDER_STYLE_LABELS["none"]
        )
        self.drop_cap_style_var = tk.StringVar(
            value=editions.DROP_CAP_STYLE_LABELS["none"]
        )
        self.drop_cap_letter_var = tk.StringVar(value=DROP_LETTER_CHOICES[0])
        self.font_pairing_var = tk.StringVar(value=FONT_PAIRING_CHOICES[0])
        self.status_var = tk.StringVar(
            value="Drop a manuscript (.md, .docx, .txt) above or click Load Sample."
        )
        self.kdp_summary_var = tk.StringVar(
            value="Load a manuscript to calculate KDP page count, inner gutter, and spine width."
        )
        self.meta_vars = {key: tk.StringVar() for key, _ in META_FIELDS}
        self.target_vars = {key: tk.BooleanVar(value=True) for key, _, _ in TARGET_LABELS}
        self.pdf_var = tk.BooleanVar(value=bool(render_print.find_pdf_renderer()))
        self.package_var = tk.BooleanVar(value=True)
        self.trim_var = tk.StringVar(value=TRIM_CHOICES[0])
        self.tier_var = tk.StringVar(value=TIER_CHOICES[0])
        self.edition_var = tk.StringVar(value=EDITION_CHOICES[0])

        if not initial_manuscript:
            self._load_prefs()

        self._build_header()

        # Main two-column studio workspace
        body_frame = tk.Frame(self, bg=BG_APP, padx=14, pady=12)
        body_frame.grid(row=1, column=0, sticky="nsew")
        body_frame.columnconfigure(0, weight=4, minsize=440)
        body_frame.columnconfigure(1, weight=7, minsize=520)
        body_frame.rowconfigure(0, weight=1)

        left_col = tk.Frame(body_frame, bg=BG_APP)
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        left_col.columnconfigure(0, weight=1)
        left_col.rowconfigure(1, weight=1)

        right_col = tk.Frame(body_frame, bg=BG_APP)
        right_col.grid(row=0, column=1, sticky="nsew")
        right_col.columnconfigure(0, weight=1)
        # Give the Live Book Spread Preview hero weight so it scales with the window
        right_col.rowconfigure(0, weight=5)
        right_col.rowconfigure(1, weight=2)

        self._build_manuscript_card(left_col, 0)
        self._build_config_tabs(left_col, 1)

        self._build_preview_card(right_col, 0)
        self._build_inspector_and_log(right_col, 1)

        # Persistent bottom studio action bar
        self._build_action_bar(row=2)

        for key in ("title", "subtitle", "author"):
            self.meta_vars[key].trace_add("write", lambda *_args: self._draw_page_preview())
        self.cover_var.trace_add("write", lambda *_args: self._draw_page_preview())

        master.bind("<Control-o>", lambda _e: self._choose_manuscript())
        master.bind("<Control-s>", lambda _e: self._save_project())
        master.bind("<Control-Return>", lambda _e: self._start_build())
        master.bind("<F5>", lambda _e: self._start_build())

        self.after(40, lambda: _apply_windows_dark_titlebar(master))
        self.after(50, lambda: _enable_windows_file_drop(master, self.handle_dropped_file))
        self.after(120, self._drain)

        if initial_manuscript:
            self.manuscript_var.set(str(Path(initial_manuscript).resolve()))
            self._load_manuscript()
        else:
            self._draw_page_preview()

    # ----------------------------------------------------------- preferences

    def _load_prefs(self):
        if not PREFS_PATH.is_file():
            return
        try:
            data = json.loads(PREFS_PATH.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return
        if data.get("author"):
            self.meta_vars["author"].set(str(data["author"]))
        if data.get("publisher"):
            self.meta_vars["publisher"].set(str(data["publisher"]))
        if data.get("trim") in TRIM_CHOICES:
            self.trim_var.set(data["trim"])
        if data.get("tier") in TIER_CHOICES:
            self.tier_var.set(data["tier"])
        if data.get("edition") in EDITION_CHOICES:
            self.edition_var.set(data["edition"])
        if data.get("font_pairing") in FONT_PAIRING_CHOICES:
            self.font_pairing_var.set(data["font_pairing"])
        if data.get("border_style") in BORDER_STYLE_CHOICES:
            self.border_style_var.set(data["border_style"])
        if data.get("border_color"):
            self.border_color_var.set(str(data["border_color"]))
        if data.get("drop_cap_style") in DROP_CAP_STYLE_CHOICES:
            self.drop_cap_style_var.set(data["drop_cap_style"])
        if data.get("drop_cap_letter") in DROP_LETTER_CHOICES:
            self.drop_cap_letter_var.set(data["drop_cap_letter"])
        if data.get("out_dir"):
            self.out_var.set(str(data["out_dir"]))

    def _save_prefs(self):
        data = {
            "author": self.meta_vars["author"].get().strip(),
            "publisher": self.meta_vars["publisher"].get().strip(),
            "trim": self.trim_var.get().strip(),
            "tier": self.tier_var.get(),
            "edition": self.edition_var.get(),
            "font_pairing": self.font_pairing_var.get(),
            "border_style": self.border_style_var.get(),
            "border_color": self.border_color_var.get().strip(),
            "drop_cap_style": self.drop_cap_style_var.get(),
            "drop_cap_letter": self.drop_cap_letter_var.get(),
            "out_dir": self.out_var.get().strip(),
        }
        try:
            PREFS_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except OSError:
            pass

    def is_pro_unlocked(self):
        """Return True when a valid Studio Pro or Founder license key is active."""
        return bool(self.license_info and self.license_info.get("valid"))

    def _refresh_license_badge(self):
        if not hasattr(self, "license_badge_btn"):
            return
        if self.is_pro_unlocked():
            plan = self.license_info.get("plan", "PRO")
            self.license_badge_btn.configure(
                text=f"✦  STUDIO {plan}",
                bg="#133326",
                fg="#34D399",
                activebackground="#194432",
                activeforeground="#34D399",
            )
        else:
            self.license_badge_btn.configure(
                text="FREE STARTER  ·  Unlock Pro",
                bg="#231D2E",
                fg="#C4B5FD",
                activebackground="#2E2540",
                activeforeground="#FFFFFF",
            )

    def _open_license_dialog(self, reason_msg=""):
        """Open a sleek dark Studio Pro offline license activation dialog."""
        dlg = tk.Toplevel(self.winfo_toplevel())
        dlg.title("Inkpress Studio Pro — Offline License")
        dlg.configure(bg=BG_CARD)
        dlg.resizable(False, False)
        dlg.transient(self.winfo_toplevel())
        dlg.grab_set()
        _apply_windows_dark_titlebar(dlg)

        wrap = tk.Frame(dlg, bg=BG_CARD, padx=22, pady=18)
        wrap.pack(fill="both", expand=True)

        tk.Label(
            wrap,
            text="INKPRESS STUDIO PRO",
            bg=BG_CARD,
            fg=INK_DARK,
            font=("Segoe UI", 12, "bold"),
            anchor="w",
        ).pack(fill="x")

        sub_txt = (
            reason_msg
            or "Free Starter exports Tier 1 Clean books. Unlock Studio Pro for Tier 2 & 3 Framed Editions, "
            "custom colored borders, drop letters, font pairings, direct KDP PDF export, and buyer ZIP packages."
        )
        tk.Label(
            wrap,
            text=sub_txt,
            bg=BG_CARD,
            fg=INK_BODY if reason_msg else INK_MUTED,
            justify="left",
            wraplength=420,
            font=("Segoe UI", 9),
        ).pack(fill="x", pady=(6, 14))

        email_var = tk.StringVar(
            value=(self.license_info.get("email", "") if self.license_info else "")
        )
        key_var = tk.StringVar(
            value=(self.license_info.get("key", "") if self.license_info else "")
        )
        feedback_var = tk.StringVar(
            value=(
                f"Active license: {self.license_info['plan']} ({self.license_info['key']})"
                if self.is_pro_unlocked()
                else "100% offline verification — enter your INKP-XXXX-XXXX-XXXX-XXXX key below."
            )
        )

        tk.Label(wrap, text="Buyer Email (optional)", bg=BG_CARD, fg=INK_MUTED, font=("Segoe UI", 8, "bold")).pack(anchor="w")
        ttk.Entry(wrap, textvariable=email_var, width=48).pack(fill="x", pady=(3, 10))

        tk.Label(wrap, text="License Key", bg=BG_CARD, fg=INK_MUTED, font=("Segoe UI", 8, "bold")).pack(anchor="w")
        key_entry = ttk.Entry(wrap, textvariable=key_var, width=48)
        key_entry.pack(fill="x", pady=(3, 8))
        key_entry.focus_set()

        fb_lbl = tk.Label(
            wrap,
            textvariable=feedback_var,
            bg=BG_CARD,
            fg="#34D399" if self.is_pro_unlocked() else INK_MUTED,
            justify="left",
            wraplength=420,
            font=("Segoe UI", 8, "bold"),
        )
        fb_lbl.pack(fill="x", pady=(2, 14))

        btn_row = tk.Frame(wrap, bg=BG_CARD)
        btn_row.pack(fill="x")

        def _do_activate():
            try:
                info = license_mod.save_license(
                    key_var.get(), email=email_var.get(), license_path=self.license_path
                )
            except ValueError as err:
                fb_lbl.configure(fg="#F87171")
                feedback_var.set(str(err))
                return
            self.license_info = info
            self._refresh_license_badge()
            self.write(f"Studio {info['plan']} unlocked ({info['key']}).", "ok")
            dlg.destroy()

        def _do_deactivate():
            license_mod.clear_license(self.license_path)
            self.license_info = None
            self._refresh_license_badge()
            fb_lbl.configure(fg=INK_MUTED)
            feedback_var.set("Returned to Free Starter tier.")

        ttk.Button(btn_row, text="Activate Key", style="Primary.TButton", command=_do_activate).pack(side="left")
        if self.is_pro_unlocked():
            ttk.Button(btn_row, text="Deactivate", command=_do_deactivate).pack(side="left", padx=(8, 0))
        ttk.Button(btn_row, text="Close", command=dlg.destroy).pack(side="right")
        key_entry.bind("<Return>", lambda _e: _do_activate())

        # Founder-only built-in customer key minter (hidden from Free & regular Pro users)
        if self.license_info and self.license_info.get("plan") == "FOUNDER":
            tk.Frame(wrap, bg=BORDER_CARD, height=1).pack(fill="x", pady=(16, 12))
            tk.Label(
                wrap,
                text="FOUNDER TOOLS · MINT CUSTOMER PRO KEY",
                bg=BG_CARD,
                fg="#34D399",
                font=("Segoe UI", 8, "bold"),
                anchor="w",
            ).pack(fill="x")

            mint_email_var = tk.StringVar()
            mint_out_var = tk.StringVar(
                value="Enter a buyer email or order ID and click Mint & Copy."
            )

            mint_row = tk.Frame(wrap, bg=BG_CARD)
            mint_row.pack(fill="x", pady=(6, 6))
            mint_row.columnconfigure(0, weight=1)
            mint_entry = ttk.Entry(mint_row, textvariable=mint_email_var)
            mint_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))

            def _do_mint_customer():
                ident = mint_email_var.get().strip() or "buyer@inkpress"
                minted = license_mod.generate_key(ident, plan="PRO")
                dlg.clipboard_clear()
                dlg.clipboard_append(minted)
                dlg.update_idletasks()
                mint_out_var.set(f"Copied to clipboard:  {minted}")
                self.write(f"Minted customer PRO key for {ident}: {minted} (copied)", "ok")

            ttk.Button(
                mint_row, text="Mint & Copy Key", command=_do_mint_customer
            ).grid(row=0, column=1)
            mint_entry.bind("<Return>", lambda _e: _do_mint_customer())

            tk.Label(
                wrap,
                textvariable=mint_out_var,
                bg=BG_CARD,
                fg=INK_BODY,
                font=("Consolas", 9, "bold"),
                anchor="w",
            ).pack(fill="x")

    # ---------------------------------------------------------------- layout

    def _build_header(self):
        header_wrap = tk.Frame(self, bg="#090B0E")
        header_wrap.grid(row=0, column=0, sticky="ew")
        header_wrap.columnconfigure(0, weight=1)

        banner = tk.Frame(header_wrap, bg="#090B0E", padx=18, pady=10)
        banner.grid(row=0, column=0, sticky="ew")
        banner.columnconfigure(2, weight=1)

        brand_dot = tk.Canvas(
            banner, width=10, height=10, bg="#090B0E", highlightthickness=0
        )
        brand_dot.create_oval(1, 1, 9, 9, fill=ACCENT_CRIMSON, outline="")
        brand_dot.grid(row=0, column=0, sticky="w", padx=(0, 8))

        tk.Label(
            banner,
            text="INKPRESS",
            bg="#090B0E",
            fg=INK_DARK,
            font=("Segoe UI", 12, "bold"),
        ).grid(row=0, column=1, sticky="w")

        tk.Label(
            banner,
            text=f"STUDIO {__version__}",
            bg="#1A202E",
            fg="#94A3B8",
            padx=8,
            pady=2,
            font=("Segoe UI", 7, "bold"),
        ).grid(row=0, column=2, sticky="w", padx=(10, 12))

        self.license_badge_btn = tk.Button(
            banner,
            text="FREE STARTER  ·  Unlock Pro",
            bd=0,
            relief="flat",
            highlightthickness=0,
            padx=10,
            pady=3,
            cursor="hand2",
            font=("Segoe UI", 8, "bold"),
            command=self._open_license_dialog,
        )
        self.license_badge_btn.grid(row=0, column=3, sticky="e", padx=(0, 12))
        self._refresh_license_badge()

        tk.Label(
            banner,
            text="Ctrl+O Open  ·  Ctrl+S Save Project  ·  F5 Format",
            bg="#131722",
            fg="#7E8B9F",
            padx=8,
            pady=2,
            font=("Consolas", 8),
        ).grid(row=0, column=4, sticky="e")

        tk.Frame(header_wrap, bg=BORDER_CARD, height=1).grid(
            row=1, column=0, sticky="ew"
        )

    def _build_manuscript_card(self, parent, row):
        card = _make_card(
            parent,
            "Manuscript Source",
            subtitle=".md  ·  .docx  ·  .txt",
            pad=12,
        )
        card.grid(row=row, column=0, sticky="ew", pady=(0, 12))
        card.columnconfigure(0, weight=1)

        self.drop_canvas = tk.Canvas(
            card,
            height=62,
            bg=BG_SUBTLE,
            highlightthickness=0,
            cursor="hand2",
        )
        self.drop_canvas.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(0, 8))
        self.drop_canvas.bind("<Configure>", lambda _e: self._draw_drop_zone())
        self.drop_canvas.bind("<Button-1>", lambda _e: self._choose_manuscript())
        self.drop_canvas.bind("<Enter>", lambda _e: self._set_drop_hover(True))
        self.drop_canvas.bind("<Leave>", lambda _e: self._set_drop_hover(False))

        entry = ttk.Entry(card, textvariable=self.manuscript_var)
        entry.grid(row=2, column=0, sticky="ew", padx=(0, 6))
        entry.bind("<Return>", lambda _e: self._load_manuscript())

        ttk.Button(card, text="Browse...", command=self._choose_manuscript).grid(
            row=2, column=1, padx=(0, 6)
        )
        ttk.Button(card, text="Load Sample", command=self._load_sample).grid(
            row=2, column=2
        )

        ttk.Label(
            card,
            textvariable=self.status_var,
            style="Muted.TLabel",
            wraplength=420,
        ).grid(row=3, column=0, columnspan=3, sticky="w", pady=(7, 0))

    def _set_drop_hover(self, hovered):
        self._drop_hover = bool(hovered)
        self._draw_drop_zone()

    def _draw_drop_zone(self):
        if not hasattr(self, "drop_canvas"):
            return
        c = self.drop_canvas
        c.delete("all")
        w = max(int(c.winfo_width()), 380)
        h = max(int(c.winfo_height()), 62)

        bg = "#21293B" if self._drop_hover else "#181D29"
        border = ACCENT_CRIMSON if self._drop_hover else "#2E384D"
        c.configure(bg=bg)
        c.create_rectangle(
            1,
            1,
            w - 2,
            h - 2,
            outline=border,
            width=1.5 if self._drop_hover else 1,
            dash=(5, 3),
            fill=bg,
        )

        ix, iy = 26, h // 2
        c.create_oval(
            ix - 13,
            iy - 13,
            ix + 13,
            iy + 13,
            fill="#252E42" if not self._drop_hover else ACCENT_CRIMSON,
            outline="",
        )
        c.create_rectangle(
            ix - 5, iy - 7, ix + 5, iy + 7, fill="", outline="#F4F6FA", width=1.2
        )
        c.create_line(ix - 2, iy - 2, ix + 2, iy - 2, fill="#F4F6FA")
        c.create_line(ix - 2, iy + 2, ix + 2, iy + 2, fill="#F4F6FA")

        c.create_text(
            48,
            iy - 7,
            text="Drop manuscript here, or click to browse",
            anchor="w",
            fill=INK_DARK,
            font=("Segoe UI", 9, "bold"),
        )
        c.create_text(
            48,
            iy + 9,
            text="Supports Markdown (.md), Word (.docx), plain text (.txt), or output folder",
            anchor="w",
            fill=INK_MUTED,
            font=("Segoe UI", 8),
        )

    def _first_paragraph_letter(self):
        """Return the chosen custom drop letter or the opening paragraph's first letter."""
        chosen = self.drop_cap_letter_var.get().strip()
        if len(chosen) == 1 and chosen.isalnum():
            return chosen.upper()
        doc = self.current_document
        if doc and doc.chapters:
            first_ch = next(
                (ch for ch in doc.chapters if ch.display_number is not None),
                doc.chapters[0],
            )
            for block in first_ch.blocks:
                if getattr(block, "kind", "") == "paragraph":
                    plain_txt = inline.plain(getattr(block, "text", ""))
                    for ch in plain_txt:
                        if ch.isalnum():
                            return ch.upper()
                    break
        return "T"

    def _select_preset(self, tier_key, edition_key):
        self.tier_var.set(editions.TIER_LABELS[tier_key])
        if edition_key:
            self.edition_var.set(editions.EDITION_LABELS[edition_key])
        base = editions.resolve(
            tier_key, edition_key if tier_key == editions.ILLUSTRATED else None
        )
        self.border_style_var.set(
            editions.BORDER_STYLE_LABELS.get(base.border_style, BORDER_STYLE_CHOICES[0])
        )
        self.border_color_var.set(base.accent)
        self.drop_cap_style_var.set(
            editions.DROP_CAP_STYLE_LABELS.get(
                base.drop_cap_style, DROP_CAP_STYLE_CHOICES[-1]
            )
        )
        self._sync_edition_state(reset_from_tier=False)

    def _select_border_color(self, hex_color):
        self.border_color_var.set(hex_color)
        if BORDER_STYLE_BY_LABEL.get(self.border_style_var.get()) == "none":
            self.border_style_var.set(editions.BORDER_STYLE_LABELS["double"])
        self._sync_edition_state(reset_from_tier=False)

    def _pick_custom_color(self):
        initial = self.border_color_var.get().strip() or ACCENT_CRIMSON
        _rgb, hex_val = colorchooser.askcolor(
            color=initial, title="Choose Border & Accent Color"
        )
        if hex_val:
            self._select_border_color(hex_val)

    def _resolved_edition(self):
        tier = TIER_BY_LABEL.get(self.tier_var.get(), editions.CLEAN)
        edition_key = EDITION_BY_LABEL.get(self.edition_var.get(), editions.ASHVEIL)
        b_style = BORDER_STYLE_BY_LABEL.get(self.border_style_var.get())
        b_color = self.border_color_var.get().strip() or None
        dc_style = DROP_CAP_STYLE_BY_LABEL.get(self.drop_cap_style_var.get())
        dc_letter_raw = self.drop_cap_letter_var.get().strip()
        dc_letter = (
            dc_letter_raw.upper()
            if (len(dc_letter_raw) == 1 and dc_letter_raw.isalnum())
            else ""
        )
        fp_key = FONT_PAIRING_BY_LABEL.get(self.font_pairing_var.get(), "edition")
        return editions.resolve(
            tier,
            edition_key if tier == editions.ILLUSTRATED else None,
            border_color=b_color,
            border_style=b_style,
            drop_cap_style=dc_style,
            drop_cap_letter=dc_letter,
            font_pairing=fp_key,
        )

    def _sync_edition_state(self, reset_from_tier=True):
        """Synchronize tier/edition dropdowns, border/drop-letter controls, and live preview."""
        tier = TIER_BY_LABEL.get(self.tier_var.get(), editions.CLEAN)
        edition_key = EDITION_BY_LABEL.get(self.edition_var.get(), editions.ASHVEIL)
        if hasattr(self, "edition_box"):
            if tier == editions.ILLUSTRATED:
                self.edition_box.configure(state="readonly")
            else:
                self.edition_box.configure(state="disabled")

        if reset_from_tier:
            base = editions.resolve(
                tier, edition_key if tier == editions.ILLUSTRATED else None
            )
            self.border_style_var.set(
                editions.BORDER_STYLE_LABELS.get(base.border_style, BORDER_STYLE_CHOICES[0])
            )
            self.border_color_var.set(base.accent)
            self.drop_cap_style_var.set(
                editions.DROP_CAP_STYLE_LABELS.get(
                    base.drop_cap_style, DROP_CAP_STYLE_CHOICES[-1]
                )
            )

        is_tier2_plus = tier != editions.CLEAN
        for w in self._drop_cap_widgets:
            w.configure(state="readonly" if is_tier2_plus else "disabled")
        if hasattr(self, "drop_tier_badge"):
            if is_tier2_plus:
                self.drop_tier_badge.configure(
                    text="TIER 2+ ACTIVE",
                    bg="#133326",
                    fg="#34D399",
                )
            else:
                self.drop_tier_badge.configure(
                    text="TIER 2+ ONLY",
                    bg="#1F2637",
                    fg="#7E8B9F",
                )

        resolved = self._resolved_edition()

        active_pair = (tier, edition_key if tier == editions.ILLUSTRATED else None)
        for pair, btn in self._preset_buttons.items():
            if pair == active_pair:
                btn.configure(
                    bg=ACCENT_CRIMSON,
                    fg="#FFFFFF",
                    activebackground=ACCENT_CRIMSON_HOVER,
                    highlightbackground=ACCENT_CRIMSON,
                )
            else:
                btn.configure(
                    bg="#181D29",
                    fg=INK_BODY,
                    activebackground="#232B3D",
                    highlightbackground="#262F42",
                )

        active_hex = resolved.accent.lower()
        for hex_code, btn in self._color_swatch_buttons.items():
            is_sel = hex_code.lower() == active_hex
            btn.configure(
                highlightthickness=2 if is_sel else 1,
                highlightbackground="#FFFFFF" if is_sel else "#2A3244",
                highlightcolor="#FFFFFF" if is_sel else "#2A3244",
                text="✓" if is_sel else "",
                fg="#FFFFFF",
            )

        if hasattr(self, "swatch_canvas"):
            self.swatch_canvas.delete("all")
            self.swatch_canvas.create_rectangle(0, 0, 22, 16, fill=resolved.ink, outline="")
            self.swatch_canvas.create_rectangle(22, 0, 44, 16, fill=resolved.accent, outline="")

        features = [editions.BORDER_STYLE_LABELS.get(resolved.border_style, "No Border")]
        if resolved.font_pairing != "edition":
            features.append(resolved.font_pairing)
        if resolved.drop_cap:
            letter_disp = resolved.drop_cap_letter or self._first_paragraph_letter()
            features.append(f"drop '{letter_disp}' ({resolved.drop_cap_style})")
        if resolved.chapter_rule:
            features.append("chapter rules")
        if hasattr(self, "tier_hint"):
            self.tier_hint.configure(
                text=f"Accent: {resolved.accent.upper()}  ·  Scene: {resolved.scene_break}  ·  {', '.join(features)}"
            )
        if hasattr(self, "page_canvas"):
            self._draw_page_preview()

    def _switch_left_tab(self, idx):
        self._flush_matter_editor()
        self.left_notebook.select(idx)
        self._update_left_pills()
        if idx == 1:
            self._load_matter_editor(self._active_matter_key)

    def _update_left_pills(self, *_args):
        if not hasattr(self, "left_notebook") or not self._left_pill_buttons:
            return
        try:
            active_idx = self.left_notebook.index(self.left_notebook.select())
        except tk.TclError:
            active_idx = 0
        for idx, btn in enumerate(self._left_pill_buttons):
            if idx == active_idx:
                btn.configure(
                    bg=BG_PILL_ACTIVE,
                    fg="#FFFFFF",
                    activebackground=BG_PILL_ACTIVE,
                )
            else:
                btn.configure(
                    bg=BG_PILL_TROUGH,
                    fg=INK_MUTED,
                    activebackground="#181E2B",
                )

    def _switch_right_tab(self, idx):
        self.notebook.select(idx)
        self._update_right_pills()

    def _update_right_pills(self, *_args):
        if not hasattr(self, "notebook") or not self._right_pill_buttons:
            return
        try:
            active_idx = self.notebook.index(self.notebook.select())
        except tk.TclError:
            active_idx = 0
        for idx, btn in enumerate(self._right_pill_buttons):
            if idx == active_idx:
                btn.configure(
                    bg=BG_PILL_ACTIVE,
                    fg="#FFFFFF",
                    activebackground=BG_PILL_ACTIVE,
                )
            else:
                btn.configure(
                    bg=BG_PILL_TROUGH,
                    fg=INK_MUTED,
                    activebackground="#181E2B",
                )

    def _build_config_tabs(self, parent, row):
        card = _make_card(parent, pad=12)
        card.grid(row=row, column=0, sticky="nsew")
        card.columnconfigure(0, weight=1)
        card.rowconfigure(1, weight=1)

        # Sleek 4-tab segmented pill bar
        pill_bar = tk.Frame(
            card,
            bg=BG_PILL_TROUGH,
            padx=3,
            pady=3,
            highlightthickness=1,
            highlightbackground="#1F2636",
        )
        pill_bar.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        tab_titles = ("Book & Cover", "Front & Back", "Style & Fonts", "Export")
        for idx, label in enumerate(tab_titles):
            pill_bar.columnconfigure(idx, weight=1)
            btn = tk.Button(
                pill_bar,
                text=label,
                bd=0,
                relief="flat",
                highlightthickness=0,
                padx=6,
                pady=5,
                cursor="hand2",
                font=("Segoe UI", 8, "bold"),
                command=lambda i=idx: self._switch_left_tab(i),
            )
            btn.grid(row=0, column=idx, sticky="ew", padx=(0 if idx == 0 else 3, 0))
            self._left_pill_buttons.append(btn)

        self.left_notebook = _TabDeck(card, on_change=self._update_left_pills)
        self.left_notebook.grid(row=1, column=0, sticky="nsew")

        details_tab = tk.Frame(self.left_notebook, bg=BG_CARD, padx=4, pady=2)
        details_tab.columnconfigure(1, weight=1)
        details_tab.columnconfigure(3, weight=1)

        matter_tab = tk.Frame(self.left_notebook, bg=BG_CARD, padx=4, pady=2)
        matter_tab.columnconfigure(0, weight=1)
        matter_tab.rowconfigure(2, weight=1)

        style_tab = tk.Frame(self.left_notebook, bg=BG_CARD, padx=4, pady=2)
        style_tab.columnconfigure(1, weight=1)

        outputs_tab = tk.Frame(self.left_notebook, bg=BG_CARD, padx=4, pady=2)
        outputs_tab.columnconfigure(1, weight=1)

        self._populate_details_tab(details_tab)
        self._populate_matter_tab(matter_tab)
        self._populate_style_tab(style_tab)
        self._populate_outputs_tab(outputs_tab)

        self.left_notebook.add(details_tab, text="Book & Cover")
        self.left_notebook.add(matter_tab, text="Front & Back")
        self.left_notebook.add(style_tab, text="Style & Fonts")
        self.left_notebook.add(outputs_tab, text="Export")
        self._update_left_pills()

    def _populate_details_tab(self, box):
        r = 0
        for key, label in (("title", "Title"), ("subtitle", "Subtitle")):
            ttk.Label(box, text=label).grid(row=r, column=0, sticky="w", pady=3)
            ttk.Entry(box, textvariable=self.meta_vars[key]).grid(
                row=r, column=1, columnspan=3, sticky="ew", padx=(8, 0), pady=3
            )
            r += 1

        paired = (
            ("author", "Author", "publisher", "Publisher"),
            ("date", "Date", "isbn", "ISBN"),
        )
        for k1, l1, k2, l2 in paired:
            ttk.Label(box, text=l1).grid(row=r, column=0, sticky="w", pady=3)
            ttk.Entry(box, textvariable=self.meta_vars[k1]).grid(
                row=r, column=1, sticky="ew", padx=(8, 12), pady=3
            )
            ttk.Label(box, text=l2).grid(row=r, column=2, sticky="w", pady=3)
            ttk.Entry(box, textvariable=self.meta_vars[k2]).grid(
                row=r, column=3, sticky="ew", padx=(8, 0), pady=3
            )
            r += 1

        ttk.Label(box, text="Description").grid(row=r, column=0, sticky="w", pady=3)
        ttk.Entry(box, textvariable=self.meta_vars["description"]).grid(
            row=r, column=1, columnspan=3, sticky="ew", padx=(8, 0), pady=3
        )
        r += 1

        tk.Frame(box, bg=BORDER_CARD, height=1).grid(
            row=r, column=0, columnspan=4, sticky="ew", pady=(6, 6)
        )
        r += 1

        ttk.Label(box, text="COVER ARTWORK (OPTIONAL)", style="Section.TLabel").grid(
            row=r, column=0, columnspan=4, sticky="w", pady=(0, 3)
        )
        r += 1

        cover_row = tk.Frame(box, bg=BG_CARD)
        cover_row.grid(row=r, column=0, columnspan=4, sticky="ew", pady=2)
        cover_row.columnconfigure(0, weight=1)
        ttk.Entry(cover_row, textvariable=self.cover_var).grid(
            row=0, column=0, sticky="ew", padx=(0, 6)
        )
        ttk.Button(cover_row, text="Browse...", command=self._choose_cover).grid(
            row=0, column=1, padx=(0, 4)
        )
        ttk.Button(cover_row, text="Clear", command=self._clear_cover).grid(
            row=0, column=2
        )
        r += 1

        ttk.Label(
            box,
            text="Leave Cover blank to generate Inkpress's framed typographic SVG cover, or attach a .jpg/.png/.svg cover (1600×2560+ px recommended). Press Ctrl+S to save per-book settings.",
            style="Muted.TLabel",
            wraplength=415,
        ).grid(row=r, column=0, columnspan=4, sticky="w", pady=(6, 0))

    def _populate_matter_tab(self, box):
        ttk.Label(
            box,
            text="FRONT & BACK MATTER BUILDER",
            style="Section.TLabel",
        ).grid(row=0, column=0, sticky="w", pady=(0, 4))

        # Two rows of compact section pills for all 7 publishing sections
        pills_wrap = tk.Frame(box, bg=BG_CARD)
        pills_wrap.grid(row=1, column=0, sticky="ew", pady=(0, 6))
        for idx, (sec_key, sec_label, _hint) in enumerate(MATTER_SECTIONS):
            row_i = 0 if idx < 4 else 1
            col_i = idx if idx < 4 else (idx - 4)
            pills_wrap.columnconfigure(col_i, weight=1)
            btn = tk.Button(
                pills_wrap,
                text=sec_label,
                bd=0,
                relief="flat",
                highlightthickness=1,
                padx=6,
                pady=4,
                cursor="hand2",
                font=("Segoe UI", 8, "bold"),
                command=lambda k=sec_key: self._select_matter_section(k),
            )
            btn.grid(
                row=row_i,
                column=col_i,
                sticky="ew",
                padx=(0 if col_i == 0 else 3, 0),
                pady=(0, 3),
            )
            self._matter_pill_buttons[sec_key] = btn

        editor_frame = tk.Frame(
            box,
            bg=BG_SUBTLE,
            highlightthickness=1,
            highlightbackground=BORDER_INPUT,
        )
        editor_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 6))
        editor_frame.columnconfigure(0, weight=1)
        editor_frame.rowconfigure(0, weight=1)

        self.matter_text = tk.Text(
            editor_frame,
            height=6,
            wrap="word",
            bg=BG_SUBTLE,
            fg=INK_DARK,
            insertbackground=INK_DARK,
            relief="flat",
            padx=8,
            pady=6,
            font=("Segoe UI", 9),
            undo=True,
        )
        self.matter_text.grid(row=0, column=0, sticky="nsew")
        m_scroll = ttk.Scrollbar(
            editor_frame, orient="vertical", command=self.matter_text.yview
        )
        m_scroll.grid(row=0, column=1, sticky="ns")
        self.matter_text.configure(yscrollcommand=m_scroll.set)
        self.matter_text.bind("<KeyRelease>", lambda _e: self._flush_matter_editor())
        self.matter_text.bind("<FocusOut>", lambda _e: self._flush_matter_editor())

        url_row = tk.Frame(box, bg=BG_CARD)
        url_row.grid(row=3, column=0, sticky="ew", pady=(0, 4))
        url_row.columnconfigure(1, weight=1)
        ttk.Label(url_row, text="CTA Link URL:").grid(row=0, column=0, sticky="w", padx=(0, 6))
        ttk.Entry(url_row, textvariable=self.meta_vars["newsletter_url"]).grid(
            row=0, column=1, sticky="ew"
        )

        self.matter_hint_var = tk.StringVar()
        ttk.Label(
            box,
            textvariable=self.matter_hint_var,
            style="Muted.TLabel",
            wraplength=415,
        ).grid(row=4, column=0, sticky="w")
        self._select_matter_section("dedication")

    def _select_matter_section(self, key):
        self._flush_matter_editor()
        self._active_matter_key = key
        self._load_matter_editor(key)

    def _load_matter_editor(self, key):
        if not hasattr(self, "matter_text"):
            return
        self._syncing_matter_text = True
        try:
            self.matter_text.delete("1.0", "end")
            val = self.meta_vars[key].get()
            if val:
                self.matter_text.insert("1.0", val)
        finally:
            self._syncing_matter_text = False
        self._refresh_matter_pills()

    def _flush_matter_editor(self):
        if self._syncing_matter_text or not hasattr(self, "matter_text"):
            return
        val = self.matter_text.get("1.0", "end-1c").strip()
        self.meta_vars[self._active_matter_key].set(val)
        self._refresh_matter_pills()

    def _refresh_matter_pills(self):
        hint_map = {k: h for k, _l, h in MATTER_SECTIONS}
        populated = []
        for sec_key, sec_label, _hint in MATTER_SECTIONS:
            has_val = bool(self.meta_vars[sec_key].get().strip())
            if has_val:
                populated.append(sec_label)
            btn = self._matter_pill_buttons.get(sec_key)
            if not btn:
                continue
            is_active = sec_key == self._active_matter_key
            dot = " •" if has_val else ""
            btn.configure(
                text=f"{sec_label}{dot}",
                bg=ACCENT_CRIMSON if is_active else ("#1C2638" if has_val else "#151A25"),
                fg="#FFFFFF" if is_active else ("#6EE7B7" if has_val else INK_MUTED),
                highlightbackground=ACCENT_CRIMSON if is_active else "#252E42",
            )
        active_hint = hint_map.get(self._active_matter_key, "")
        summary = ", ".join(populated) if populated else "Auto Copyright only"
        if hasattr(self, "matter_hint_var"):
            self.matter_hint_var.set(f"{active_hint}  (Populated: {summary})")

    def _populate_style_tab(self, box):
        r = 0
        ttk.Label(box, text="TYPOGRAPHY TIER, EDITION & FONTS", style="Section.TLabel").grid(
            row=r, column=0, columnspan=3, sticky="w", pady=(0, 3)
        )
        r += 1

        ttk.Label(box, text="Tier").grid(row=r, column=0, sticky="w", pady=2)
        tier_row = tk.Frame(box, bg=BG_CARD)
        tier_row.grid(row=r, column=1, columnspan=2, sticky="ew", padx=(8, 0), pady=2)
        tier_row.columnconfigure(0, weight=1)

        tier_box = ttk.Combobox(
            tier_row, textvariable=self.tier_var, values=TIER_CHOICES, state="readonly"
        )
        tier_box.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        tier_box.bind("<<ComboboxSelected>>", lambda _event: self._sync_edition_state())

        ttk.Label(tier_row, text="Trim:").grid(row=0, column=1, sticky="w", padx=(0, 4))
        trim_cb = ttk.Combobox(
            tier_row, textvariable=self.trim_var, values=TRIM_CHOICES, width=7
        )
        trim_cb.grid(row=0, column=2, sticky="e")
        trim_cb.bind("<<ComboboxSelected>>", lambda _e: self._refresh_kdp_and_preview())
        r += 1

        ttk.Label(box, text="Edition").grid(row=r, column=0, sticky="w", pady=2)
        self.edition_box = ttk.Combobox(
            box, textvariable=self.edition_var, values=EDITION_CHOICES, state="disabled"
        )
        self.edition_box.grid(row=r, column=1, columnspan=2, sticky="ew", padx=(8, 0), pady=2)
        self.edition_box.bind("<<ComboboxSelected>>", lambda _event: self._sync_edition_state())
        r += 1

        ttk.Label(box, text="Font pairing").grid(row=r, column=0, sticky="w", pady=2)
        self.font_pairing_box = ttk.Combobox(
            box,
            textvariable=self.font_pairing_var,
            values=FONT_PAIRING_CHOICES,
            state="readonly",
        )
        self.font_pairing_box.grid(row=r, column=1, columnspan=2, sticky="ew", padx=(8, 0), pady=2)
        self.font_pairing_box.bind(
            "<<ComboboxSelected>>",
            lambda _e: self._sync_edition_state(reset_from_tier=False),
        )
        r += 1

        tk.Frame(box, bg=BORDER_CARD, height=1).grid(
            row=r, column=0, columnspan=3, sticky="ew", pady=(3, 3)
        )
        r += 1

        drop_hdr_row = tk.Frame(box, bg=BG_CARD)
        drop_hdr_row.grid(row=r, column=0, columnspan=3, sticky="ew", pady=(0, 2))
        ttk.Label(
            drop_hdr_row,
            text="FIRST PARAGRAPH DROP LETTER",
            style="Section.TLabel",
        ).pack(side="left")
        self.drop_tier_badge = tk.Label(
            drop_hdr_row,
            text="TIER 2+ ONLY",
            bg="#1F2637",
            fg="#7E8B9F",
            padx=6,
            pady=1,
            font=("Segoe UI", 7, "bold"),
        )
        self.drop_tier_badge.pack(side="left", padx=(8, 0))
        r += 1

        ttk.Label(box, text="Drop letter").grid(row=r, column=0, sticky="w", pady=2)
        drop_row = tk.Frame(box, bg=BG_CARD)
        drop_row.grid(row=r, column=1, columnspan=2, sticky="ew", padx=(8, 0), pady=2)
        drop_row.columnconfigure(0, weight=1)

        self.drop_cap_style_box = ttk.Combobox(
            drop_row,
            textvariable=self.drop_cap_style_var,
            values=DROP_CAP_STYLE_CHOICES,
            state="disabled",
            width=18,
        )
        self.drop_cap_style_box.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.drop_cap_style_box.bind(
            "<<ComboboxSelected>>",
            lambda _e: self._sync_edition_state(reset_from_tier=False),
        )

        ttk.Label(drop_row, text="Letter:").grid(
            row=0, column=1, sticky="w", padx=(0, 4)
        )
        self.drop_cap_letter_box = ttk.Combobox(
            drop_row,
            textvariable=self.drop_cap_letter_var,
            values=DROP_LETTER_CHOICES,
            state="disabled",
            width=10,
        )
        self.drop_cap_letter_box.grid(row=0, column=2, sticky="e")
        self.drop_cap_letter_box.bind(
            "<<ComboboxSelected>>",
            lambda _e: self._sync_edition_state(reset_from_tier=False),
        )
        self._drop_cap_widgets = [self.drop_cap_style_box, self.drop_cap_letter_box]
        r += 1

        tk.Frame(box, bg=BORDER_CARD, height=1).grid(
            row=r, column=0, columnspan=3, sticky="ew", pady=(3, 3)
        )
        r += 1

        ttk.Label(box, text="COLORED PAGE & COVER BORDERS", style="Section.TLabel").grid(
            row=r, column=0, columnspan=3, sticky="w", pady=(0, 2)
        )
        r += 1

        ttk.Label(box, text="Border style").grid(row=r, column=0, sticky="w", pady=2)
        border_cb = ttk.Combobox(
            box,
            textvariable=self.border_style_var,
            values=BORDER_STYLE_CHOICES,
            state="readonly",
        )
        border_cb.grid(row=r, column=1, columnspan=2, sticky="ew", padx=(8, 0), pady=2)
        border_cb.bind(
            "<<ComboboxSelected>>",
            lambda _e: self._sync_edition_state(reset_from_tier=False),
        )
        r += 1

        ttk.Label(box, text="Border color").grid(row=r, column=0, sticky="w", pady=2)
        palette_row = tk.Frame(box, bg=BG_CARD)
        palette_row.grid(row=r, column=1, columnspan=2, sticky="ew", padx=(8, 0), pady=2)

        for idx, (_name, hex_code) in enumerate(editions.COLOR_PRESETS):
            sw = tk.Button(
                palette_row,
                bg=hex_code,
                activebackground=hex_code,
                width=2,
                height=1,
                bd=0,
                relief="flat",
                highlightthickness=1,
                highlightbackground="#2A3244",
                cursor="hand2",
                font=("Segoe UI", 6, "bold"),
                command=lambda h=hex_code: self._select_border_color(h),
            )
            sw.grid(row=0, column=idx, padx=(0, 4))
            self._color_swatch_buttons[hex_code] = sw

        ttk.Button(
            palette_row, text="Custom...", command=self._pick_custom_color
        ).grid(row=0, column=len(editions.COLOR_PRESETS), padx=(4, 0))
        r += 1

        swatch_row = tk.Frame(
            box,
            bg="#0F131B",
            padx=8,
            pady=4,
            highlightthickness=1,
            highlightbackground="#1E2534",
        )
        swatch_row.grid(row=r, column=0, columnspan=3, sticky="ew", pady=(3, 0))
        self.swatch_canvas = tk.Canvas(
            swatch_row,
            width=44,
            height=16,
            bg="#0F131B",
            highlightthickness=1,
            highlightbackground="#2D364B",
        )
        self.swatch_canvas.grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.tier_hint = tk.Label(
            swatch_row,
            text="",
            bg="#0F131B",
            fg=INK_MUTED,
            justify="left",
            anchor="w",
            wraplength=365,
            font=("Segoe UI", 8),
        )
        self.tier_hint.grid(row=0, column=1, sticky="w")

    def _populate_outputs_tab(self, box):
        r = 0
        ttk.Label(box, text="DELIVERABLES TO BUILD", style="Section.TLabel").grid(
            row=r, column=0, columnspan=3, sticky="w", pady=(0, 6)
        )
        r += 1

        for key, label, hint in TARGET_LABELS:
            ttk.Checkbutton(box, text=label, variable=self.target_vars[key]).grid(
                row=r, column=0, sticky="w", pady=4
            )
            ttk.Label(box, text=hint, style="Muted.TLabel").grid(
                row=r, column=1, columnspan=2, sticky="w", padx=(8, 0), pady=4
            )
            r += 1

        ttk.Checkbutton(box, text="Print PDF (KDP ready)", variable=self.pdf_var).grid(
            row=r, column=0, sticky="w", pady=4
        )
        ttk.Label(
            box, text="Direct PDF via headless Edge/Chrome or WeasyPrint", style="Muted.TLabel"
        ).grid(row=r, column=1, columnspan=2, sticky="w", padx=(8, 0), pady=4)
        r += 1

        ttk.Checkbutton(box, text="Package buyer ZIP", variable=self.package_var).grid(
            row=r, column=0, sticky="w", pady=4
        )
        ttk.Label(
            box, text="Bundle outputs + delivery notes in build/orders/", style="Muted.TLabel"
        ).grid(row=r, column=1, columnspan=2, sticky="w", padx=(8, 0), pady=4)
        r += 1

        tk.Frame(box, bg=BORDER_CARD, height=1).grid(
            row=r, column=0, columnspan=3, sticky="ew", pady=(10, 10)
        )
        r += 1

        ttk.Label(box, text="OUTPUT & WEB TEMPLATE", style="Section.TLabel").grid(
            row=r, column=0, columnspan=3, sticky="w", pady=(0, 6)
        )
        r += 1

        pickers = (
            ("Save to", self.out_var, self._choose_out),
            ("Web template", self.chrome_var, self._choose_chrome),
        )
        for label, var, cmd in pickers:
            ttk.Label(box, text=label).grid(row=r, column=0, sticky="w", pady=4)
            ttk.Entry(box, textvariable=var).grid(
                row=r, column=1, sticky="ew", padx=(8, 8), pady=4
            )
            ttk.Button(box, text="Browse...", command=cmd).grid(row=r, column=2, pady=4)
            r += 1

    def _build_action_bar(self, row):
        wrap = tk.Frame(self, bg="#090B0E")
        wrap.grid(row=row, column=0, sticky="ew")
        wrap.columnconfigure(0, weight=1)

        tk.Frame(wrap, bg=BORDER_CARD, height=1).grid(row=0, column=0, sticky="ew")

        bar = tk.Frame(wrap, bg="#090B0E", padx=16, pady=10)
        bar.grid(row=1, column=0, sticky="ew")
        bar.columnconfigure(4, weight=1)

        self.format_button = ttk.Button(
            bar, text="✦  Format Book", style="Primary.TButton", command=self._start_build
        )
        self.format_button.grid(row=0, column=0)

        self.save_project_button = ttk.Button(
            bar, text="Save Project", command=self._save_project
        )
        self.save_project_button.grid(row=0, column=1, padx=(8, 0))

        self.open_button = ttk.Button(
            bar, text="Open Folder", command=self._open_output, state="disabled"
        )
        self.open_button.grid(row=0, column=2, padx=(6, 0))

        self.preview_print_button = ttk.Button(
            bar, text="Preview Print", command=self._preview_print, state="disabled"
        )
        self.preview_print_button.grid(row=0, column=3, padx=(6, 0))

        self.preview_web_button = ttk.Button(
            bar, text="Preview Web", command=self._preview_web, state="disabled"
        )
        self.preview_web_button.grid(row=0, column=4, sticky="w", padx=(6, 0))

        self.progress = ttk.Progressbar(
            bar, mode="determinate", maximum=100, value=0, length=220
        )
        self.progress.grid(row=0, column=5, sticky="e", padx=(14, 0))

    # ---------------------------------------------------- right column studio

    def _build_preview_card(self, parent, row):
        card = _make_card(
            parent,
            "Live Book Spread Preview",
            subtitle="Interactive Cover & Chapter 1 Stage",
            pad=12,
        )
        card.grid(row=row, column=0, sticky="nsew", pady=(0, 12))
        card.columnconfigure(0, weight=1)
        card.rowconfigure(3, weight=1)

        preset_bar = tk.Frame(
            card,
            bg=BG_PILL_TROUGH,
            padx=3,
            pady=3,
            highlightthickness=1,
            highlightbackground="#1F2636",
        )
        preset_bar.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        presets = (
            ("Clean", editions.CLEAN, None),
            ("Styled", editions.STYLED, None),
            ("Ashveil", editions.ILLUSTRATED, editions.ASHVEIL),
            ("Systemfall", editions.ILLUSTRATED, editions.SYSTEMFALL),
            ("Vantablack", editions.ILLUSTRATED, editions.VANTABLACK),
        )
        for idx, (label, t_key, e_key) in enumerate(presets):
            preset_bar.columnconfigure(idx, weight=1)
            btn = tk.Button(
                preset_bar,
                text=label,
                bd=0,
                relief="flat",
                highlightthickness=1,
                padx=8,
                pady=4,
                cursor="hand2",
                font=("Segoe UI", 8, "bold"),
                command=lambda tk_k=t_key, ed_k=e_key: self._select_preset(tk_k, ed_k),
            )
            btn.grid(row=0, column=idx, sticky="ew", padx=(0 if idx == 0 else 3, 0))
            self._preset_buttons[(t_key, e_key)] = btn

        # Quick Border Style + Border Color toolbar right above the spread canvas
        border_bar = tk.Frame(card, bg=BG_CARD)
        border_bar.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        tk.Label(
            border_bar,
            text="Border:",
            bg=BG_CARD,
            fg=INK_MUTED,
            font=("Segoe UI", 8, "bold"),
        ).pack(side="left", padx=(0, 6))

        border_quick_cb = ttk.Combobox(
            border_bar,
            textvariable=self.border_style_var,
            values=BORDER_STYLE_CHOICES,
            state="readonly",
            width=18,
        )
        border_quick_cb.pack(side="left", padx=(0, 14))
        border_quick_cb.bind(
            "<<ComboboxSelected>>",
            lambda _e: self._sync_edition_state(reset_from_tier=False),
        )

        tk.Label(
            border_bar,
            text="Accent:",
            bg=BG_CARD,
            fg=INK_MUTED,
            font=("Segoe UI", 8, "bold"),
        ).pack(side="left", padx=(0, 6))

        for _name, hex_code in editions.COLOR_PRESETS:
            sw = tk.Button(
                border_bar,
                bg=hex_code,
                activebackground=hex_code,
                width=2,
                height=1,
                bd=0,
                relief="flat",
                highlightthickness=1,
                highlightbackground="#2A3244",
                cursor="hand2",
                font=("Segoe UI", 6),
                command=lambda h=hex_code: self._select_border_color(h),
            )
            sw.pack(side="left", padx=(0, 4))

        self.page_canvas = tk.Canvas(
            card,
            width=480,
            height=275,
            bg=BG_STAGE,
            highlightthickness=1,
            highlightbackground="#1F2636",
        )
        self.page_canvas.grid(row=3, column=0, sticky="nsew")
        self.page_canvas.bind("<Configure>", lambda _e: self._draw_page_preview())
        self._sync_edition_state()

    def _build_inspector_and_log(self, parent, row):
        card = _make_card(parent, pad=10)
        card.grid(row=row, column=0, sticky="nsew")
        card.columnconfigure(0, weight=1)
        card.rowconfigure(1, weight=1)

        top_bar = tk.Frame(card, bg=BG_CARD)
        top_bar.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        top_bar.columnconfigure(1, weight=1)

        pill_bar = tk.Frame(
            top_bar,
            bg=BG_PILL_TROUGH,
            padx=3,
            pady=3,
            highlightthickness=1,
            highlightbackground="#1F2636",
        )
        pill_bar.grid(row=0, column=0, sticky="w")
        for idx, label in enumerate(("Chapters & KDP", "Build Console")):
            btn = tk.Button(
                pill_bar,
                text=label,
                bd=0,
                relief="flat",
                highlightthickness=0,
                padx=8,
                pady=4,
                cursor="hand2",
                font=("Segoe UI", 8, "bold"),
                command=lambda i=idx: self._switch_right_tab(i),
            )
            btn.grid(row=0, column=idx, padx=(0 if idx == 0 else 3, 0))
            self._right_pill_buttons.append(btn)

        tk.Label(
            top_bar,
            textvariable=self.kdp_summary_var,
            bg=BG_CARD,
            fg="#94A3B8",
            font=("Segoe UI", 8, "bold"),
            anchor="e",
        ).grid(row=0, column=1, sticky="e", padx=(8, 0))

        self.notebook = _TabDeck(card, on_change=self._update_right_pills)
        self.notebook.grid(row=1, column=0, sticky="nsew")

        outline_tab = tk.Frame(self.notebook, bg=BG_CARD)
        outline_tab.columnconfigure(0, weight=1)
        outline_tab.rowconfigure(0, weight=1)

        columns = ("num", "title", "words", "status")
        self.chapter_tree = ttk.Treeview(
            outline_tab, columns=columns, show="headings", height=4
        )
        self.chapter_tree.heading("num", text="#")
        self.chapter_tree.heading("title", text="Chapter / Section")
        self.chapter_tree.heading("words", text="Words")
        self.chapter_tree.heading("status", text="Role")

        self.chapter_tree.column("num", width=42, anchor="center", stretch=False)
        self.chapter_tree.column("title", width=210, anchor="w")
        self.chapter_tree.column("words", width=75, anchor="e", stretch=False)
        self.chapter_tree.column("status", width=120, anchor="w")
        self.chapter_tree.grid(row=0, column=0, sticky="nsew")

        tree_scroll = ttk.Scrollbar(
            outline_tab, orient="vertical", command=self.chapter_tree.yview
        )
        tree_scroll.grid(row=0, column=1, sticky="ns")
        self.chapter_tree.configure(yscrollcommand=tree_scroll.set)

        log_tab = tk.Frame(self.notebook, bg=BG_CARD)
        log_tab.columnconfigure(0, weight=1)
        log_tab.rowconfigure(0, weight=1)

        self.log = tk.Text(
            log_tab,
            height=5,
            wrap="word",
            state="disabled",
            bg="#0E1118",
            fg=INK_BODY,
            relief="flat",
            padx=10,
            pady=8,
            font=("Consolas", 9),
        )
        self.log.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(log_tab, orient="vertical", command=self.log.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self.log.configure(yscrollcommand=scroll.set)

        self.log.tag_configure("ok", foreground="#34D399")
        self.log.tag_configure("warn", foreground="#FBBF24")
        self.log.tag_configure("error", foreground="#F87171")
        self.log.tag_configure("muted", foreground=INK_MUTED)

        self.notebook.add(outline_tab, text="Chapters & KDP Specs")
        self.notebook.add(log_tab, text="Build Console")
        self._update_right_pills()

    def _draw_sheet_border(self, canvas, x0, y0, x1, y1, border_style, color, scale=1.0):
        """Draw the selected colored border style inside a page sheet."""
        pad_outer = max(7, int(round(8 * scale)))
        pad_inner = max(11, int(round(12 * scale)))
        if border_style == "double":
            canvas.create_rectangle(
                x0 + pad_outer,
                y0 + pad_outer,
                x1 - pad_outer,
                y1 - pad_outer,
                outline=color,
                width=max(1.5, 2.0 * scale),
            )
            canvas.create_rectangle(
                x0 + pad_inner,
                y0 + pad_inner,
                x1 - pad_inner,
                y1 - pad_inner,
                outline=color,
                width=max(1.0, 1.0 * scale),
            )
        elif border_style == "single":
            canvas.create_rectangle(
                x0 + pad_outer + 1,
                y0 + pad_outer + 1,
                x1 - pad_outer - 1,
                y1 - pad_outer - 1,
                outline=color,
                width=max(1.5, 1.6 * scale),
            )
        elif border_style == "rules":
            canvas.create_line(
                x0 + pad_inner,
                y0 + pad_inner,
                x1 - pad_inner,
                y0 + pad_inner,
                fill=color,
                width=max(1.5, 2.0 * scale),
            )
            canvas.create_line(
                x0 + pad_inner,
                y1 - pad_inner,
                x1 - pad_inner,
                y1 - pad_inner,
                fill=color,
                width=max(1.2, 1.5 * scale),
            )

    def _draw_page_preview(self):
        """Render a responsive, hero-sized two-page spread preview on the dark studio stage."""
        if not hasattr(self, "page_canvas"):
            return
        canvas = self.page_canvas
        canvas.delete("all")

        c_width = max(int(canvas.winfo_width()), 480)
        c_height = max(int(canvas.winfo_height()), 265)

        # Subtle studio stage framing lines
        canvas.create_rectangle(
            8, 8, c_width - 8, c_height - 8, outline="#161B26", width=1
        )

        edition = self._resolved_edition()
        border_style = getattr(edition, "border_style", "double")
        doc = self.current_document
        book_title = (
            self.meta_vars["title"].get().strip()
            or (doc.plain_title() if doc else "The Lamplighter’s Round")
        )
        subtitle = (
            self.meta_vars["subtitle"].get().strip()
            or (
                doc.meta.get("subtitle", "")
                if doc
                else "A Short Passage for Setting the Press"
            )
        )
        author_name = (
            self.meta_vars["author"].get().strip()
            or (doc.meta.get("author", "J.S. Warden") if doc else "J.S. Warden")
        )
        chap_title = (
            doc.chapters[0].title
            if (doc and doc.chapters and not doc.chapters[0].implicit)
            else "The First Round"
        )

        fp_key = getattr(edition, "font_pairing", "edition")
        if fp_key == "mono_serif":
            heading_face = "Consolas"
        elif fp_key == "sans_serif":
            heading_face = "Segoe UI"
        elif fp_key == "baskerville":
            heading_face = "Baskerville Old Face"
        elif fp_key == "palatino":
            heading_face = "Palatino Linotype"
        elif fp_key == "garamond":
            heading_face = "Garamond"
        else:
            heading_face = (
                "Consolas"
                if edition.key == editions.SYSTEMFALL
                else ("Arial" if edition.key == editions.VANTABLACK else "Georgia")
            )
        heading_style = "bold" if edition.display_weight == "800" else "normal"

        trim_key = self.trim_var.get().strip() or "6x9"
        aspect = _TRIM_ASPECT.get(trim_key, 6.0 / 9.0)

        avail_h = max(215, c_height - 46)
        avail_w = max(360, c_width - 56)
        gap = max(18, int(avail_w * 0.035))

        page_h = min(avail_h, int((avail_w - gap) / (2.0 * aspect)))
        page_h = max(210, page_h)
        page_w = max(145, int(round(page_h * aspect)))
        scale = page_h / 230.0

        def fs(pt):
            return max(pt, int(round(pt * (0.75 + 0.25 * scale))))

        total_w = page_w * 2 + gap
        start_x = (c_width - total_w) // 2
        sy0 = (c_height - page_h) // 2 + 6
        sy1 = sy0 + page_h

        # ---------------- LEFT SHEET: FRAMED COVER PREVIEW ----------------
        cx0 = start_x
        cx1 = cx0 + page_w
        # Soft multi-layer studio shadow
        canvas.create_rectangle(
            cx0 + 5, sy0 + 6, cx1 + 5, sy1 + 6, fill="#040507", outline=""
        )
        canvas.create_rectangle(
            cx0 + 2, sy0 + 3, cx1 + 2, sy1 + 3, fill="#07090E", outline=""
        )
        canvas.create_rectangle(
            cx0, sy0, cx1, sy1, fill=edition.paper, outline="#2D3548"
        )

        self._draw_sheet_border(
            canvas,
            cx0,
            sy0,
            cx1,
            sy1,
            border_style if border_style != "none" else "single",
            edition.accent,
            scale=scale,
        )

        cover_file = self.cover_var.get().strip()
        cover_hdr = (
            f"CUSTOM COVER: {Path(cover_file).name[:18]}"
            if cover_file
            else "TYPOGRAPHIC COVER"
        )
        canvas.create_text(
            cx0 + page_w // 2,
            sy0 - 11,
            text=cover_hdr,
            fill="#34D399" if cover_file else "#64748B",
            font=("Segoe UI", 7, "bold"),
        )

        title_item = canvas.create_text(
            cx0 + page_w // 2,
            sy0 + int(42 * scale),
            text=book_title.upper(),
            anchor="n",
            width=page_w - int(36 * scale),
            justify="center",
            fill=edition.ink,
            font=(heading_face, fs(8), "bold"),
        )
        t_bbox = canvas.bbox(title_item)
        title_bottom = t_bbox[3] if t_bbox else (sy0 + int(68 * scale))

        if subtitle:
            sub_item = canvas.create_text(
                cx0 + page_w // 2,
                title_bottom + int(6 * scale),
                text=subtitle[:42],
                anchor="n",
                width=page_w - int(38 * scale),
                justify="center",
                fill="#5A534C",
                font=("Georgia", fs(6), "italic"),
            )
            s_bbox = canvas.bbox(sub_item)
            rule_y = (
                (s_bbox[3] + int(10 * scale))
                if s_bbox
                else (title_bottom + int(22 * scale))
            )
        else:
            rule_y = title_bottom + int(12 * scale)

        rule_half = int(26 * scale)
        canvas.create_line(
            cx0 + page_w // 2 - rule_half,
            rule_y,
            cx0 + page_w // 2 + rule_half,
            rule_y,
            fill=edition.accent,
            width=max(1.5, 1.6 * scale),
        )

        canvas.create_text(
            cx0 + page_w // 2,
            rule_y + int(18 * scale),
            text=edition.scene_break,
            fill=edition.accent,
            font=("Georgia", fs(9)),
        )

        canvas.create_text(
            cx0 + page_w // 2,
            sy1 - int(24 * scale),
            text=author_name[:24].upper(),
            fill=edition.ink,
            font=("Segoe UI", fs(6), "bold"),
        )

        # ---------------- RIGHT SHEET: CHAPTER 1 INTERIOR ----------------
        sx0 = cx1 + gap
        sx1 = sx0 + page_w

        canvas.create_rectangle(
            sx0 + 5, sy0 + 6, sx1 + 5, sy1 + 6, fill="#040507", outline=""
        )
        canvas.create_rectangle(
            sx0 + 2, sy0 + 3, sx1 + 2, sy1 + 3, fill="#07090E", outline=""
        )
        canvas.create_rectangle(
            sx0, sy0, sx1, sy1, fill=edition.paper, outline="#2D3548"
        )

        self._draw_sheet_border(
            canvas, sx0, sy0, sx1, sy1, border_style, edition.accent, scale=scale
        )

        canvas.create_text(
            sx0 + page_w // 2,
            sy0 - 11,
            text=f"CHAPTER OPENER ({trim_key})",
            fill="#64748B",
            font=("Segoe UI", 7, "bold"),
        )

        # Running head
        canvas.create_text(
            sx1 - int(18 * scale),
            sy0 + int(20 * scale),
            text=book_title[:22].upper(),
            anchor="e",
            fill="#7A756E",
            font=("Georgia", fs(5)),
        )

        cursor_y = sy0 + int(34 * scale)
        margin_x = sx0 + int(20 * scale)
        inner_w = page_w - int(40 * scale)

        if edition.chapter_number:
            cnum_item = canvas.create_text(
                sx0 + page_w // 2,
                cursor_y,
                text="CHAPTER 1",
                anchor="n",
                fill=edition.accent,
                font=(
                    "Consolas" if edition.key == editions.SYSTEMFALL else "Georgia",
                    fs(6),
                    "bold",
                ),
            )
            cn_bbox = canvas.bbox(cnum_item)
            cursor_y = (
                (cn_bbox[3] + int(4 * scale))
                if cn_bbox
                else (cursor_y + int(15 * scale))
            )

        ch_item = canvas.create_text(
            sx0 + page_w // 2,
            cursor_y,
            text=inline.plain(chap_title)[:24].upper(),
            anchor="n",
            width=inner_w,
            justify="center",
            fill=edition.ink,
            font=(heading_face, fs(7), heading_style),
        )
        ch_bbox = canvas.bbox(ch_item)
        cursor_y = (
            (ch_bbox[3] + int(7 * scale)) if ch_bbox else (cursor_y + int(18 * scale))
        )

        if edition.chapter_rule:
            c_rule_half = int(22 * scale)
            canvas.create_line(
                sx0 + page_w // 2 - c_rule_half,
                cursor_y,
                sx0 + page_w // 2 + c_rule_half,
                cursor_y,
                fill=edition.accent,
                width=max(1.5, 1.5 * scale),
            )
            cursor_y += int(12 * scale)
        else:
            cursor_y += int(7 * scale)

        line_step = max(7, int(round(7 * scale)))
        box_sz = max(16, int(round(17 * scale)))

        if edition.drop_cap:
            letter = edition.drop_cap_letter or self._first_paragraph_letter()
            dc_style = getattr(edition, "drop_cap_style", "classic")
            if dc_style == "boxed":
                canvas.create_rectangle(
                    margin_x,
                    cursor_y - 3,
                    margin_x + box_sz,
                    cursor_y + box_sz - 3,
                    fill=edition.accent,
                    outline=edition.accent,
                )
                canvas.create_text(
                    margin_x + box_sz // 2,
                    cursor_y + box_sz // 2 - 3,
                    text=letter,
                    fill=edition.paper,
                    font=(heading_face, fs(9), "bold"),
                )
                indent_dc = box_sz + max(4, int(5 * scale))
                line_offsets = [indent_dc, indent_dc, 0, 0, 0]
            elif dc_style == "framed":
                canvas.create_rectangle(
                    margin_x,
                    cursor_y - 3,
                    margin_x + box_sz,
                    cursor_y + box_sz - 3,
                    fill=edition.paper,
                    outline=edition.accent,
                    width=1.5,
                )
                canvas.create_text(
                    margin_x + box_sz // 2,
                    cursor_y + box_sz // 2 - 3,
                    text=letter,
                    fill=edition.accent,
                    font=(heading_face, fs(9), "bold"),
                )
                indent_dc = box_sz + max(4, int(5 * scale))
                line_offsets = [indent_dc, indent_dc, 0, 0, 0]
            else:
                canvas.create_text(
                    margin_x + 1,
                    cursor_y - 4,
                    text=letter,
                    anchor="nw",
                    fill=edition.accent,
                    font=(heading_face, fs(13), "bold"),
                )
                indent_dc = max(15, int(16 * scale))
                line_offsets = [indent_dc, indent_dc, 0, 0, 0]
        else:
            line_offsets = [int(9 * scale), 0, 0, 0, 0]

        line_w = max(2.0, 2.0 * scale)
        for idx, indent_px in enumerate(line_offsets):
            ly = cursor_y + idx * line_step
            end_trim = int(14 * scale) if idx == len(line_offsets) - 1 else 0
            canvas.create_line(
                margin_x + indent_px,
                ly,
                margin_x + inner_w - end_trim,
                ly,
                fill="#3E3B38" if idx > 0 else edition.ink,
                width=line_w,
            )
        cursor_y += len(line_offsets) * line_step + int(10 * scale)

        canvas.create_text(
            sx0 + page_w // 2,
            cursor_y,
            text=edition.scene_break,
            fill=edition.accent,
            font=("Georgia", fs(8)),
        )
        cursor_y += int(11 * scale)

        for idx in range(5):
            ly = cursor_y + idx * line_step
            if ly > sy1 - int(28 * scale):
                break
            indent_px = int(9 * scale) if idx == 0 else 0
            end_trim = int(24 * scale) if idx == 4 else 0
            canvas.create_line(
                margin_x + indent_px,
                ly,
                margin_x + inner_w - end_trim,
                ly,
                fill="#524E4A",
                width=line_w,
            )

        canvas.create_text(
            sx0 + page_w // 2,
            sy1 - int(20 * scale),
            text="1",
            fill="#6E665E",
            font=("Georgia", fs(6)),
        )

    # ---------------------------------------------------------------- helpers

    def write(self, message, tag=None):
        self.log.configure(state="normal")
        self.log.insert("end", message + "\n", tag or ())
        self.log.see("end")
        self.log.configure(state="disabled")

    def _load_sample(self):
        if SAMPLE_PATH.is_file():
            self.manuscript_var.set(str(SAMPLE_PATH))
            self._load_manuscript()
        else:
            self.write("Sample manuscript not found in manuscripts/.", "warn")

    def handle_dropped_file(self, dropped_path):
        """Handle a file or folder dragged and dropped onto the app window."""
        path = Path(str(dropped_path).strip().strip('"'))
        if path.is_dir():
            self.out_var.set(str(path))
            self.write(f"Output folder set via drag & drop: {path}", "ok")
            return
        if not path.is_file():
            return

        ext = path.suffix.lower()
        if ext in (".jpg", ".jpeg", ".png", ".svg"):
            self.cover_var.set(str(path))
            self.write(f"Cover file attached: {path.name}", "ok")
        elif ext in (".html", ".htm"):
            self.chrome_var.set(str(path))
            self.write(f"Web template attached via drag & drop: {path.name}", "ok")
        else:
            self.manuscript_var.set(str(path))
            self._load_manuscript()
            if hasattr(self, "notebook"):
                self._switch_right_tab(0)

    def _choose_manuscript(self):
        path = filedialog.askopenfilename(
            title="Choose a manuscript",
            initialdir=str(HERE / "manuscripts"),
            filetypes=[
                ("Manuscripts", "*.md *.markdown *.txt *.docx"),
                ("All files", "*.*"),
            ],
        )
        if path:
            self.manuscript_var.set(path)
            self._load_manuscript()

    def _choose_cover(self):
        path = filedialog.askopenfilename(
            title="Choose a cover image (.jpg, .png, .svg)",
            initialdir=str(Path(self.manuscript_var.get()).parent)
            if self.manuscript_var.get()
            else str(HERE),
            filetypes=[
                ("Cover Images", "*.jpg *.jpeg *.png *.svg"),
                ("All files", "*.*"),
            ],
        )
        if path:
            self.cover_var.set(path)
            self.write(f"Cover file attached: {Path(path).name}", "ok")

    def _clear_cover(self):
        self.cover_var.set("")

    def _choose_out(self):
        path = filedialog.askdirectory(
            title="Where should the files go?",
            initialdir=self.out_var.get() or str(HERE),
        )
        if path:
            self.out_var.set(path)

    def _choose_chrome(self):
        path = filedialog.askopenfilename(
            title="Choose a page from your site to match",
            filetypes=[("Web pages", "*.html *.htm"), ("All files", "*.*")],
        )
        if path:
            self.chrome_var.set(path)

    def _collect_project_settings(self):
        """Collect all current book metadata, front/back matter, and style settings."""
        self._flush_matter_editor()
        settings = {key: var.get().strip() for key, var in self.meta_vars.items()}
        tier = TIER_BY_LABEL.get(self.tier_var.get(), editions.CLEAN)
        settings["tier"] = tier
        if tier == editions.ILLUSTRATED:
            settings["edition"] = EDITION_BY_LABEL.get(
                self.edition_var.get(), editions.ASHVEIL
            )
        fp_key = FONT_PAIRING_BY_LABEL.get(self.font_pairing_var.get(), "edition")
        if fp_key and fp_key != "edition":
            settings["font_pairing"] = fp_key
        b_style = BORDER_STYLE_BY_LABEL.get(self.border_style_var.get())
        if b_style:
            settings["border_style"] = b_style
        b_color = self.border_color_var.get().strip()
        if b_color:
            settings["border_color"] = b_color
        dc_style = DROP_CAP_STYLE_BY_LABEL.get(self.drop_cap_style_var.get())
        if dc_style:
            settings["drop_cap_style"] = dc_style
        dc_letter_raw = self.drop_cap_letter_var.get().strip()
        if len(dc_letter_raw) == 1 and dc_letter_raw.isalnum():
            settings["drop_cap_letter"] = dc_letter_raw.upper()
        trim = self.trim_var.get().strip()
        if trim:
            settings["trim"] = trim
        cover = self.cover_var.get().strip()
        if cover:
            settings["cover"] = cover
        return settings

    def _save_project(self):
        """Save per-book settings to <manuscript-stem>.inkpress.json next to the manuscript."""
        raw_ms = self.manuscript_var.get().strip()
        if not raw_ms or not Path(raw_ms).is_file():
            self._switch_right_tab(1)
            self.write("Load a manuscript first before saving a project sidecar.", "warn")
            return None
        sidecar = project.save_project(raw_ms, self._collect_project_settings())
        self._save_prefs()
        self.status_var.set(f"Saved project settings to {sidecar.name}.")
        self.write(f"Saved per-book project: {sidecar}", "ok")
        return sidecar

    def _refresh_kdp_and_preview(self):
        doc = self.current_document
        if doc:
            trim = self.trim_var.get().strip() or "6x9"
            stats = estimate_kdp_stats(doc.word_count, len(doc.chapters), trim=trim)
            kdp_flag = "" if stats["pages"] >= 24 else " (<24p)"
            self.kdp_summary_var.set(
                f"{trim} · ~{stats['pages']} pp{kdp_flag} · "
                f"Gutter {stats['gutter']} · "
                f"Spine {stats['spine_in']:.3f}\""
            )
        self._draw_page_preview()

    def _load_manuscript(self):
        """Read the file, merge any .inkpress.json project sidecar, and populate the UI."""
        path = Path(self.manuscript_var.get())
        if not path.is_file():
            self.status_var.set("That file could not be found.")
            return

        try:
            parsed = ms.load(path)
            sidecar_meta = project.load_project(path)
            for s_key, s_val in sidecar_meta.items():
                if s_val not in (None, "", []):
                    parsed.meta[s_key] = s_val
            doc = structure.build(parsed)
        except ms.ManuscriptError as error:
            self.status_var.set("Could not read that manuscript.")
            self.write(f"Could not read {path.name}: {error}", "error")
            return

        self.current_document = doc

        for key, _ in META_FIELDS:
            value = parsed.meta.get(key, "")
            self.meta_vars[key].set("" if isinstance(value, list) else str(value))

        if not self.meta_vars["date"].get():
            self.meta_vars["date"].set(date.today().isoformat())
        if not self.meta_vars["title"].get():
            self.meta_vars["title"].set(path.stem.replace("-", " ").replace("_", " ").title())

        tier_key = str(parsed.meta.get("tier", "")).strip().lower()
        self.tier_var.set(editions.TIER_LABELS.get(tier_key, TIER_CHOICES[0]))

        edition_key = str(parsed.meta.get("edition", "")).strip().lower()
        self.edition_var.set(editions.EDITION_LABELS.get(edition_key, EDITION_CHOICES[0]))
        self._sync_edition_state(reset_from_tier=True)

        fp_key = str(parsed.meta.get("font_pairing", "edition")).strip().lower()
        self.font_pairing_var.set(
            editions.FONT_PAIRING_LABELS.get(fp_key, FONT_PAIRING_CHOICES[0])
        )
        if parsed.meta.get("border_style"):
            bs_key = str(parsed.meta["border_style"]).strip().lower()
            if bs_key in editions.BORDER_STYLE_LABELS:
                self.border_style_var.set(editions.BORDER_STYLE_LABELS[bs_key])
        if parsed.meta.get("border_color"):
            self.border_color_var.set(str(parsed.meta["border_color"]).strip())
        if parsed.meta.get("drop_cap_style"):
            dc_key = str(parsed.meta["drop_cap_style"]).strip().lower()
            if dc_key in editions.DROP_CAP_STYLE_LABELS:
                self.drop_cap_style_var.set(editions.DROP_CAP_STYLE_LABELS[dc_key])
        if parsed.meta.get("drop_cap_letter"):
            dc_let = str(parsed.meta["drop_cap_letter"]).strip()[:1].upper()
            if dc_let in DROP_LETTER_CHOICES:
                self.drop_cap_letter_var.set(dc_let)
        else:
            self.drop_cap_letter_var.set(DROP_LETTER_CHOICES[0])
        self._sync_edition_state(reset_from_tier=False)

        trim_val = str(parsed.meta.get("trim", "")).strip()
        self.trim_var.set(trim_val if trim_val else TRIM_CHOICES[0])

        cover_val = str(parsed.meta.get("cover", "")).strip()
        self.cover_var.set(cover_val)

        self._load_matter_editor(self._active_matter_key)

        for item in self.chapter_tree.get_children():
            self.chapter_tree.delete(item)

        for ch in doc.chapters:
            num_disp = (
                "—"
                if ch.implicit or ch.display_number is None
                else str(ch.display_number)
            )
            if ch.implicit:
                note = "Implicit dispatch"
            elif ch.display_number is None:
                note = "Front/Back matter"
            elif getattr(ch, "part_title", None):
                note = f"Part: {inline.plain(ch.part_title)[:18]}"
            else:
                note = "Chapter"
            self.chapter_tree.insert(
                "",
                "end",
                values=(num_disp, inline.plain(ch.title), f"{ch.word_count:,}", note),
            )

        trim = self.trim_var.get().strip() or "6x9"
        stats = estimate_kdp_stats(doc.word_count, len(doc.chapters), trim=trim)
        chapter_text = (
            f"{len(doc.chapters)} chapters"
            if len(doc.chapters) != 1
            else ("no chapter breaks" if not doc.has_real_chapters else "1 chapter")
        )
        sidecar_note = " (+ saved project)" if sidecar_meta else ""
        self.status_var.set(
            f"Loaded {path.name}{sidecar_note} — {chapter_text}, {doc.word_count:,} words (~{stats['pages']} paperback pages)."
        )
        self._refresh_kdp_and_preview()
        self.write(
            f"Loaded {path.name}{sidecar_note} ({chapter_text}, {doc.word_count:,} words).",
            "muted",
        )

    def _open_output(self):
        if self.last_out_dir and not open_folder(self.last_out_dir):
            self.write(f"Could not open {self.last_out_dir}", "warn")

    def _preview_print(self):
        target = self.last_outputs.get("pdf") or self.last_outputs.get("print")
        if target and not open_folder(target):
            self.write(f"Could not open {target}", "warn")

    def _preview_web(self):
        target = self.last_outputs.get("site")
        if target and not open_folder(target):
            self.write(f"Could not open {target}", "warn")

    # ------------------------------------------------------------------ build

    def _pro_features_requested(self, tier, border_style, font_pairing, pdf, package):
        """Return a list of Studio Pro features currently selected for export."""
        reasons = []
        if tier != editions.CLEAN:
            reasons.append(editions.TIER_LABELS.get(tier, tier))
        if border_style and border_style != "none":
            reasons.append("Colored Page Borders")
        if font_pairing and font_pairing != "edition":
            reasons.append("Custom Font Pairing")
        if pdf:
            reasons.append("Direct KDP PDF Export")
        if package:
            reasons.append("Buyer ZIP Package")
        return reasons

    def _start_build(self):
        if self.busy:
            return

        self._flush_matter_editor()

        source = Path(self.manuscript_var.get())
        if not source.is_file():
            self._switch_right_tab(1)
            self.write("Choose a manuscript first (or click Load Sample).", "error")
            return

        targets = [key for key, _, _ in TARGET_LABELS if self.target_vars[key].get()]
        if not targets:
            self._switch_right_tab(1)
            self.write("Tick at least one format to build.", "error")
            return

        overrides = {key: var.get().strip() for key, var in self.meta_vars.items()}
        trim = self.trim_var.get().strip()
        if trim:
            overrides["trim"] = trim
        fp_key = FONT_PAIRING_BY_LABEL.get(self.font_pairing_var.get(), "edition")
        if fp_key and fp_key != "edition":
            overrides["font_pairing"] = fp_key
        b_style = BORDER_STYLE_BY_LABEL.get(self.border_style_var.get())
        if b_style:
            overrides["border_style"] = b_style
        b_color = self.border_color_var.get().strip()
        if b_color:
            overrides["border_color"] = b_color
        dc_style = DROP_CAP_STYLE_BY_LABEL.get(self.drop_cap_style_var.get())
        if dc_style:
            overrides["drop_cap_style"] = dc_style
        dc_letter_raw = self.drop_cap_letter_var.get().strip()
        if len(dc_letter_raw) == 1 and dc_letter_raw.isalnum():
            overrides["drop_cap_letter"] = dc_letter_raw.upper()
        cover = self.cover_var.get().strip()
        if cover:
            overrides["cover"] = cover
        out_dir = self.out_var.get().strip() or str(HERE / "build")
        chrome_path = self.chrome_var.get().strip() or None
        pdf = bool(self.pdf_var.get()) and ("print" in targets)
        package = bool(self.package_var.get())

        tier = TIER_BY_LABEL.get(self.tier_var.get(), editions.CLEAN)
        edition = (
            EDITION_BY_LABEL.get(self.edition_var.get())
            if tier == editions.ILLUSTRATED
            else None
        )

        if not self.is_pro_unlocked():
            pro_used = self._pro_features_requested(tier, b_style, fp_key, pdf, package)
            if pro_used:
                summary = ", ".join(pro_used)
                self._switch_right_tab(1)
                self.write(
                    f"Studio Pro required to export: {summary}. "
                    "Enter your license key or switch to Tier 1 Clean (no borders / PDF / ZIP) for Free Starter export.",
                    "warn",
                )
                self._open_license_dialog(
                    f"Studio Pro is required to export: {summary}.\n\n"
                    "Enter your INKP-XXXX-XXXX-XXXX-XXXX license key below, or switch to Tier 1 Clean to export for free."
                )
                return

        self._save_prefs()
        self._switch_right_tab(1)

        self.busy = True
        self.format_button.configure(state="disabled")
        self.progress.configure(mode="indeterminate")
        self.progress.start(12)
        self.write("")
        self.write(f"Formatting {source.name}...")

        threading.Thread(
            target=self._run_build,
            args=(source, out_dir, targets, overrides, chrome_path, tier, edition, pdf, package),
            daemon=True,
        ).start()

    def _run_build(self, source, out_dir, targets, overrides, chrome_path, tier, edition,
                   pdf=False, package=False):
        """Worker thread. Never touches widgets — results go through the queue."""
        try:
            chrome = pipeline.load_chrome(chrome_path) if chrome_path else None
            result = pipeline.build(
                source,
                out_dir=out_dir,
                targets=targets,
                chrome=chrome,
                meta_overrides=overrides,
                tier=tier,
                edition=edition,
                pdf=pdf,
                package=package,
            )
            self.results.put(("done", result, out_dir))
        except editions.EditionError as error:
            self.results.put(("missing", str(error), None))
        except ms.ManuscriptError as error:
            self.results.put(("manuscript", str(error), None))
        except validate.ValidationError as error:
            self.results.put(("invalid", str(error), None))
        except FileNotFoundError as error:
            self.results.put(("missing", str(error), None))
        except Exception:  # noqa: BLE001 - surface anything unexpected in the log
            self.results.put(("crash", traceback.format_exc(), None))

    def _drain(self):
        """Poll the worker queue on the UI thread."""
        try:
            while True:
                kind, payload, out_dir = self.results.get_nowait()
                self._finish(kind, payload, out_dir)
        except queue.Empty:
            pass
        self.after(120, self._drain)

    def _finish(self, kind, payload, out_dir):
        self.busy = False
        self.progress.stop()
        self.progress.configure(mode="determinate", value=100 if kind == "done" else 0)
        self.format_button.configure(state="normal")

        if kind == "done":
            if payload.edition:
                self.write(f"  {payload.edition.label}", "muted")
            for warning in payload.warnings:
                self.write(f"  Heads up: {warning}", "warn")
            for target, path in payload:
                label = OUTPUT_NAMES.get(target, target)
                self.write(f"  {label}: {path}", "ok")
            self.write("Done.", "ok")
            self.last_out_dir = out_dir
            self.last_outputs = dict(payload.outputs)
            self.open_button.configure(state="normal")
            self.preview_print_button.configure(
                state="normal" if ("pdf" in payload.outputs or "print" in payload.outputs) else "disabled"
            )
            self.preview_web_button.configure(
                state="normal" if "site" in payload.outputs else "disabled"
            )

        elif kind == "invalid":
            self.write("Cannot format yet - some details are missing:", "error")
            for line in payload.splitlines():
                cleaned = line.strip().lstrip("- ").strip()
                if cleaned:
                    self.write(f"  {self._friendly(cleaned)}", "error")

        elif kind == "manuscript":
            self.write(f"Could not read the manuscript: {payload}", "error")

        elif kind == "missing":
            self.write(payload, "error")

        else:
            self.write("Something went wrong:", "error")
            self.write(payload, "error")

    @staticmethod
    def _friendly(message):
        """Turn a validator message into something a person can act on."""
        if "missing required key" in message:
            key = message.rsplit(":", 1)[-1].strip()
            names = dict(META_FIELDS)
            if key in names:
                return f"Fill in the {names[key]} field above."
            return f"The manuscript needs a '{key}' line in its header."
        if "expected YYYY-MM-DD" in message:
            return "Date must look like 2026-08-22."
        return message


def main():
    initial = sys.argv[1] if len(sys.argv) > 1 else None

    if platform.system() == "Windows":
        try:
            import ctypes

            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "builtbyjoshstudio.inkpress"
            )
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:  # noqa: BLE001
            pass

    if not initial and not _acquire_single_instance_lock():
        return

    root = tk.Tk()
    root.title(f"inkpress {__version__} — Book & Dispatch Formatting Studio")
    root.geometry("1160x820")
    root.minsize(980, 720)
    ico_path = HERE / "inkpress.ico"
    if ico_path.is_file():
        try:
            root.iconbitmap(str(ico_path))
        except tk.TclError:
            pass

    InkpressApp(root, initial_manuscript=initial)
    root.mainloop()


if __name__ == "__main__":
    main()
