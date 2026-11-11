#!/usr/bin/env python3
"""
test_pipeline.py — end-to-end and per-stage tests.

    python -m unittest discover -s tests -t .
"""
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from inkpress_lib import art, body, editions, inline, pipeline, structure  # noqa: E402
from inkpress_lib import typography, validate  # noqa: E402
from inkpress_lib import manuscript as ms  # noqa: E402

HERE = Path(__file__).resolve().parent
SAMPLE = HERE.parent / "manuscripts" / "sample-manuscript.md"

MINIMAL = """---
title: Test Book
author: A. Writer
date: 2026-01-02
language: en
description: A minimal manuscript.
---

## One

First paragraph.

* * *

Second paragraph.

## Two

Third paragraph.
"""


def write_temp(text, directory):
    path = Path(directory) / "temp-manuscript.md"
    path.write_text(text, encoding="utf-8")
    return path


class TestTypography(unittest.TestCase):
    def test_dashes_and_ellipsis(self):
        self.assertEqual(typography.apply("a---b"), "a—b")
        self.assertEqual(typography.apply("1--2"), "1–2")
        self.assertEqual(typography.apply("wait..."), "wait…")

    def test_longest_dash_wins(self):
        self.assertNotIn("-", typography.apply("east---west"))

    def test_double_quotes_are_directional(self):
        self.assertEqual(typography.apply('"hi"'), "“hi”")

    def test_apostrophe_not_treated_as_quote(self):
        self.assertEqual(typography.apply("don't"), "don’t")

    def test_elided_decade(self):
        self.assertEqual(typography.apply("the '90s"), "the ’90s")
        self.assertEqual(typography.apply("the ‘90s"), "the ’90s")

    def test_single_quotes_are_directional(self):
        self.assertEqual(typography.apply("he said 'go' then"), "he said ‘go’ then")

    def test_quotes_inside_and_outside_emphasis(self):
        self.assertEqual(typography.apply('*"Hello,"*'), "*“Hello,”*")
        self.assertEqual(typography.apply('"*Hello,*"'), "“*Hello,*”")
        self.assertEqual(typography.apply('**"Stop!"**'), "**“Stop!”**")
        self.assertEqual(typography.apply("_'90s_"), "_’90s_")

    def test_spaced_dashes_and_double_spaces_normalized(self):
        self.assertEqual(typography.apply("wait - what"), "wait—what")
        self.assertEqual(typography.apply("wait -- what"), "wait—what")
        self.assertEqual(typography.apply("One.  Two."), "One. Two.")

    def test_code_spans_are_untouched(self):
        self.assertEqual(typography.apply('`a--b`'), '`a--b`')

    def test_link_targets_are_untouched(self):
        source = "[x](https://e.com/a--b)"
        self.assertIn("a--b", typography.apply(source))


class TestInline(unittest.TestCase):
    def test_escapes_html(self):
        self.assertEqual(inline.render("a < b & c"), "a &lt; b &amp; c")

    def test_strong_and_em(self):
        self.assertEqual(inline.render("**a** and *b*"), "<strong>a</strong> and <em>b</em>")

    def test_underscore_em_ignores_snake_case(self):
        self.assertEqual(inline.render("some_var_name"), "some_var_name")

    def test_link(self):
        self.assertEqual(
            inline.render("[t](https://e.com)"), '<a href="https://e.com">t</a>'
        )

    def test_code_content_is_not_markup(self):
        self.assertEqual(inline.render("`*a*`"), "<code>*a*</code>")

    def test_plain_strips_markup(self):
        self.assertEqual(inline.plain("**a** *b* `c`"), "a b c")


