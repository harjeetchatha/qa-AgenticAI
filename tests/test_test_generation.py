"""Tests for Test Generation stage and handoff validation."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock

from ai_qe_studio.config import AnthropicConfig, TestGenerationConfig
from ai_qe_studio.errors import EmptyFileError, MissingFileError, OrchestratorError, OutputExistsError
from ai_qe_studio.files import ensure_output_writable
from ai_qe_studio.handoff import (
    parse_handoff,
    resolve_requirement_id,
    validate_handoff_for_test_generation,
)
from ai_qe_studio.paths import project_root, test_generation_paths
from ai_qe_studio.prompts import build_test_generation_user_prompt
from ai_qe_studio.stages.test_generation import run_test_generation
from tests.test_suite_validation import build_valid_poc_suite

TEST_TMP_ROOT = project_root() / "tests" / "tmp"

VALID_HANDOFF = """
handoff:
  schema_version: "1.1"
  requirement_id: "US-042"
  ready_for_test_generation: true
  blocker_reason: null
  open_questions:
    - id: "Q-1"
      question: "Example question?"
      blocking_for_specific_tests: true
      blocking_for_entire_suite: false
      affected_acceptance_criteria: ["AC-1"]
      affected_test_areas: ["Positive"]
"""

BLOCKED_HANDOFF = """
handoff:
  requirement_id: "US-042"
  ready_for_test_generation: false
  blocker_reason: "No testable acceptance criteria."
  open_questions: []
"""

DEPRECATED_HANDOFF = """
handoff:
  requirement_id: "US-042"
  ready_for_test_generation: true
  blocker_reason: null
  open_questions:
    - id: "Q-1"
      question: "Legacy question?"
      blocking: true
      affects_ready: false
      affected_acceptance_criteria: ["AC-1"]
      affected_test_areas: ["Positive"]
