#!/usr/bin/env python3
"""
inkpress_app.py — the inkpress Editorial Studio desktop app.

A two-column studio window over the same pipeline the CLI uses:
  - Left column: manuscript loader (with one-click sample), book details,
    tier & edition selector, format targets, and print/web options.
  - Right column: live miniature book page & chapter-opener art preview canvas,
    chapter outline & KDP paperback spine/page estimator, and build log.

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
    from tkinter import filedialog, ttk
except ImportError:  # pragma: no cover - only on a Python built without Tk
    sys.stderr.write(
        "This build of Python has no Tkinter, so the desktop app cannot start.\n"
        "Reinstall Python from python.org (the standard installer includes it),\n"
        "or use the command line version instead:  .\\inkpress.ps1 draft.md\n"
    )
    sys.exit(1)

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from inkpress_lib import __version__, art, editions, inline  # noqa: E402
from inkpress_lib import manuscript as ms  # noqa: E402
from inkpress_lib import pipeline, render_print, structure, validate  # noqa: E402

SAMPLE_PATH = HERE / "manuscripts" / "sample-manuscript.md"
PREFS_PATH = Path.home() / ".inkpress_prefs.json"

TIER_CHOICES = [editions.TIER_LABELS[key] for key in editions.TIERS]
TIER_BY_LABEL = {editions.TIER_LABELS[key]: key for key in editions.TIERS}

EDITION_CHOICES = [editions.EDITION_LABELS[key] for key in editions.EDITIONS]
EDITION_BY_LABEL = {editions.EDITION_LABELS[key]: key for key in editions.EDITIONS}

TRIM_CHOICES = ("6x9", "5.5x8.5", "5.25x8", "5x8")

_WORDS_PER_PAGE = {
    "6x9": 320,
    "5.5x8.5": 275,
    "5.25x8": 250,
    "5x8": 235,
}

TARGET_LABELS = (
    ("epub", "Ebook (EPUB 3)", "Kindle, Kobo, Apple Books (with cover)"),
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

PAD = 8


def estimate_kdp_stats(word_count, chapter_count, trim="6x9"):
    """Estimate paperback page count, KDP inner gutter, and cream spine width."""
    wpp = _WORDS_PER_PAGE.get(str(trim).strip().lower(), 300)
    prose_pages = max(1, round(word_count / float(wpp))) if word_count > 0 else 0
    front_pages = 4 if chapter_count > 1 else 2
    chapter_overhead = max(1, round(chapter_count * 0.6))
    total_pages = prose_pages + front_pages + chapter_overhead if word_count > 0 else 0
    # KDP requires even page count for spine calculation
    if total_pages % 2 == 1:
        total_pages += 1
    spine_in = round(total_pages * 0.0025, 3)  # KDP cream paper multiplier
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


class InkpressApp(ttk.Frame):
    def __init__(self, master, initial_manuscript=None):
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

        self.manuscript_var = tk.StringVar()
        self.out_var = tk.StringVar(value=str(HERE / "build"))
        self.chrome_var = tk.StringVar()
        self.cover_var = tk.StringVar()
        self.status_var = tk.StringVar(
            value="Choose a manuscript (.md, .docx, .txt) or click Load Sample to explore."
        )
        self.kdp_summary_var = tk.StringVar(
            value="KDP Estimate: load a manuscript to see page count, gutter, and spine width."
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

        body_frame = ttk.Frame(self, padding=PAD)
        body_frame.grid(row=1, column=0, sticky="nsew")
        body_frame.columnconfigure(0, weight=5, minsize=430)
        body_frame.columnconfigure(1, weight=6, minsize=440)
        body_frame.rowconfigure(0, weight=1)

        left_col = ttk.Frame(body_frame)
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, PAD))
        left_col.columnconfigure(0, weight=1)

        right_col = ttk.Frame(body_frame)
        right_col.grid(row=0, column=1, sticky="nsew")
        right_col.columnconfigure(0, weight=1)
        right_col.rowconfigure(1, weight=1)

        lrow = 0
        lrow = self._build_manuscript_row(left_col, lrow)
        lrow = self._build_details(left_col, lrow)
        lrow = self._build_tier(left_col, lrow)
        lrow = self._build_targets(left_col, lrow)
        lrow = self._build_options(left_col, lrow)
        self._build_actions(left_col, lrow)

        self._build_preview_card(right_col, 0)
        self._build_inspector_and_log(right_col, 1)

        for key in ("title", "subtitle", "author"):
            self.meta_vars[key].trace_add("write", lambda *_args: self._draw_page_preview())

        master.bind("<Control-o>", lambda _e: self._choose_manuscript())
        master.bind("<Control-Return>", lambda _e: self._start_build())
        master.bind("<F5>", lambda _e: self._start_build())

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
        if data.get("out_dir"):
            self.out_var.set(str(data["out_dir"]))

    def _save_prefs(self):
        data = {
            "author": self.meta_vars["author"].get().strip(),
            "publisher": self.meta_vars["publisher"].get().strip(),
            "trim": self.trim_var.get().strip(),
            "tier": self.tier_var.get(),
            "edition": self.edition_var.get(),
            "out_dir": self.out_var.get().strip(),
        }
        try:
            PREFS_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except OSError:
            pass

    # ---------------------------------------------------------------- layout

    def _build_header(self):
        banner = tk.Frame(self, bg="#191817", padx=14, pady=10)
        banner.grid(row=0, column=0, sticky="ew")
        banner.columnconfigure(1, weight=1)

        tk.Label(
            banner,
            text="INKPRESS",
            bg="#191817",
            fg="#fdfbf7",
            font=("Georgia", 13, "bold"),
        ).grid(row=0, column=0, sticky="w")

        tk.Label(
            banner,
            text=f"  v{__version__}  ·  Book & Dispatch Formatting Studio",
            bg="#191817",
            fg="#b8afa6",
            font=("Segoe UI", 9),
        ).grid(row=0, column=1, sticky="w")

        tk.Label(
            banner,
            text="Ctrl+O Open   ·   F5 Format",
            bg="#191817",
            fg="#8c8278",
            font=("Consolas", 8),
        ).grid(row=0, column=2, sticky="e")

    def _build_manuscript_row(self, parent, row):
        box = ttk.LabelFrame(parent, text="1. Manuscript", padding=PAD)
        box.grid(row=row, column=0, sticky="ew", pady=(0, PAD))
        box.columnconfigure(0, weight=1)

        entry = ttk.Entry(box, textvariable=self.manuscript_var)
        entry.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        entry.bind("<Return>", lambda _e: self._load_manuscript())

        ttk.Button(box, text="Choose file...", command=self._choose_manuscript).grid(
            row=0, column=1, padx=(0, 4)
        )
        ttk.Button(box, text="Load Sample", command=self._load_sample).grid(
            row=0, column=2
        )

        ttk.Label(box, textvariable=self.status_var, foreground="#333", wraplength=410).grid(
            row=1, column=0, columnspan=3, sticky="w", pady=(6, 0)
        )
        return row + 1

    def _build_details(self, parent, row):
        box = ttk.LabelFrame(parent, text="2. Book Details", padding=PAD)
        box.grid(row=row, column=0, sticky="ew", pady=(0, PAD))
        box.columnconfigure(1, weight=1)
        box.columnconfigure(3, weight=1)

        # Compact two-column grid for short fields, full-width for longer ones
        paired = (
            ("title", "Title", "subtitle", "Subtitle"),
            ("author", "Author", "publisher", "Publisher"),
            ("date", "Date", "dedication", "Dedication"),
        )
        for r_idx, (k1, l1, k2, l2) in enumerate(paired):
            ttk.Label(box, text=l1).grid(row=r_idx, column=0, sticky="w", pady=2)
            ttk.Entry(box, textvariable=self.meta_vars[k1]).grid(
                row=r_idx, column=1, sticky="ew", padx=(6, 10), pady=2
            )
            ttk.Label(box, text=l2).grid(row=r_idx, column=2, sticky="w", pady=2)
            ttk.Entry(box, textvariable=self.meta_vars[k2]).grid(
                row=r_idx, column=3, sticky="ew", padx=(6, 0), pady=2
            )

        ttk.Label(box, text="Description").grid(row=3, column=0, sticky="w", pady=2)
        ttk.Entry(box, textvariable=self.meta_vars["description"]).grid(
            row=3, column=1, columnspan=3, sticky="ew", padx=(6, 0), pady=2
        )

        ttk.Label(box, text="Copyright").grid(row=4, column=0, sticky="w", pady=2)
        ttk.Entry(box, textvariable=self.meta_vars["copyright"]).grid(
            row=4, column=1, columnspan=3, sticky="ew", padx=(6, 0), pady=2
        )

        ttk.Label(
            box,
            text="Prefilled from the manuscript (.md or .docx). Leave Copyright blank for automatic © line.",
            foreground="#666",
            wraplength=410,
        ).grid(row=5, column=0, columnspan=4, sticky="w", pady=(4, 0))
        return row + 1

    def _build_tier(self, parent, row):
        box = ttk.LabelFrame(parent, text="3. Design Tier & Edition", padding=PAD)
        box.grid(row=row, column=0, sticky="ew", pady=(0, PAD))
        box.columnconfigure(1, weight=1)

        ttk.Label(box, text="Tier").grid(row=0, column=0, sticky="w")
        tier_box = ttk.Combobox(
            box, textvariable=self.tier_var, values=TIER_CHOICES,
            state="readonly",
        )
        tier_box.grid(row=0, column=1, sticky="ew", padx=(PAD, 0))
        tier_box.bind("<<ComboboxSelected>>", lambda _event: self._sync_edition_state())

        ttk.Label(box, text="Edition").grid(row=1, column=0, sticky="w", pady=(6, 0))
        self.edition_box = ttk.Combobox(
            box, textvariable=self.edition_var, values=EDITION_CHOICES,
            state="disabled",
        )
        self.edition_box.grid(row=1, column=1, sticky="ew", padx=(PAD, 0), pady=(6, 0))
        self.edition_box.bind("<<ComboboxSelected>>", lambda _event: self._sync_edition_state())

        swatch_row = ttk.Frame(box)
        swatch_row.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        self.swatch_canvas = tk.Canvas(
            swatch_row, width=44, height=18, highlightthickness=1, highlightbackground="#ccc"
        )
        self.swatch_canvas.grid(row=0, column=0, sticky="w", padx=(0, PAD))
        self.tier_hint = ttk.Label(swatch_row, text="", foreground="#555", wraplength=355)
        self.tier_hint.grid(row=0, column=1, sticky="w")

        self._sync_edition_state()
        return row + 1

    def _resolved_edition(self):
        tier = TIER_BY_LABEL.get(self.tier_var.get(), editions.CLEAN)
        edition_key = EDITION_BY_LABEL.get(self.edition_var.get(), editions.ASHVEIL)
        return editions.resolve(
            tier, edition_key if tier == editions.ILLUSTRATED else None
        )

    def _sync_edition_state(self):
        """Edition only applies to tier 3, so only enable it there."""
        tier = TIER_BY_LABEL.get(self.tier_var.get(), editions.CLEAN)
        resolved = self._resolved_edition()
        if tier == editions.ILLUSTRATED:
            self.edition_box.configure(state="readonly")
        else:
            self.edition_box.configure(state="disabled")

        self.swatch_canvas.delete("all")
        self.swatch_canvas.create_rectangle(0, 0, 22, 18, fill=resolved.ink, outline="")
        self.swatch_canvas.create_rectangle(22, 0, 44, 18, fill=resolved.accent, outline="")

        features = []
        if resolved.drop_cap:
            features.append("drop caps")
        if resolved.chapter_rule:
            features.append("chapter rules")
        if resolved.art:
            features.append(f"{resolved.art} SVG art")
        if not features:
            features.append("plain headings")
        self.tier_hint.configure(
            text=f"{resolved.label}  |  Scene break: {resolved.scene_break}  |  {', '.join(features)}"
        )
        if hasattr(self, "page_canvas"):
            self._draw_page_preview()

    def _build_targets(self, parent, row):
        box = ttk.LabelFrame(parent, text="4. Deliverables", padding=PAD)
        box.grid(row=row, column=0, sticky="ew", pady=(0, PAD))

        for index, (key, label, hint) in enumerate(TARGET_LABELS):
            ttk.Checkbutton(box, text=label, variable=self.target_vars[key]).grid(
                row=index, column=0, sticky="w"
            )
            ttk.Label(box, text=hint, foreground="#666").grid(
                row=index, column=1, sticky="w", padx=(PAD, 0)
            )

        pdf_row = len(TARGET_LABELS)
        ttk.Checkbutton(box, text="Print PDF (KDP ready)", variable=self.pdf_var).grid(
            row=pdf_row, column=0, sticky="w"
        )
        ttk.Label(box, text="Direct PDF export via headless browser / WeasyPrint", foreground="#666").grid(
            row=pdf_row, column=1, sticky="w", padx=(PAD, 0)
        )

        pkg_row = pdf_row + 1
        ttk.Checkbutton(box, text="Package buyer ZIP", variable=self.package_var).grid(
            row=pkg_row, column=0, sticky="w"
        )
        ttk.Label(box, text="Bundle outputs + delivery notes into build/orders/", foreground="#666").grid(
            row=pkg_row, column=1, sticky="w", padx=(PAD, 0)
        )
        return row + 1

    def _build_options(self, parent, row):
        box = ttk.LabelFrame(parent, text="5. Trim & Output Options", padding=PAD)
        box.grid(row=row, column=0, sticky="ew", pady=(0, PAD))
        box.columnconfigure(1, weight=1)

        ttk.Label(box, text="Print trim").grid(row=0, column=0, sticky="w")
        trim_cb = ttk.Combobox(box, textvariable=self.trim_var, values=TRIM_CHOICES)
        trim_cb.grid(row=0, column=1, sticky="ew", padx=(PAD, PAD))
        trim_cb.bind("<<ComboboxSelected>>", lambda _e: self._refresh_kdp_and_preview())

        ttk.Label(box, text="Save to").grid(row=1, column=0, sticky="w", pady=(5, 0))
        ttk.Entry(box, textvariable=self.out_var).grid(
            row=1, column=1, sticky="ew", padx=(PAD, PAD), pady=(5, 0)
        )
        ttk.Button(box, text="Browse...", command=self._choose_out).grid(
            row=1, column=2, pady=(5, 0)
        )

        ttk.Label(box, text="Cover image").grid(row=2, column=0, sticky="w", pady=(5, 0))
        ttk.Entry(box, textvariable=self.cover_var).grid(
            row=2, column=1, sticky="ew", padx=(PAD, PAD), pady=(5, 0)
        )
        ttk.Button(box, text="Browse...", command=self._choose_cover).grid(
            row=2, column=2, pady=(5, 0)
        )

        ttk.Label(box, text="Web template").grid(row=3, column=0, sticky="w", pady=(5, 0))
        ttk.Entry(box, textvariable=self.chrome_var).grid(
            row=3, column=1, sticky="ew", padx=(PAD, PAD), pady=(5, 0)
        )
        ttk.Button(box, text="Browse...", command=self._choose_chrome).grid(
            row=3, column=2, pady=(5, 0)
        )
        return row + 1

    def _build_actions(self, parent, row):
        bar = ttk.Frame(parent)
        bar.grid(row=row, column=0, sticky="ew")
        bar.columnconfigure(4, weight=1)

        self.format_button = ttk.Button(bar, text="Format Book", command=self._start_build)
        self.format_button.grid(row=0, column=0)

        self.open_button = ttk.Button(
            bar, text="Open Folder", command=self._open_output, state="disabled"
        )
        self.open_button.grid(row=0, column=1, padx=(6, 0))

        self.preview_print_button = ttk.Button(
            bar, text="Preview Print", command=self._preview_print, state="disabled"
        )
        self.preview_print_button.grid(row=0, column=2, padx=(6, 0))

        self.preview_web_button = ttk.Button(
            bar, text="Preview Web", command=self._preview_web, state="disabled"
        )
        self.preview_web_button.grid(row=0, column=3, padx=(6, 0))

        self.progress = ttk.Progressbar(bar, mode="indeterminate")
        self.progress.grid(row=0, column=4, sticky="ew", padx=(8, 0))
        return row + 1

    # ---------------------------------------------------- right column studio

    def _build_preview_card(self, parent, row):
        box = ttk.LabelFrame(parent, text="Live Page & Edition Preview", padding=PAD)
        box.grid(row=row, column=0, sticky="ew", pady=(0, PAD))
        box.columnconfigure(0, weight=1)

        self.page_canvas = tk.Canvas(
            box,
            width=420,
            height=295,
            bg="#e3e1dc",
            highlightthickness=1,
            highlightbackground="#c8c4bc",
        )
        self.page_canvas.grid(row=0, column=0, sticky="ew")
        self.page_canvas.bind("<Configure>", lambda _e: self._draw_page_preview())

    def _build_inspector_and_log(self, parent, row):
        self.notebook = ttk.Notebook(parent)
        self.notebook.grid(row=row, column=0, sticky="nsew")

        # Tab 1: Chapter Outline & KDP Paperback Estimator
        outline_tab = ttk.Frame(self.notebook, padding=PAD)
        outline_tab.columnconfigure(0, weight=1)
        outline_tab.rowconfigure(1, weight=1)

        ttk.Label(
            outline_tab,
            textvariable=self.kdp_summary_var,
            foreground="#191817",
            font=("Segoe UI", 9, "bold"),
            wraplength=410,
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))

        columns = ("num", "title", "words", "status")
        self.chapter_tree = ttk.Treeview(
            outline_tab, columns=columns, show="headings", height=7
        )
        self.chapter_tree.heading("num", text="#")
        self.chapter_tree.heading("title", text="Chapter / Section")
        self.chapter_tree.heading("words", text="Words")
        self.chapter_tree.heading("status", text="Notes")

        self.chapter_tree.column("num", width=36, anchor="center", stretch=False)
        self.chapter_tree.column("title", width=185, anchor="w")
        self.chapter_tree.column("words", width=65, anchor="e", stretch=False)
        self.chapter_tree.column("status", width=115, anchor="w")
        self.chapter_tree.grid(row=1, column=0, sticky="nsew")

        tree_scroll = ttk.Scrollbar(
            outline_tab, orient="vertical", command=self.chapter_tree.yview
        )
        tree_scroll.grid(row=1, column=1, sticky="ns")
        self.chapter_tree.configure(yscrollcommand=tree_scroll.set)

        # Tab 2: Build Log
        log_tab = ttk.Frame(self.notebook, padding=PAD)
        log_tab.columnconfigure(0, weight=1)
        log_tab.rowconfigure(0, weight=1)

        self.log = tk.Text(
            log_tab, height=8, wrap="word", state="disabled", font=("Consolas", 9)
        )
        self.log.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(log_tab, orient="vertical", command=self.log.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self.log.configure(yscrollcommand=scroll.set)

        self.log.tag_configure("ok", foreground="#1a7f37")
        self.log.tag_configure("warn", foreground="#9a6700")
        self.log.tag_configure("error", foreground="#b42318")
        self.log.tag_configure("muted", foreground="#666")

        self.notebook.add(outline_tab, text="Chapters & KDP Specs")
        self.notebook.add(log_tab, text="Build Log")

    def _draw_page_preview(self):
        """Render a miniature book page showing the active Edition's typography and art."""
        if not hasattr(self, "page_canvas"):
            return
        canvas = self.page_canvas
        canvas.delete("all")

        c_width = max(int(canvas.winfo_width()), 420)
        c_height = max(int(canvas.winfo_height()), 295)

        edition = self._resolved_edition()
        doc = self.current_document
        book_title = (
            self.meta_vars["title"].get().strip()
            or (doc.plain_title() if doc else "The Lamplighter’s Round")
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

        # Page sheet geometry centered in the studio preview canvas
        sheet_w = 216
        sheet_h = 272
        sx0 = (c_width - sheet_w) // 2
        sy0 = (c_height - sheet_h) // 2
        sx1 = sx0 + sheet_w
        sy1 = sy0 + sheet_h

        # Drop shadow + paper sheet
        canvas.create_rectangle(
            sx0 + 4, sy0 + 5, sx1 + 4, sy1 + 5, fill="#b8b4ac", outline=""
        )
        canvas.create_rectangle(
            sx0, sy0, sx1, sy1, fill=edition.paper, outline="#beb9b0"
        )

        # Running head (recto)
        canvas.create_text(
            sx1 - 18,
            sy0 + 13,
            text=book_title[:24].upper(),
            anchor="e",
            fill="#777",
            font=("Georgia", 6),
        )

        cursor_y = sy0 + 26
        margin_x = sx0 + 20
        inner_w = sheet_w - 40

        # Chapter opener artwork for Tier 3 Illustrated editions
        if edition.art:
            art_h = 36
            ax0, ay0 = margin_x, cursor_y
            ax1, ay1 = margin_x + inner_w, cursor_y + art_h
            rng = art._Rng(f"{edition.key}|1|{chap_title}")

            if edition.art == editions.ASHVEIL:
                for layer, tint in enumerate(("#d0cec9", "#8c8881", edition.ink)):
                    base = ay0 + 25 - layer * 2
                    pts = [ax0, ay1, ax0, base]
                    x = float(ax0)
                    while x < ax1:
                        x = min(float(ax1), x + rng.between(12, 24))
                        peak = base - rng.between(4, 12) + layer * 2
                        pts.extend([x, peak])
                    pts.extend([ax1, ay1])
                    canvas.create_polygon(pts, fill=tint, outline="")
                for _ in range(6):
                    ex = rng.between(ax0 + 8, ax1 - 8)
                    ey = rng.between(ay0 + 10, ay1 - 5)
                    canvas.create_oval(
                        ex - 1.5, ey - 1.5, ex + 1.5, ey + 1.5,
                        fill=edition.accent, outline=""
                    )
                canvas.create_line(ax0, ay1, ax1, ay1, fill=edition.ink, width=1)

            elif edition.art == editions.SYSTEMFALL:
                cols = 10
                step = inner_w / float(cols + 1)
                tx = ax0 + step * 0.5
                ty = ay0 + 22
                trace_pts = [tx, ty]
                while tx < ax1 - step:
                    tx = min(ax1 - 4, tx + rng.between(step * 0.8, step * 1.8))
                    trace_pts.extend([tx, ty])
                    if rng.chance(0.6):
                        ty = max(ay0 + 6, min(ay1 - 6, ty + rng.between(-8, 8)))
                        trace_pts.extend([tx, ty])
                canvas.create_line(trace_pts, fill=edition.accent, width=1)
                for c in range(1, cols + 1):
                    nx = ax0 + c * step
                    for ny in (ay0 + 10, ay0 + 18, ay0 + 26):
                        if rng.chance(0.5):
                            filled = rng.chance(0.4)
                            canvas.create_rectangle(
                                nx - 1.5, ny - 1.5, nx + 1.5, ny + 1.5,
                                fill=edition.accent if filled else edition.paper,
                                outline=edition.ink,
                            )
                canvas.create_line(ax0, ay1, ax1, ay1, fill=edition.ink, width=1)

            elif edition.art == editions.VANTABLACK:
                bt = ay0 + 6
                bh = 20
                canvas.create_rectangle(ax0, bt, ax1, bt + bh, fill=edition.ink, outline="")
                cut_x = ax0 + inner_w * 0.52
                canvas.create_polygon(
                    [cut_x, bt, cut_x + 8, bt, cut_x + 2, bt + bh, cut_x - 6, bt + bh],
                    fill=edition.paper,
                    outline="",
                )
                thin_x = ax0 + inner_w * 0.18
                canvas.create_rectangle(
                    thin_x, bt, thin_x + 2, bt + bh, fill=edition.paper, outline=""
                )
                bx = ax0 + inner_w * 0.82
                canvas.create_rectangle(
                    bx, bt + bh + 3, bx + 5, bt + bh + 8, fill=edition.ink, outline=""
                )

            cursor_y += art_h + 10
        else:
            cursor_y += 18

        # Chapter number banner
        if edition.chapter_number:
            canvas.create_text(
                sx0 + sheet_w // 2,
                cursor_y,
                text="CHAPTER 1",
                fill=edition.accent,
                font=("Consolas" if edition.key == editions.SYSTEMFALL else "Georgia", 7),
            )
            cursor_y += 14

        # Chapter heading
        heading_face = (
            "Consolas"
            if edition.key == editions.SYSTEMFALL
            else ("Arial" if edition.key == editions.VANTABLACK else "Georgia")
        )
        heading_style = "bold" if edition.display_weight == "800" else "normal"
        canvas.create_text(
            sx0 + sheet_w // 2,
            cursor_y,
            text=inline.plain(chap_title)[:22].upper(),
            fill=edition.ink,
            font=(heading_face, 10, heading_style),
        )
        cursor_y += 12

        if edition.chapter_rule:
            canvas.create_line(
                sx0 + sheet_w // 2 - 16,
                cursor_y,
                sx0 + sheet_w // 2 + 16,
                cursor_y,
                fill=edition.accent,
                width=1,
            )
            cursor_y += 10
        else:
            cursor_y += 6

        # Opening paragraph with optional Drop Cap
        if edition.drop_cap:
            canvas.create_text(
                margin_x,
                cursor_y - 2,
                text="T",
                anchor="nw",
                fill=edition.accent,
                font=(heading_face, 22, "bold"),
            )
            line_offsets = [18, 18, 0, 0]
        else:
            line_offsets = [0, 0, 0, 0]

        for idx, indent_px in enumerate(line_offsets):
            ly = cursor_y + idx * 8
            end_trim = 14 if idx == len(line_offsets) - 1 else 0
            canvas.create_line(
                margin_x + indent_px,
                ly,
                margin_x + inner_w - end_trim,
                ly,
                fill="#3a3835" if idx > 0 else edition.ink,
                width=2,
            )
        cursor_y += len(line_offsets) * 8 + 10

        # Scene break ornament
        canvas.create_text(
            sx0 + sheet_w // 2,
            cursor_y,
            text=edition.scene_break,
            fill=edition.accent,
            font=("Georgia", 9),
        )
        cursor_y += 14

        # Second paragraph lines
        for idx in range(4):
            ly = cursor_y + idx * 8
            if ly > sy1 - 24:
                break
            indent_px = 10 if idx == 0 else 0
            end_trim = 28 if idx == 3 else 0
            canvas.create_line(
                margin_x + indent_px,
                ly,
                margin_x + inner_w - end_trim,
                ly,
                fill="#4a4845",
                width=2,
            )

        # Bottom folio
        canvas.create_text(
            sx0 + sheet_w // 2,
            sy1 - 11,
            text="1",
            fill="#666",
            font=("Georgia", 7),
        )

        # Side badge labels
        canvas.create_text(
            10,
            12,
            text=edition.label,
            anchor="nw",
            fill="#333",
            font=("Segoe UI", 8, "bold"),
        )
        canvas.create_text(
            10,
            c_height - 10,
            text=f"{author_name[:22]}  ·  {self.trim_var.get() or '6x9'} trim",
            anchor="sw",
            fill="#555",
            font=("Segoe UI", 8),
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

    def _choose_cover(self):
        path = filedialog.askopenfilename(
            title="Choose a cover image for EPUB",
            filetypes=[("Cover images", "*.jpg *.jpeg *.png *.svg"), ("All files", "*.*")],
        )
        if path:
            self.cover_var.set(path)

    def _refresh_kdp_and_preview(self):
        doc = self.current_document
        if doc:
            trim = self.trim_var.get().strip() or "6x9"
            stats = estimate_kdp_stats(doc.word_count, len(doc.chapters), trim=trim)
            self.kdp_summary_var.set(
                f"KDP Paperback ({trim}): ~{stats['pages']} pages  ·  "
                f"Inner gutter: {stats['gutter']}  ·  "
                f"Cream spine width: {stats['spine_in']:.3f} in"
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
        self._sync_edition_state()

        trim_val = str(parsed.meta.get("trim", "")).strip()
        self.trim_var.set(trim_val if trim_val else TRIM_CHOICES[0])

        cover_val = str(parsed.meta.get("cover", "")).strip()
        self.cover_var.set(cover_val)

        # Populate chapter outline treeview
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
            f"{path.name} — {chapter_text}, {doc.word_count:,} words (~{stats['pages']} paperback pages)."
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
    root.minsize(920, 640)
    ico_path = HERE / "inkpress.ico"
    if ico_path.is_file():
        try:
            root.iconbitmap(str(ico_path))
        except tk.TclError:
            pass
    try:
        ttk.Style().theme_use("vista")
    except tk.TclError:
        pass

    InkpressApp(root, initial_manuscript=initial)
    root.mainloop()


if __name__ == "__main__":
    main()
