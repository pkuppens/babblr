#!/usr/bin/env python3
"""Check local Markdown link targets exist in the repository.

This script scans Markdown files for inline links/images and reference-style
link definitions, and fails when a local (relative) link target points to a
file or directory that does not exist. It ignores external URLs (http/https),
mailto links, and pure in-page anchors (e.g. `#section`).

It is designed to run in `pre-commit`, so it accepts a list of Markdown files
as CLI arguments and exits non-zero on any missing targets.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlparse


@dataclass(frozen=True)
class LinkOccurrence:
    """Represents a single Markdown link occurrence in a file."""

    source_file: Path
    source_line: int
    raw_target: str


def _is_local_target(target: str) -> bool:
    """Return True when `target` looks like a local path we should validate."""

    stripped = target.strip()
    if not stripped:
        return False
    if stripped.startswith("#"):
        return False

    parsed = urlparse(stripped)
    if parsed.scheme in {"http", "https", "mailto", "tel", "data"}:
        return False

    return True


def _normalize_target_for_fs(target: str) -> str:
    """Normalize a Markdown link target to a filesystem path string."""

    # Remove fragment/query: we only validate the file/directory exists.
    for sep in ("#", "?"):
        if sep in target:
            target = target.split(sep, 1)[0]

    target = target.strip()

    # Markdown allows link destinations wrapped in <...>.
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1].strip()

    return unquote(target)


def _extract_inline_link_targets(text: str, source_file: Path) -> list[LinkOccurrence]:
    """Extract inline Markdown link/image targets from `text`."""

    occurrences: list[LinkOccurrence] = []

    i = 0
    while True:
        start = text.find("](", i)
        if start == -1:
            break

        # Parse the `( ... )` destination with basic parenthesis balancing.
        j = start + 2  # points to the first char after '('
        depth = 1
        dest_start = j
        while j < len(text) and depth > 0:
            ch = text[j]
            if ch == "\\":  # skip escaped characters
                j += 2
                continue
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    break
            j += 1

        if depth != 0:
            # Unbalanced parentheses; let other tooling handle this.
            i = start + 2
            continue

        raw_dest = text[dest_start:j].strip()

        # Drop optional title part: (dest "title") or (dest 'title')
        # If the destination is in <...>, keep it intact (it may contain spaces).
        if raw_dest.startswith("<"):
            target = raw_dest
        else:
            target = raw_dest.split(maxsplit=1)[0] if raw_dest else raw_dest

        line = text.count("\n", 0, start) + 1
        occurrences.append(
            LinkOccurrence(source_file=source_file, source_line=line, raw_target=target)
        )
        i = j + 1

    return occurrences


def _extract_reference_definition_targets(
    text: str, source_file: Path
) -> list[LinkOccurrence]:
    """Extract reference-style link definition targets from `text`."""

    occurrences: list[LinkOccurrence] = []
    for idx, line_text in enumerate(text.splitlines(), start=1):
        stripped = line_text.lstrip()
        if not stripped.startswith("[") or "]: " not in stripped:
            continue

        # Very small parser for: [id]: destination (optional title...)
        try:
            after = stripped.split("]:", 1)[1].strip()
        except IndexError:
            continue

        if not after:
            continue

        if after.startswith("<"):
            target = after.split(">", 1)[0] + ">"
        else:
            target = after.split(maxsplit=1)[0]

        occurrences.append(
            LinkOccurrence(source_file=source_file, source_line=idx, raw_target=target)
        )

    return occurrences


def find_missing_local_link_targets(markdown_file: Path) -> list[str]:
    """Find missing local link targets in a Markdown file.

    Args:
        markdown_file (Path): Path to the Markdown file to check.

    Returns:
        list[str]: A list of human-readable error messages for missing targets.

    Raises:
        FileNotFoundError: If `markdown_file` does not exist.
        UnicodeDecodeError: If the file cannot be decoded as UTF-8.
    """

    text = markdown_file.read_text(encoding="utf-8")

    occurrences = []
    occurrences.extend(_extract_inline_link_targets(text, markdown_file))
    occurrences.extend(_extract_reference_definition_targets(text, markdown_file))

    missing: list[str] = []
    for occ in occurrences:
        if not _is_local_target(occ.raw_target):
            continue

        target = _normalize_target_for_fs(occ.raw_target)
        if not target:
            continue

        # Skip "rooted" paths like `/docs/...` (often website-root, not repo-root).
        if target.startswith(("/", "\\")):
            continue

        target_path = (markdown_file.parent / target).resolve()
        if not target_path.exists():
            missing.append(
                f"{occ.source_file.as_posix()}:{occ.source_line}: missing local link target `{target}`"
            )

    return missing


def main(argv: list[str]) -> int:
    """Check Markdown files provided on the command line for missing local link targets."""

    files = [Path(a) for a in argv[1:] if a.endswith(".md")]
    if not files:
        return 0

    errors: list[str] = []
    for md_file in files:
        if not md_file.exists():
            # pre-commit shouldn't pass non-existent files, but be defensive.
            errors.append(f"{md_file.as_posix()}: file does not exist")
            continue

        try:
            errors.extend(find_missing_local_link_targets(md_file))
        except UnicodeDecodeError as exc:
            errors.append(f"{md_file.as_posix()}: cannot decode as UTF-8 ({exc})")

    if errors:
        print("\n".join(errors))
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

