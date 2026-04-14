"""Shared utilities for .ctx scripts (build_distilled, ctx_validate, etc.)."""
import re

_FRONTMATTER_RE = re.compile(r'^---\n(.*?)\n---', re.DOTALL | re.MULTILINE)


def split_frontmatter(text: str) -> tuple[str, str]:
    """Split YAML frontmatter from body.

    Returns:
        (frontmatter_block, body) — frontmatter_block includes the --- markers,
        body is everything after.
    """
    stripped = text.lstrip("\ufeff")  # strip BOM
    if not stripped.startswith("---"):
        return "", stripped

    end = stripped.find("\n---", 3)
    if end == -1:
        return "", stripped

    end_pos = end + 4
    if end_pos < len(stripped) and stripped[end_pos] in ("\n", "\r"):
        end_pos += 1

    return stripped[:end_pos], stripped[end_pos:]


def extract_frontmatter_body(text: str) -> str:
    """Return only the frontmatter content (without --- markers)."""
    match = _FRONTMATTER_RE.search(text)
    return match.group(1) if match else ""


def parse_frontmatter_field(text: str, field: str) -> list[str]:
    """Extract a list field from YAML frontmatter.

    Supports:
    - Inline: 'field: [item1, item2]'
    - Block:  'field:\\n  - item1\\n  - item2'

    Returns: list of items, or [] if not found.
    """
    frontmatter = extract_frontmatter_body(text)
    if not frontmatter:
        return []

    # Pattern 1: field: [item1, item2]
    inline_match = re.search(
        rf'^{re.escape(field)}:\s*\[(.*?)\]',
        frontmatter,
        re.MULTILINE,
    )
    if inline_match:
        return [
            item.strip().strip('\'"')
            for item in inline_match.group(1).split(',')
            if item.strip()
        ]

    # Pattern 2: field:\n  - item1\n  - item2
    block_matches = re.findall(
        rf'^{re.escape(field)}:(?:\n  - (.+))+',
        frontmatter,
        re.MULTILINE,
    )
    if block_matches:
        return [item.strip().strip('\'"') for item in block_matches]

    return []


def parse_frontmatter_scalar(text: str, field: str) -> str | None:
    """Extract a scalar field from frontmatter (e.g. module: src/infra)."""
    frontmatter = extract_frontmatter_body(text)
    if not frontmatter:
        return None
    match = re.search(rf'^{re.escape(field)}:\s+(\S+)', frontmatter, re.MULTILINE)
    return match.group(1) if match else None
