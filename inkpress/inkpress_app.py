#!/usr/bin/env python3
"""
inkpress_app.py — the desktop app.

A window over the same pipeline the CLI uses. Pick a manuscript, fill in
anything its header is missing, tick the formats you want, click Format.

Launch by double-clicking inkpress-app.cmd, or:
    python inkpress_app.py
    python inkpress_app.py path\\to\\draft.md      (also works if you drag a
                                                   manuscript onto the .cmd)

Tkinter ships with Python, so there is still nothing to install. Builds run on
a worker thread so the window never freezes, and the log pane reports exactly
what was written and where.
"""
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

from inkpress_lib import __version__  # noqa: E402
from inkpress_lib import manuscript as ms  # noqa: E402
from inkpress_lib import pipeline, validate  # noqa: E402

TARGET_LABELS = (
    ("site", "Web page", "A styled page for your site"),
    ("epub", "Ebook (EPUB)", "For Kindle, Kobo, Apple Books"),
    ("print", "Print interior", "Paperback pages, ready for PDF"),
)

META_FIELDS = (
    ("title", "Title"),
    ("author", "Author"),
    ("date", "Date"),
    ("description", "Description"),
)

PAD = 8


def open_folder(path):
    """Open a folder in the system file manager."""
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
        super().__init__(master, padding=PAD)
        self.grid(sticky="nsew")
        master.columnconfigure(0, weight=1)
        master.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.results = queue.Queue()
        self.last_out_dir = None
        self.busy = False

        self.manuscript_var = tk.StringVar()
        self.out_var = tk.StringVar(value=str(HERE / "build"))
        self.chrome_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Choose a manuscript to begin.")
        self.meta_vars = {key: tk.StringVar() for key, _ in META_FIELDS}
        self.target_vars = {key: tk.BooleanVar(value=True) for key, _, _ in TARGET_LABELS}

        row = 0
        row = self._build_manuscript_row(row)
        row = self._build_details(row)
        row = self._build_targets(row)
        row = self._build_options(row)
        row = self._build_actions(row)
        self._build_log(row)

        self.after(120, self._drain)

        if initial_manuscript:
            self.manuscript_var.set(str(Path(initial_manuscript).resolve()))
            self._load_manuscript()

    # ---------------------------------------------------------------- layout

    def _build_manuscript_row(self, row):
        box = ttk.LabelFrame(self, text="Manuscript", padding=PAD)
        box.grid(row=row, column=0, sticky="ew", pady=(0, PAD))
        box.columnconfigure(0, weight=1)

        entry = ttk.Entry(box, textvariable=self.manuscript_var)
        entry.grid(row=0, column=0, sticky="ew", padx=(0, PAD))
        ttk.Button(box, text="Choose file...", command=self._choose_manuscript).grid(
            row=0, column=1
        )

        ttk.Label(box, textvariable=self.status_var, foreground="#444").grid(
            row=1, column=0, columnspan=2, sticky="w", pady=(6, 0)
        )
        return row + 1

    def _build_details(self, row):
        box = ttk.LabelFrame(self, text="Details", padding=PAD)
        box.grid(row=row, column=0, sticky="ew", pady=(0, PAD))
        box.columnconfigure(1, weight=1)

        for index, (key, label) in enumerate(META_FIELDS):
            ttk.Label(box, text=label).grid(row=index, column=0, sticky="w", pady=2)
            ttk.Entry(box, textvariable=self.meta_vars[key]).grid(
                row=index, column=1, sticky="ew", padx=(PAD, 0), pady=2
            )

        ttk.Label(
            box,
            text="Filled in from the manuscript when it has a header. Anything you type here wins.",
            foreground="#666",
            wraplength=520,
        ).grid(row=len(META_FIELDS), column=0, columnspan=2, sticky="w", pady=(6, 0))
        return row + 1

    def _build_targets(self, row):
        box = ttk.LabelFrame(self, text="Formats to build", padding=PAD)
        box.grid(row=row, column=0, sticky="ew", pady=(0, PAD))

        for index, (key, label, hint) in enumerate(TARGET_LABELS):
            ttk.Checkbutton(box, text=label, variable=self.target_vars[key]).grid(
                row=index, column=0, sticky="w"
            )
            ttk.Label(box, text=hint, foreground="#666").grid(
                row=index, column=1, sticky="w", padx=(PAD, 0)
            )
        return row + 1

    def _build_options(self, row):
        box = ttk.LabelFrame(self, text="Options", padding=PAD)
        box.grid(row=row, column=0, sticky="ew", pady=(0, PAD))
        box.columnconfigure(1, weight=1)

        ttk.Label(box, text="Save to").grid(row=0, column=0, sticky="w")
        ttk.Entry(box, textvariable=self.out_var).grid(
            row=0, column=1, sticky="ew", padx=(PAD, PAD)
        )
        ttk.Button(box, text="Browse...", command=self._choose_out).grid(row=0, column=2)

        ttk.Label(box, text="Match site page").grid(row=1, column=0, sticky="w", pady=(6, 0))
        ttk.Entry(box, textvariable=self.chrome_var).grid(
            row=1, column=1, sticky="ew", padx=(PAD, PAD), pady=(6, 0)
        )
        ttk.Button(box, text="Browse...", command=self._choose_chrome).grid(
            row=1, column=2, pady=(6, 0)
        )

        ttk.Label(
            box,
            text="Optional: point at a page from your site and the web page copies its "
                 "styling, menu and footer.",
            foreground="#666",
            wraplength=520,
        ).grid(row=2, column=0, columnspan=3, sticky="w", pady=(6, 0))
        return row + 1

    def _build_actions(self, row):
        bar = ttk.Frame(self)
        bar.grid(row=row, column=0, sticky="ew", pady=(0, PAD))
        bar.columnconfigure(2, weight=1)

        self.format_button = ttk.Button(bar, text="Format", command=self._start_build)
        self.format_button.grid(row=0, column=0)

        self.open_button = ttk.Button(
            bar, text="Open output folder", command=self._open_output, state="disabled"
        )
        self.open_button.grid(row=0, column=1, padx=(PAD, 0))

        self.progress = ttk.Progressbar(bar, mode="indeterminate")
        self.progress.grid(row=0, column=2, sticky="ew", padx=(PAD, 0))
        return row + 1

    def _build_log(self, row):
        box = ttk.LabelFrame(self, text="What happened", padding=PAD)
        box.grid(row=row, column=0, sticky="nsew")
        box.columnconfigure(0, weight=1)
        box.rowconfigure(0, weight=1)
        self.rowconfigure(row, weight=1)

        self.log = tk.Text(box, height=11, wrap="word", state="disabled",
                           font=("Consolas", 9))
        self.log.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(box, orient="vertical", command=self.log.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self.log.configure(yscrollcommand=scroll.set)

        self.log.tag_configure("ok", foreground="#1a7f37")
        self.log.tag_configure("warn", foreground="#9a6700")
        self.log.tag_configure("error", foreground="#b42318")
        self.log.tag_configure("muted", foreground="#666")

    # ---------------------------------------------------------------- helpers

    def write(self, message, tag=None):
        self.log.configure(state="normal")
        self.log.insert("end", message + "\n", tag or ())
        self.log.see("end")
        self.log.configure(state="disabled")

    def _choose_manuscript(self):
        path = filedialog.askopenfilename(
            title="Choose a manuscript",
            initialdir=str(HERE / "manuscripts"),
            filetypes=[("Manuscripts", "*.md *.markdown *.txt"), ("All files", "*.*")],
        )
        if path:
            self.manuscript_var.set(path)
            self._load_manuscript()

    def _choose_out(self):
        path = filedialog.askdirectory(title="Where should the files go?",
                                       initialdir=self.out_var.get() or str(HERE))
        if path:
            self.out_var.set(path)

    def _choose_chrome(self):
        path = filedialog.askopenfilename(
            title="Choose a page from your site to match",
            filetypes=[("Web pages", "*.html *.htm"), ("All files", "*.*")],
        )
        if path:
            self.chrome_var.set(path)

    def _load_manuscript(self):
        """Read the file and prefill the details form."""
        path = Path(self.manuscript_var.get())
        if not path.is_file():
            self.status_var.set("That file could not be found.")
            return

        try:
            parsed = ms.load(path)
        except ms.ManuscriptError as error:
            self.status_var.set("Could not read that manuscript.")
            self.write(f"Could not read {path.name}: {error}", "error")
            return

        for key, _ in META_FIELDS:
            value = parsed.meta.get(key, "")
            self.meta_vars[key].set("" if isinstance(value, list) else str(value))

        if not self.meta_vars["date"].get():
            self.meta_vars["date"].set(date.today().isoformat())
        if not self.meta_vars["title"].get():
            self.meta_vars["title"].set(path.stem.replace("-", " ").replace("_", " ").title())

        chapters = sum(1 for block in parsed.blocks if block.kind == ms.CHAPTER)
        words = sum(
            len(block.text.split())
            for block in parsed.blocks
            if block.kind in (ms.PARAGRAPH, ms.BLOCKQUOTE)
        )
        chapter_text = f"{chapters} chapters" if chapters != 1 else "1 chapter"
        if chapters == 0:
            chapter_text = "no chapter breaks"
        self.status_var.set(f"{path.name} — {chapter_text}, about {words:,} words.")
        self.write(f"Loaded {path.name} ({chapter_text}, ~{words:,} words).", "muted")

    def _open_output(self):
        if self.last_out_dir and not open_folder(self.last_out_dir):
            self.write(f"Could not open {self.last_out_dir}", "warn")

    # ------------------------------------------------------------------ build

    def _start_build(self):
        if self.busy:
            return

        source = Path(self.manuscript_var.get())
        if not source.is_file():
            self.write("Choose a manuscript first.", "error")
            return

        targets = [key for key, _, _ in TARGET_LABELS if self.target_vars[key].get()]
        if not targets:
            self.write("Tick at least one format to build.", "error")
            return

        overrides = {key: var.get().strip() for key, var in self.meta_vars.items()}
        out_dir = self.out_var.get().strip() or str(HERE / "build")
        chrome_path = self.chrome_var.get().strip() or None

        self.busy = True
        self.format_button.configure(state="disabled")
        self.progress.start(12)
        self.write("")
        self.write(f"Formatting {source.name}...")

        threading.Thread(
            target=self._run_build,
            args=(source, out_dir, targets, overrides, chrome_path),
            daemon=True,
        ).start()

    def _run_build(self, source, out_dir, targets, overrides, chrome_path):
        """Worker thread. Never touches widgets — results go through the queue."""
        try:
            chrome = pipeline.load_chrome(chrome_path) if chrome_path else None
            result = pipeline.build(
                source,
                out_dir=out_dir,
                targets=targets,
                chrome=chrome,
                meta_overrides=overrides,
            )
            self.results.put(("done", result, out_dir))
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
            for warning in payload.warnings:
                self.write(f"  Heads up: {warning}", "warn")
            for target, path in payload:
                label = dict((key, name) for key, name, _ in TARGET_LABELS)[target]
                self.write(f"  {label}: {path}", "ok")
            self.write("Done.", "ok")
            self.last_out_dir = out_dir
            self.open_button.configure(state="normal")

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

    root = tk.Tk()
    root.title(f"inkpress {__version__}")
    root.minsize(620, 720)
    try:
        ttk.Style().theme_use("vista")
    except tk.TclError:
        pass

    InkpressApp(root, initial_manuscript=initial)
    root.mainloop()


if __name__ == "__main__":
    main()
