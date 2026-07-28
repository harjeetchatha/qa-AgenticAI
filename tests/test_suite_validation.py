"""Tests for POC test suite post-generation validation."""

from __future__ import annotations

import textwrap
import unittest

from ai_qe_studio.errors import OrchestratorError
from ai_qe_studio.suite_validation import (
    HandoffExtractionError,
    extract_validation_handoff_yaml,
    validate_poc_suite,
)


def _test_case(
    number: int,
    *,
    status: str = "READY",
    title: str | None = None,
) -> str:
    test_id = f"TC-{number:03d}"
    suffix = ""
    if status == "CONSTRAINED":
        suffix = " [CONSTRAINED]"
        expected = (
            "CONSTRAINED — The following assertions are verified:\n"
            "- Partial behaviour is observable.\n\n"
            "The following are excluded pending resolution of Q-3:\n"
            "- Field completeness cannot be asserted."
        )
        open_questions = "- Q-3: Comparison view field list unresolved."
    elif status == "BLOCKED":
        suffix = " [BLOCKED]"
        expected = (
            "BLOCKED — Expected result cannot be determined until "
            "open question Q-1 is resolved."
        )
        open_questions = "- Q-1: Duplicate Flag representation unresolved."
    else:
        expected = "1. The system behaves as expected."
        open_questions = "- None."

    display_title = title or f"Example Test {number}"
    return textwrap.dedent(
        f"""
        ## {test_id} — {display_title}{suffix}

        - **Requirement:** US-042 — Example behaviour
        - **Objective:** Verify example behaviour for {test_id}.
        - **Priority:** P2-High
        - **Test Type:** Positive
        - **Confidence:** [CERTAIN]
        - **Related Business Rules:** BR-011 — Automatic Duplicate Flagging
        - **Related Limitations:** None.
        - **Preconditions:**
          1. Acting user has Agent role.
        - **Test Data:**
          - `first_name`: `Example`

        ### Steps
        1. Perform the action.

        ### Expected Results
        {expected}

        ### Assumptions
        - [CERTAIN]: Grounded in BR-011.

        ### Open Questions
        {open_questions}

        ### Automation Candidate
        Yes — Deterministic scenario.
        """
    ).strip()


def _dismissal_ready_test(number: int = 6) -> str:
    """READY behavioral dismissal test with Q-6 persistence exclusion."""
    test_id = f"TC-{number:03d}"
    return textwrap.dedent(
        f"""
        ## {test_id} — Supervisor Dismisses Flag With Written Reason

        - **Requirement:** US-042 — Supervisor dismissal workflow
        - **Objective:** Verify dismissal is accepted, flag cleared, activation eligible.
        - **Priority:** P1-Critical
        - **Test Type:** Lifecycle
        - **Confidence:** [CERTAIN]
        - **Related Business Rules:** BR-014 — Duplicate Dismissal Requires Authorization
        - **Related Limitations:** None.
        - **Preconditions:**
          1. A Pending record with an open Duplicate Flag exists.
          2. The acting user has Supervisor role.
        - **Test Data:**
          - `dismissal_reason`: `Reviewed records — confirmed not a duplicate`

        ### Steps
        1. Log in as Supervisor.
        2. Dismiss the Duplicate Flag with the written reason.
        3. Attempt Pending to Active transition.

        ### Expected Results
        1. The dismissal is accepted.
        2. The Duplicate Flag is cleared.
        3. The Pending to Active transition is accepted when other prerequisites are met.

        ### Assumptions
        - [UNCERTAIN]: Storage location for the written reason is unresolved.

        ### Open Questions
        - Q-6: Dismissal reason persistence is excluded from Expected Results.

        ### Automation Candidate
        Yes — core behavioral flow.
        """
    ).strip()


