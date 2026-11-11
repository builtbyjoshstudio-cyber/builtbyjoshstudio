#!/usr/bin/env python3
"""
project.py — per-book sidecar project files (<manuscript-stem>.inkpress.json).

Allows authors working from Word (.docx) or plain text (.txt/.md) manuscripts to
save and reload all book metadata, front/back matter, cover path, font pairing,
colored border settings, drop letters, and KDP trim per book without editing
YAML front matter by hand.
"""
import json
from pathlib import Path

PROJECT_SUFFIX = ".inkpress.json"

# Keys persisted in a per-book .inkpress.json project file.
PROJECT_META_KEYS = (
    "title",
    "subtitle",
    "author",
    "date",
    "language",
    "publisher",
    "isbn",
    "description",
    "cover",
    "trim",
    "tier",
    "edition",
    "font_pairing",
    "border_style",
    "border_color",
    "drop_cap_style",
    "drop_cap_letter",
    "dedication",
    "epigraph",
    "copyright",
    "also_by",
    "acknowledgments",
    "about_author",
    "newsletter_cta",
    "newsletter_url",
)


def project_path_for(manuscript_path):
    """Return the sidecar .inkpress.json path next to manuscript_path."""
    mpath = Path(manuscript_path)
    return mpath.with_name(f"{mpath.stem}{PROJECT_SUFFIX}")


def load_project(manuscript_path):
    """Load saved per-book settings dict if a sidecar exists, else {}."""
    if not manuscript_path:
        return {}
    sidecar = project_path_for(manuscript_path)
    if not sidecar.is_file():
        return {}
    try:
        raw = json.loads(sidecar.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    if not isinstance(raw, dict):
        return {}
    meta = raw.get("meta", raw)
    if not isinstance(meta, dict):
        return {}
    cleaned = {}
    for key in PROJECT_META_KEYS:
        val = meta.get(key)
        if val not in (None, ""):
            cleaned[key] = val
    return cleaned


def save_project(manuscript_path, settings):
    """Write per-book settings to <manuscript-stem>.inkpress.json. Returns Path."""
    sidecar = project_path_for(manuscript_path)
    filtered = {}
    for key in PROJECT_META_KEYS:
        val = settings.get(key)
        if val not in (None, ""):
            filtered[key] = str(val)
    payload = {
        "inkpress_project": 1,
        "manuscript": Path(manuscript_path).name,
        "meta": filtered,
    }
    sidecar.parent.mkdir(parents=True, exist_ok=True)
    sidecar.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return sidecar
