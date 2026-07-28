"""Tests for Anthropic configuration loading and overrides."""

from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from ai_qe_studio.config import (
    DEFAULT_MAX_TOKENS,
    DEFAULT_POC_MAX_TESTS,
    DEFAULT_TIMEOUT_SECONDS,
    AnthropicConfig,
    TestGenerationConfig,
    load_anthropic_config,
    load_test_generation_config,
    with_max_tests,
    with_max_tokens,
)
from ai_qe_studio.errors import OrchestratorError

BASE_ENV = {
    "ANTHROPIC_API_KEY": "test-key",
    "ANTHROPIC_MODEL": "claude-sonnet-5",
}


class LoadAnthropicConfigTests(unittest.TestCase):
    def test_default_timeout(self) -> None:
        with patch.dict(os.environ, BASE_ENV, clear=True):
            config = load_anthropic_config()

        self.assertEqual(config.timeout_seconds, DEFAULT_TIMEOUT_SECONDS)
        self.assertEqual(config.max_tokens, DEFAULT_MAX_TOKENS)

    def test_timeout_from_env(self) -> None:
        env = {**BASE_ENV, "ANTHROPIC_TIMEOUT_SECONDS": "120"}
        with patch.dict(os.environ, env, clear=True):
            config = load_anthropic_config()

        self.assertEqual(config.timeout_seconds, 120.0)

    def test_max_tokens_from_env(self) -> None:
        env = {**BASE_ENV, "ANTHROPIC_MAX_TOKENS": "8192"}
        with patch.dict(os.environ, env, clear=True):
            config = load_anthropic_config()

        self.assertEqual(config.max_tokens, 8192)

    def test_invalid_timeout_raises(self) -> None:
        env = {**BASE_ENV, "ANTHROPIC_TIMEOUT_SECONDS": "not-a-number"}
        with patch.dict(os.environ, env, clear=True):
            with self.assertRaises(OrchestratorError) as ctx:
                load_anthropic_config()

        self.assertIn("ANTHROPIC_TIMEOUT_SECONDS", str(ctx.exception))

    def test_zero_timeout_raises(self) -> None:
        env = {**BASE_ENV, "ANTHROPIC_TIMEOUT_SECONDS": "0"}
        with patch.dict(os.environ, env, clear=True):
            with self.assertRaises(OrchestratorError) as ctx:
                load_anthropic_config()

        self.assertIn("ANTHROPIC_TIMEOUT_SECONDS", str(ctx.exception))


class WithMaxTokensTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = AnthropicConfig(
            api_key="test-key",
            model="claude-sonnet-5",
            max_tokens=16384,
            timeout_seconds=600.0,
        )

    def test_none_returns_same_config(self) -> None:
        result = with_max_tokens(self.config, None)
        self.assertIs(result, self.config)

    def test_overrides_max_tokens(self) -> None:
        result = with_max_tokens(self.config, 4096)
        self.assertEqual(result.max_tokens, 4096)
        self.assertEqual(result.timeout_seconds, self.config.timeout_seconds)
        self.assertEqual(result.model, self.config.model)

    def test_invalid_max_tokens_raises(self) -> None:
        with self.assertRaises(OrchestratorError) as ctx:
            with_max_tokens(self.config, 0)

        self.assertIn("--max-tokens", str(ctx.exception))


class LoadTestGenerationConfigTests(unittest.TestCase):
    def test_default_poc_max_tests_is_10(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            config = load_test_generation_config()

        self.assertEqual(config.max_tests, DEFAULT_POC_MAX_TESTS)
        self.assertEqual(config.max_tests, 10)

    def test_poc_max_tests_from_env(self) -> None:
        with patch.dict(os.environ, {"AI_QE_POC_MAX_TESTS": "8"}, clear=True):
            config = load_test_generation_config()

        self.assertEqual(config.max_tests, 8)

    def test_zero_poc_max_tests_from_env_raises(self) -> None:
        with patch.dict(os.environ, {"AI_QE_POC_MAX_TESTS": "0"}, clear=True):
            with self.assertRaises(OrchestratorError) as ctx:
                load_test_generation_config()

        self.assertIn("AI_QE_POC_MAX_TESTS", str(ctx.exception))


class WithMaxTestsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = TestGenerationConfig(max_tests=10)

    def test_none_returns_same_config(self) -> None:
        result = with_max_tests(self.config, None)
        self.assertIs(result, self.config)

    def test_overrides_max_tests(self) -> None:
        result = with_max_tests(self.config, 5)
        self.assertEqual(result.max_tests, 5)

    def test_zero_max_tests_raises(self) -> None:
        with self.assertRaises(OrchestratorError) as ctx:
            with_max_tests(self.config, 0)

        self.assertIn("--max-tests", str(ctx.exception))

    def test_negative_max_tests_raises(self) -> None:
        with self.assertRaises(OrchestratorError) as ctx:
            with_max_tests(self.config, -3)

        self.assertIn("--max-tests", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
