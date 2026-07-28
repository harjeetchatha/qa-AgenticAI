"""File loading and output writing helpers."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from ai_qe_studio.errors import EmptyFileError, MissingFileError, OutputExistsError


def read_required_text(path: Path) -> str:
    """Read a required text file, failing on missing or empty content."""
    if not path.is_file():
        raise MissingFileError(str(path))

    content = path.read_text(encoding="utf-8")
    if not content.strip():
        raise EmptyFileError(str(path))

    return content


def ensure_output_writable(path: Path, *, overwrite: bool) -> None:
    """Refuse to overwrite an existing output file unless allowed."""
    if path.exists() and not overwrite:
        raise OutputExistsError(str(path))


def write_output(path: Path, content: str, *, overwrite: bool) -> None:
    """Write output content, refusing to overwrite unless allowed."""
    write_validated_output(path, content, overwrite=overwrite)


def write_validated_output(path: Path, content: str, *, overwrite: bool) -> None:
    """Atomically write validated output content to the destination path."""
    ensure_output_writable(path, overwrite=overwrite)

    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_path = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
    )
    temp_file = Path(temp_path)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
        os.replace(temp_file, path)
    except Exception:
        if temp_file.exists():
            temp_file.unlink()
        raise
