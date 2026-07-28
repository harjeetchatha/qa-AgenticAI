"""Post-generation validation for POC test suites."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

import yaml

from ai_qe_studio.errors import OrchestratorError

TC_HEADER_PATTERN = re.compile(
    r"^## (TC-\d+) — (.+?)(?:\s*\[(CONSTRAINED|BLOCKED)\])?\s*$",
    re.MULTILINE,
)
TC_REF_PATTERN = re.compile(r"TC-(\d+)(?:\s*[–-]\s*TC-(\d+))?")
VALIDATION_HANDOFF_HEADING = "Validation Handoff Package"
HEADING_PATTERN = re.compile(
    rf"^##\s+{re.escape(VALIDATION_HANDOFF_HEADING)}\s*$",
    re.MULTILINE,
)
FENCE_OPEN_PATTERN = re.compile(r"^```(yaml|yml)\s*$", re.MULTILINE | re.IGNORECASE)
ANY_HEADING_PATTERN = re.compile(r"^## .+$", re.MULTILINE)
REQUIRED_HANDOFF_KEYS = (
    "schema_version",
    "poc_mode",
    "max_test_count",
    "total_tests",
    "ready_count",
    "constrained_count",
    "blocked_count",
    "included_acceptance_criteria",
    "deferred_coverage",
    "open_questions_referenced",
    "test_cases",
)
REQUIRED_TEST_SECTIONS = (
    "### Steps",
    "### Expected Results",
    "### Assumptions",
    "### Open Questions",
    "### Automation Candidate",
)


@dataclass(frozen=True)
class ParsedTestCase:
    test_id: str
    number: int
    title: str
    body: str
    status: str


@dataclass(frozen=True)
class HandoffExtractionDiagnostics:
    exact_heading_present: bool
    heading_count: int
    yaml_fence_found: bool
    yaml_fence_closed: bool
    headings_near_end: list[str]
    tail_excerpt: str


class HandoffExtractionError(ValueError):
    """Raised when the Validation Handoff Package cannot be extracted."""

    def __init__(self, message: str, *, diagnostics: HandoffExtractionDiagnostics) -> None:
        super().__init__(message)
        self.diagnostics = diagnostics

    def formatted_diagnostics(self) -> str:
        lines = [
            "Validation Handoff Package diagnostics:",
            f"- exact heading present: {self.diagnostics.exact_heading_present}",
            f"- heading occurrences: {self.diagnostics.heading_count}",
            f"- yaml/yml fence found after heading: {self.diagnostics.yaml_fence_found}",
            f"- yaml/yml fence closed: {self.diagnostics.yaml_fence_closed}",
        ]
        if self.diagnostics.headings_near_end:
            lines.append(
                "- headings near end: "
                + "; ".join(self.diagnostics.headings_near_end)
            )
        else:
            lines.append("- headings near end: (none)")
        lines.append("- final 1000 characters of response:")
        lines.append(self.diagnostics.tail_excerpt)
        return "\n".join(lines)


def normalize_response_text(text: str) -> str:
    """Normalize line endings and trailing whitespace for parsing."""
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return normalized.rstrip()


def _format_tc(number: int) -> str:
    return f"TC-{number:03d}"


def _parse_tc_number(test_id: str) -> int:
    match = re.fullmatch(r"TC-(\d+)", test_id)
    if not match:
        raise ValueError(f"Invalid test ID: {test_id}")
    return int(match.group(1))


def _build_diagnostics(text: str) -> HandoffExtractionDiagnostics:
    normalized = normalize_response_text(text)
    headings_near_end = ANY_HEADING_PATTERN.findall(normalized[-2000:])
    heading_matches = list(HEADING_PATTERN.finditer(normalized))
    exact_heading_present = bool(heading_matches)

    yaml_fence_found = False
    yaml_fence_closed = False
    if heading_matches:
        after_heading = normalized[heading_matches[-1].end() :].lstrip("\n")
        yaml_fence_found = bool(FENCE_OPEN_PATTERN.search(after_heading))
        if yaml_fence_found:
            fence_open = FENCE_OPEN_PATTERN.search(after_heading)
            assert fence_open is not None
            content_start = fence_open.end()
            yaml_fence_closed = "\n```" in after_heading[content_start:]

    tail = normalized[-1000:] if len(normalized) > 1000 else normalized
    return HandoffExtractionDiagnostics(
        exact_heading_present=exact_heading_present,
        heading_count=len(heading_matches),
        yaml_fence_found=yaml_fence_found,
        yaml_fence_closed=yaml_fence_closed,
        headings_near_end=headings_near_end,
        tail_excerpt=tail,
    )


def extract_validation_handoff_yaml(text: str) -> tuple[str, dict[str, Any]]:
    """Extract and parse the canonical Validation Handoff Package YAML block."""
    normalized = normalize_response_text(text)
    diagnostics = _build_diagnostics(normalized)
    heading_matches = list(HEADING_PATTERN.finditer(normalized))

    if not heading_matches:
        raise HandoffExtractionError(
            f"Required heading '## {VALIDATION_HANDOFF_HEADING}' was not found.",
            diagnostics=diagnostics,
        )

    if len(heading_matches) > 1:
        raise HandoffExtractionError(
            f"Expected exactly one '## {VALIDATION_HANDOFF_HEADING}' section, "
            f"found {len(heading_matches)}.",
            diagnostics=diagnostics,
        )

    heading = heading_matches[0]
    later_headings = [
        match.group(0)
        for match in ANY_HEADING_PATTERN.finditer(normalized)
        if match.start() > heading.start()
    ]
    if later_headings:
        raise HandoffExtractionError(
            "Validation Handoff Package must be the final section; "
            f"found later headings: {', '.join(later_headings)}.",
            diagnostics=diagnostics,
        )

    after_heading = normalized[heading.end() :].lstrip("\n")
    fence_open = FENCE_OPEN_PATTERN.search(after_heading)
    if not fence_open:
        raise HandoffExtractionError(
            "Validation Handoff Package must contain a fenced ```yaml or ```yml block.",
            diagnostics=diagnostics,
        )

    content_start = fence_open.end()
    close_match = re.search(r"\n```[ \t]*(?:\n|$)", after_heading[content_start:])
    if not close_match:
        raise HandoffExtractionError(
            "Validation Handoff Package YAML fence is not closed with ```.",
            diagnostics=diagnostics,
        )

    yaml_text = after_heading[content_start : content_start + close_match.start()]
    remainder = after_heading[content_start + close_match.end() :].strip()
    if remainder:
        raise HandoffExtractionError(
            "Validation Handoff Package must be the final section; "
            "content appears after the closing code fence.",
            diagnostics=diagnostics,
        )

    try:
        data = yaml.safe_load(yaml_text)
    except yaml.YAMLError as exc:
        raise HandoffExtractionError(
            f"Validation Handoff Package YAML is malformed: {exc}",
            diagnostics=diagnostics,
        ) from exc

    if not isinstance(data, dict):
        raise HandoffExtractionError(
            "Validation Handoff Package YAML must contain a mapping at the top level.",
            diagnostics=diagnostics,
        )

    return yaml_text, data


def _extract_test_cases(text: str) -> list[ParsedTestCase]:
    matches = list(TC_HEADER_PATTERN.finditer(text))
    tests: list[ParsedTestCase] = []

    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[start:end]
        status_tag = match.group(3)

        if status_tag == "BLOCKED":
            status = "BLOCKED"
        elif status_tag == "CONSTRAINED":
            status = "CONSTRAINED"
        else:
            status = _classify_status_from_body(body)

        test_id = match.group(1)
        tests.append(
            ParsedTestCase(
                test_id=test_id,
                number=_parse_tc_number(test_id),
                title=match.group(2).strip(),
                body=body,
                status=status,
            )
        )

    return tests


def _classify_status_from_body(body: str) -> str:
    expected = re.search(
        r"### Expected Results\s*\n(.*?)(?=\n### |\n---|\Z)",
        body,
        re.DOTALL,
    )
    if expected:
        first_line = (
            expected.group(1).strip().splitlines()[0]
            if expected.group(1).strip()
            else ""
        )
        if first_line.startswith("BLOCKED"):
            return "BLOCKED"
        if first_line.startswith("CONSTRAINED"):
            return "CONSTRAINED"
    return "READY"


def _expand_tc_references(text: str) -> set[str]:
    references: set[str] = set()
    for match in TC_REF_PATTERN.finditer(text):
        start = int(match.group(1))
        end = int(match.group(2)) if match.group(2) else start
        if end < start:
            start, end = end, start
        for number in range(start, end + 1):
            references.add(_format_tc(number))
    return references


def _count_statuses(tests: list[ParsedTestCase]) -> dict[str, int]:
    counts = {"READY": 0, "CONSTRAINED": 0, "BLOCKED": 0}
    for test in tests:
        counts[test.status] += 1
    return counts


def _reference_sections(text: str, tests: list[ParsedTestCase]) -> str:
    if not tests:
        return text

    first_heading = text.find(f"## {tests[0].test_id}")
    prefix_end = first_heading if first_heading >= 0 else len(text)

    heading_match = HEADING_PATTERN.search(text)
    if heading_match:
        return text[:prefix_end] + text[heading_match.start() :]

    return text[:prefix_end]


def _validate_handoff_contents(
    handoff: dict[str, Any],
    *,
    tests: list[ParsedTestCase],
    counts: dict[str, int],
    generated_ids: set[str],
    max_tests: int,
    issues: list[str],
) -> None:
    for key in REQUIRED_HANDOFF_KEYS:
        if key not in handoff:
            issues.append(f"Validation Handoff Package missing required key: {key}.")
        elif handoff[key] in (None, "", []):
            issues.append(f"Validation Handoff Package key '{key}' must not be empty.")

    if handoff.get("poc_mode") is not True:
        issues.append("Validation Handoff Package poc_mode must be true.")

    configured_count = handoff.get("max_test_count")
    if configured_count != max_tests:
        issues.append(
            "Validation Handoff Package max_test_count "
            f"({configured_count!r}) must match configured value {max_tests}."
        )

    expected_fields = {
        "total_tests": len(tests),
        "ready_count": counts["READY"],
        "constrained_count": counts["CONSTRAINED"],
        "blocked_count": counts["BLOCKED"],
    }
    status_mismatches: list[str] = []
    for field, expected in expected_fields.items():
        actual = handoff.get(field)
        if actual != expected:
            issues.append(
                f"Validation Handoff Package {field} is {actual!r}; expected {expected}."
            )

    handoff_test_cases = handoff.get("test_cases")
    if isinstance(handoff_test_cases, list) and handoff_test_cases:
        handoff_ids: set[str] = set()
        for entry in handoff_test_cases:
            if not isinstance(entry, dict):
                continue
            test_id = entry.get("test_id") or entry.get("id")
            if test_id:
                handoff_ids.add(str(test_id))
                matching = next((t for t in tests if t.test_id == test_id), None)
                if matching and entry.get("status") != matching.status:
                    status_mismatches.append(
                        f"{test_id}: handoff {entry.get('status')!r}, "
                        f"body {matching.status!r}"
                    )
        if status_mismatches:
            issues.append(
                "Validation Handoff Package test_cases statuses do not match "
                "test bodies (test bodies are the source of truth): "
                + "; ".join(status_mismatches)
                + "."
            )
        if handoff_ids and handoff_ids != generated_ids:
            issues.append(
                "Validation Handoff Package test_cases IDs do not match generated tests."
            )


def validate_poc_suite(text: str, *, max_tests: int) -> None:
    """Validate a generated POC test suite before writing output."""
    issues: list[str] = []

    if max_tests <= 0:
        issues.append("--max-tests / AI_QE_POC_MAX_TESTS must be greater than zero.")

    normalized = normalize_response_text(text)
    tests = _extract_test_cases(normalized)
    counts = _count_statuses(tests)
    generated_ids = {test.test_id for test in tests}

    if not tests:
        issues.append("No test cases found (expected TC-001 through TC-NNN).")
    elif len(tests) > max_tests:
        issues.append(
            f"Test count {len(tests)} exceeds configured maximum {max_tests}."
        )

    if tests:
        numbers = [test.number for test in tests]
        if len(numbers) != len(set(numbers)):
            issues.append("Duplicate test IDs detected.")

        expected_numbers = list(range(1, len(tests) + 1))
        if sorted(numbers) != expected_numbers:
            issues.append(
                "Test IDs must be sequential starting at TC-001 with no gaps."
            )

        if counts["READY"] < 1:
            issues.append("At least one READY test is required.")
        if counts["CONSTRAINED"] < 1:
            issues.append("At least one CONSTRAINED test is required.")
        if counts["BLOCKED"] < 1:
            issues.append("At least one BLOCKED test is required.")

        last_test = tests[-1]
        for section in REQUIRED_TEST_SECTIONS:
            if section not in last_test.body:
                issues.append(
                    f"Final test case {last_test.test_id} is incomplete "
                    f"(missing '{section}')."
                )
                break

    reference_text = _reference_sections(normalized, tests)
    referenced_ids = _expand_tc_references(reference_text)
    phantom_ids = sorted(
        referenced_ids - generated_ids,
        key=_parse_tc_number,
    )
    if phantom_ids:
        issues.append(
            "Phantom test IDs referenced in coverage map or handoff: "
            + ", ".join(phantom_ids)
            + "."
        )

    handoff: dict[str, Any] | None = None
    try:
        _, handoff = extract_validation_handoff_yaml(normalized)
    except HandoffExtractionError as exc:
        issues.append(str(exc))
        issues.append(exc.formatted_diagnostics())
    except ValueError as exc:
        issues.append(f"Validation Handoff Package invalid: {exc}")
        issues.append(_build_diagnostics(normalized).tail_excerpt)

    if handoff is not None:
        _validate_handoff_contents(
            handoff,
            tests=tests,
            counts=counts,
            generated_ids=generated_ids,
            max_tests=max_tests,
            issues=issues,
        )

    if issues:
        has_handoff_status_issue = any(
            "test_cases statuses do not match" in issue
            or "ready_count" in issue
            or "constrained_count" in issue
            or "blocked_count" in issue
            for issue in issues
        )
        if has_handoff_status_issue:
            issues.insert(
                0,
                "Test case bodies are the source of truth for READY/CONSTRAINED/"
                "BLOCKED status; Validation Handoff Package counts and "
                "test_cases[].status must be reconciled from the final test bodies.",
            )
        message = "POC test suite validation failed:\n" + "\n".join(
            f"- {issue}" for issue in issues
        )
        raise OrchestratorError(message)
