from __future__ import annotations

import keyword
from pathlib import Path
import re
from string import Template
from typing import Sequence


_NON_ALNUM_RE = re.compile(r"[^0-9a-zA-Z]+")


def normalize_scaffold_name(raw_name: str, *, kind: str) -> str:
    normalized_name = _NON_ALNUM_RE.sub("-", raw_name.strip().lstrip("/"))
    normalized_name = normalized_name.strip("-").lower()
    if not normalized_name:
        raise ValueError(f"{kind} should not be empty")

    module_name = slug_to_module_name(normalized_name)
    if module_name[0].isdigit():
        raise ValueError(f"{kind} should not start with a digit")
    if not module_name.isidentifier():
        raise ValueError(f"Invalid {kind.lower()} `{raw_name}`")
    if keyword.iskeyword(module_name):
        raise ValueError(f"{kind} `{raw_name}` resolves to a Python keyword")

    return normalized_name


def slug_to_module_name(normalized_name: str) -> str:
    return normalized_name.replace("-", "_")


def module_name_to_pascal_case(module_name: str) -> str:
    return "".join(part.capitalize() for part in module_name.split("_"))


def write_template(path: Path, template: Template, context: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(template.safe_substitute(context), encoding="utf-8")


def append_marked_lines(
    path: Path,
    *,
    start_marker: str,
    end_marker: str,
    new_lines: Sequence[str],
) -> None:
    original_content = path.read_text(encoding="utf-8")
    trailing_newline = original_content.endswith("\n")
    lines = original_content.splitlines()

    try:
        start_index = lines.index(start_marker)
        end_index = lines.index(end_marker)
    except ValueError as exc:
        raise RuntimeError(
            f"Couldn't find scaffold markers in `{path}`",
        ) from exc

    if start_index >= end_index:
        raise RuntimeError(f"Invalid scaffold markers order in `{path}`")

    block_lines = lines[start_index + 1 : end_index]
    for new_line in new_lines:
        if new_line in block_lines:
            raise FileExistsError(f"`{new_line}` already exists in `{path}`")
        block_lines.append(new_line)

    updated_lines = lines[: start_index + 1] + block_lines + lines[end_index:]
    path.write_text(
        "\n".join(updated_lines) + ("\n" if trailing_newline else ""),
        encoding="utf-8",
    )
