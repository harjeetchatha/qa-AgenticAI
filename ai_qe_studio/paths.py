"""Project path resolution."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

KNOWLEDGE_PACK_DIR = Path("knowledge/customer-management-pack")
REQUIREMENTS_DIR = Path("knowledge/requirements")
AGENTS_DIR = Path("agents")
SCHEMAS_DIR = Path("schemas")
GENERATED_DIR = Path("generated")

KNOWLEDGE_FILES = (
    "application-context.md",
    "business-rules.md",
    "data-model.md",
    "glossary.md",
    "known-limitations.md",
)


@dataclass(frozen=True)
class StoryPaths:
    story_name: str
    project_root: Path
    requirement_path: Path
    requirement_source: str
    agent_path: Path
    schema_path: Path
    knowledge_paths: dict[str, Path]
    output_dir: Path
    output_path: Path


@dataclass(frozen=True)
class TestGenerationPaths:
    story_name: str
    project_root: Path
    requirement_path: Path
    requirement_source: str
    analysis_path: Path
    agent_path: Path
    knowledge_paths: dict[str, Path]
    output_dir: Path
    output_path: Path


def project_root() -> Path:
    """Return the repository root directory."""
    return Path(__file__).resolve().parent.parent


def story_paths(story_name: str, root: Path | None = None) -> StoryPaths:
    """Build canonical paths for a story workflow run."""
    root = root or project_root()
    requirement_path = root / REQUIREMENTS_DIR / f"{story_name}.md"
    requirement_source = str(REQUIREMENTS_DIR / f"{story_name}.md")

    knowledge_paths = {
        filename: root / KNOWLEDGE_PACK_DIR / filename
        for filename in KNOWLEDGE_FILES
    }

    output_dir = root / GENERATED_DIR / story_name
    output_path = output_dir / "requirement-analysis.md"

    return StoryPaths(
        story_name=story_name,
        project_root=root,
        requirement_path=requirement_path,
        requirement_source=requirement_source,
        agent_path=root / AGENTS_DIR / "requirement-analysis-agent.md",
        schema_path=root / SCHEMAS_DIR / "requirement-analysis-schema.md",
        knowledge_paths=knowledge_paths,
        output_dir=output_dir,
        output_path=output_path,
    )


def test_generation_paths(
    story_name: str,
    root: Path | None = None,
) -> TestGenerationPaths:
    """Build canonical paths for the Test Generation stage."""
    root = root or project_root()
    requirement_path = root / REQUIREMENTS_DIR / f"{story_name}.md"
    requirement_source = str(REQUIREMENTS_DIR / f"{story_name}.md")

    knowledge_paths = {
        filename: root / KNOWLEDGE_PACK_DIR / filename
        for filename in KNOWLEDGE_FILES
    }

    output_dir = root / GENERATED_DIR / story_name
    output_path = output_dir / "generated-test-suite.md"

    return TestGenerationPaths(
        story_name=story_name,
        project_root=root,
        requirement_path=requirement_path,
        requirement_source=requirement_source,
        analysis_path=output_dir / "requirement-analysis.md",
        agent_path=root / AGENTS_DIR / "test-generation-agent.md",
        knowledge_paths=knowledge_paths,
        output_dir=output_dir,
        output_path=output_path,
    )
