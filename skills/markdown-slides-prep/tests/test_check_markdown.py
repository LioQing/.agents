"""Check the prep helper against the actual renderer and reference examples."""

import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("prep_check", ROOT / "scripts" / "check_markdown.py")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class PreparationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp.name)
        self.source = self.directory / "draft.md"

    def tearDown(self):
        self.temp.cleanup()

    def write(self, text):
        self.source.write_bytes(text.encode("utf-8"))

    def test_source_unchanged_and_no_render_artifacts(self):
        text = "# First\r\n\r\nContent.\r\n---\r\ninstruction: |\r\n  Draw the supplied steps.\r\n\r\n# Flow\r\n\r\n1. Request.\r\n2. Approve.\r\n"
        self.write(text)
        result = checker.check_markdown(self.source)
        self.assertTrue(result["valid"])
        self.assertEqual(result["slide_count"], 2)
        self.assertEqual(result["slides"][1]["instruction"], "Draw the supplied steps.")
        self.assertEqual(self.source.read_bytes(), text.encode("utf-8"))
        self.assertEqual(list(self.directory.iterdir()), [self.source])

    def test_bad_syntax_reports_error_without_rewriting(self):
        text = "# One\n---\n\n---\n# Two\n"
        self.write(text)
        result = checker.check_markdown(self.source)
        self.assertFalse(result["valid"])
        self.assertIn("Empty slide", result["error"])
        self.assertEqual(self.source.read_bytes(), text.encode("utf-8"))

    def test_relative_image_warning(self):
        self.write("# Image\n\n![Diagram](missing.png)\n")
        result = checker.check_markdown(self.source)
        self.assertTrue(result["valid"])
        self.assertEqual(len(result["warnings"]), 1)
        (self.directory / "missing.png").write_bytes(b"local asset")
        self.assertFalse(checker.check_markdown(self.source)["warnings"])

    def test_absent_renderer_is_actionable(self):
        self.write("# One\n")
        result = checker.check_markdown(self.source, self.directory / "absent.py")
        self.assertFalse(result["valid"])
        self.assertIn("Install markdown-slides", result["error"])

    def test_code_annotations_stay_literal(self):
        self.write("# Example\n\n```markdown\n---\ninstruction: literal\n```\n---\n# Next\n")
        result = checker.check_markdown(self.source)
        self.assertEqual(result["slide_count"], 2)
        self.assertTrue(all(not slide["instruction"] for slide in result["slides"]))

    def test_instruction_only_slide_warns(self):
        self.write("instruction: Generate the requested title slide.\n")
        result = checker.check_markdown(self.source)
        self.assertTrue(result["valid"])
        self.assertFalse(result["slides"][0]["has_markdown_body"])
        self.assertIn("intentionally deferred", result["warnings"][0])

    def test_authoring_examples_match_the_installed_parser(self):
        text = (ROOT / "references" / "authoring-examples.md").read_text(encoding="utf-8")
        examples = []
        marker, lines = None, []
        for line in text.splitlines(keepends=True):
            if marker is None and line.strip() in {"```markdown", "````markdown"}:
                marker = line.strip().removesuffix("markdown")
                lines = []
            elif marker is not None and line.strip() == marker:
                examples.append("".join(lines))
                marker = None
            elif marker is not None:
                lines.append(line)
        self.assertEqual(len(examples), 3)
        expected_counts = [3, 1, 2]
        expected_annotations = [1, 1, 0]
        for text, count, annotations in zip(examples, expected_counts, expected_annotations):
            self.write(text)
            result = checker.check_markdown(self.source)
            self.assertTrue(result["valid"], result)
            self.assertEqual(result["slide_count"], count)
            self.assertEqual(sum(bool(slide["instruction"]) for slide in result["slides"]), annotations)


if __name__ == "__main__":
    unittest.main()