class TestManuscript(unittest.TestCase):
    def test_front_matter_and_blocks(self):
        with tempfile.TemporaryDirectory() as directory:
            parsed = ms.load(write_temp(MINIMAL, directory))
        self.assertEqual(parsed.meta["title"], "Test Book")
        kinds = [block.kind for block in parsed.blocks]
        self.assertEqual(kinds.count(ms.CHAPTER), 2)
        self.assertEqual(kinds.count(ms.SCENE_BREAK), 1)
        self.assertEqual(kinds.count(ms.PARAGRAPH), 3)

    def test_front_matter_list(self):
        source = MINIMAL.replace(
            "language: en", "language: en\nsubjects:\n  - Alpha\n  - Beta"
        )
        with tempfile.TemporaryDirectory() as directory:
            parsed = ms.load(write_temp(source, directory))
        self.assertEqual(parsed.meta["subjects"], ["Alpha", "Beta"])

    def test_unclosed_front_matter_raises(self):
        with tempfile.TemporaryDirectory() as directory:
            path = write_temp("---\ntitle: X\n\nbody\n", directory)
            with self.assertRaises(ms.ManuscriptError):
                ms.load(path)

    def test_missing_file_raises(self):
        with self.assertRaises(ms.ManuscriptError):
            ms.load(Path("does-not-exist.md"))

    def test_utf8_bom_does_not_break_front_matter(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bom.md"
            path.write_bytes(b"\xef\xbb\xbf" + MINIMAL.encode("utf-8"))
            parsed = ms.load(path)
        self.assertEqual(parsed.meta["title"], "Test Book")
        self.assertEqual(len(parsed.blocks), 6)

    def test_docx_manuscript_loads_chapters_and_inline_runs(self):
        core_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
                           xmlns:dc="http://purl.org/dc/elements/1.1/">
          <dc:title>Word Draft</dc:title>
          <dc:creator>J. Author</dc:creator>
          <dc:language>en</dc:language>
        </cp:coreProperties>"""
        doc_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
          <w:body>
            <w:p>
              <w:pPr><w:pStyle w:val="Heading1"/></w:pPr>
              <w:r><w:t>Chapter One</w:t></w:r>
            </w:p>
            <w:p>
              <w:r><w:t>Opening with </w:t></w:r>
              <w:r><w:rPr><w:i/></w:rPr><w:t>italic</w:t></w:r>
              <w:r><w:t> and </w:t></w:r>
              <w:r><w:rPr><w:b/></w:rPr><w:t>bold</w:t></w:r>
              <w:r><w:t> words.</w:t></w:r>
            </w:p>
            <w:p>
              <w:pPr><w:pStyle w:val="Quote"/></w:pPr>
              <w:r><w:t>A quoted line.</w:t></w:r>
            </w:p>
          </w:body>
        </w:document>"""

        with tempfile.TemporaryDirectory() as directory:
            docx_path = Path(directory) / "draft.docx"
            with zipfile.ZipFile(docx_path, "w") as archive:
                archive.writestr("docProps/core.xml", core_xml)
                archive.writestr("word/document.xml", doc_xml)

            parsed = ms.load(docx_path)
            doc = structure.build(parsed)

        self.assertEqual(doc.title, "Word Draft")
        self.assertEqual(doc.meta["author"], "J. Author")
        self.assertEqual(len(doc.chapters), 1)
        self.assertEqual(doc.chapters[0].title, "Chapter One")
        rendered = "\n".join(body.blocks_to_html(doc.chapters[0].blocks))
        self.assertIn("<em>italic</em>", rendered)
        self.assertIn("<strong>bold</strong>", rendered)
        self.assertIn("<blockquote>", rendered)

    def test_bare_chapter_headings_detected_when_no_h2_present(self):
        raw = (
            "---\ntitle: Plain Draft\nauthor: A. Writer\ndate: 2026-01-02\n---\n\n"
            "Chapter 1\n\n"
            "First chapter prose.\n\n"
            "Chapter Two: The Return\n\n"
            "Chapter two starts with a normal sentence about chapters.\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            doc = structure.build(ms.load(write_temp(raw, directory)))

        self.assertEqual(len(doc.chapters), 2)
        self.assertEqual(doc.chapters[0].title, "Chapter 1")
        self.assertEqual(doc.chapters[1].title, "Chapter Two: The Return")

    def test_shunn_and_tilde_scene_breaks(self):
        raw = (
            "---\ntitle: Breaks\nauthor: A. Writer\ndate: 2026-01-02\n---\n\n"
            "Scene one.\n\n#\n\nScene two.\n\n~ ~ ~\n\nScene three.\n\n****\n\nScene four.\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            parsed = ms.load(write_temp(raw, directory))
        breaks = [b for b in parsed.blocks if b.kind == ms.SCENE_BREAK]
        self.assertEqual(len(breaks), 3)


class TestStructure(unittest.TestCase):
    def test_chapters_and_word_count(self):
        with tempfile.TemporaryDirectory() as directory:
            document = structure.build(ms.load(write_temp(MINIMAL, directory)))
        self.assertEqual(len(document.chapters), 2)
        self.assertTrue(document.has_real_chapters)
        self.assertEqual(document.word_count, 6)

    def test_implicit_chapter_when_no_headings(self):
        source = MINIMAL.replace("## One\n\n", "").replace("## Two\n\n", "")
        with tempfile.TemporaryDirectory() as directory:
            document = structure.build(ms.load(write_temp(source, directory)))
        self.assertEqual(len(document.chapters), 1)
        self.assertFalse(document.has_real_chapters)

    def test_slugify(self):
        self.assertEqual(structure.slugify("The Things I Let Go"), "the-things-i-let-go")
        self.assertEqual(structure.slugify("Café — Two"), "cafe-two")


class TestValidate(unittest.TestCase):
    def _document(self, source, directory):
        return structure.build(ms.load(write_temp(source, directory)))

    def test_missing_required_key_raises(self):
        source = MINIMAL.replace("author: A. Writer\n", "")
        with tempfile.TemporaryDirectory() as directory:
            document = self._document(source, directory)
            with self.assertRaises(validate.ValidationError):
                validate.check(document, ("epub",))

    def test_bad_date_raises(self):
        source = MINIMAL.replace("date: 2026-01-02", "date: Jan 2 2026")
        with tempfile.TemporaryDirectory() as directory:
            document = self._document(source, directory)
            with self.assertRaises(validate.ValidationError):
                validate.check(document, ("site",))

    def test_long_description_warns_not_raises(self):
        source = MINIMAL.replace(
            "description: A minimal manuscript.", "description: " + ("x" * 200)
        )
        with tempfile.TemporaryDirectory() as directory:
            document = self._document(source, directory)
            warnings = validate.check(document, ("site",))
        self.assertTrue(any("truncate" in warning for warning in warnings))

    def test_site_target_requires_description(self):
        source = MINIMAL.replace("description: A minimal manuscript.\n", "")
        with tempfile.TemporaryDirectory() as directory:
            document = self._document(source, directory)
            validate.check(document, ("print",))  # print does not need it
            with self.assertRaises(validate.ValidationError):
                validate.check(document, ("site",))

    def test_proofing_warns_on_repeated_words_and_placeholders(self):
        source = MINIMAL.replace(
            "First paragraph.",
            "She walked into the the room and had had enough. TODO fix ending.",
        )
        with tempfile.TemporaryDirectory() as directory:
            document = self._document(source, directory)
            warnings = validate.check(document, ("print",))

        self.assertTrue(any("the the" in w for w in warnings))
        self.assertFalse(any("had had" in w for w in warnings))
        self.assertTrue(any("TODO" in w for w in warnings))


class TestPipeline(unittest.TestCase):
    def test_builds_all_three_targets(self):
        with tempfile.TemporaryDirectory() as directory:
            source = write_temp(MINIMAL, directory)
            out = Path(directory) / "build"
            result = pipeline.build(source, out)

            self.assertEqual(set(result.outputs), {"site", "epub", "print"})
            for path in result.outputs.values():
                self.assertTrue(path.is_file(), f"{path} was not written")

    def test_dry_run_writes_nothing(self):
        with tempfile.TemporaryDirectory() as directory:
            source = write_temp(MINIMAL, directory)
            out = Path(directory) / "build"
            result = pipeline.build(source, out, dry_run=True)
            self.assertFalse(out.exists())
        self.assertEqual(len(result.outputs), 3)

    def test_unknown_target_raises(self):
        with tempfile.TemporaryDirectory() as directory:
            source = write_temp(MINIMAL, directory)
            with self.assertRaises(ValueError):
                pipeline.build(source, Path(directory) / "build", targets=("pdf",))

    def test_epub_is_a_valid_archive(self):
        with tempfile.TemporaryDirectory() as directory:
            source = write_temp(MINIMAL, directory)
            out = Path(directory) / "build"
            result = pipeline.build(source, out, targets=("epub",))
            epub_path = result.outputs["epub"]

            with zipfile.ZipFile(epub_path) as archive:
                names = archive.namelist()
                self.assertEqual(names[0], "mimetype")
                self.assertEqual(
                    archive.getinfo("mimetype").compress_type, zipfile.ZIP_STORED
                )
                self.assertEqual(archive.read("mimetype").decode(), "application/epub+zip")
                for required in ("META-INF/container.xml", "OEBPS/content.opf",
                                 "OEBPS/nav.xhtml", "OEBPS/chap-001.xhtml"):
                    self.assertIn(required, names)
                self.assertIsNone(archive.testzip())

    def test_epub_build_is_reproducible(self):
        with tempfile.TemporaryDirectory() as directory:
            source = write_temp(MINIMAL, directory)
            first = pipeline.build(source, Path(directory) / "a", targets=("epub",))
            second = pipeline.build(source, Path(directory) / "b", targets=("epub",))
            self.assertEqual(
                first.outputs["epub"].read_bytes(), second.outputs["epub"].read_bytes()
            )

    def test_site_page_has_metadata_and_typeset_prose(self):
        with tempfile.TemporaryDirectory() as directory:
            source = write_temp(MINIMAL, directory)
            result = pipeline.build(source, Path(directory) / "build", targets=("site",))
            html = result.outputs["site"].read_text(encoding="utf-8")

        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn('rel="canonical"', html)
        self.assertIn('"@type": "BlogPosting"', html)
        self.assertIn('property="og:title"', html)
        self.assertIn("scene-break", html)

    def test_print_interior_has_paged_media(self):
        with tempfile.TemporaryDirectory() as directory:
            source = write_temp(MINIMAL, directory)
            result = pipeline.build(source, Path(directory) / "build", targets=("print",))
            html = result.outputs["print"].read_text(encoding="utf-8")

        self.assertIn("@page", html)
        self.assertIn("size: 6in 9in", html)
        self.assertIn("page-break-before: right", html)

    def test_print_uses_absolute_spacing_not_percentages(self):
        """Percentages resolve against container width and collapse on screen."""
        with tempfile.TemporaryDirectory() as directory:
            source = write_temp(MINIMAL, directory)
            result = pipeline.build(source, Path(directory) / "build", targets=("print",))
            css = result.outputs["print"].read_text(encoding="utf-8")

        for rule in ("margin: 18%", "margin-top: 30%"):
            self.assertNotIn(rule, css)

    def test_print_has_screen_preview_at_trim_size(self):
        with tempfile.TemporaryDirectory() as directory:
            source = write_temp(MINIMAL, directory)
            result = pipeline.build(source, Path(directory) / "build", targets=("print",))
            html = result.outputs["print"].read_text(encoding="utf-8")

        self.assertIn("@media screen", html)
        self.assertIn("width: 6in", html)
        self.assertIn("min-height: 9in", html)
        self.assertIn("sheet-note", html)

    def test_trim_dimensions_parse(self):
        from inkpress_lib.render_print import _trim_dimensions

        self.assertEqual(_trim_dimensions("6x9"), ("6in", "9in"))
        self.assertEqual(_trim_dimensions("5.5x8.5"), ("5.5in", "8.5in"))
        self.assertEqual(_trim_dimensions("210mm 297mm"), ("210mm", "297mm"))
        self.assertEqual(_trim_dimensions("nonsense"), ("6in", "9in"))

    def test_site_page_is_styled_without_a_donor(self):
        """A page with no donor must not come out as raw unstyled HTML."""
        with tempfile.TemporaryDirectory() as directory:
            source = write_temp(MINIMAL, directory)
            result = pipeline.build(source, Path(directory) / "build", targets=("site",))
            html = result.outputs["site"].read_text(encoding="utf-8")

        self.assertIn('data-inkpress="base"', html)
        self.assertIn("max-width: 40rem", html)
        self.assertIn(".scene-break", html)

    def test_site_page_with_donor_adds_only_the_gaps(self):
        donor = """<!DOCTYPE html><html><head>
        <link rel="stylesheet" href="/css/site.css" />
        </head><body><nav class="site-nav">x</nav></body></html>"""

        with tempfile.TemporaryDirectory() as directory:
            donor_path = Path(directory) / "donor.html"
            donor_path.write_text(donor, encoding="utf-8")
            source = write_temp(MINIMAL, directory)
            result = pipeline.build(
                source,
                Path(directory) / "build",
                targets=("site",),
                chrome=pipeline.load_chrome(donor_path),
            )
            html = result.outputs["site"].read_text(encoding="utf-8")

        # The donor's stylesheet owns layout; inkpress only supplies its own classes.
        self.assertNotIn("max-width: 40rem", html)
        self.assertIn(".scene-break", html)

    def test_epub_centres_inline_for_strict_readers(self):
        with tempfile.TemporaryDirectory() as directory:
            source = write_temp(MINIMAL, directory)
            result = pipeline.build(source, Path(directory) / "build", targets=("epub",))

            with zipfile.ZipFile(result.outputs["epub"]) as archive:
                chapter = archive.read("OEBPS/chap-001.xhtml").decode()
                title_page = archive.read("OEBPS/titlepage.xhtml").decode()

        self.assertIn('class="scene-break" style="text-align: center;', chapter)
        self.assertIn("text-align: center", title_page)

    def test_chrome_is_lifted_from_donor(self):
        donor = """<!DOCTYPE html><html><head>
        <link rel="stylesheet" href="/css/site.css" />
        </head><body>
        <nav class="site-nav"><ul><li><a href="/">Home</a></li></ul></nav>
        <footer><div class="footer-legal">c 2026</div></footer>
        </body></html>"""

        with tempfile.TemporaryDirectory() as directory:
            donor_path = Path(directory) / "donor.html"
            donor_path.write_text(donor, encoding="utf-8")
            chrome = pipeline.load_chrome(donor_path)

            source = write_temp(MINIMAL, directory)
            result = pipeline.build(
                source, Path(directory) / "build", targets=("site",), chrome=chrome
            )
            html = result.outputs["site"].read_text(encoding="utf-8")

        self.assertIn('class="site-nav"', html)
        self.assertIn("footer-legal", html)
        self.assertIn("/css/site.css", html)

    def test_missing_donor_raises(self):
        with self.assertRaises(FileNotFoundError):
            pipeline.load_chrome("no-such-page.html")

    def test_meta_overrides_supply_missing_front_matter(self):
        """The desktop app's form fields fill in what a bare manuscript lacks."""
        bare = "Just prose, no header at all.\n"
        with tempfile.TemporaryDirectory() as directory:
            source = write_temp(bare, directory)

            with self.assertRaises(validate.ValidationError):
                pipeline.build(source, Path(directory) / "a", targets=("site",))

            result = pipeline.build(
                source,
                Path(directory) / "b",
                targets=("site",),
                meta_overrides={
                    "title": "Supplied Title",
                    "author": "A. Writer",
                    "date": "2026-08-22",
                    "description": "Supplied description.",
                },
            )
            html = result.outputs["site"].read_text(encoding="utf-8")

        self.assertEqual(result.document.slug, "supplied-title")
        self.assertIn("Supplied Title", html)
        self.assertIn("Supplied description.", html)

    def test_blank_overrides_do_not_clobber_front_matter(self):
        with tempfile.TemporaryDirectory() as directory:
            source = write_temp(MINIMAL, directory)
            result = pipeline.build(
                source,
                Path(directory) / "build",
                targets=("site",),
                meta_overrides={"title": "", "author": None},
            )
        self.assertEqual(result.document.title, "Test Book")
        self.assertEqual(result.document.meta["author"], "A. Writer")

    def test_overridden_meta_is_typeset(self):
        with tempfile.TemporaryDirectory() as directory:
            source = write_temp(MINIMAL, directory)
            result = pipeline.build(
                source,
                Path(directory) / "build",
                targets=("site",),
                meta_overrides={"title": "The Lamplighter's Round---A Test"},
            )
        self.assertIn("’", result.document.title)
        self.assertIn("—", result.document.title)


class TestEditions(unittest.TestCase):
    def test_tier_one_is_the_default(self):
        edition = editions.resolve()
        self.assertEqual(edition.tier, editions.CLEAN)
        self.assertFalse(edition.drop_cap)
        self.assertIsNone(edition.art)

    def test_styled_has_drop_caps_but_no_art(self):
        edition = editions.resolve("styled")
        self.assertTrue(edition.drop_cap)
        self.assertIsNone(edition.art)
        self.assertFalse(edition.is_illustrated)

    def test_illustrated_requires_an_edition(self):
        with self.assertRaises(editions.EditionError):
            editions.resolve("illustrated")

    def test_each_edition_sets_typography_and_art(self):
        for key in editions.EDITIONS:
            edition = editions.resolve("illustrated", key)
            self.assertTrue(edition.is_illustrated)
            self.assertEqual(edition.art, key)
            self.assertTrue(edition.drop_cap)
            self.assertTrue(art.is_available(edition.art))

    def test_editions_are_visually_distinct(self):
        resolved = [editions.resolve("illustrated", key) for key in editions.EDITIONS]
        fonts = {edition.display_font for edition in resolved}
        accents = {edition.accent for edition in resolved}
        self.assertEqual(len(fonts), 3, "each edition needs its own display face")
        self.assertEqual(len(accents), 3, "each edition needs its own accent")

    def test_unknown_names_are_rejected(self):
        with self.assertRaises(editions.EditionError):
            editions.resolve("deluxe")
        with self.assertRaises(editions.EditionError):
            editions.resolve("illustrated", "obsidian")

    def test_overrides_beat_front_matter(self):
        meta = {"tier": "clean", "edition": "ashveil"}
        self.assertEqual(editions.from_meta(meta).tier, editions.CLEAN)
        resolved = editions.from_meta(meta, tier_override="illustrated")
        self.assertEqual(resolved.key, "ashveil")


class TestArt(unittest.TestCase):
    def test_art_is_deterministic(self):
        first = art.render("ashveil", seed="chapter-one", ink="#000", accent="#f00")
        second = art.render("ashveil", seed="chapter-one", ink="#000", accent="#f00")
        self.assertEqual(first, second)

    def test_different_chapters_differ(self):
        first = art.render("ashveil", seed="chapter-one", ink="#000", accent="#f00")
        second = art.render("ashveil", seed="chapter-two", ink="#000", accent="#f00")
        self.assertNotEqual(first, second)

    def test_art_is_well_formed_svg(self):
        import xml.dom.minidom

        for key in editions.EDITIONS:
            svg = art.render(key, seed="x", ink="#111111", accent="#abcdef")
            xml.dom.minidom.parseString(svg)
            self.assertIn("viewBox", svg)

    def test_title_is_escaped(self):
        svg = art.render("ashveil", seed="x", title="Fish & <Chips>")
        self.assertIn("Fish &amp; &lt;Chips&gt;", svg)
        self.assertNotIn("<Chips>", svg)

    def test_unknown_edition_renders_nothing(self):
        self.assertEqual(art.render("nope", seed="x"), "")


class TestDropCap(unittest.TestCase):
    def test_wraps_first_letter(self):
        self.assertEqual(
            body.apply_drop_cap("The lamps went on."),
            '<span class="dropcap">T</span>he lamps went on.',
        )

    def test_punctuation_rides_along(self):
        """A paragraph opening on dialogue must not drop a lone quote mark."""
        result = body.apply_drop_cap("“You’re early,” he said.")
        self.assertEqual(result, '<span class="dropcap">“Y</span>ou’re early,” he said.')

    def test_skips_leading_tags(self):
        result = body.apply_drop_cap("<em>Later</em>, she left.")
        self.assertEqual(result, '<em><span class="dropcap">L</span>ater</em>, she left.')

    def test_only_the_first_paragraph_gets_one(self):
        with tempfile.TemporaryDirectory() as directory:
            document = structure.build(ms.load(write_temp(MINIMAL, directory)))
        html = "\n".join(
            body.blocks_to_html(document.chapters[0].blocks, drop_cap=True)
        )
        self.assertEqual(html.count("dropcap"), 1)


class TestTierBuilds(unittest.TestCase):
    def _build(self, directory, tier, edition=None, targets=pipeline.ALL_TARGETS):
        source = write_temp(MINIMAL, directory)
        return pipeline.build(
            source, Path(directory) / f"build-{tier}-{edition}",
            targets=targets, tier=tier, edition=edition,
        )

    def test_all_three_tiers_build(self):
        with tempfile.TemporaryDirectory() as directory:
            for tier, edition in (
                ("clean", None),
                ("styled", None),
                ("illustrated", "ashveil"),
                ("illustrated", "systemfall"),
                ("illustrated", "vantablack"),
            ):
                result = self._build(directory, tier, edition)
                self.assertEqual(len(result.outputs), 3, f"{tier}/{edition}")
                for path in result.outputs.values():
                    self.assertTrue(path.is_file())

    def test_clean_has_no_drop_cap_and_styled_does(self):
        with tempfile.TemporaryDirectory() as directory:
            clean = self._build(directory, "clean", targets=("print",))
            styled = self._build(directory, "styled", targets=("print",))

            clean_html = clean.outputs["print"].read_text(encoding="utf-8")
            styled_html = styled.outputs["print"].read_text(encoding="utf-8")

        self.assertNotIn("dropcap", clean_html)
        self.assertIn("dropcap", styled_html)

    def test_only_illustrated_carries_art(self):
        with tempfile.TemporaryDirectory() as directory:
            styled = self._build(directory, "styled", targets=("print",))
            illustrated = self._build(directory, "illustrated", "vantablack",
                                      targets=("print",))

            styled_html = styled.outputs["print"].read_text(encoding="utf-8")
            art_html = illustrated.outputs["print"].read_text(encoding="utf-8")

        self.assertNotIn("chapter-art", styled_html)
        self.assertIn("chapter-art", art_html)
        self.assertIn("<svg", art_html)

    def test_epub_packages_and_manifests_its_art(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self._build(directory, "illustrated", "ashveil", targets=("epub",))

            with zipfile.ZipFile(result.outputs["epub"]) as archive:
                names = archive.namelist()
                opf = archive.read("OEBPS/content.opf").decode()

        art_files = [name for name in names if name.startswith("OEBPS/art/")]
        self.assertEqual(len(art_files), 2, "one per chapter")
        for name in art_files:
            self.assertIn(name.replace("OEBPS/", ""), opf)
            self.assertIn('media-type="image/svg+xml"', opf)

    def test_illustrated_epub_is_still_reproducible(self):
        with tempfile.TemporaryDirectory() as directory:
            source = write_temp(MINIMAL, directory)
            kwargs = dict(targets=("epub",), tier="illustrated", edition="systemfall")
            first = pipeline.build(source, Path(directory) / "a", **kwargs)
            second = pipeline.build(source, Path(directory) / "b", **kwargs)
            self.assertEqual(
                first.outputs["epub"].read_bytes(), second.outputs["epub"].read_bytes()
            )

    def test_stray_edition_on_a_lower_tier_warns(self):
        source_text = MINIMAL.replace(
            "language: en", "language: en\ntier: styled\nedition: ashveil"
        )
        with tempfile.TemporaryDirectory() as directory:
            source = write_temp(source_text, directory)
            result = pipeline.build(source, Path(directory) / "build", targets=("print",))

        self.assertTrue(any("ignored" in warning for warning in result.warnings))

    def test_tier_read_from_front_matter(self):
        source_text = MINIMAL.replace(
            "language: en", "language: en\ntier: illustrated\nedition: vantablack"
        )
        with tempfile.TemporaryDirectory() as directory:
            source = write_temp(source_text, directory)
            result = pipeline.build(source, Path(directory) / "build", targets=("print",))

        self.assertEqual(result.edition.key, "vantablack")

    def test_bad_tier_in_front_matter_raises(self):
        source_text = MINIMAL.replace("language: en", "language: en\ntier: platinum")
        with tempfile.TemporaryDirectory() as directory:
            source = write_temp(source_text, directory)
            with self.assertRaises(editions.EditionError):
                pipeline.build(source, Path(directory) / "build", targets=("print",))

    def test_chapter_rule_appears_in_all_three_targets(self):
        with tempfile.TemporaryDirectory() as directory:
            clean = self._build(directory, "clean")
            styled = self._build(directory, "styled")

            clean_site = clean.outputs["site"].read_text(encoding="utf-8")
            styled_site = styled.outputs["site"].read_text(encoding="utf-8")
            self.assertNotIn("h2::after", clean_site)
            self.assertIn("h2::after", styled_site)

            with zipfile.ZipFile(clean.outputs["epub"]) as archive:
                clean_epub_css = archive.read("OEBPS/style.css").decode()
            with zipfile.ZipFile(styled.outputs["epub"]) as archive:
                styled_epub_css = archive.read("OEBPS/style.css").decode()
            self.assertNotIn("h2::after", clean_epub_css)
            self.assertIn("h2::after", styled_epub_css)

    def test_implicit_chapter_omits_duplicate_heading_in_epub_and_marks_opening(self):
        source_text = MINIMAL.replace("## One\n\n", "").replace("## Two\n\n", "")
        with tempfile.TemporaryDirectory() as directory:
            source = write_temp(source_text, directory)
            result = pipeline.build(
                source, Path(directory) / "build", tier="styled"
            )
            print_html = result.outputs["print"].read_text(encoding="utf-8")
            with zipfile.ZipFile(result.outputs["epub"]) as archive:
                chap_xhtml = archive.read("OEBPS/chap-001.xhtml").decode()

        self.assertNotIn("<h2", chap_xhtml)
        self.assertNotIn("chapter-number", chap_xhtml)
        self.assertIn('class="opening"', chap_xhtml)
        self.assertIn('class="opening"', print_html)

    def test_app_prefills_tier_and_edition_from_front_matter(self):
        try:
            import tkinter as tk
            import inkpress_app
        except ImportError:
            self.skipTest("Tkinter unavailable")

        try:
            root = tk.Tk()
            root.withdraw()
        except tk.TclError:
            self.skipTest("No display available for Tk")

        try:
            source_text = MINIMAL.replace(
                "language: en", "language: en\ntier: illustrated\nedition: systemfall"
            )
            with tempfile.TemporaryDirectory() as directory:
                source = write_temp(source_text, directory)
                app = inkpress_app.InkpressApp(root, initial_manuscript=source)
                self.assertEqual(
                    app.tier_var.get(), editions.TIER_LABELS[editions.ILLUSTRATED]
                )
                self.assertEqual(
                    app.edition_var.get(), editions.EDITION_LABELS[editions.SYSTEMFALL]
                )
                self.assertEqual(str(app.edition_box.cget("state")), "readonly")
                self.assertEqual(len(app.chapter_tree.get_children()), 2)

                for ed_label in inkpress_app.EDITION_CHOICES:
                    app.edition_var.set(ed_label)
                    app._sync_edition_state()
                    self.assertGreater(len(app.page_canvas.find_all()), 5)

                stats_6x9 = inkpress_app.estimate_kdp_stats(60000, 20, trim="6x9")
                stats_5x8 = inkpress_app.estimate_kdp_stats(60000, 20, trim="5x8")
                self.assertEqual(stats_6x9["pages"] % 2, 0)
                self.assertGreater(stats_5x8["pages"], stats_6x9["pages"])
                self.assertGreater(stats_6x9["spine_in"], 0.4)

                # Test drag-and-drop handler routing for manuscripts, covers, templates, and folders
                dropped_ms = Path(directory) / "dropped-book.md"
                dropped_ms.write_text(MINIMAL, encoding="utf-8")
                app.handle_dropped_file(f'"{dropped_ms}"')
                self.assertEqual(Path(app.manuscript_var.get()), dropped_ms)
                self.assertEqual(app.meta_vars["title"].get(), "Test Book")

                dropped_cover = Path(directory) / "cover.svg"
                dropped_cover.write_text("<svg xmlns='http://www.w3.org/2000/svg'/>", encoding="utf-8")
                app.handle_dropped_file(str(dropped_cover))
                self.assertEqual(Path(app.cover_var.get()), dropped_cover)

                dropped_chrome = Path(directory) / "template.html"
                dropped_chrome.write_text("<html><body><main></main></body></html>", encoding="utf-8")
                app.handle_dropped_file(str(dropped_chrome))
                self.assertEqual(Path(app.chrome_var.get()), dropped_chrome)

                dropped_out = Path(directory) / "custom-out"
                dropped_out.mkdir()
                app.handle_dropped_file(str(dropped_out))
                self.assertEqual(Path(app.out_var.get()), dropped_out)

                if inkpress_app.platform.system() == "Windows":
                    self.assertTrue(
                        inkpress_app._enable_windows_file_drop(root, app.handle_dropped_file)
                    )

                # Test colored border selection in the app
                app._select_preset("clean", None)
                self.assertEqual(app._resolved_edition().border_style, "none")
                app._select_border_color("#1E3A5F")
                resolved_custom = app._resolved_edition()
                self.assertEqual(resolved_custom.accent, "#1E3A5F")
                self.assertEqual(resolved_custom.border_style, "double")
        finally:
            root.destroy()

    def test_custom_border_color_and_style_render_across_all_targets(self):
        with tempfile.TemporaryDirectory() as directory:
            source = write_temp(MINIMAL, directory)
            result = pipeline.build(
                source,
                Path(directory) / "build",
                meta_overrides={"border_color": "#1E3A5F", "border_style": "double"},
            )
            print_html = result.outputs["print"].read_text(encoding="utf-8")
            site_html = result.outputs["site"].read_text(encoding="utf-8")
            with zipfile.ZipFile(result.outputs["epub"]) as archive:
                epub_css = archive.read("OEBPS/style.css").decode("utf-8")
                cover_svg = archive.read("OEBPS/cover.svg").decode("utf-8")

        self.assertIn("3.5px double #1E3A5F", print_html)
        self.assertIn("4px double #1E3A5F", site_html)
        self.assertIn("3px double #1E3A5F", epub_css)
        self.assertIn('stroke="#1E3A5F"', cover_svg)

    def test_package_bundles_buyer_deliverables(self):
        with tempfile.TemporaryDirectory() as directory:
            source = write_temp(MINIMAL, directory)
            result = pipeline.build(
                source,
                Path(directory) / "build",
                tier="illustrated",
                edition="ashveil",
                package=True,
            )
            self.assertIn("package", result.outputs)
            zip_path = result.outputs["package"]
            self.assertTrue(zip_path.is_file())
            self.assertEqual(zip_path.name, "test-book-ashveil.zip")

            with zipfile.ZipFile(zip_path) as archive:
                self.assertEqual(
                    sorted(archive.namelist()),
                    [
                        "DELIVERY-NOTES.txt",
                        "test-book-interior.html",
                        "test-book.epub",
                        "test-book.html",
                    ],
                )
                notes = archive.read("DELIVERY-NOTES.txt").decode("utf-8")
                self.assertIn("Test Book", notes)
                self.assertIn("Ashveil", notes)

    def test_unnumbered_front_back_matter_and_redundant_chapter_prefixes(self):
        raw = (
            "---\ntitle: Test Book\nauthor: A. Writer\ndate: 2026-01-02\n"
            "language: en\ndescription: Short.\n---\n\n"
            "## Prologue\n\nOpening prologue.\n\n"
            "## Chapter 1: The Gate\n\nFirst real chapter.\n\n"
            "## Chapter Two\n\nSecond real chapter.\n\n"
            "## About the Author\n\nBio text.\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            source = write_temp(raw, directory)
            result = pipeline.build(
                source, Path(directory) / "build", targets=("print",), tier="styled"
            )
            html = result.outputs["print"].read_text(encoding="utf-8")

        self.assertEqual(result.document.chapters[0].display_number, None)
        self.assertEqual(result.document.chapters[1].display_number, 1)
        self.assertEqual(result.document.chapters[2].display_number, 2)
        self.assertEqual(result.document.chapters[3].display_number, None)
        self.assertIn('<span class="chapter-number">Chapter 1</span>', html)
        self.assertIn('<h2 id="chapter-1-the-gate">The Gate</h2>', html)
        self.assertNotIn('<span class="chapter-number">Chapter 2</span>', html)
        self.assertIn('<h2 id="chapter-two">Chapter Two</h2>', html)

    def test_copyright_and_dedication_render_in_print_and_epub(self):
        source_text = MINIMAL.replace(
            "language: en",
            "language: en\ncopyright: Copyright 2026 A. Writer\ndedication: For Mara",
        )
        with tempfile.TemporaryDirectory() as directory:
            source = write_temp(source_text, directory)
            result = pipeline.build(
                source, Path(directory) / "build", targets=("print", "epub")
            )
            print_html = result.outputs["print"].read_text(encoding="utf-8")
            with zipfile.ZipFile(result.outputs["epub"]) as archive:
                titlepage = archive.read("OEBPS/titlepage.xhtml").decode()

        self.assertIn("copyright-page", print_html)
        self.assertIn("Copyright 2026 A. Writer", print_html)
        self.assertIn("dedication-page", print_html)
        self.assertIn("For Mara", titlepage)

    def test_dynamic_kdp_gutter_scales_with_word_count(self):
        from inkpress_lib.render_print import _default_gutter

        self.assertEqual(_default_gutter(5000), "0.25in")
        self.assertEqual(_default_gutter(45000), "0.375in")
        self.assertEqual(_default_gutter(75000), "0.5in")

    def test_print_includes_toc_and_auto_copyright(self):
        with tempfile.TemporaryDirectory() as directory:
            source = write_temp(MINIMAL, directory)
            result = pipeline.build(
                source, Path(directory) / "build", targets=("print",)
            )
            html = result.outputs["print"].read_text(encoding="utf-8")

        self.assertIn('class="toc-page"', html)
        self.assertIn("Copyright © 2026 by A. Writer", html)

    def test_epub_includes_generated_cover_image(self):
        with tempfile.TemporaryDirectory() as directory:
            source = write_temp(MINIMAL, directory)
            result = pipeline.build(
                source,
                Path(directory) / "build",
                targets=("epub",),
                tier="illustrated",
                edition="vantablack",
            )
            with zipfile.ZipFile(result.outputs["epub"]) as archive:
                names = archive.namelist()
                opf = archive.read("OEBPS/content.opf").decode()
                cover_svg = archive.read("OEBPS/cover.svg").decode()

        self.assertIn("OEBPS/cover.svg", names)
        self.assertIn('properties="cover-image"', opf)
        self.assertIn("Test Book", cover_svg)

    def test_dual_pov_duplicate_chapter_titles_disambiguate_and_warn(self):
        raw = (
            "---\ntitle: Dual POV\nauthor: A. Writer\ndate: 2026-01-02\n"
            "language: en\ndescription: Dual POV novel.\n---\n\n"
            "## Mara\n\nChapter one prose.\n\n"
            "## Corin\n\nChapter two prose.\n\n"
            "## Mara\n\nChapter three prose.\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            source = write_temp(raw, directory)
            result = pipeline.build(
                source, Path(directory) / "build", targets=("print", "site")
            )
            print_html = result.outputs["print"].read_text(encoding="utf-8")

        self.assertEqual(
            [ch.slug for ch in result.document.chapters],
            ["mara", "corin", "mara-2"],
        )
        self.assertIn('id="mara"', print_html)
        self.assertIn('id="mara-2"', print_html)
        self.assertTrue(any("share the title" in w for w in result.warnings))

    def test_drop_letter_is_tier2_feature_with_style_and_custom_letter(self):
        # Tier 1 (Clean) ignores drop_cap_style and drop_cap_letter
        clean_ed = editions.resolve(
            "clean", drop_cap_style="boxed", drop_cap_letter="W"
        )
        self.assertFalse(clean_ed.drop_cap)
        self.assertEqual(clean_ed.drop_cap_style, "none")
        self.assertEqual(clean_ed.drop_cap_letter, "")

        # Tier 2 (Styled) supports custom drop_cap_style and drop_cap_letter
        styled_ed = editions.resolve(
            "styled", drop_cap_style="framed", drop_cap_letter="w"
        )
        self.assertTrue(styled_ed.drop_cap)
        self.assertEqual(styled_ed.drop_cap_style, "framed")
        self.assertEqual(styled_ed.drop_cap_letter, "W")

        # Pipeline renders custom drop letter and style CSS across Print, EPUB, and Site
        with tempfile.TemporaryDirectory() as directory:
            source = write_temp(MINIMAL, directory)
            result = pipeline.build(
                source,
                Path(directory) / "build",
                targets=("print", "epub", "site"),
                tier="styled",
                meta_overrides={
                    "drop_cap_style": "boxed",
                    "drop_cap_letter": "W",
                },
            )
            print_html = result.outputs["print"].read_text(encoding="utf-8")
            site_html = result.outputs["site"].read_text(encoding="utf-8")
            with zipfile.ZipFile(result.outputs["epub"]) as archive:
                ch1_xhtml = archive.read("OEBPS/chap-001.xhtml").decode()
                epub_css = archive.read("OEBPS/style.css").decode()

        self.assertIn('<span class="dropcap">W</span>First paragraph.', print_html)
        self.assertIn('<span class="dropcap">W</span>First paragraph.', site_html)
        self.assertIn('<span class="dropcap">W</span>First paragraph.', ch1_xhtml)
        self.assertIn("background: #6b5b4a;", print_html)
        self.assertIn("background: #6b5b4a;", epub_css)


class TestSampleManuscript(unittest.TestCase):
    def test_sample_builds_cleanly(self):
        self.assertTrue(SAMPLE.is_file(), f"sample manuscript missing at {SAMPLE}")
        with tempfile.TemporaryDirectory() as directory:
            result = pipeline.build(SAMPLE, Path(directory) / "build")
        self.assertEqual(len(result.outputs), 3)
        self.assertEqual(len(result.document.chapters), 2)

    def test_sample_prose_is_typeset(self):
        with tempfile.TemporaryDirectory() as directory:
            result = pipeline.build(SAMPLE, Path(directory) / "build", targets=("site",))
            html = result.outputs["site"].read_text(encoding="utf-8")
        self.assertIn("—", html)  # em dash
        self.assertIn("“", html)  # opening double quote
        self.assertIn("’", html)  # apostrophe
        self.assertNotIn("---", html)

    def test_powershell_scripts_remain_utf8_bom_and_plain_ascii(self):
        for script_name in ("bootstrap-inkpress.ps1", "inkpress.ps1"):
            script_path = HERE.parent / script_name
            raw = script_path.read_bytes()
            self.assertTrue(
                raw.startswith(b"\xef\xbb\xbf"),
                f"{script_name} is missing its UTF-8 BOM",
            )
            body_bytes = raw[3:]
            non_ascii = [b for b in body_bytes if b >= 128]
            self.assertEqual(
                non_ascii,
                [],
                f"{script_name} contains non-ASCII bytes: {non_ascii}",
            )

    def test_long_cover_title_wraps_into_multiple_tspans(self):
        edition = editions.resolve("illustrated", "ashveil")
        svg = art.render_cover(
            edition,
            title="The Chronicles of the Last Lamplighter of Harbour Row",
            author="J.S. Warden",
        )
        self.assertGreaterEqual(svg.count("<tspan"), 2)

    def test_build_exe_writes_valid_ico_and_pe_executable(self):
        import build_exe

        with tempfile.TemporaryDirectory() as directory:
            ico = build_exe.write_icon(Path(directory) / "test.ico")
            self.assertTrue(ico.is_file())
            self.assertEqual(ico.read_bytes()[:4], b"\x00\x00\x01\x00")

            if build_exe.find_csc():
                exe = build_exe.build_exe(Path(directory) / "test.exe", ico)
                self.assertTrue(exe.is_file())
                self.assertEqual(exe.read_bytes()[:2], b"MZ")


def _make_tiny_png(width=64, height=96):
    """Build a valid minimal RGB PNG byte buffer using only Python stdlib."""
    import struct
    import zlib

    raw_rows = b"".join(b"\x00" + (b"\x1e\x29\x3b" * width) for _ in range(height))

    def _chunk(tag, payload):
        crc = zlib.crc32(tag + payload) & 0xFFFFFFFF
        return struct.pack(">I", len(payload)) + tag + payload + struct.pack(">I", crc)

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    idat = zlib.compress(raw_rows)
    return b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr) + _chunk(b"IDAT", idat) + _chunk(b"IEND", b"")


class TestMarketBlockTypes(unittest.TestCase):
    def test_multiline_yaml_lists_callouts_parts_and_inline_images(self):
        with tempfile.TemporaryDirectory() as directory:
            tmp = Path(directory)
            img_path = tmp / "harbor-map.png"
            img_path.write_bytes(_make_tiny_png(800, 600))

            text = """---
title: System of the Tides
author: J.S. Warden
date: 2026-09-15
language: en
description: A LitRPG maritime fantasy with maps, letters, and part dividers.
dedication: |
  For the night watch,
  who keep the lanterns lit.
---

# Part I: The Outer Shoals

## Chapter 1: Wake-Up Prompt

First paragraph at the dock.

- Salt rations
- Brass sextant

1. Check the tide gauge
2. Sound the bell

::: system
**QUEST UNLOCKED:** Light the Breakwater Beacon
Reward: +250 Harbor Renown
:::

::: letter
Harbor Master,

Do not open the sea-gate before midnight.
:::

![Map of the Outer Shoals](harbor-map.png "Chart drawn in 1894")

## Chapter 2: The Sea-Gate

Second chapter prose so the print Table of Contents is generated.
"""
            src = write_temp(text, tmp)
            parsed = ms.load(src)
            self.assertIn("For the night watch,\nwho keep the lanterns lit.", parsed.meta["dedication"])

            doc = structure.build(parsed)
            self.assertEqual(len(doc.chapters), 2)
            self.assertEqual(doc.chapters[0].part_title, "Part I: The Outer Shoals")
            self.assertGreater(doc.word_count, 30)

            out = tmp / "out"
            res = pipeline.build(
                src,
                out_dir=out,
                targets=("print", "epub", "site"),
                tier="styled",
            )

            print_html = res.outputs["print"].read_text(encoding="utf-8")
            self.assertIn('class="part-page"', print_html)
            self.assertIn('class="toc-part"', print_html)
            self.assertIn("<li>Salt rations</li>", print_html)
            self.assertIn("<li>Check the tide gauge</li>", print_html)
            self.assertIn('class="callout callout-system"', print_html)
            self.assertIn('class="callout callout-letter"', print_html)
            self.assertIn('class="inline-figure"', print_html)
            self.assertIn("Chart drawn in 1894", print_html)
            self.assertIn("file:///", print_html)

            site_html = res.outputs["site"].read_text(encoding="utf-8")
            self.assertIn('class="part-divider"', site_html)
            self.assertIn('class="callout callout-system"', site_html)
            self.assertIn('class="inline-figure"', site_html)

            with zipfile.ZipFile(res.outputs["epub"]) as zf:
                names = set(zf.namelist())
                self.assertIn("OEBPS/images/img-001.png", names)
                opf = zf.read("OEBPS/content.opf").decode("utf-8")
                self.assertIn('href="images/img-001.png"', opf)
                self.assertIn('media-type="image/png"', opf)
                chap1 = zf.read("OEBPS/chap-001.xhtml").decode("utf-8")
                self.assertIn('class="part-page"', chap1)
                self.assertIn('src="images/img-001.png"', chap1)
                self.assertIn('class="callout callout-system"', chap1)

    def test_docx_part_headings_lists_and_intense_quote_callouts(self):
        with tempfile.TemporaryDirectory() as directory:
            docx_path = Path(directory) / "book.docx"
            document_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading1"/></w:pPr>
      <w:r><w:t>Part I: Iron Harbor</w:t></w:r>
    </w:p>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading2"/></w:pPr>
      <w:r><w:t>The Watchtower</w:t></w:r>
    </w:p>
    <w:p>
      <w:r><w:t>Opening prose line.</w:t></w:r>
    </w:p>
    <w:p>
      <w:pPr><w:pStyle w:val="ListBullet"/></w:pPr>
      <w:r><w:t>First supply crate</w:t></w:r>
    </w:p>
    <w:p>
      <w:pPr><w:pStyle w:val="ListBullet"/></w:pPr>
      <w:r><w:t>Second supply crate</w:t></w:r>
    </w:p>
    <w:p>
      <w:pPr><w:pStyle w:val="IntenseQuote"/></w:pPr>
      <w:r><w:t>SYSTEM ALERT: Tide rising.</w:t></w:r>
    </w:p>
  </w:body>
</w:document>"""
            with zipfile.ZipFile(docx_path, "w") as zf:
                zf.writestr("word/document.xml", document_xml)

            parsed = ms.load(docx_path)
            kinds = [b.kind for b in parsed.blocks]
            self.assertIn(ms.PART, kinds)
            self.assertIn(ms.ULIST, kinds)
            self.assertIn(ms.CALLOUT, kinds)
            doc = structure.build(parsed)
            self.assertEqual(doc.chapters[0].part_title, "Part I: Iron Harbor")


class TestFontPairingsAndBackMatter(unittest.TestCase):
    def test_font_pairing_overrides_typography_stack(self):
        ed = editions.resolve("styled", font_pairing="garamond")
        self.assertEqual(ed.font_pairing, "garamond")
        self.assertIn("Garamond", ed.body_font)

        mono = editions.from_meta({"tier": "styled", "font_pairing": "mono_serif"})
        self.assertEqual(mono.font_pairing, "mono_serif")
        self.assertIn("Consolas", mono.display_font)

        with self.assertRaises(editions.EditionError):
            editions.resolve("styled", font_pairing="papyrus_comic")

    def test_structured_front_and_back_matter_and_isbn_render_everywhere(self):
        with tempfile.TemporaryDirectory() as directory:
            tmp = Path(directory)
            src = write_temp(MINIMAL, tmp)
            overrides = {
                "isbn": "978-1-999999-01-2",
                "also_by": "The Fog Bell\nHarbor of Glass",
                "epigraph": "All rivers remember the sea.\n— Old Mariner Proverb",
                "dedication": "For Mara.\nAlways.",
                "acknowledgments": "Thanks to my beta readers and harbor historians.",
                "about_author": "A. Writer lives on the northern coast and writes maritime mysteries.",
                "newsletter_cta": "Get the free prequel novella when you join the reader list.",
                "newsletter_url": "https://example.com/readers",
                "font_pairing": "baskerville",
            }
            res = pipeline.build(
                src,
                out_dir=tmp / "out",
                targets=("print", "epub", "site"),
                meta_overrides=overrides,
                tier="styled",
            )

            print_html = res.outputs["print"].read_text(encoding="utf-8")
            self.assertIn("Baskerville", print_html)
            self.assertIn("978-1-999999-01-2", print_html)
            self.assertIn('class="also-by-page"', print_html)
            self.assertIn("Harbor of Glass", print_html)
            self.assertIn('class="epigraph-page"', print_html)
            self.assertIn('class="backmatter-page"', print_html)
            self.assertIn("Acknowledgments", print_html)
            self.assertIn("About the Author", print_html)
            self.assertIn('class="newsletter-cta"', print_html)
            self.assertIn("https://example.com/readers", print_html)

            site_html = res.outputs["site"].read_text(encoding="utf-8")
            self.assertIn('class="dispatch-backmatter"', site_html)
            self.assertIn("https://example.com/readers", site_html)

            with zipfile.ZipFile(res.outputs["epub"]) as zf:
                names = set(zf.namelist())
                self.assertIn("OEBPS/backmatter.xhtml", names)
                opf = zf.read("OEBPS/content.opf").decode("utf-8")
                self.assertIn("urn:isbn:978-1-999999-01-2", opf)
                self.assertIn('href="backmatter.xhtml"', opf)
                title_xhtml = zf.read("OEBPS/titlepage.xhtml").decode("utf-8")
                self.assertIn("Harbor of Glass", title_xhtml)
                self.assertIn("All rivers remember the sea.", title_xhtml)
                back_xhtml = zf.read("OEBPS/backmatter.xhtml").decode("utf-8")
                self.assertIn("Acknowledgments", back_xhtml)
                self.assertIn("About the Author", back_xhtml)
                self.assertIn("https://example.com/readers", back_xhtml)


class TestKdpPreflightAndValidation(unittest.TestCase):
    def test_low_res_cover_missing_image_and_short_kdp_page_count_warn(self):
        with tempfile.TemporaryDirectory() as directory:
            tmp = Path(directory)
            small_cover = tmp / "tiny-cover.png"
            small_cover.write_bytes(_make_tiny_png(120, 180))
            self.assertEqual(validate._image_dimensions(small_cover), (120, 180))

            text = """---
title: Short Proof
author: A. Writer
date: 2026-05-01
language: en
description: A short test book with ISBN and inline image check.
isbn: 978-1-999999-02-9
cover: tiny-cover.png
---

## One

A very short chapter.

![Missing Diagram](does-not-exist.png)
"""
            src = write_temp(text, tmp)
            parsed = ms.load(src)
            doc = structure.build(parsed)
            warnings = validate.check(doc, targets=("print", "epub"))
            joined = "\n".join(warnings)
            self.assertIn("120x180px", joined)
            self.assertIn("does-not-exist.png", joined)
            self.assertIn("24-page paperback minimum", joined)


class TestProjectSidecarAndLicense(unittest.TestCase):
    def test_project_sidecar_roundtrip_and_pipeline_merge(self):
        from inkpress_lib import project

        with tempfile.TemporaryDirectory() as directory:
            tmp = Path(directory)
            src = write_temp(MINIMAL, tmp)
            saved_path = project.save_project(
                src,
                {
                    "subtitle": "From the Sidecar",
                    "isbn": "978-1-999999-09-8",
                    "tier": "styled",
                    "font_pairing": "palatino",
                },
            )
            self.assertTrue(saved_path.is_file())
            loaded = project.load_project(src)
            self.assertEqual(loaded["subtitle"], "From the Sidecar")

            res = pipeline.build(
                src,
                out_dir=tmp / "out",
                targets=("print",),
                meta_overrides={"subtitle": "Explicit Override Wins"},
            )
            html_out = res.outputs["print"].read_text(encoding="utf-8")
            self.assertIn("Explicit Override Wins", html_out)
            self.assertIn("978-1-999999-09-8", html_out)
            self.assertIn("Palatino", html_out)

    def test_offline_license_mint_verify_tamper_and_storage(self):
        from inkpress_lib import license as lic

        key = lic.generate_key("reader@example.com", plan="PRO")
        self.assertTrue(key.startswith("INKP-"))
        self.assertEqual(len(key.split("-")), 5)

        # Lowercase + confusable O/I normalization works offline
        info = lic.verify_key(key.lower())
        self.assertTrue(info["valid"])
        self.assertEqual(info["plan"], "PRO")

        # Tampering with a character invalidates the HMAC signature
        last_ch = "A" if key[-1] != "A" else "B"
        tampered = key[:-1] + last_ch
        self.assertIsNone(lic.verify_key(tampered))
        self.assertIsNone(lic.verify_key("FAKE-1234-5678-9ABC-DEFG"))

        with tempfile.TemporaryDirectory() as directory:
            lic_file = Path(directory) / "license.json"
            self.assertIsNone(lic.load_saved_license(lic_file))
            lic.save_license(key, email="reader@example.com", license_path=lic_file)
            reloaded = lic.load_saved_license(lic_file)
            self.assertTrue(reloaded["valid"])
            self.assertEqual(reloaded["email"], "reader@example.com")
            lic.clear_license(lic_file)
            self.assertIsNone(lic.load_saved_license(lic_file))

    def test_studio_app_free_vs_pro_gating_and_project_save(self):
        import tkinter as tk
        import inkpress_app
        from inkpress_lib import license as lic

        with tempfile.TemporaryDirectory() as directory:
            tmp = Path(directory)
            lic_file = tmp / "test_license.json"
            src = write_temp(MINIMAL, tmp)

            root = tk.Tk()
            root.withdraw()
            try:
                inkpress_app._configure_studio_theme(root)
                app = inkpress_app.InkpressApp(
                    root, initial_manuscript=src, license_path=lic_file
                )
                self.assertFalse(app.is_pro_unlocked())
                self.assertEqual(
                    app._pro_features_requested("clean", "none", "edition", False, False),
                    [],
                )
                pro_reasons = app._pro_features_requested(
                    "illustrated", "double", "garamond", True, True
                )
                self.assertEqual(len(pro_reasons), 5)

                # Save project sidecar via UI and reload
                app.meta_vars["isbn"].set("978-1-999999-77-7")
                app.meta_vars["about_author"].set("J.S. Warden writes by lantern light.")
                sidecar = app._save_project()
                self.assertTrue(sidecar and sidecar.is_file())

                app.meta_vars["isbn"].set("")
                app._load_manuscript()
                self.assertEqual(app.meta_vars["isbn"].get(), "978-1-999999-77-7")

                # Activate Studio Pro key and confirm unlocked state
                pro_key = lic.generate_key("buyer@example.com", plan="PRO")
                app.license_info = lic.save_license(pro_key, license_path=lic_file)
                app._refresh_license_badge()
                self.assertTrue(app.is_pro_unlocked())
                self.assertIn("STUDIO PRO", app.license_badge_btn.cget("text"))
            finally:
                root.destroy()


class TestStandaloneBundleRelease(unittest.TestCase):
    def test_lightweight_bundle_creates_portable_exe_installer_and_zip(self):
        import bundle_release

        with tempfile.TemporaryDirectory() as directory:
            bundle_dir, zip_path = bundle_release.build_bundle(
                out_root=directory,
                include_runtime=False,
                create_zip=True,
            )
            self.assertTrue((bundle_dir / "inkpress.exe").is_file())
            self.assertEqual((bundle_dir / "inkpress.exe").read_bytes()[:2], b"MZ")
            self.assertTrue((bundle_dir / "inkpress_app.py").is_file())
            self.assertTrue((bundle_dir / "inkpress_lib" / "pipeline.py").is_file())
            self.assertTrue((bundle_dir / "README.txt").is_file())
            self.assertTrue((bundle_dir / "installer" / "inkpress-setup.iss").is_file())
            self.assertTrue(zip_path and zip_path.is_file())


if __name__ == "__main__":
    unittest.main()
