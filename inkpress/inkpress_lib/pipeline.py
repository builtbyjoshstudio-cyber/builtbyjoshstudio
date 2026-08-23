#!/usr/bin/env python3
"""
pipeline.py — wire the stages together and fan out to the render targets.

    parse -> structure -> typography -> validate -+-> site HTML
                                                  +-> EPUB 3
                                                  +-> print HTML

Everything left of the fork happens exactly once, which is the whole point of
the design: the site page and the book files cannot drift apart because they
are rendered from the same Document object.
"""
from pathlib import Path

from . import editions
from . import manuscript as ms
from . import render_epub, render_print, render_site, structure, validate

ALL_TARGETS = ("site", "epub", "print")


class BuildResult:
    """What a build produced, for the CLI to report on."""

    def __init__(self, document, edition=None):
        self.document = document
        self.edition = edition
        self.outputs = {}
        self.warnings = []

    def add(self, target, path):
        self.outputs[target] = Path(path)

    def __iter__(self):
        return iter(sorted(self.outputs.items()))


def load_chrome(donor_path):
    """Read site chrome from a donor HTML page. Returns None if unavailable."""
    if not donor_path:
        return None
    path = Path(donor_path)
    if not path.is_file():
        raise FileNotFoundError(f"chrome donor page not found: {path}")
    return render_site.extract_chrome(path.read_text(encoding="utf-8"))


def build(source, out_dir, targets=ALL_TARGETS, chrome=None, base_url=None,
          path_prefix="writing", print_css=None, dry_run=False, meta_overrides=None,
          tier=None, edition=None):
    """Run the full pipeline for one manuscript.

    meta_overrides supplies front matter the file itself is missing — the
    desktop app passes what the user typed into its form. Applied before
    structure.build so overridden values are typeset like any other.
    """
    targets = tuple(targets)
    unknown = [target for target in targets if target not in ALL_TARGETS]
    if unknown:
        raise ValueError(f"unknown target(s): {', '.join(unknown)}")

    parsed = ms.load(source)

    if meta_overrides:
        for key, value in meta_overrides.items():
            if value not in (None, "", []):
                parsed.meta[key] = value

    document = structure.build(parsed)
    resolved_edition = editions.from_meta(
        document.meta, tier_override=tier, edition_override=edition
    )

    result = BuildResult(document, resolved_edition)
    result.warnings = validate.check(document, targets, resolved_edition)

    out_dir = Path(out_dir)
    slug = document.slug

    if "site" in targets:
        html = render_site.render(
            document,
            chrome=chrome,
            base_url=base_url or render_site.DEFAULT_BASE_URL,
            path_prefix=path_prefix,
            edition=resolved_edition,
        )
        path = out_dir / "site" / f"{slug}.html"
        if not dry_run:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(html, encoding="utf-8")
        result.add("site", path)

    if "print" in targets:
        html = render_print.render(
            document, css_override=print_css, edition=resolved_edition
        )
        path = out_dir / "print" / f"{slug}-interior.html"
        if not dry_run:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(html, encoding="utf-8")
        result.add("print", path)

    if "epub" in targets:
        path = out_dir / "epub" / f"{slug}.epub"
        if not dry_run:
            render_epub.render(document, path, edition=resolved_edition)
        result.add("epub", path)

    return result
