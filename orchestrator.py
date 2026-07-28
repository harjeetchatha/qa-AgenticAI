#!/usr/bin/env python3
"""AI-QE Studio orchestrator CLI."""

from __future__ import annotations

import argparse
import logging
import sys

from ai_qe_studio.config import (
    load_anthropic_config,
    load_test_generation_config,
    with_max_tests,
    with_max_tokens,
)
from ai_qe_studio.errors import OrchestratorError
from ai_qe_studio.stages.requirement_analysis import run_requirement_analysis
from ai_qe_studio.stages.test_generation import run_test_generation

STAGE_REQUIREMENT_ANALYSIS = "requirement-analysis"
STAGE_TEST_GENERATION = "test-generation"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the AI-QE Studio orchestrator workflow.",
    )
    parser.add_argument(
        "story_name",
        help="Story slug matching knowledge/requirements/{story_name}.md",
    )
    parser.add_argument(
        "--stage",
        choices=[STAGE_REQUIREMENT_ANALYSIS, STAGE_TEST_GENERATION],
        default=STAGE_REQUIREMENT_ANALYSIS,
        help=(
            "Workflow stage to run "
            f"(default: {STAGE_REQUIREMENT_ANALYSIS})."
        ),
    )
    parser.add_argument(
        "--requirement-id",
        help=(
            "Requirement ID for requirement-analysis, or override check "
            "for test-generation (must match the handoff when supplied)."
        ),
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        help="Override ANTHROPIC_MAX_TOKENS for this run.",
    )
    parser.add_argument(
        "--max-tests",
        type=int,
        help="Override AI_QE_POC_MAX_TESTS for test-generation (default: 10).",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace an existing generated output file.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    parser = build_parser()
    args = parser.parse_args(argv)

    story_name = args.story_name

    try:
        config = with_max_tokens(load_anthropic_config(), args.max_tokens)
        generation_config = with_max_tests(
            load_test_generation_config(),
            args.max_tests,
        )

        if args.stage == STAGE_REQUIREMENT_ANALYSIS:
            requirement_id = args.requirement_id or story_name
            result = run_requirement_analysis(
                story_name,
                requirement_id=requirement_id,
                config=config,
                overwrite=args.overwrite,
            )
        else:
            result = run_test_generation(
                story_name,
                cli_requirement_id=args.requirement_id,
                config=config,
                generation_config=generation_config,
                overwrite=args.overwrite,
            )
    except OrchestratorError as exc:
        print(f"FAILURE: {exc}", file=sys.stderr)
        return 1

    if args.stage == STAGE_REQUIREMENT_ANALYSIS:
        print("SUCCESS: Requirement analysis completed.")
    else:
        print("SUCCESS: Test generation completed.")

    print(f"Story: {result.story_name}")
    print(f"Requirement ID: {result.requirement_id}")
    print(f"Output: {result.output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
