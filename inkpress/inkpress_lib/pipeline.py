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
import zipfile
from pathlib import Path

from . import editions
from . import manuscript as ms
from . import project, render_epub, render_print, render_site, structure, validate

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


def _delivery_notes(result):
    doc = result.document
    edition_label = result.edition.label if result.edition else editions.TIER_LABELS[editions.CLEAN]
    trim = doc.meta.get("trim", render_print.DEFAULT_TRIM)
    lines = [
        f"{doc.plain_title()} — Buyer Delivery Package",
        "=" * (len(doc.plain_title()) + 27),
        "",
        f"Author:   {doc.meta.get('author', '')}",
        f"Edition:  {edition_label}",
        f"Length:   {len(doc.chapters)} chapters, {doc.word_count:,} words",
        f"Trim:     {trim}",
        "",
        "Included files:",
    ]
    for target, path in sorted(result.outputs.items()):
        if target == "package":
            continue
        desc = {
            "epub": "EPUB 3 ebook (ready for Kindle KDP, Apple Books, Kobo)",
            "pdf": f"Print-ready KDP interior PDF ({trim} trim)",
            "print": f"Paged-media print interior HTML ({trim} trim)",
            "site": "Standalone web page HTML",
        }.get(target, target)
        lines.append(f"  - {path.name:<36} {desc}")
    lines.append("")
    return "\n".join(lines)


def package_order(result, out_dir, dry_run=False):
    """Bundle all built deliverables into a deterministic buyer ZIP archive."""
    out_dir = Path(out_dir)
    slug = result.document.slug
    edition_key = result.edition.key if result.edition else editions.CLEAN
    zip_path = out_dir / "orders" / f"{slug}-{edition_key}.zip"

    if not dry_run:
        zip_path.parent.mkdir(parents=True, exist_ok=True)
        stamp = (1980, 1, 1, 0, 0, 0)
        with zipfile.ZipFile(zip_path, "w") as archive:
            notes_info = zipfile.ZipInfo("DELIVERY-NOTES.txt", date_time=stamp)
            notes_info.compress_type = zipfile.ZIP_DEFLATED
            notes_info.external_attr = 0o644 << 16
            archive.writestr(notes_info, _delivery_notes(result).encode("utf-8"))

            for target, path in sorted(result.outputs.items()):
                if target == "package" or not path.is_file():
                    continue
                info = zipfile.ZipInfo(path.name, date_time=stamp)
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o644 << 16
                archive.writestr(info, path.read_bytes())

    result.add("package", zip_path)
    return zip_path


def build(source, out_dir, targets=ALL_TARGETS, chrome=None, base_url=None,
          path_prefix="writing", print_css=None, dry_run=False, meta_overrides=None,
          tier=None, edition=None, pdf=False, package=False, cover=None):
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

    sidecar_meta = project.load_project(source)
    for key, value in sidecar_meta.items():
        if value not in (None, "", []):
            parsed.meta[key] = value

    if meta_overrides:
        for key, value in meta_overrides.items():
            if value not in (None, "", []):
                parsed.meta[key] = value
    if cover:
        parsed.meta["cover"] = cover

    document = structure.build(parsed)
    resolved_edition = editions.from_meta(
        document.meta, tier_override=tier, edition_override=edition
    )

    result = BuildResult(document, resolved_edition)
    result.warnings = validate.check(
        document, targets, resolved_edition, kdp_preflight=bool(pdf)
    )

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

        if pdf:
            pdf_path = out_dir / "print" / f"{slug}-interior.pdf"
            if dry_run:
                result.add("pdf", pdf_path)
            else:
                try:
                    render_print.render_pdf(path, pdf_path)
                    result.add("pdf", pdf_path)
                except RuntimeError as error:
                    result.warnings.append(str(error))

    if "epub" in targets:
        path = out_dir / "epub" / f"{slug}.epub"
        if not dry_run:
            render_epub.render(document, path, edition=resolved_edition)
        result.add("epub", path)

    if package:
        package_order(result, out_dir, dry_run=dry_run)

    return result
