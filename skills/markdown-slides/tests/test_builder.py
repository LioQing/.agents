"""Behavioral regression tests using isolated temporary decks."""

import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "slide_builder.py"
spec = importlib.util.spec_from_file_location("slide_builder", SCRIPT)
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class ParsingTests(unittest.TestCase):
    def test_basic_and_opening_boundary(self):
        slides = builder.parse_slides("---\n# One\n---\n# Two\n---\n")
        self.assertEqual([slide["title"] for slide in slides], ["One", "Two"])

    def test_no_blank_lines_needed(self):
        slides = builder.parse_slides("Title\n---\ninstruction: Use supplied text.\n# Second\n")
        self.assertEqual(len(slides), 2)
        self.assertIn("Title", slides[0]["markup"])
        self.assertEqual(slides[1]["instruction"], "Use supplied text.")

    def test_separator_contexts(self):
        text = "# One\n\n```md\n---\ninstruction: Literal\n```\n\n    ---\n\n> ---\n\n- List\n  ---\n\n<div>\n---\n</div>\n\n***\n\n---\n# Two\n"
        slides = builder.parse_slides(text)
        self.assertEqual(len(slides), 2)
        self.assertIn("instruction: Literal", slides[0]["markup"])

    def test_multiline_instruction(self):
        text = "\n\ninstruction: |\n  Design a diagram.\n  ---\n\n  Keep supplied values.\n\n# One\n---\n# Two"
        slides = builder.parse_slides(text)
        self.assertEqual(len(slides), 2)
        self.assertEqual(slides[0]["instruction"], "Design a diagram.\n---\n\nKeep supplied values.")
        self.assertNotIn("Design a diagram", slides[0]["markup"])
        self.assertIn("# One", slides[0]["markdown"])

    def test_original_crlf(self):
        slides = builder.parse_slides("instruction: hello\r\n# One\r\n---\r\n# Two\r\n")
        self.assertEqual(slides[0]["annotation"], "instruction: hello\r\n")
        self.assertEqual(slides[0]["markdown"], "# One\r\n")

    def test_empty_interior(self):
        with self.assertRaises(builder.BuildError):
            builder.parse_slides("# One\n---\n\n---\n# Two")

    def test_annotation_not_in_later_content(self):
        slide = builder.parse_slides("# One\n\ninstruction: literal content\n")[0]
        self.assertEqual(slide["instruction"], "")
        self.assertIn("instruction: literal content", slide["markup"])

    def test_all_supported_admonitions(self):
        text = "# Alerts\n\n" + "\n\n".join(f"> [!{kind}]\n> **Bold** text.\n>\n> - Nested item" for kind in ("NOTE", "INFO", "TIP", "IMPORTANT", "WARNING", "CAUTION"))
        slide = builder.parse_slides(text)[0]
        soup = builder.BeautifulSoup(slide["markup"], "html.parser")
        self.assertEqual(len(soup.select('aside[role="note"]')), 6)
        self.assertEqual(len(soup.select(".admonition-body strong")), 6)
        self.assertEqual(len(soup.select(".admonition-body li")), 6)
        self.assertEqual(soup.select_one(".admonition-info > .admonition-title").get_text(), "Info")

    def test_info_nesting_case_and_literal_code(self):
        slide = builder.parse_slides("# Info\n\n> [!NOTE]\n> Outer\n>\n> > [!INFO]\n> > First line.\n> > Second line.\n\n> [!info]\n> Ordinary quote.\n\n```markdown\n> [!INFO]\n```\n")[0]
        soup = builder.BeautifulSoup(slide["markup"], "html.parser")
        info = soup.select_one(".admonition-note .admonition-info")
        self.assertEqual(info["role"], "note")
        self.assertIn("First line.\nSecond line.", info.select_one(".admonition-body").get_text())
        self.assertEqual(len(soup.select("aside")), 2)
        self.assertIn("[!info]", soup.blockquote.get_text())
        self.assertIn("[!INFO]", soup.code.get_text())

    def test_nested_and_unknown_admonition(self):
        slide = builder.parse_slides("# One\n\n> [!NOTE]\n> Outer\n>\n> > [!TIP]\n> > Inner\n\n> [!CUSTOM]\n> ordinary\n\n```\n> [!WARNING]\n```\n")[0]
        soup = builder.BeautifulSoup(slide["markup"], "html.parser")
        self.assertIsNotNone(soup.select_one(".admonition-note .admonition-tip"))
        self.assertEqual(len(soup.select("aside")), 2)
        self.assertIn("[!CUSTOM]", soup.blockquote.get_text())
        self.assertIn("[!WARNING]", soup.code.get_text())

    def test_rich_markdown_and_sanitization(self):
        slide = builder.parse_slides('# One\n\n| A | B |\n|---|---|\n| 1 | 2 |\n\n- [x] Task\n\n~~gone~~\n\n<script>alert(1)</script>\n\n<img src="x.png" onerror="evil()">\n')[0]
        soup = builder.BeautifulSoup(slide["markup"], "html.parser")
        self.assertTrue(soup.select_one(".table-scroll th[scope=col]"))
        self.assertTrue(soup.select_one("input[disabled][checked]"))
        self.assertTrue(soup.s)
        self.assertIsNone(soup.script)
        self.assertFalse(soup.img.has_attr("onerror"))

    def test_safe_source_json(self):
        raw = '# Source\n\n```html\n</script><script>window.evil=true</script>\n```\n'
        parsed = builder.parse_slides(raw)[0]
        parsed.update({"id": "s-test", "bundle": {"markup": parsed["markup"], "css": "", "script": "\n"}})
        document = builder.render_document([parsed], "", "Deck")
        soup = builder.BeautifulSoup(document, "html.parser")
        self.assertEqual(json.loads(soup.find(id="deck-source").get_text())[0]["raw"], raw)
        self.assertNotIn("<script>window.evil=true", document)

    def test_table_alignment_and_literal_annotation(self):
        slide = builder.parse_slides("instruction\\: literal text\n\n| Left | Right | Center |\n| :--- | ---: | :---: |\n| a | 1 | c |\n")[0]
        soup = builder.BeautifulSoup(slide["markup"], "html.parser")
        self.assertEqual(slide["instruction"], "")
        self.assertIn("instruction: literal text", soup.get_text())
        self.assertEqual([cell["align"] for cell in soup.find_all("th")], ["left", "right", "center"])

    def test_literal_css_slot_markers_in_source_are_not_edit_slots(self):
        raw = "# Source\n\n```css\n/* slides:s-test:css:start */\n/* slides:s-test:css:end */\n```\n"
        parsed = builder.parse_slides(raw)[0]
        parsed.update({"id": "s-test", "bundle": {"markup": parsed["markup"], "css": "", "script": "\n"}})
        document = builder.render_document([parsed], "", "Deck")
        bundles, _ = builder.extract_slots(document, ["s-test"])
        self.assertEqual(bundles["s-test"]["css"], "")
        self.assertIn("slides:s-test:css:start", bundles["s-test"]["markup"])


class DeckTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.source = self.base / "source.md"
        self.output = self.base / "deck.html"
        builder.atomic_write(self.source, "# One\n\nText.\n---\ninstruction: Improve the layout.\n# Two\n\nMore.\n")

    def tearDown(self):
        self.temp.cleanup()

    def args(self, **values):
        defaults = dict(input=str(self.source), output=str(self.output), design=None, title=None, dry_run=False, map=[], drop=[], resolve=[], replace_existing=False, discard_edits=False)
        defaults.update(values)
        return type("Args", (), defaults)()

    def call(self, function, args):
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            status = function(args)
        return status, json.loads(stream.getvalue())

    def build(self, **values):
        return self.call(builder.build, self.args(**values))

    def state(self):
        return builder.load_state(self.output)

    def edit(self, number=1, kind="markup", value="<h1>Customized</h1>"):
        state = self.state()
        identifier = state["slides"][number - 1]["id"]
        document = builder.read_text(self.output)
        start, end = builder.slot_markers(identifier, kind)
        left, tail = document.split(start, 1)
        _, right = tail.split(end, 1)
        builder.atomic_write(self.output, left + start + value + end + right)
        return identifier

    def authorize(self, mode="design", slides="1"):
        return self.call(builder.authorize, self.args(mode=mode, slides=slides))

    def capture(self, complete="1"):
        return self.call(builder.capture, self.args(complete=complete))

    def test_baseline_work_queue_and_validation(self):
        self.assertEqual(self.build()[0], 0)
        self.assertEqual([record["status"] for record in self.state()["slides"]], ["needs-permission", "needs-agent"])
        status, result = self.call(builder.validate, self.args())
        self.assertEqual(status, 0)
        self.assertFalse(result["errors"])

    def test_bottom_bar_and_overview_close(self):
        self.assertEqual(self.build()[0], 0)
        soup = builder.BeautifulSoup(builder.read_text(self.output), "html.parser")
        controls = soup.select_one("body > footer#control-bar")
        self.assertIsNotNone(controls)
        self.assertEqual(len(controls.select("button")), 7)
        self.assertIsNotNone(controls.select_one("#navigation #previous-slide"))
        self.assertIsNotNone(controls.select_one("#utilities #overview-toggle"))
        self.assertIsNone(soup.select_one("#deck #control-bar"))
        self.assertIsNotNone(soup.select_one("body > main#stage + aside#overview"))
        self.assertIsNone(soup.select_one("#stage #overview"))
        close = soup.select_one("#overview #overview-header #overview-close")
        self.assertEqual(close["type"], "button")
        self.assertEqual(close["aria-label"], "Close slide overview")

    def test_round_trip_and_reorder(self):
        self.build()
        self.authorize()
        identifier = self.edit()
        self.capture()
        self.assertEqual(self.build()[0], 0)
        self.assertIn("Customized", builder.read_text(self.output))
        source = builder.read_text(self.source)
        first, second = source.split("---\n")
        builder.atomic_write(self.source, second + "---\n" + first)
        self.assertEqual(self.build()[0], 0)
        self.assertEqual(self.state()["slides"][1]["id"], identifier)
        self.assertIn("Customized", self.state()["slides"][1]["bundle"]["markup"])

    def test_permissions_required(self):
        self.build()
        self.edit()
        with self.assertRaises(builder.BuildError):
            self.capture()
        self.assertEqual(self.state()["slides"][0]["status"], "needs-permission")

    def test_preserve_forbids_edits(self):
        self.build()
        self.authorize(mode="preserve")
        self.edit()
        with self.assertRaises(builder.BuildError):
            self.capture()

    def test_unrecorded_changes_block_rebuild(self):
        self.build()
        self.authorize()
        self.edit()
        previous = self.output.read_bytes()
        status, result = self.build()
        self.assertEqual(status, 2)
        self.assertEqual(result["conflicts"][0]["type"], "uncaptured-edits")
        self.assertEqual(self.output.read_bytes(), previous)

    def test_changed_source_requires_explicit_identity_and_review(self):
        self.build()
        self.authorize()
        identifier = self.edit()
        self.capture()
        builder.atomic_write(self.source, builder.read_text(self.source).replace("Text.", "Changed text."))
        status, result = self.build()
        self.assertEqual(status, 2)
        self.assertIn("unmatched-prior-slide", [item["type"] for item in result["conflicts"]])
        self.assertEqual(self.build(map=[f"1={identifier}"])[0], 2)
        self.assertEqual(self.build(map=[f"1={identifier}"], resolve=[f"{identifier}=adapt"])[0], 0)
        record = self.state()["slides"][0]
        self.assertEqual(record["id"], identifier)
        self.assertIsNone(record["permission"])
        self.assertIn("Customized", record["previous"]["bundle"]["markup"])
        self.assertIn("Changed text", record["bundle"]["markup"])

    def test_duplicate_changed_deck_is_ambiguous(self):
        builder.atomic_write(self.source, "# Same\n---\n# Same\n")
        self.build()
        self.assertEqual(self.build()[0], 0)
        builder.atomic_write(self.source, "# Same\n---\n# Same\n---\n# New\n")
        self.assertEqual(self.build()[0], 2)

    def test_design_replacement_requires_review_then_changes_css(self):
        self.build()
        design = self.base / "DESIGN.md"
        original = builder.read_text(builder.ROOT / "DESIGN.md")
        design.write_text(original.replace("#ffffff", "#fffdf8"), encoding="utf-8")
        status, result = self.build(design=str(design))
        self.assertEqual(status, 2)
        self.assertEqual(len(result["conflicts"]), 2)
        choices = [f"{record['id']}=regenerate" for record in self.state()["slides"]]
        self.assertEqual(self.build(design=str(design), resolve=choices)[0], 0)
        self.assertIn("#fffdf8", builder.read_text(self.output))

    def test_relative_asset_rebase_and_changes(self):
        image = self.base / "pixel.png"
        image.write_bytes(b"first")
        builder.atomic_write(self.source, "# Image\n\n![Pixel](pixel.png)\n")
        self.output = self.base / "out" / "deck.html"
        self.build()
        self.assertIn('src="../pixel.png"', builder.read_text(self.output))
        image.write_bytes(b"second")
        status, result = self.build()
        self.assertEqual(status, 2)
        self.assertEqual(result["conflicts"][0]["type"], "changed-slide")

    def test_custom_css_asset_change_is_detected(self):
        image = self.base / "custom.png"
        image.write_bytes(b"asset one")
        self.build()
        self.authorize()
        identifier = self.state()["slides"][0]["id"]
        self.edit(kind="css", value=f'#{identifier} .art {{ background-image: url("custom.png"); }}')
        self.assertEqual(self.capture()[0], 0)
        self.assertEqual(len(self.state()["slides"][0]["custom_assets"]), 1)
        image.write_bytes(b"asset two")
        status, result = self.build()
        self.assertEqual(status, 2)
        self.assertEqual(result["conflicts"][0]["type"], "changed-slide")

    def test_heading_links_are_namespaced_and_cross_slide(self):
        builder.atomic_write(self.source, "# One\n\n[Jump](#two)\n---\n# Two\n\n[Local](#two)\n\n## Two\n")
        self.assertEqual(self.build()[0], 0)
        state = self.state()
        identifier = state["slides"][1]["id"]
        target = identifier + "-two"
        soup = builder.BeautifulSoup(builder.read_text(self.output), "html.parser")
        self.assertEqual(soup.select_one("#" + state["slides"][0]["id"] + " a")["href"], "#" + target)
        self.assertTrue(soup.find(id=target))
        self.assertTrue(soup.find(id=identifier + "-two-1"))
        self.assertEqual(self.call(builder.validate, self.args())[0], 0)

    def test_missing_asset_build_warns_final_validation_errors(self):
        builder.atomic_write(self.source, "# Image\n\n![Missing](absent.png)\n")
        self.assertEqual(self.build()[0], 0)
        status, result = self.call(builder.validate, self.args())
        self.assertEqual(status, 2)
        self.assertIn("missing local asset", result["errors"][0])

    def test_crlf_file_stays_unchanged(self):
        original = b"instruction: Layout only.\r\n# One\r\n---\r\n# Two\r\n"
        self.source.write_bytes(original)
        self.build()
        self.assertEqual(self.source.read_bytes(), original)
        self.assertEqual(self.state()["slides"][0]["annotation"], "instruction: Layout only.\r\n")

    def test_deleted_slide_requires_drop_and_is_archived(self):
        self.build()
        removed = self.state()["slides"][1]["id"]
        builder.atomic_write(self.source, builder.read_text(self.source).split("---\n")[0])
        self.assertEqual(self.build()[0], 2)
        self.assertEqual(self.build(drop=[removed])[0], 0)
        self.assertEqual(len(self.state()["slides"]), 1)
        self.assertTrue(any(item["slide"]["id"] == removed for item in self.state()["history"]))

    def test_protected_change_rejected(self):
        self.build()
        document = builder.read_text(self.output).replace("Previous</button>", "Changed</button>")
        builder.atomic_write(self.output, document)
        self.assertEqual(self.capture()[0], 2)

    def test_scoped_css_and_script_capture(self):
        self.build()
        self.authorize()
        identifier = self.state()["slides"][0]["id"]
        self.edit(kind="css", value=f"\n#{identifier} .item {{ color: var(--ink); }}\n")
        self.edit(kind="script", value="return { enter() { api.announce('Ready'); } };\n")
        self.assertEqual(self.capture()[0], 0)
        self.assertEqual(self.build()[0], 0)
        self.assertIn("api.announce('Ready')", builder.read_text(self.output))

    def test_global_css_rejected(self):
        self.build()
        self.authorize()
        self.edit(kind="css", value="body { color: red; }")
        self.assertEqual(self.capture()[0], 2)

    def test_sibling_css_escape_rejected(self):
        self.build()
        self.authorize()
        identifier = self.state()["slides"][0]["id"]
        for selector in (f"#{identifier}  + #utilities", f"#{identifier}.slide ~ #utilities"):
            self.edit(kind="css", value=selector + " { display: none; }")
            self.assertEqual(self.capture()[0], 2)

    def test_markup_breakout_rejected(self):
        self.build()
        self.authorize()
        self.edit(value="</div><div>Escaped container</div><div>")
        self.assertEqual(self.capture()[0], 2)

    def test_backups_before_explicit_discard(self):
        self.build()
        self.authorize()
        self.edit()
        previous = builder.read_text(self.output)
        status, result = self.build(discard_edits=True)
        self.assertEqual(status, 0)
        self.assertEqual(builder.read_text(result["backup"]), previous)

    def test_untracked_output_not_overwritten(self):
        self.output.write_text("User work", encoding="utf-8")
        self.assertEqual(self.build()[0], 2)
        self.assertEqual(builder.read_text(self.output), "User work")
        status, result = self.build(replace_existing=True)
        self.assertEqual(status, 0)
        self.assertEqual(builder.read_text(result["backup"]), "User work")


if __name__ == "__main__":
    unittest.main()
