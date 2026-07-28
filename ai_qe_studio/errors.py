"""Custom exceptions for the AI-QE Studio orchestrator."""


class OrchestratorError(Exception):
    """Base exception for orchestrator failures."""


class MissingFileError(OrchestratorError):
    """Raised when a required file does not exist."""

    def __init__(self, path: str) -> None:
        self.path = path
        super().__init__(f"Required file not found: {path}")


class EmptyFileError(OrchestratorError):
    """Raised when a required file exists but has no usable content."""

    def __init__(self, path: str) -> None:
        self.path = path
        super().__init__(f"Required file is empty: {path}")


class OutputExistsError(OrchestratorError):
    """Raised when output would overwrite an existing file without permission."""

    def __init__(self, path: str) -> None:
        self.path = path
        super().__init__(
            f"Output already exists: {path}. "
            "Pass --overwrite to replace it."
        )


class AnthropicCallError(OrchestratorError):
    """Raised when an Anthropic API call fails."""

    def __init__(self, message: str) -> None:
        super().__init__(f"Anthropic API call failed: {message}")