def _build_handoff_yaml(
    *,
    max_tests: int,
    total: int,
    ready_count: int,
    constrained_count: int,
    blocked_count: int,
    statuses: list[str],
    include_deferred_coverage: bool = True,
    omit_schema_version: bool = False,
    malformed: bool = False,
) -> str:
    if malformed:
        return "schema_version: \"1.0\"\n  bad indent: true\n"

    lines = []
    if not omit_schema_version:
        lines.append('schema_version: "1.0"')
    lines.extend(
        [
            "poc_mode: true",
            f"max_test_count: {max_tests}",
            f"total_tests: {total}",
            f"ready_count: {ready_count}",
            f"constrained_count: {constrained_count}",
            f"blocked_count: {blocked_count}",
            "included_acceptance_criteria:",
            "  - AC-1",
            "  - AC-2",
        ]
    )
    if include_deferred_coverage:
        lines.extend(
            [
                "deferred_coverage:",
                "  - area: \"Boundary\"",
                "    reason: \"POC subset — full boundary matrix deferred\"",
            ]
        )
    lines.extend(
        [
            "open_questions_referenced:",
            "  - Q-1",
            "  - Q-3",
            "test_cases:",
        ]
    )
    for index, status in enumerate(statuses, start=1):
        lines.append(f"  - test_id: TC-{index:03d}")
        lines.append(f"    status: {status}")
    return "\n".join(lines) + "\n"


def build_valid_poc_suite(
    *,
    max_tests: int = 10,
    ready_count: int = 6,
    constrained_count: int = 2,
    blocked_count: int = 2,
    include_handoff: bool = True,
    phantom_in_coverage: str | None = None,
    omit_deferred_coverage: bool = False,
    wrong_handoff_counts: bool = False,
    incomplete_final_test: bool = False,
    fence_lang: str = "yaml",
    heading_suffix: str = "",
    line_ending: str = "\n",
    trailing_section: str | None = None,
    duplicate_handoff: bool = False,
    unclosed_fence: bool = False,
    handoff_malformed: bool = False,
    omit_required_key: str | None = None,
    yaml_statuses: list[str] | None = None,
) -> str:
    body_statuses: list[str] = (
        ["READY"] * ready_count
        + ["CONSTRAINED"] * constrained_count
        + ["BLOCKED"] * blocked_count
    )
    total = len(body_statuses)
    if total > max_tests:
        raise ValueError("status list exceeds max_tests")

    handoff_statuses = yaml_statuses or body_statuses
    if len(handoff_statuses) != total:
        raise ValueError("yaml_statuses length must match body status count")

    coverage_lines = []
    for index, status in enumerate(body_statuses, start=1):
        test_id = f"TC-{index:03d}"
        label = f" [{status}]" if status != "READY" else ""
        coverage_lines.append(f"- AC-1: {test_id}{label}")

    if phantom_in_coverage:
        coverage_lines.append(phantom_in_coverage)

    body_parts = [
        "# Test Suite — US-042",
        "## Coverage Plan (Internal Pre-Generation Plan)",
        "\n".join(coverage_lines),
    ]

    for index, status in enumerate(body_statuses, start=1):
        case = _test_case(index, status=status)
        if incomplete_final_test and index == total:
            case = case.split("### Open Questions", 1)[0].rstrip()
        body_parts.append(case)
        body_parts.append("---")

    if include_handoff:
        yaml_ready = sum(1 for status in handoff_statuses if status == "READY")
        yaml_constrained = sum(
            1 for status in handoff_statuses if status == "CONSTRAINED"
        )
        yaml_blocked = sum(1 for status in handoff_statuses if status == "BLOCKED")
        if wrong_handoff_counts:
            yaml_ready += 1

        handoff_yaml = _build_handoff_yaml(
            max_tests=max_tests,
            total=total,
            ready_count=yaml_ready,
            constrained_count=yaml_constrained,
            blocked_count=yaml_blocked,
            statuses=handoff_statuses,
            include_deferred_coverage=not omit_deferred_coverage,
            malformed=handoff_malformed,
        )
        if omit_required_key:
            handoff_yaml = "\n".join(
                line
                for line in handoff_yaml.splitlines()
                if not line.startswith(f"{omit_required_key}:")
            )

        fence_close = "" if unclosed_fence else f"{line_ending}```"
        handoff_block = (
            f"## Validation Handoff Package{heading_suffix}{line_ending}"
            f"{line_ending}```{fence_lang}{line_ending}"
            f"{handoff_yaml}{fence_close}"
        )
        body_parts.append(handoff_block)

        if duplicate_handoff:
            body_parts.append(handoff_block)

    if trailing_section:
        body_parts.append(trailing_section)

    return line_ending.join(part for part in body_parts if part != "")


