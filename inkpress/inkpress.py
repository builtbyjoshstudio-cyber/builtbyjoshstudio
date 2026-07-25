#!/usr/bin/env python3
"""
inkpress.py — build a manuscript into a site page, an EPUB and a print interior.

Usage (from the inkpress folder):
    python inkpress.py manuscripts/sample-manuscript.md
    python inkpress.py draft.md --targets site
    python inkpress.py draft.md --targets epub print --out build
    python inkpress.py draft.md --chrome-from ../writing/directors-voice.html
    python inkpress.py draft.md --dry-run
    python inkpress.py --check draft.md

Exit codes:
    0  build succeeded
    1  manuscript or validation error
    2  bad invocation
"""
import argparse
import sys
from pathlib import Path

from inkpress_lib import __version__
from inkpress_lib import manuscript as ms
from inkpress_lib import pipeline, validate

HERE = Path(__file__).resolve().parent
DEFAULT_OUT = HERE / "build"


def die(message, code=1):
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(code)


def human_size(path):
    try:
        size = path.stat().st_size
    except OSError:
        return "—"
    for unit in ("B", "KB", "MB"):
        if size < 1024 or unit == "MB":
            return f"{size:.0f}{unit}" if unit == "B" else f"{size / 1:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}MB"


def parse_args(argv):
    parser = argparse.ArgumentParser(
        prog="inkpress",
        description="One manuscript in, a site page and book files out.",
    )
    parser.add_argument("manuscript", help="path to the manuscript .md file")
    parser.add_argument(
        "--targets",
        nargs="+",
        choices=pipeline.ALL_TARGETS,
        default=list(pipeline.ALL_TARGETS),
        help="which outputs to build (default: all three)",
    )
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="output directory")
    parser.add_argument(
        "--chrome-from",
        metavar="PAGE.html",
        help="existing site page to lift nav, footer and stylesheet links from",
    )
    parser.add_argument("--base-url", help="site base URL for canonical and schema links")
    parser.add_argument(
        "--path-prefix", default="writing", help="site directory the page will live in"
    )
    parser.add_argument(
        "--print-css", metavar="FILE.css", help="override the generated paged-media CSS"
    )
    parser.add_argument(
        "--check", action="store_true", help="parse and validate only, write nothing"
    )
    parser.add_argument("--dry-run", action="store_true", help="report paths, write nothing")
    parser.add_argument("--quiet", action="store_true", help="only print errors")
    parser.add_argument("--version", action="version", version=f"inkpress {__version__}")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv if argv is not None else sys.argv[1:])

    source = Path(args.manuscript)
    if not source.is_file():
        die(f"manuscript not found: {source}")

    print_css = None
    if args.print_css:
        css_path = Path(args.print_css)
        if not css_path.is_file():
            die(f"print CSS not found: {css_path}")
        print_css = css_path.read_text(encoding="utf-8")

    try:
        chrome = pipeline.load_chrome(args.chrome_from)
    except FileNotFoundError as error:
        die(str(error))

    try:
        result = pipeline.build(
            source,
            out_dir=args.out,
            targets=args.targets,
            chrome=chrome,
            base_url=args.base_url,
            path_prefix=args.path_prefix,
            print_css=print_css,
            dry_run=args.dry_run or args.check,
        )
    except ms.ManuscriptError as error:
        die(f"{source.name}: {error}")
    except validate.ValidationError as error:
        die(f"{source.name} failed validation:\n{error}")

    if args.quiet:
        return 0

    document = result.document
    chapter_word = "chapter" if len(document.chapters) == 1 else "chapters"
    print(f"inkpress {__version__} — {document.plain_title()}")
    print(
        f"  {len(document.chapters)} {chapter_word}, {document.word_count:,} words"
        f"{' (implicit single chapter)' if not document.has_real_chapters else ''}"
    )

    for warning in result.warnings:
        print(f"  WARNING: {warning}")

    if args.check:
        print("  check passed — nothing written")
        return 0

    if args.chrome_from and chrome and not chrome.get("nav"):
        print(f"  WARNING: no <nav class=\"site-nav\"> found in {args.chrome_from}")

    verb = "would write" if args.dry_run else "wrote"
    for target, path in result:
        try:
            display = path.relative_to(Path.cwd())
        except ValueError:
            display = path
        suffix = "" if args.dry_run else f"  [{human_size(path)}]"
        print(f"  {verb} {target:<6} {display}{suffix}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
