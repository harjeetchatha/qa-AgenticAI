"""Environment and runtime configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass, replace

from dotenv import load_dotenv

from ai_qe_studio.errors import OrchestratorError

DEFAULT_MODEL = "claude-sonnet-5"
DEFAULT_MAX_TOKENS = 16384
DEFAULT_TIMEOUT_SECONDS = 600
DEFAULT_POC_MAX_TESTS = 10


@dataclass(frozen=True)
class AnthropicConfig:
    api_key: str
    model: str
    max_tokens: int
    timeout_seconds: float


@dataclass(frozen=True)
class TestGenerationConfig:
    max_tests: int


def _parse_positive_int(name: str, raw: str) -> int:
    try:
        value = int(raw)
    except ValueError as exc:
        raise OrchestratorError(f"ERROR: {name} must be an integer") from exc

    if value <= 0:
        raise OrchestratorError(f"ERROR: {name} must be greater than zero")

    return value


def _parse_positive_float(name: str, raw: str) -> float:
    try:
        value = float(raw)
    except ValueError as exc:
        raise OrchestratorError(f"ERROR: {name} must be a number") from exc

    if value <= 0:
        raise OrchestratorError(f"ERROR: {name} must be greater than zero")

    return value


def load_anthropic_config() -> AnthropicConfig:
    """Load Anthropic settings from the environment."""
    load_dotenv()

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise OrchestratorError(
            "ERROR: ANTHROPIC_API_KEY was not found in .env"
        )

    model = os.getenv("ANTHROPIC_MODEL", DEFAULT_MODEL)
    max_tokens = _parse_positive_int(
        "ANTHROPIC_MAX_TOKENS",
        os.getenv("ANTHROPIC_MAX_TOKENS", str(DEFAULT_MAX_TOKENS)),
    )
    timeout_seconds = _parse_positive_float(
        "ANTHROPIC_TIMEOUT_SECONDS",
        os.getenv("ANTHROPIC_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS)),
    )

    return AnthropicConfig(
        api_key=api_key,
        model=model,
        max_tokens=max_tokens,
        timeout_seconds=timeout_seconds,
    )


def with_max_tokens(
    config: AnthropicConfig,
    max_tokens: int | None,
) -> AnthropicConfig:
    """Return a copy with max_tokens overridden when CLI provides a value."""
    if max_tokens is None:
        return config

    if max_tokens <= 0:
        raise OrchestratorError("ERROR: --max-tokens must be greater than zero")

    return replace(config, max_tokens=max_tokens)


def load_test_generation_config() -> TestGenerationConfig:
    """Load Test Generation settings from the environment."""
    load_dotenv()
    max_tests = _parse_positive_int(
        "AI_QE_POC_MAX_TESTS",
        os.getenv("AI_QE_POC_MAX_TESTS", str(DEFAULT_POC_MAX_TESTS)),
    )
    return TestGenerationConfig(max_tests=max_tests)


def with_max_tests(
    config: TestGenerationConfig,
    max_tests: int | None,
) -> TestGenerationConfig:
    """Return a copy with max_tests overridden when CLI provides a value."""
    if max_tests is None:
        return config

    if max_tests <= 0:
        raise OrchestratorError("ERROR: --max-tests must be greater than zero")

    return replace(config, max_tests=max_tests)
