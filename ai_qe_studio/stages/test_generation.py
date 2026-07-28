"""Test Generation stage."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ai_qe_studio.anthropic_client import create_client, create_message
from ai_qe_studio.config import AnthropicConfig, TestGenerationConfig
from ai_qe_studio.errors import OrchestratorError
from ai_qe_studio.files import ensure_output_writable, read_required_text, write_validated_output
from ai_qe_studio.handoff import (
    parse_handoff,
    resolve_requirement_id,
    validate_handoff_for_test_generation,
)
from ai_qe_studio.paths import TestGenerationPaths, test_generation_paths
from ai_qe_studio.prompts import build_test_generation_user_prompt
from ai_qe_studio.suite_validation import validate_poc_suite

CreateClientFn = Callable[[AnthropicConfig], Any]
CreateMessageFn = Callable[..., str]


@dataclass(frozen=True)
class TestGenerationResult:
    story_name: str
    requirement_id: str
    output_path: Path
    max_tests: int


def load_test_generation_inputs(
    story_name: str,
    *,
    root: Path | None = None,
) -> tuple[TestGenerationPaths, str, str, str, dict[str, str], dict[str, Any]]:
    """Load all inputs required for the Test Generation stage."""
    paths = test_generation_paths(story_name, root=root)

    analysis_text = read_required_text(paths.analysis_path)
    requirement_text = read_required_text(paths.requirement_path)
    agent_text = read_required_text(paths.agent_path)

    knowledge_contents = {
        filename: read_required_text(path)
        for filename, path in paths.knowledge_paths.items()
    }

    handoff = parse_handoff(analysis_text)

    return (
        paths,
        analysis_text,
        requirement_text,
        agent_text,
        knowledge_contents,
        handoff,
    )


def run_test_generation(
    story_name: str,
    *,
    cli_requirement_id: str | None = None,
    config: AnthropicConfig,
    generation_config: TestGenerationConfig,
    overwrite: bool = False,
    root: Path | None = None,
    create_client_fn: CreateClientFn = create_client,
    create_message_fn: CreateMessageFn = create_message,
) -> TestGenerationResult:
    """Run the Test Generation Agent and save its output."""
    (
        paths,
        analysis_text,
        requirement_text,
        agent_text,
        knowledge_contents,
        handoff,
    ) = load_test_generation_inputs(story_name, root=root)

    validate_handoff_for_test_generation(handoff)
    requirement_id = resolve_requirement_id(handoff, cli_requirement_id)

    ensure_output_writable(paths.output_path, overwrite=overwrite)

    max_tests = generation_config.max_tests
    user_prompt = build_test_generation_user_prompt(
        paths=paths,
        requirement_text=requirement_text,
        requirement_id=requirement_id,
        analysis_text=analysis_text,
        knowledge_contents=knowledge_contents,
        max_tests=max_tests,
    )

    client = create_client_fn(config)
    response_text = create_message_fn(
        client,
        config,
        system=agent_text,
        user=user_prompt,
    )

    try:
        validate_poc_suite(response_text, max_tests=max_tests)
    except OrchestratorError:
        raise

    write_validated_output(paths.output_path, response_text, overwrite=overwrite)

    return TestGenerationResult(
        story_name=story_name,
        requirement_id=requirement_id,
        output_path=paths.output_path,
        max_tests=max_tests,
    )
