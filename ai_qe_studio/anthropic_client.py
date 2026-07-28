"""Anthropic API client wrapper."""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone

from anthropic import Anthropic

from ai_qe_studio.config import AnthropicConfig
from ai_qe_studio.errors import AnthropicCallError

logger = logging.getLogger(__name__)


def create_client(config: AnthropicConfig) -> Anthropic:
    """Create an Anthropic client from configuration."""
    return Anthropic(
        api_key=config.api_key,
        timeout=config.timeout_seconds,
    )


def extract_text(response: object) -> str:
    """Extract text blocks from an Anthropic message response."""
    content = getattr(response, "content", None)
    if not content:
        return ""

    return "".join(
        block.text
        for block in content
        if getattr(block, "type", None) == "text"
    )


def create_message(
    client: Anthropic,
    config: AnthropicConfig,
    *,
    system: str,
    user: str,
) -> str:
    """Send a message to Anthropic and return the text response."""
    system_chars = len(system)
    user_chars = len(user)
    started_at = datetime.now(timezone.utc).isoformat()
    start = time.perf_counter()

    logger.info(
        "Anthropic call starting: model=%s max_tokens=%s system_chars=%s "
        "user_chars=%s started_at=%s",
        config.model,
        config.max_tokens,
        system_chars,
        user_chars,
        started_at,
    )

    try:
        response = client.messages.create(
            model=config.model,
            max_tokens=config.max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
    except Exception as exc:
        raise AnthropicCallError(str(exc)) from exc

    elapsed = time.perf_counter() - start
    text = extract_text(response).strip()
    if not text:
        raise AnthropicCallError("Response contained no text content")

    logger.info(
        "Anthropic call completed: elapsed_seconds=%.1f response_chars=%s",
        elapsed,
        len(text),
    )

    return text
