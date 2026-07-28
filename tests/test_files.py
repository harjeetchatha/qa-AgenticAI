"""Tests for file loading and output writing."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from ai_qe_studio.errors import EmptyFileError, MissingFileError, OutputExistsError
from ai_qe_studio.files import read_required_text, write_output
from ai_qe_studio.paths import project_root, story_paths

TEST_TMP_ROOT = project_root() / "tests" / "tmp"


class ReadRequiredTextTests(unittest.TestCase):
    def setUp(self) -> None:
        TEST_TMP_ROOT.mkdir(parents=True, exist_ok=True)

    def test_reads_non_empty_file(self) -> None:
        with tempfile.TemporaryDirectory(dir=TEST_TMP_ROOT) as tmpdir:
            path = Path(tmpdir) / "sample.md"
            path.write_text("Requirement content", encoding="utf-8")

            content = read_required_text(path)

        self.assertEqual(content, "Requirement content")

    def test_raises_for_missing_file(self) -> None:
        with tempfile.TemporaryDirectory(dir=TEST_TMP_ROOT) as tmpdir:
            path = Path(tmpdir) / "missing.md"

            with self.assertRaises(MissingFileError) as ctx:
                read_required_text(path)

        self.assertIn("missing.md", str(ctx.exception))

    def test_raises_for_empty_file(self) -> None:
        with tempfile.TemporaryDirectory(dir=TEST_TMP_ROOT) as tmpdir:
            path = Path(tmpdir) / "empty.md"
            path.write_text("   \n\t  ", encoding="utf-8")

            with self.assertRaises(EmptyFileError) as ctx:
                read_required_text(path)

        self.assertIn("empty.md", str(ctx.exception))


class WriteOutputTests(unittest.TestCase):
    def setUp(self) -> None:
        TEST_TMP_ROOT.mkdir(parents=True, exist_ok=True)

    def test_writes_new_file(self) -> None:
        with tempfile.TemporaryDirectory(dir=TEST_TMP_ROOT) as tmpdir:
            path = Path(tmpdir) / "generated" / "story" / "output.md"

            write_output(path, "analysis output", overwrite=False)

            self.assertEqual(path.read_text(encoding="utf-8"), "analysis output")

    def test_refuses_overwrite_without_flag(self) -> None:
        with tempfile.TemporaryDirectory(dir=TEST_TMP_ROOT) as tmpdir:
            path = Path(tmpdir) / "output.md"
            path.write_text("existing", encoding="utf-8")

            with self.assertRaises(OutputExistsError) as ctx:
                write_output(path, "new content", overwrite=False)

            self.assertIn("output.md", str(ctx.exception))
            self.assertEqual(path.read_text(encoding="utf-8"), "existing")

    def test_allows_overwrite_when_requested(self) -> None:
        with tempfile.TemporaryDirectory(dir=TEST_TMP_ROOT) as tmpdir:
            path = Path(tmpdir) / "output.md"
            path.write_text("existing", encoding="utf-8")

            write_output(path, "replacement", overwrite=True)

            self.assertEqual(path.read_text(encoding="utf-8"), "replacement")


class StoryPathsTests(unittest.TestCase):
    def test_builds_expected_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            paths = story_paths("duplicate-customer-story", root=root)

        self.assertEqual(
            paths.requirement_path,
            root / "knowledge/requirements/duplicate-customer-story.md",
        )
        self.assertEqual(
            paths.output_path,
            root / "generated/duplicate-customer-story/requirement-analysis.md",
        )
        self.assertEqual(
            paths.requirement_source,
            "knowledge/requirements/duplicate-customer-story.md",
        )
        self.assertIn("business-rules.md", paths.knowledge_paths)


if __name__ == "__main__":
    unittest.main()
