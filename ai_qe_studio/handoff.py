"""Requirement Analysis handoff extraction and validation."""

from __future__ import annotations

import re
from typing import Any

import yaml

from ai_qe_studio.errors import OrchestratorError

HANDOFF_HEADING = "## Handoff Package"


def extract_handoff_yaml(analysis_text: str) -> str:
    """Extract the YAML block from a Requirement Analysis document."""
    pattern = (
        rf"{re.escape(HANDOFF_HEADING)}\s*\n\s*```yaml\s*\n(.*?)\n```"
    )
    match = re.search(pattern, analysis_text, re.DOTALL)
    if not match:
        raise OrchestratorError(
            f"Handoff Package not found in analysis output. "
            f"Expected a '{HANDOFF_HEADING}' section with a ```yaml block."
        )
    return match.group(1)


def parse_handoff(analysis_text: str) -> dict[str, Any]:
    """Parse the handoff object from a Requirement Analysis document."""
    yaml_text = extract_handoff_yaml(analysis_text)
    try:
        data = yaml.safe_load(yaml_text)
    except yaml.YAMLError as exc:
        raise OrchestratorError(
            f"Handoff Package YAML is not parseable: {exc}"
        ) from exc

    if not isinstance(data, dict):
        raise OrchestratorError(
            "Handoff Package YAML must contain a mapping at the top level."
        )

    handoff = data.get("handoff", data)
    if not isinstance(handoff, dict):
        raise OrchestratorError(
            "Handoff Package must contain a 'handoff' mapping."
        )

    return handoff


def _coerce_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if value is None:
        return None
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "yes"}:
            return True
        if lowered in {"false", "no"}:
            return False
    return None


def normalize_question(question: dict[str, Any]) -> dict[str, Any]:
    """Normalize a question object for schema 1.1 with 1.0 fallback."""
    normalized = dict(question)

    specific = _coerce_bool(normalized.get("blocking_for_specific_tests"))
    entire = _coerce_bool(normalized.get("blocking_for_entire_suite"))

    if specific is None and "blocking" in normalized:
        specific = _coerce_bool(normalized.get("blocking"))
    if entire is None and "affects_ready" in normalized:
        entire = _coerce_bool(normalized.get("affects_ready"))

    if specific is None:
        specific = False
    if entire is None:
        entire = False

    normalized["blocking_for_specific_tests"] = specific
    normalized["blocking_for_entire_suite"] = entire
    return normalized


def validate_handoff_for_test_generation(handoff: dict[str, Any]) -> None:
    """Validate that the handoff permits test generation to proceed."""
    requirement_id = handoff.get("requirement_id")
    if not requirement_id or not str(requirement_id).strip():
        raise OrchestratorError(
            "ERROR: handoff_package.requirement_id is missing."
        )

    ready = _coerce_bool(handoff.get("ready_for_test_generation"))
    if ready is None:
        raise OrchestratorError(
            "ERROR: handoff_package.ready_for_test_generation is missing or invalid."
        )

    if not ready:
        blocker_reason = handoff.get("blocker_reason") or "No reason provided."
        raise OrchestratorError(
            "BLOCKED: Test generation cannot proceed. "
            f"Reason: {blocker_reason}"
        )

    open_questions = handoff.get("open_questions") or []
    if not isinstance(open_questions, list):
        raise OrchestratorError(
            "ERROR: handoff_package.open_questions must be a list."
        )

    for raw_question in open_questions:
        if not isinstance(raw_question, dict):
            continue
        question = normalize_question(raw_question)
        qid = question.get("id", "<unknown>")
        if question["blocking_for_entire_suite"]:
            raise OrchestratorError(
                "ERROR: Handoff inconsistency — question "
                f"{qid} has blocking_for_entire_suite: true but "
                "ready_for_test_generation is true. "
                "Re-run Requirement Analysis Agent."
            )


def resolve_requirement_id(
    handoff: dict[str, Any],
    cli_requirement_id: str | None,
) -> str:
    """Return the requirement ID, validating CLI override when provided."""
    handoff_requirement_id = str(handoff["requirement_id"]).strip()
    if cli_requirement_id is None:
        return handoff_requirement_id

    cli_requirement_id = cli_requirement_id.strip()
    if cli_requirement_id != handoff_requirement_id:
        raise OrchestratorError(
            "ERROR: --requirement-id "
            f"'{cli_requirement_id}' does not match handoff requirement_id "
            f"'{handoff_requirement_id}'."
        )
    return handoff_requirement_id