"""


def _write_story_root(root: Path, *, handoff_yaml: str = VALID_HANDOFF) -> None:
    requirement = root / "knowledge/requirements/duplicate-customer-story.md"
    requirement.parent.mkdir(parents=True, exist_ok=True)
    requirement.write_text(
        "# Duplicate Customer Story\n\nAcceptance criteria here.\n",
        encoding="utf-8",
    )

    pack_dir = root / "knowledge/customer-management-pack"
    for filename in (
        "application-context.md",
        "business-rules.md",
        "data-model.md",
        "glossary.md",
        "known-limitations.md",
    ):
        pack_dir.mkdir(parents=True, exist_ok=True)
        (pack_dir / filename).write_text(f"# {filename}\n", encoding="utf-8")

    agents_dir = root / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)
    (agents_dir / "test-generation-agent.md").write_text(
        "# Test Generation Agent\n",
        encoding="utf-8",
    )

    generated_dir = root / "generated/duplicate-customer-story"
    generated_dir.mkdir(parents=True, exist_ok=True)
    (generated_dir / "requirement-analysis.md").write_text(
        "# Requirement Analysis\n\n"
        "## Handoff Package\n\n"
        f"```yaml\n{handoff_yaml.strip()}\n```\n",
        encoding="utf-8",
    )


class HandoffValidationTests(unittest.TestCase):
    def test_parse_and_validate_ready_handoff(self) -> None:
        analysis = f"# Analysis\n\n## Handoff Package\n\n```yaml\n{VALID_HANDOFF}\n```\n"
        handoff = parse_handoff(analysis)
        validate_handoff_for_test_generation(handoff)
        self.assertEqual(handoff["requirement_id"], "US-042")

    def test_ready_false_raises(self) -> None:
        analysis = (
            f"# Analysis\n\n## Handoff Package\n\n```yaml\n{BLOCKED_HANDOFF}\n```\n"
        )
        handoff = parse_handoff(analysis)
        with self.assertRaises(OrchestratorError) as ctx:
            validate_handoff_for_test_generation(handoff)
        self.assertIn("BLOCKED: Test generation cannot proceed", str(ctx.exception))

    def test_deprecated_fields_supported(self) -> None:
        analysis = (
            "# Analysis\n\n## Handoff Package\n\n"
            f"```yaml\n{DEPRECATED_HANDOFF}\n```\n"
        )
        handoff = parse_handoff(analysis)
        validate_handoff_for_test_generation(handoff)

    def test_requirement_id_mismatch_raises(self) -> None:
        handoff = {"requirement_id": "US-042"}
        with self.assertRaises(OrchestratorError) as ctx:
            resolve_requirement_id(handoff, "OTHER-ID")
        self.assertIn("does not match handoff requirement_id", str(ctx.exception))

    def test_requirement_id_from_handoff_when_omitted(self) -> None:
        handoff = {"requirement_id": "US-042"}
        self.assertEqual(resolve_requirement_id(handoff, None), "US-042")


class TestGenerationStageTests(unittest.TestCase):
    def setUp(self) -> None:
        TEST_TMP_ROOT.mkdir(parents=True, exist_ok=True)
        self.config = AnthropicConfig(
            api_key="test-key",
            model="claude-sonnet-5",
            max_tokens=16384,
            timeout_seconds=600.0,
        )
        self.generation_config = TestGenerationConfig(max_tests=10)

    def test_missing_analysis_file_raises(self) -> None:
        with tempfile.TemporaryDirectory(dir=TEST_TMP_ROOT) as tmpdir:
            root = Path(tmpdir)
            _write_story_root(root)
            paths = test_generation_paths("duplicate-customer-story", root=root)
            paths.analysis_path.unlink()

            with self.assertRaises(MissingFileError):
                run_test_generation(
                    "duplicate-customer-story",
                    config=self.config,
                    generation_config=self.generation_config,
                    root=root,
                )

    def test_empty_analysis_file_raises(self) -> None:
        with tempfile.TemporaryDirectory(dir=TEST_TMP_ROOT) as tmpdir:
            root = Path(tmpdir)
            _write_story_root(root)
            paths = test_generation_paths("duplicate-customer-story", root=root)
            paths.analysis_path.write_text("   \n", encoding="utf-8")

            with self.assertRaises(EmptyFileError):
                run_test_generation(
                    "duplicate-customer-story",
                    config=self.config,
                    generation_config=self.generation_config,
                    root=root,
                )

    def test_ready_false_handoff_raises(self) -> None:
        with tempfile.TemporaryDirectory(dir=TEST_TMP_ROOT) as tmpdir:
            root = Path(tmpdir)
            _write_story_root(root, handoff_yaml=BLOCKED_HANDOFF)

            with self.assertRaises(OrchestratorError) as ctx:
                run_test_generation(
                    "duplicate-customer-story",
                    config=self.config,
                    generation_config=self.generation_config,
                    root=root,
                )
            self.assertIn("BLOCKED: Test generation cannot proceed", str(ctx.exception))

    def test_overwrite_protection_before_api_call(self) -> None:
        with tempfile.TemporaryDirectory(dir=TEST_TMP_ROOT) as tmpdir:
            root = Path(tmpdir)
            _write_story_root(root)
            paths = test_generation_paths("duplicate-customer-story", root=root)
            paths.output_path.write_text("existing suite", encoding="utf-8")

            create_message_fn = MagicMock(return_value=build_valid_poc_suite())

            with self.assertRaises(OutputExistsError):
                run_test_generation(
                    "duplicate-customer-story",
                    config=self.config,
                    generation_config=self.generation_config,
                    root=root,
                    create_message_fn=create_message_fn,
                )

            create_message_fn.assert_not_called()

    def test_prompt_contains_max_test_count(self) -> None:
        with tempfile.TemporaryDirectory(dir=TEST_TMP_ROOT) as tmpdir:
            root = Path(tmpdir)
            _write_story_root(root)
            paths = test_generation_paths("duplicate-customer-story", root=root)

            prompt = build_test_generation_user_prompt(
                paths=paths,
                requirement_text="Requirement text",
                requirement_id="US-042",
                analysis_text="Analysis text",
                knowledge_contents={"business-rules.md": "rules"},
                max_tests=10,
            )

            self.assertIn("no more than 10", prompt)
            self.assertIn("POC Run Constraints", prompt)
            self.assertIn("READY", prompt)
            self.assertIn("CONSTRAINED", prompt)
            self.assertIn("BLOCKED", prompt)
            self.assertIn("deferred_coverage", prompt)
            self.assertIn("Required Response Ending", prompt)
            self.assertIn("Your response is **invalid**", prompt)
            self.assertIn("POC Output Compactness", prompt)
            self.assertIn("Do **not** repeat the complete Requirement Analysis", prompt)
            self.assertIn("Validation Handoff Consistency (Strict)", prompt)
            self.assertIn("Partial Open Question Routing", prompt)
            self.assertIn("Dismissal Workflow READY Pattern", prompt)
            self.assertIn("Final Self-Check Before Validation Handoff", prompt)
            self.assertIn("source of truth", prompt)

    def test_successful_generation_mocked(self) -> None:
        with tempfile.TemporaryDirectory(dir=TEST_TMP_ROOT) as tmpdir:
            root = Path(tmpdir)
            _write_story_root(root)
            valid_suite = build_valid_poc_suite()

            create_client_fn = MagicMock(return_value=MagicMock())
            create_message_fn = MagicMock(return_value=valid_suite)

            result = run_test_generation(
                "duplicate-customer-story",
                cli_requirement_id="US-042",
                config=self.config,
                generation_config=self.generation_config,
                root=root,
                create_client_fn=create_client_fn,
                create_message_fn=create_message_fn,
            )

            self.assertEqual(result.requirement_id, "US-042")
            self.assertEqual(result.max_tests, 10)
            self.assertTrue(result.output_path.is_file())
            written = result.output_path.read_text(encoding="utf-8")
            self.assertEqual(written, valid_suite)
            self.assertIn("[CONSTRAINED]", written)
            self.assertIn("[BLOCKED]", written)
            create_client_fn.assert_called_once_with(self.config)
            create_message_fn.assert_called_once()

            _, kwargs = create_message_fn.call_args
            self.assertIn("no more than 10", kwargs["user"])

    def test_failed_validation_does_not_replace_existing_output(self) -> None:
        with tempfile.TemporaryDirectory(dir=TEST_TMP_ROOT) as tmpdir:
            root = Path(tmpdir)
            _write_story_root(root)
            paths = test_generation_paths("duplicate-customer-story", root=root)
            existing_content = "existing valid placeholder suite"
            paths.output_path.write_text(existing_content, encoding="utf-8")

            invalid_suite = build_valid_poc_suite(phantom_in_coverage="- AC-8: TC-099")
            create_message_fn = MagicMock(return_value=invalid_suite)

            with self.assertRaises(OrchestratorError) as ctx:
                run_test_generation(
                    "duplicate-customer-story",
                    config=self.config,
                    generation_config=self.generation_config,
                    root=root,
                    overwrite=True,
                    create_message_fn=create_message_fn,
                )

            self.assertIn("Phantom test IDs", str(ctx.exception))
            self.assertEqual(
                paths.output_path.read_text(encoding="utf-8"),
                existing_content,
            )

    def test_valid_response_is_written_successfully(self) -> None:
        with tempfile.TemporaryDirectory(dir=TEST_TMP_ROOT) as tmpdir:
            root = Path(tmpdir)
            _write_story_root(root)
            paths = test_generation_paths("duplicate-customer-story", root=root)
            valid_suite = build_valid_poc_suite(
                max_tests=7,
                ready_count=5,
                constrained_count=1,
                blocked_count=1,
            )
            create_message_fn = MagicMock(return_value=valid_suite)

            run_test_generation(
                "duplicate-customer-story",
                config=self.config,
                generation_config=TestGenerationConfig(max_tests=7),
                root=root,
                create_message_fn=create_message_fn,
            )

            self.assertEqual(paths.output_path.read_text(encoding="utf-8"), valid_suite)

    def test_config_override_respected_in_prompt(self) -> None:
        with tempfile.TemporaryDirectory(dir=TEST_TMP_ROOT) as tmpdir:
            root = Path(tmpdir)
            _write_story_root(root)

            create_message_fn = MagicMock(
                return_value=build_valid_poc_suite(
                    max_tests=5,
                    ready_count=3,
                    constrained_count=1,
                    blocked_count=1,
                )
            )

            run_test_generation(
                "duplicate-customer-story",
                config=self.config,
                generation_config=TestGenerationConfig(max_tests=5),
                root=root,
                create_message_fn=create_message_fn,
            )

            _, kwargs = create_message_fn.call_args
            self.assertIn("no more than 5", kwargs["user"])

    def test_ensure_output_writable_helper(self) -> None:
        with tempfile.TemporaryDirectory(dir=TEST_TMP_ROOT) as tmpdir:
            path = Path(tmpdir) / "generated-test-suite.md"
            path.write_text("existing", encoding="utf-8")

            with self.assertRaises(OutputExistsError):
                ensure_output_writable(path, overwrite=False)


if __name__ == "__main__":
    unittest.main()
