#!/usr/bin/env python3
"""
inkpress_app.py — the inkpress Editorial Studio desktop app.

A modern two-column studio window over the same pipeline the CLI uses:
  - Header bar: studio branding + keyboard shortcut badges.
  - Left column: interactive drag-and-drop zone and clean tabbed configuration
    (Book Details / Edition, Borders & Print / Outputs) so controls never clip
    on High-DPI screens.
  - Right column: live two-page spread preview (Typographic Framed Cover +
    Chapter 1 Opener with customizable colored borders) and tabbed Chapter
    Outline / KDP Spine Inspector & Build Log.
  - Bottom bar: persistent Format Book primary CTA and preview actions.

Launch by double-clicking inkpress.exe (or inkpress-app.cmd), or:
    python inkpress_app.py
    python inkpress_app.py path\\to\\draft.md
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
from inkpress_lib import manuscript as ms  # noqa: E402
from inkpress_lib import pipeline, render_print, structure, validate  # noqa: E402

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

TRIM_CHOICES = ("6x9", "5.5x8.5", "5.25x8", "5x8")

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
    ("description", "Description"),
    ("dedication", "Dedication"),
    ("copyright", "Copyright"),
)

# Studio color palette
BG_APP = "#F4F1EA"
BG_CARD = "#FFFFFF"
BG_SUBTLE = "#FAF8F4"
BORDER_CARD = "#DDD6C9"
INK_DARK = "#191817"
INK_BODY = "#2E2B28"
INK_MUTED = "#6E665E"
ACCENT_CRIMSON = "#8B261D"
ACCENT_CRIMSON_HOVER = "#A63026"

PAD = 10
_WNDPROC_REFS = []


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
    """Apply a cohesive warm-paper editorial theme over ttk."""
    root.configure(bg=BG_APP)
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure(".", background=BG_APP, foreground=INK_BODY, font=("Segoe UI", 9))
    style.configure("TFrame", background=BG_APP)
    style.configure("Card.TFrame", background=BG_CARD)
    style.configure("TLabel", background=BG_CARD, foreground=INK_BODY, font=("Segoe UI", 9))
    style.configure(
        "Muted.TLabel", background=BG_CARD, foreground=INK_MUTED, font=("Segoe UI", 8)
    )
    style.configure(
        "Section.TLabel",
        background=BG_CARD,
        foreground="#7A6D5D",
        font=("Segoe UI", 8, "bold"),
    )
    style.configure(
        "TCheckbutton",
        background=BG_CARD,
        foreground=INK_BODY,
        font=("Segoe UI", 9, "bold"),
    )
    style.map("TCheckbutton", background=[("active", BG_CARD)])

    style.configure(
        "TEntry",
        fieldbackground=BG_SUBTLE,
        foreground=INK_DARK,
        bordercolor="#D2C9BA",
        lightcolor=BG_SUBTLE,
        darkcolor=BG_SUBTLE,
        padding=4,
    )
    style.configure(
        "TCombobox",
        fieldbackground=BG_SUBTLE,
        background=BG_SUBTLE,
        foreground=INK_DARK,
        bordercolor="#D2C9BA",
        arrowcolor=INK_BODY,
        padding=4,
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", BG_SUBTLE), ("disabled", "#EFECE6")],
        selectbackground=[("readonly", BG_SUBTLE)],
        selectforeground=[("readonly", INK_DARK)],
    )

    style.configure(
        "TButton",
        background="#EDE8DF",
        foreground=INK_DARK,
        bordercolor="#CFC6B8",
        lightcolor="#EDE8DF",
        darkcolor="#EDE8DF",
        focusthickness=0,
        padding=(10, 5),
        font=("Segoe UI", 9),
    )
    style.map(
        "TButton",
        background=[("active", "#E2DBD0"), ("disabled", "#F2EFE9")],
        foreground=[("disabled", "#A8A096")],
    )

    style.configure(
        "Primary.TButton",
        background=ACCENT_CRIMSON,
        foreground="#FFFFFF",
        bordercolor=ACCENT_CRIMSON,
        lightcolor=ACCENT_CRIMSON,
        darkcolor=ACCENT_CRIMSON,
        padding=(16, 7),
        font=("Segoe UI", 9, "bold"),
    )
    style.map(
        "Primary.TButton",
        background=[("active", ACCENT_CRIMSON_HOVER), ("disabled", "#B89A96")],
        foreground=[("disabled", "#F5ECEB")],
    )

    style.configure(
        "TNotebook",
        background=BG_APP,
        borderwidth=0,
        tabmargins=(0, 0, 0, 0),
    )
    style.configure(
        "TNotebook.Tab",
        background="#E5DFD3",
        foreground=INK_MUTED,
        padding=(9, 6),
        borderwidth=0,
        font=("Segoe UI", 9, "bold"),
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", BG_CARD), ("active", "#EDE8DE")],
        foreground=[("selected", INK_DARK), ("active", INK_DARK)],
    )

    style.configure(
        "Treeview",
        background=BG_CARD,
        fieldbackground=BG_CARD,
        foreground=INK_BODY,
        rowheight=24,
        borderwidth=0,
        font=("Segoe UI", 9),
    )
    style.configure(
        "Treeview.Heading",
        background="#EFECE4",
        foreground=INK_DARK,
        relief="flat",
        padding=(6, 4),
        font=("Segoe UI", 8, "bold"),
    )
    style.map("Treeview", background=[("selected", "#EFE7DA")], foreground=[("selected", INK_DARK)])

    style.configure(
        "Horizontal.TProgressbar",
        troughcolor="#E6E0D4",
        background=ACCENT_CRIMSON,
        bordercolor="#E6E0D4",
        lightcolor=ACCENT_CRIMSON,
        darkcolor=ACCENT_CRIMSON,
        thickness=8,
    )


def _make_card(parent, title=None, pad=12):
    """Create a crisp bordered studio card container."""
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
        hdr = tk.Label(
            outer,
            text=title.upper(),
            bg=BG_CARD,
            fg="#7A6D5D",
            font=("Segoe UI", 8, "bold"),
            anchor="w",
        )
        hdr.grid(row=0, column=0, columnspan=10, sticky="w", pady=(0, 8))
    return outer


class InkpressApp(ttk.Frame):
    def __init__(self, master, initial_manuscript=None):
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
        self.status_var = tk.StringVar(
            value="No manuscript loaded yet — drop a file above or click Load Sample."
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

        # Main two-column studio body
        body_frame = ttk.Frame(self, padding=(14, 12, 14, 8))
        body_frame.grid(row=1, column=0, sticky="nsew")
        body_frame.columnconfigure(0, weight=5, minsize=440)
        body_frame.columnconfigure(1, weight=6, minsize=460)
        body_frame.rowconfigure(0, weight=1)

        left_col = ttk.Frame(body_frame)
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        left_col.columnconfigure(0, weight=1)
        left_col.rowconfigure(1, weight=1)

        right_col = ttk.Frame(body_frame)
        right_col.grid(row=0, column=1, sticky="nsew")
        right_col.columnconfigure(0, weight=1)
        right_col.rowconfigure(1, weight=1)

        self._build_manuscript_card(left_col, 0)
        self._build_config_tabs(left_col, 1)

        self._build_preview_card(right_col, 0)
        self._build_inspector_and_log(right_col, 1)

        # Persistent bottom action bar (never clipped)
        self._build_action_bar(row=2)

        for key in ("title", "subtitle", "author"):
            self.meta_vars[key].trace_add("write", lambda *_args: self._draw_page_preview())

        master.bind("<Control-o>", lambda _e: self._choose_manuscript())
        master.bind("<Control-Return>", lambda _e: self._start_build())
        master.bind("<F5>", lambda _e: self._start_build())

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

    # ---------------------------------------------------------------- layout

    def _build_header(self):
        header_wrap = tk.Frame(self, bg=INK_DARK)
        header_wrap.grid(row=0, column=0, sticky="ew")
        header_wrap.columnconfigure(0, weight=1)

        banner = tk.Frame(header_wrap, bg=INK_DARK, padx=16, pady=10)
        banner.grid(row=0, column=0, sticky="ew")
        banner.columnconfigure(2, weight=1)

        tk.Label(
            banner,
            text="INKPRESS",
            bg=INK_DARK,
            fg="#FDFBF7",
            font=("Georgia", 14, "bold"),
        ).grid(row=0, column=0, sticky="w")

        tk.Label(
            banner,
            text=f"STUDIO v{__version__}",
            bg="#2C2825",
            fg="#D6C7B2",
            padx=7,
            pady=2,
            font=("Segoe UI", 7, "bold"),
        ).grid(row=0, column=1, sticky="w", padx=(10, 10))

        tk.Label(
            banner,
            text="Book, EPUB & KDP Print Formatting Pipeline",
            bg=INK_DARK,
            fg="#A89F94",
            font=("Segoe UI", 9),
        ).grid(row=0, column=2, sticky="w")

        tk.Label(
            banner,
            text="Ctrl+O Open   ·   F5 Format",
            bg=INK_DARK,
            fg="#857B70",
            font=("Consolas", 8),
        ).grid(row=0, column=3, sticky="e")

        tk.Frame(header_wrap, bg=ACCENT_CRIMSON, height=2).grid(
            row=1, column=0, sticky="ew"
        )

    def _build_manuscript_card(self, parent, row):
        card = _make_card(parent, "1 · Manuscript Source", pad=11)
        card.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        card.columnconfigure(0, weight=1)

        self.drop_canvas = tk.Canvas(
            card,
            height=58,
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
            row=2, column=1, padx=(0, 4)
        )
        ttk.Button(card, text="Load Sample", command=self._load_sample).grid(
            row=2, column=2
        )

        ttk.Label(
            card,
            textvariable=self.status_var,
            style="Muted.TLabel",
            wraplength=420,
        ).grid(row=3, column=0, columnspan=3, sticky="w", pady=(6, 0))

    def _set_drop_hover(self, hovered):
        self._drop_hover = bool(hovered)
        self._draw_drop_zone()

    def _draw_drop_zone(self):
        if not hasattr(self, "drop_canvas"):
            return
        c = self.drop_canvas
        c.delete("all")
        w = max(int(c.winfo_width()), 380)
        h = max(int(c.winfo_height()), 58)

        bg = "#F5EFE6" if self._drop_hover else BG_SUBTLE
        border = ACCENT_CRIMSON if self._drop_hover else "#C8BFAF"
        c.configure(bg=bg)
        c.create_rectangle(
            2, 2, w - 3, h - 3,
            outline=border,
            width=1.5 if self._drop_hover else 1,
            dash=(5, 3),
            fill=bg,
        )

        ix, iy = 22, h // 2
        c.create_rectangle(ix - 8, iy - 11, ix + 8, iy + 11, fill="#FFFFFF", outline=border)
        c.create_line(ix - 4, iy - 4, ix + 4, iy - 4, fill=border)
        c.create_line(ix - 4, iy, ix + 4, iy, fill=border)
        c.create_line(ix - 4, iy + 4, ix + 2, iy + 4, fill=border)

        c.create_text(
            42,
            iy - 7,
            text="Drop a manuscript here (.md, .docx, .txt)",
            anchor="w",
            fill=INK_DARK,
            font=("Segoe UI", 8, "bold"),
        )
        c.create_text(
            42,
            iy + 8,
            text="Click to browse  ·  Drop a web template (.html) or output folder",
            anchor="w",
            fill=INK_MUTED,
            font=("Segoe UI", 7),
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
        # If borders are currently 'none', enable Double Frame automatically when picking a color
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
        return editions.resolve(
            tier,
            edition_key if tier == editions.ILLUSTRATED else None,
            border_color=b_color,
            border_style=b_style,
            drop_cap_style=dc_style,
            drop_cap_letter=dc_letter,
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
                    bg="#E6F2EA",
                    fg="#1A7F37",
                )
            else:
                self.drop_tier_badge.configure(
                    text="TIER 2+ ONLY (SELECT TIER 2 OR 3)",
                    bg="#EFE8DC",
                    fg="#7A6D5D",
                )

        resolved = self._resolved_edition()

        active_pair = (tier, edition_key if tier == editions.ILLUSTRATED else None)
        for pair, btn in self._preset_buttons.items():
            if pair == active_pair:
                btn.configure(bg=INK_DARK, fg="#FDFBF7", activebackground=INK_DARK)
            else:
                btn.configure(bg=BG_SUBTLE, fg=INK_BODY, activebackground="#EDE7DC")

        active_hex = resolved.accent.lower()
        for hex_code, btn in self._color_swatch_buttons.items():
            is_sel = hex_code.lower() == active_hex
            btn.configure(
                relief="solid",
                bd=2 if is_sel else 1,
                text="✓" if is_sel else "",
                fg="#FFFFFF",
            )

        if hasattr(self, "swatch_canvas"):
            self.swatch_canvas.delete("all")
            self.swatch_canvas.create_rectangle(0, 0, 22, 16, fill=resolved.ink, outline="")
            self.swatch_canvas.create_rectangle(22, 0, 44, 16, fill=resolved.accent, outline="")

        features = [editions.BORDER_STYLE_LABELS.get(resolved.border_style, "No Border")]
        if resolved.drop_cap:
            letter_disp = resolved.drop_cap_letter or self._first_paragraph_letter()
            features.append(f"drop letter '{letter_disp}' ({resolved.drop_cap_style})")
        if resolved.chapter_rule:
            features.append("chapter rules")
        if hasattr(self, "tier_hint"):
            self.tier_hint.configure(
                text=f"Color: {resolved.accent.upper()}  ·  Scene break: {resolved.scene_break}  ·  {', '.join(features)}"
            )
        if hasattr(self, "page_canvas"):
            self._draw_page_preview()

    def _build_config_tabs(self, parent, row):
        self.left_notebook = ttk.Notebook(parent)
        self.left_notebook.grid(row=row, column=0, sticky="nsew")

        details_tab = tk.Frame(
            self.left_notebook,
            bg=BG_CARD,
            padx=14,
            pady=12,
            highlightthickness=1,
            highlightbackground=BORDER_CARD,
        )
        details_tab.columnconfigure(1, weight=1)
        details_tab.columnconfigure(3, weight=1)

        style_tab = tk.Frame(
            self.left_notebook,
            bg=BG_CARD,
            padx=12,
            pady=9,
            highlightthickness=1,
            highlightbackground=BORDER_CARD,
        )
        style_tab.columnconfigure(1, weight=1)

        outputs_tab = tk.Frame(
            self.left_notebook,
            bg=BG_CARD,
            padx=14,
            pady=12,
            highlightthickness=1,
            highlightbackground=BORDER_CARD,
        )
        outputs_tab.columnconfigure(1, weight=1)

        self._populate_details_tab(details_tab)
        self._populate_style_tab(style_tab)
        self._populate_outputs_tab(outputs_tab)

        self.left_notebook.add(details_tab, text="2 · Book Details")
        self.left_notebook.add(style_tab, text="3 · Borders & Style")
        self.left_notebook.add(outputs_tab, text="4 · Outputs")

    def _populate_details_tab(self, box):
        r = 0
        for key, label in (("title", "Title"), ("subtitle", "Subtitle")):
            ttk.Label(box, text=label).grid(row=r, column=0, sticky="w", pady=4)
            ttk.Entry(box, textvariable=self.meta_vars[key]).grid(
                row=r, column=1, columnspan=3, sticky="ew", padx=(8, 0), pady=4
            )
            r += 1

        paired = (
            ("author", "Author", "publisher", "Publisher"),
            ("date", "Date", "dedication", "Dedication"),
        )
        for k1, l1, k2, l2 in paired:
            ttk.Label(box, text=l1).grid(row=r, column=0, sticky="w", pady=4)
            ttk.Entry(box, textvariable=self.meta_vars[k1]).grid(
                row=r, column=1, sticky="ew", padx=(8, 12), pady=4
            )
            ttk.Label(box, text=l2).grid(row=r, column=2, sticky="w", pady=4)
            ttk.Entry(box, textvariable=self.meta_vars[k2]).grid(
                row=r, column=3, sticky="ew", padx=(8, 0), pady=4
            )
            r += 1

        for key, label in (("description", "Description"), ("copyright", "Copyright")):
            ttk.Label(box, text=label).grid(row=r, column=0, sticky="w", pady=4)
            ttk.Entry(box, textvariable=self.meta_vars[key]).grid(
                row=r, column=1, columnspan=3, sticky="ew", padx=(8, 0), pady=4
            )
            r += 1

        ttk.Label(
            box,
            text="Prefilled from your manuscript (.md or .docx). Leave Copyright blank for an automatic © page.",
            style="Muted.TLabel",
            wraplength=410,
        ).grid(row=r, column=0, columnspan=4, sticky="w", pady=(8, 0))

    def _populate_style_tab(self, box):
        r = 0
        ttk.Label(box, text="TYPOGRAPHY TIER & EDITION", style="Section.TLabel").grid(
            row=r, column=0, columnspan=3, sticky="w", pady=(0, 4)
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

        tk.Frame(box, bg=BORDER_CARD, height=1).grid(
            row=r, column=0, columnspan=3, sticky="ew", pady=(5, 5)
        )
        r += 1

        drop_hdr_row = tk.Frame(box, bg=BG_CARD)
        drop_hdr_row.grid(row=r, column=0, columnspan=3, sticky="ew", pady=(0, 4))
        ttk.Label(
            drop_hdr_row,
            text="FIRST PARAGRAPH DROP LETTER",
            style="Section.TLabel",
        ).pack(side="left")
        self.drop_tier_badge = tk.Label(
            drop_hdr_row,
            text="TIER 2+ ONLY (SELECT TIER 2 OR 3)",
            bg="#EFE8DC",
            fg="#7A6D5D",
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
            row=r, column=0, columnspan=3, sticky="ew", pady=(5, 5)
        )
        r += 1

        ttk.Label(box, text="COLORED PAGE & COVER BORDERS", style="Section.TLabel").grid(
            row=r, column=0, columnspan=3, sticky="w", pady=(0, 4)
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

        ttk.Label(box, text="Border color").grid(row=r, column=0, sticky="w", pady=3)
        palette_row = tk.Frame(box, bg=BG_CARD)
        palette_row.grid(row=r, column=1, columnspan=2, sticky="ew", padx=(8, 0), pady=3)

        for idx, (_name, hex_code) in enumerate(editions.COLOR_PRESETS):
            sw = tk.Button(
                palette_row,
                bg=hex_code,
                activebackground=hex_code,
                width=2,
                height=1,
                bd=1,
                relief="solid",
                cursor="hand2",
                font=("Segoe UI", 6, "bold"),
                command=lambda h=hex_code: self._select_border_color(h),
            )
            sw.grid(row=0, column=idx, padx=(0, 3))
            self._color_swatch_buttons[hex_code] = sw

        ttk.Button(
            palette_row, text="Custom...", command=self._pick_custom_color
        ).grid(row=0, column=len(editions.COLOR_PRESETS), padx=(3, 0))
        r += 1

        swatch_row = tk.Frame(box, bg=BG_CARD)
        swatch_row.grid(row=r, column=0, columnspan=3, sticky="ew", pady=(4, 0))
        self.swatch_canvas = tk.Canvas(
            swatch_row,
            width=44,
            height=16,
            bg=BG_CARD,
            highlightthickness=1,
            highlightbackground="#CFC6B8",
        )
        self.swatch_canvas.grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.tier_hint = ttk.Label(swatch_row, text="", style="Muted.TLabel", wraplength=355)
        self.tier_hint.grid(row=0, column=1, sticky="w")

    def _populate_outputs_tab(self, box):
        r = 0
        ttk.Label(box, text="DELIVERABLES TO BUILD", style="Section.TLabel").grid(
            row=r, column=0, columnspan=3, sticky="w", pady=(0, 6)
        )
        r += 1

        for key, label, hint in TARGET_LABELS:
            ttk.Checkbutton(box, text=label, variable=self.target_vars[key]).grid(
                row=r, column=0, sticky="w", pady=3
            )
            ttk.Label(box, text=hint, style="Muted.TLabel").grid(
                row=r, column=1, columnspan=2, sticky="w", padx=(8, 0), pady=3
            )
            r += 1

        ttk.Checkbutton(box, text="Print PDF (KDP ready)", variable=self.pdf_var).grid(
            row=r, column=0, sticky="w", pady=3
        )
        ttk.Label(
            box, text="Direct PDF via headless Edge/Chrome or WeasyPrint", style="Muted.TLabel"
        ).grid(row=r, column=1, columnspan=2, sticky="w", padx=(8, 0), pady=3)
        r += 1

        ttk.Checkbutton(box, text="Package buyer ZIP", variable=self.package_var).grid(
            row=r, column=0, sticky="w", pady=3
        )
        ttk.Label(
            box, text="Bundle outputs + delivery notes in build/orders/", style="Muted.TLabel"
        ).grid(row=r, column=1, columnspan=2, sticky="w", padx=(8, 0), pady=3)
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
            ttk.Label(box, text=label).grid(row=r, column=0, sticky="w", pady=3)
            ttk.Entry(box, textvariable=var).grid(
                row=r, column=1, sticky="ew", padx=(8, 8), pady=3
            )
            ttk.Button(box, text="Browse...", command=cmd).grid(row=r, column=2, pady=3)
            r += 1

    def _build_action_bar(self, row):
        wrap = tk.Frame(self, bg=BG_CARD)
        wrap.grid(row=row, column=0, sticky="ew")
        wrap.columnconfigure(0, weight=1)

        tk.Frame(wrap, bg=BORDER_CARD, height=1).grid(row=0, column=0, sticky="ew")

        bar = tk.Frame(wrap, bg=BG_CARD, padx=14, pady=10)
        bar.grid(row=1, column=0, sticky="ew")
        bar.columnconfigure(4, weight=1)

        self.format_button = ttk.Button(
            bar, text="✦  Format Book", style="Primary.TButton", command=self._start_build
        )
        self.format_button.grid(row=0, column=0)

        self.open_button = ttk.Button(
            bar, text="Open Folder", command=self._open_output, state="disabled"
        )
        self.open_button.grid(row=0, column=1, padx=(8, 0))

        self.preview_print_button = ttk.Button(
            bar, text="Preview Print", command=self._preview_print, state="disabled"
        )
        self.preview_print_button.grid(row=0, column=2, padx=(6, 0))

        self.preview_web_button = ttk.Button(
            bar, text="Preview Web", command=self._preview_web, state="disabled"
        )
        self.preview_web_button.grid(row=0, column=3, padx=(6, 0))

        self.progress = ttk.Progressbar(bar, mode="determinate", maximum=100, value=0)
        self.progress.grid(row=0, column=4, sticky="ew", padx=(14, 0))

    # ---------------------------------------------------- right column studio

    def _build_preview_card(self, parent, row):
        card = _make_card(parent, "Live Book Spread Preview (Cover & Chapter Opener)", pad=10)
        card.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        card.columnconfigure(0, weight=1)

        preset_bar = tk.Frame(card, bg=BG_CARD)
        preset_bar.grid(row=1, column=0, sticky="ew", pady=(0, 6))
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
                bd=1,
                relief="solid",
                padx=6,
                pady=3,
                cursor="hand2",
                font=("Segoe UI", 8, "bold"),
                command=lambda tk_k=t_key, ed_k=e_key: self._select_preset(tk_k, ed_k),
            )
            btn.grid(row=0, column=idx, sticky="ew", padx=(0 if idx == 0 else 4, 0))
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
        ).pack(side="left", padx=(0, 4))

        border_quick_cb = ttk.Combobox(
            border_bar,
            textvariable=self.border_style_var,
            values=BORDER_STYLE_CHOICES,
            state="readonly",
            width=16,
        )
        border_quick_cb.pack(side="left", padx=(0, 10))
        border_quick_cb.bind(
            "<<ComboboxSelected>>",
            lambda _e: self._sync_edition_state(reset_from_tier=False),
        )

        tk.Label(
            border_bar,
            text="Color:",
            bg=BG_CARD,
            fg=INK_MUTED,
            font=("Segoe UI", 8, "bold"),
        ).pack(side="left", padx=(0, 4))

        for _name, hex_code in editions.COLOR_PRESETS:
            sw = tk.Button(
                border_bar,
                bg=hex_code,
                activebackground=hex_code,
                width=2,
                height=1,
                bd=1,
                relief="solid",
                cursor="hand2",
                font=("Segoe UI", 6),
                command=lambda h=hex_code: self._select_border_color(h),
            )
            sw.pack(side="left", padx=(0, 3))

        self.page_canvas = tk.Canvas(
            card,
            width=450,
            height=262,
            bg="#E5E0D5",
            highlightthickness=1,
            highlightbackground="#CFC8BA",
        )
        self.page_canvas.grid(row=3, column=0, sticky="ew")
        self.page_canvas.bind("<Configure>", lambda _e: self._draw_page_preview())
        self._sync_edition_state()

    def _build_inspector_and_log(self, parent, row):
        self.notebook = ttk.Notebook(parent)
        self.notebook.grid(row=row, column=0, sticky="nsew")

        outline_tab = tk.Frame(
            self.notebook,
            bg=BG_CARD,
            padx=10,
            pady=10,
            highlightthickness=1,
            highlightbackground=BORDER_CARD,
        )
        outline_tab.columnconfigure(0, weight=1)
        outline_tab.rowconfigure(1, weight=1)

        ttk.Label(
            outline_tab,
            textvariable=self.kdp_summary_var,
            foreground=INK_DARK,
            font=("Segoe UI", 9, "bold"),
            wraplength=430,
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))

        columns = ("num", "title", "words", "status")
        self.chapter_tree = ttk.Treeview(
            outline_tab, columns=columns, show="headings", height=6
        )
        self.chapter_tree.heading("num", text="#")
        self.chapter_tree.heading("title", text="Chapter / Section")
        self.chapter_tree.heading("words", text="Words")
        self.chapter_tree.heading("status", text="Role")

        self.chapter_tree.column("num", width=38, anchor="center", stretch=False)
        self.chapter_tree.column("title", width=195, anchor="w")
        self.chapter_tree.column("words", width=70, anchor="e", stretch=False)
        self.chapter_tree.column("status", width=115, anchor="w")
        self.chapter_tree.grid(row=1, column=0, sticky="nsew")

        tree_scroll = ttk.Scrollbar(
            outline_tab, orient="vertical", command=self.chapter_tree.yview
        )
        tree_scroll.grid(row=1, column=1, sticky="ns")
        self.chapter_tree.configure(yscrollcommand=tree_scroll.set)

        log_tab = tk.Frame(
            self.notebook,
            bg=BG_CARD,
            padx=10,
            pady=10,
            highlightthickness=1,
            highlightbackground=BORDER_CARD,
        )
        log_tab.columnconfigure(0, weight=1)
        log_tab.rowconfigure(0, weight=1)

        self.log = tk.Text(
            log_tab,
            height=7,
            wrap="word",
            state="disabled",
            bg=BG_SUBTLE,
            fg=INK_BODY,
            relief="flat",
            padx=8,
            pady=6,
            font=("Consolas", 9),
        )
        self.log.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(log_tab, orient="vertical", command=self.log.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self.log.configure(yscrollcommand=scroll.set)

        self.log.tag_configure("ok", foreground="#1A7F37")
        self.log.tag_configure("warn", foreground="#9A6700")
        self.log.tag_configure("error", foreground="#B42318")
        self.log.tag_configure("muted", foreground=INK_MUTED)

        self.notebook.add(outline_tab, text="Chapters & KDP Specs")
        self.notebook.add(log_tab, text="Build Log")

    def _draw_sheet_border(self, canvas, x0, y0, x1, y1, border_style, color):
        """Draw the selected colored border style inside a miniature page sheet."""
        if border_style == "double":
            canvas.create_rectangle(
                x0 + 8, y0 + 8, x1 - 8, y1 - 8, outline=color, width=2
            )
            canvas.create_rectangle(
                x0 + 12, y0 + 12, x1 - 12, y1 - 12, outline=color, width=1
            )
        elif border_style == "single":
            canvas.create_rectangle(
                x0 + 9, y0 + 9, x1 - 9, y1 - 9, outline=color, width=1.5
            )
        elif border_style == "rules":
            canvas.create_line(
                x0 + 12, y0 + 12, x1 - 12, y0 + 12, fill=color, width=2
            )
            canvas.create_line(
                x0 + 12, y1 - 12, x1 - 12, y1 - 12, fill=color, width=1.5
            )

    def _draw_page_preview(self):
        """Render a miniature two-page studio preview: Typographic Cover + Chapter Opener."""
        if not hasattr(self, "page_canvas"):
            return
        canvas = self.page_canvas
        canvas.delete("all")

        c_width = max(int(canvas.winfo_width()), 450)
        c_height = max(int(canvas.winfo_height()), 262)

        edition = self._resolved_edition()
        border_style = getattr(edition, "border_style", "double")
        doc = self.current_document
        book_title = (
            self.meta_vars["title"].get().strip()
            or (doc.plain_title() if doc else "The Lamplighter’s Round")
        )
        subtitle = (
            self.meta_vars["subtitle"].get().strip()
            or (doc.meta.get("subtitle", "") if doc else "A Short Passage for Setting the Press")
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

        heading_face = (
            "Consolas"
            if edition.key == editions.SYSTEMFALL
            else ("Arial" if edition.key == editions.VANTABLACK else "Georgia")
        )
        heading_style = "bold" if edition.display_weight == "800" else "normal"

        page_w = 180
        page_h = 230
        gap = 18
        total_w = page_w * 2 + gap
        start_x = (c_width - total_w) // 2
        sy0 = (c_height - page_h) // 2 + 5
        sy1 = sy0 + page_h

        # ---------------- LEFT SHEET: FRAMED COVER PREVIEW ----------------
        cx0 = start_x
        cx1 = cx0 + page_w
        canvas.create_rectangle(cx0 + 3, sy0 + 4, cx1 + 3, sy1 + 4, fill="#C5BFB2", outline="")
        canvas.create_rectangle(cx0, sy0, cx1, sy1, fill=edition.paper, outline="#B8B1A4")

        self._draw_sheet_border(
            canvas,
            cx0,
            sy0,
            cx1,
            sy1,
            border_style if border_style != "none" else "single",
            edition.accent,
        )

        canvas.create_text(
            cx0 + page_w // 2,
            sy0 - 9,
            text="TYPOGRAPHIC COVER",
            fill=INK_MUTED,
            font=("Segoe UI", 7, "bold"),
        )

        title_item = canvas.create_text(
            cx0 + page_w // 2,
            sy0 + 42,
            text=book_title.upper(),
            anchor="n",
            width=page_w - 36,
            justify="center",
            fill=edition.ink,
            font=(heading_face, 7, "bold"),
        )
        t_bbox = canvas.bbox(title_item)
        title_bottom = t_bbox[3] if t_bbox else (sy0 + 68)

        if subtitle:
            sub_item = canvas.create_text(
                cx0 + page_w // 2,
                title_bottom + 6,
                text=subtitle[:36],
                anchor="n",
                width=page_w - 38,
                justify="center",
                fill="#5A534C",
                font=("Georgia", 6, "italic"),
            )
            s_bbox = canvas.bbox(sub_item)
            rule_y = (s_bbox[3] + 10) if s_bbox else (title_bottom + 22)
        else:
            rule_y = title_bottom + 12

        canvas.create_line(
            cx0 + page_w // 2 - 24,
            rule_y,
            cx0 + page_w // 2 + 24,
            rule_y,
            fill=edition.accent,
            width=1.5,
        )

        canvas.create_text(
            cx0 + page_w // 2,
            rule_y + 18,
            text=edition.scene_break,
            fill=edition.accent,
            font=("Georgia", 9),
        )

        canvas.create_text(
            cx0 + page_w // 2,
            sy1 - 24,
            text=author_name[:22].upper(),
            fill=edition.ink,
            font=("Segoe UI", 6, "bold"),
        )

        # ---------------- RIGHT SHEET: CHAPTER 1 INTERIOR ----------------
        sx0 = cx1 + gap
        sx1 = sx0 + page_w

        canvas.create_rectangle(sx0 + 3, sy0 + 4, sx1 + 3, sy1 + 4, fill="#C5BFB2", outline="")
        canvas.create_rectangle(sx0, sy0, sx1, sy1, fill=edition.paper, outline="#B8B1A4")

        self._draw_sheet_border(canvas, sx0, sy0, sx1, sy1, border_style, edition.accent)

        canvas.create_text(
            sx0 + page_w // 2,
            sy0 - 9,
            text=f"CHAPTER OPENER ({self.trim_var.get() or '6x9'})",
            fill=INK_MUTED,
            font=("Segoe UI", 7, "bold"),
        )

        # Running head
        canvas.create_text(
            sx1 - 18,
            sy0 + 20,
            text=book_title[:20].upper(),
            anchor="e",
            fill="#7A756E",
            font=("Georgia", 5),
        )

        cursor_y = sy0 + 34
        margin_x = sx0 + 20
        inner_w = page_w - 40

        if edition.chapter_number:
            cnum_item = canvas.create_text(
                sx0 + page_w // 2,
                cursor_y,
                text="CHAPTER 1",
                anchor="n",
                fill=edition.accent,
                font=("Consolas" if edition.key == editions.SYSTEMFALL else "Georgia", 6, "bold"),
            )
            cn_bbox = canvas.bbox(cnum_item)
            cursor_y = (cn_bbox[3] + 4) if cn_bbox else (cursor_y + 15)

        ch_item = canvas.create_text(
            sx0 + page_w // 2,
            cursor_y,
            text=inline.plain(chap_title)[:22].upper(),
            anchor="n",
            width=inner_w,
            justify="center",
            fill=edition.ink,
            font=(heading_face, 7, heading_style),
        )
        ch_bbox = canvas.bbox(ch_item)
        cursor_y = (ch_bbox[3] + 7) if ch_bbox else (cursor_y + 18)

        if edition.chapter_rule:
            canvas.create_line(
                sx0 + page_w // 2 - 22,
                cursor_y,
                sx0 + page_w // 2 + 22,
                cursor_y,
                fill=edition.accent,
                width=1.5,
            )
            cursor_y += 12
        else:
            cursor_y += 7

        if edition.drop_cap:
            letter = edition.drop_cap_letter or self._first_paragraph_letter()
            dc_style = getattr(edition, "drop_cap_style", "classic")
            if dc_style == "boxed":
                canvas.create_rectangle(
                    margin_x,
                    cursor_y - 3,
                    margin_x + 18,
                    cursor_y + 13,
                    fill=edition.accent,
                    outline=edition.accent,
                )
                canvas.create_text(
                    margin_x + 9,
                    cursor_y + 5,
                    text=letter,
                    fill=edition.paper,
                    font=(heading_face, 10, "bold"),
                )
                line_offsets = [22, 22, 0, 0]
            elif dc_style == "framed":
                canvas.create_rectangle(
                    margin_x,
                    cursor_y - 3,
                    margin_x + 18,
                    cursor_y + 13,
                    fill=edition.paper,
                    outline=edition.accent,
                    width=1.5,
                )
                canvas.create_text(
                    margin_x + 9,
                    cursor_y + 5,
                    text=letter,
                    fill=edition.accent,
                    font=(heading_face, 10, "bold"),
                )
                line_offsets = [22, 22, 0, 0]
            else:
                canvas.create_text(
                    margin_x + 1,
                    cursor_y - 4,
                    text=letter,
                    anchor="nw",
                    fill=edition.accent,
                    font=(heading_face, 14, "bold"),
                )
                line_offsets = [16, 16, 0, 0]
        else:
            line_offsets = [9, 0, 0, 0]

        for idx, indent_px in enumerate(line_offsets):
            ly = cursor_y + idx * 7
            end_trim = 12 if idx == len(line_offsets) - 1 else 0
            canvas.create_line(
                margin_x + indent_px,
                ly,
                margin_x + inner_w - end_trim,
                ly,
                fill="#3E3B38" if idx > 0 else edition.ink,
                width=2,
            )
        cursor_y += len(line_offsets) * 7 + 10

        canvas.create_text(
            sx0 + page_w // 2,
            cursor_y,
            text=edition.scene_break,
            fill=edition.accent,
            font=("Georgia", 8),
        )
        cursor_y += 11

        for idx in range(4):
            ly = cursor_y + idx * 7
            if ly > sy1 - 28:
                break
            indent_px = 9 if idx == 0 else 0
            end_trim = 24 if idx == 3 else 0
            canvas.create_line(
                margin_x + indent_px,
                ly,
                margin_x + inner_w - end_trim,
                ly,
                fill="#524E4A",
                width=2,
            )

        canvas.create_text(
            sx0 + page_w // 2,
            sy1 - 21,
            text="1",
            fill="#6E665E",
            font=("Georgia", 6),
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
                self.notebook.select(0)

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

    def _refresh_kdp_and_preview(self):
        doc = self.current_document
        if doc:
            trim = self.trim_var.get().strip() or "6x9"
            stats = estimate_kdp_stats(doc.word_count, len(doc.chapters), trim=trim)
            self.kdp_summary_var.set(
                f"KDP Paperback ({trim}): ~{stats['pages']} pages   ·   "
                f"Inner gutter: {stats['gutter']}   ·   "
                f"Cream spine: {stats['spine_in']:.3f} in"
            )
        self._draw_page_preview()

    def _load_manuscript(self):
        """Read the file, prefill details, and populate the chapter inspector."""
        path = Path(self.manuscript_var.get())
        if not path.is_file():
            self.status_var.set("That file could not be found.")
            return

        try:
            parsed = ms.load(path)
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

        for item in self.chapter_tree.get_children():
            self.chapter_tree.delete(item)

        for ch in doc.chapters:
            num_disp = (
                "—"
                if ch.implicit or ch.display_number is None
                else str(ch.display_number)
            )
            note = (
                "Implicit dispatch"
                if ch.implicit
                else ("Front/Back matter" if ch.display_number is None else "Chapter")
            )
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
        self.status_var.set(
            f"Loaded {path.name} — {chapter_text}, {doc.word_count:,} words (~{stats['pages']} paperback pages)."
        )
        self._refresh_kdp_and_preview()
        self.write(f"Loaded {path.name} ({chapter_text}, {doc.word_count:,} words).", "muted")

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

    def _start_build(self):
        if self.busy:
            return

        source = Path(self.manuscript_var.get())
        if not source.is_file():
            self.notebook.select(1)
            self.write("Choose a manuscript first (or click Load Sample).", "error")
            return

        targets = [key for key, _, _ in TARGET_LABELS if self.target_vars[key].get()]
        if not targets:
            self.notebook.select(1)
            self.write("Tick at least one format to build.", "error")
            return

        overrides = {key: var.get().strip() for key, var in self.meta_vars.items()}
        trim = self.trim_var.get().strip()
        if trim:
            overrides["trim"] = trim
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

        self._save_prefs()
        self.notebook.select(1)

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

    root = tk.Tk()
    root.title(f"inkpress {__version__} — Book & Dispatch Formatting Studio")
    root.geometry("1120x820")
    root.minsize(980, 740)
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