class HandoffExtractionTests(unittest.TestCase):
    def test_exact_canonical_package_accepted(self) -> None:
        suite = build_valid_poc_suite()
        _, handoff = extract_validation_handoff_yaml(suite)
        self.assertTrue(handoff["poc_mode"])
        self.assertEqual(handoff["max_test_count"], 10)
        self.assertEqual(handoff["total_tests"], 10)

    def test_yml_fence_accepted(self) -> None:
        suite = build_valid_poc_suite(fence_lang="yml")
        _, handoff = extract_validation_handoff_yaml(suite)
        self.assertEqual(handoff["ready_count"], 6)

    def test_crlf_accepted(self) -> None:
        suite = build_valid_poc_suite(line_ending="\r\n")
        _, handoff = extract_validation_handoff_yaml(suite)
        self.assertEqual(handoff["blocked_count"], 2)

    def test_heading_with_trailing_whitespace_accepted(self) -> None:
        suite = build_valid_poc_suite(heading_suffix="   ")
        _, handoff = extract_validation_handoff_yaml(suite)
        self.assertIn("test_cases", handoff)

    def test_missing_package_rejected_with_diagnostics(self) -> None:
        suite = build_valid_poc_suite(include_handoff=False)
        with self.assertRaises(HandoffExtractionError) as ctx:
            extract_validation_handoff_yaml(suite)
        message = str(ctx.exception)
        self.assertIn("not found", message)
        diagnostics = ctx.exception.formatted_diagnostics()
        self.assertIn("exact heading present: False", diagnostics)
        self.assertIn("final 1000 characters", diagnostics)

    def test_unclosed_yaml_fence_rejected(self) -> None:
        suite = build_valid_poc_suite(unclosed_fence=True)
        with self.assertRaises(HandoffExtractionError) as ctx:
            extract_validation_handoff_yaml(suite)
        self.assertIn("not closed", str(ctx.exception))
        self.assertIn("yaml/yml fence closed: False", ctx.exception.formatted_diagnostics())

    def test_malformed_yaml_rejected(self) -> None:
        suite = build_valid_poc_suite(handoff_malformed=True)
        with self.assertRaises(HandoffExtractionError) as ctx:
            extract_validation_handoff_yaml(suite)
        self.assertIn("malformed", str(ctx.exception))

    def test_duplicate_packages_rejected(self) -> None:
        suite = build_valid_poc_suite(duplicate_handoff=True)
        with self.assertRaises(HandoffExtractionError) as ctx:
            extract_validation_handoff_yaml(suite)
        self.assertIn("found 2", str(ctx.exception))

    def test_package_not_final_section_rejected(self) -> None:
        suite = build_valid_poc_suite(trailing_section="## Extra Section")
        with self.assertRaises(HandoffExtractionError) as ctx:
            extract_validation_handoff_yaml(suite)
        self.assertIn("final section", str(ctx.exception))

    def test_missing_required_keys_rejected(self) -> None:
        suite = build_valid_poc_suite(omit_required_key="deferred_coverage")
        with self.assertRaises(OrchestratorError) as ctx:
            validate_poc_suite(suite, max_tests=10)
        self.assertIn("deferred_coverage", str(ctx.exception))


class ValidatePocSuiteTests(unittest.TestCase):
    def test_valid_representative_mix_passes(self) -> None:
        suite = build_valid_poc_suite()
        validate_poc_suite(suite, max_tests=10)

    def test_rejects_over_limit(self) -> None:
        suite = build_valid_poc_suite(max_tests=10)
        with self.assertRaises(OrchestratorError) as ctx:
            validate_poc_suite(suite, max_tests=5)
        self.assertIn("exceeds configured maximum", str(ctx.exception))

    def test_rejects_phantom_inventory(self) -> None:
        suite = build_valid_poc_suite(
            phantom_in_coverage="- AC-8: TC-015",
        )
        with self.assertRaises(OrchestratorError) as ctx:
            validate_poc_suite(suite, max_tests=10)
        self.assertIn("Phantom test IDs", str(ctx.exception))

    def test_rejects_missing_constrained(self) -> None:
        suite = build_valid_poc_suite(
            ready_count=8,
            constrained_count=0,
            blocked_count=2,
        )
        with self.assertRaises(OrchestratorError) as ctx:
            validate_poc_suite(suite, max_tests=10)
        self.assertIn("CONSTRAINED", str(ctx.exception))

    def test_rejects_missing_blocked(self) -> None:
        suite = build_valid_poc_suite(
            ready_count=8,
            constrained_count=2,
            blocked_count=0,
        )
        with self.assertRaises(OrchestratorError) as ctx:
            validate_poc_suite(suite, max_tests=10)
        self.assertIn("BLOCKED", str(ctx.exception))

    def test_rejects_handoff_count_mismatch(self) -> None:
        suite = build_valid_poc_suite(wrong_handoff_counts=True)
        with self.assertRaises(OrchestratorError) as ctx:
            validate_poc_suite(suite, max_tests=10)
        self.assertIn("ready_count", str(ctx.exception))

    def test_rejects_missing_deferred_coverage(self) -> None:
        suite = build_valid_poc_suite(omit_deferred_coverage=True)
        with self.assertRaises(OrchestratorError) as ctx:
            validate_poc_suite(suite, max_tests=10)
        self.assertIn("deferred_coverage", str(ctx.exception))

    def test_rejects_incomplete_final_test(self) -> None:
        suite = build_valid_poc_suite(incomplete_final_test=True)
        with self.assertRaises(OrchestratorError) as ctx:
            validate_poc_suite(suite, max_tests=10)
        self.assertIn("incomplete", str(ctx.exception))

    def test_rejects_missing_validation_handoff(self) -> None:
        suite = build_valid_poc_suite(include_handoff=False)
        with self.assertRaises(OrchestratorError) as ctx:
            validate_poc_suite(suite, max_tests=10)
        self.assertIn("Validation Handoff Package", str(ctx.exception))
        self.assertIn("exact heading present: False", str(ctx.exception))


