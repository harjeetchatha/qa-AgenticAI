"""Requirement Analysis stage."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ai_qe_studio.anthropic_client import create_client, create_message
from ai_qe_studio.config import AnthropicConfig
from ai_qe_studio.files import read_required_text, write_output
from ai_qe_studio.paths import StoryPaths, story_paths
from ai_qe_studio.prompts import build_requirement_analysis_user_prompt


@dataclass(frozen=True)
class RequirementAnalysisResult:
    story_name: str
    requirement_id: str
    output_path: Path


def load_requirement_analysis_inputs(
    story_name: str,
    *,
    root: Path | None = None,
) -> tuple[StoryPaths, str, str, dict[str, str], str]:
    """Load all inputs required for the Requirement Analysis stage."""
    paths = story_paths(story_name, root=root)

    requirement_text = read_required_text(paths.requirement_path)
    agent_text = read_required_text(paths.agent_path)
    schema_text = read_required_text(paths.schema_path)

    knowledge_contents = {
        filename: read_required_text(path)
        for filename, path in paths.knowledge_paths.items()
    }

    return paths, requirement_text, agent_text, knowledge_contents, schema_text


def run_requirement_analysis(
    story_name: str,
    *,
    requirement_id: str,
    config: AnthropicConfig,
    overwrite: bool = False,
    root: Path | None = None,
) -> RequirementAnalysisResult:
    """Run the Requirement Analysis Agent and save its output."""
    (
        paths,
        requirement_text,
        agent_text,
        knowledge_contents,
        schema_text,
    ) = load_requirement_analysis_inputs(story_name, root=root)

    user_prompt = build_requirement_analysis_user_prompt(
        paths=paths,
        requirement_text=requirement_text,
        requirement_id=requirement_id,
        knowledge_contents=knowledge_contents,
        schema_text=schema_text,
    )

    client = create_client(config)
    response_text = create_message(
        client,
        config,
        system=agent_text,
        user=user_prompt,
    )

    write_output(paths.output_path, response_text, overwrite=overwrite)

    return RequirementAnalysisResult(
        story_name=story_name,
        requirement_id=requirement_id,
        output_path=paths.output_path,
    )
