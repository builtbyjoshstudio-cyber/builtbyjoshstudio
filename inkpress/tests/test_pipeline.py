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

    def test_single_quotes_are_directional(self):
        self.assertEqual(typography.apply("he said 'go' then"), "he said ‘go’ then")

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


if __name__ == "__main__":
    unittest.main()