class HandoffConsistencyTests(unittest.TestCase):
    def test_ready_body_with_ready_yaml_passes(self) -> None:
        suite = build_valid_poc_suite(
            max_tests=3,
            ready_count=1,
            constrained_count=1,
            blocked_count=1,
        )
        validate_poc_suite(suite, max_tests=3)

    def test_ready_body_with_constrained_yaml_fails(self) -> None:
        suite = build_valid_poc_suite(
            max_tests=3,
            ready_count=3,
            constrained_count=0,
            blocked_count=0,
            yaml_statuses=["CONSTRAINED", "READY", "READY"],
        )
        with self.assertRaises(OrchestratorError) as ctx:
            validate_poc_suite(suite, max_tests=3)
        message = str(ctx.exception)
        self.assertIn("source of truth", message)
        self.assertIn("TC-001", message)
        self.assertIn("CONSTRAINED", message)
        self.assertIn("READY", message)

    def test_status_counts_must_match_bodies(self) -> None:
        suite = build_valid_poc_suite(
            max_tests=3,
            ready_count=1,
            constrained_count=1,
            blocked_count=1,
            wrong_handoff_counts=True,
        )
        with self.assertRaises(OrchestratorError) as ctx:
            validate_poc_suite(suite, max_tests=3)
        self.assertIn("ready_count", str(ctx.exception))

    def test_dismissal_ready_with_persistence_exclusion_passes(self) -> None:
        body_parts = [
            "# Test Suite",
            _dismissal_ready_test(1),
            "---",
            _test_case(2, status="CONSTRAINED"),
            "---",
            _test_case(3, status="BLOCKED"),
            "---",
            "## Validation Handoff Package",
            "```yaml",
            _build_handoff_yaml(
                max_tests=3,
                total=3,
                ready_count=1,
                constrained_count=1,
                blocked_count=1,
                statuses=["READY", "CONSTRAINED", "BLOCKED"],
            ).rstrip(),
            "```",
        ]
        suite = "\n\n".join(body_parts)
        validate_poc_suite(suite, max_tests=3)

    def test_dismissal_ready_body_with_constrained_yaml_fails(self) -> None:
        body_parts = [
            "# Test Suite",
            _dismissal_ready_test(1),
            "---",
            _test_case(2, status="CONSTRAINED"),
            "---",
            _test_case(3, status="BLOCKED"),
            "---",
            "## Validation Handoff Package",
            "```yaml",
            _build_handoff_yaml(
                max_tests=3,
                total=3,
                ready_count=0,
                constrained_count=2,
                blocked_count=1,
                statuses=["CONSTRAINED", "CONSTRAINED", "BLOCKED"],
            ).rstrip(),
            "```",
        ]
        suite = "\n\n".join(body_parts)
        with self.assertRaises(OrchestratorError) as ctx:
            validate_poc_suite(suite, max_tests=3)
        message = str(ctx.exception)
        self.assertIn("TC-001", message)
        self.assertIn("source of truth", message)


if __name__ == "__main__":
    unittest.main()
