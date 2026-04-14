#!/usr/bin/env python3
"""
new_knowledge.py — Knowledge Distillate Creator

Creates a new knowledge distillate from the template, archives the previous
LATEST.yaml, and opens the new file for editing.

Usage:
    python scripts/new_knowledge.py "Short topic description"
    python scripts/new_knowledge.py "Auth module refactor"

What it does:
    1. Archives knowledge/LATEST.yaml → knowledge/archive/YYYY-MM-DD_topic.yaml
       (skipped if LATEST is the initial placeholder)
    2. Copies knowledge/TEMPLATE.yaml → knowledge/LATEST.yaml
    3. Pre-fills date and topic
    4. Prints the path so you can open it in your editor
"""

import re
import shutil
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent.parent
KNOWLEDGE_DIR = ROOT / "knowledge"
LATEST = KNOWLEDGE_DIR / "LATEST.yaml"
TEMPLATE = KNOWLEDGE_DIR / "TEMPLATE.yaml"
ARCHIVE_DIR = KNOWLEDGE_DIR / "archive"


def slugify(text: str) -> str:
    """Convert topic text to a safe filename slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text[:60].rstrip("-")


def is_placeholder(path: Path) -> bool:
    """Return True if LATEST is still the initial placeholder (never filled in)."""
    try:
        content = path.read_text(encoding="utf-8")
        return "_state: initial" in content
    except FileNotFoundError:
        return True


def archive_latest(topic: str) -> Path | None:
    """Move LATEST.yaml to archive/. Return the archive path, or None if skipped."""
    if not LATEST.exists() or is_placeholder(LATEST):
        return None

    today = date.today().isoformat()
    slug = slugify(topic)
    archive_path = ARCHIVE_DIR / f"{today}_{slug}.yaml"

    # Avoid overwriting if a file with the same name already exists
    counter = 1
    while archive_path.exists():
        archive_path = ARCHIVE_DIR / f"{today}_{slug}_{counter}.yaml"
        counter += 1

    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(LATEST, archive_path)
    print(f"  Archived: knowledge/archive/{archive_path.name}")
    return archive_path


def create_new(topic: str) -> Path:
    """Copy template to LATEST, pre-fill date and topic."""
    if not TEMPLATE.exists():
        print(f"Error: template not found at {TEMPLATE}", file=sys.stderr)
        sys.exit(1)

    today = date.today().isoformat()
    content = TEMPLATE.read_text(encoding="utf-8")

    # Strip the header comment block (lines starting with #) from the template
    lines = content.splitlines(keepends=True)
    body_start = next(
        (i for i, line in enumerate(lines) if not line.startswith("#") and line.strip()),
        0,
    )
    body = "".join(lines[body_start:])

    # Pre-fill date and topic
    body = body.replace('date: "YYYY-MM-DD"', f'date: "{today}"')
    body = body.replace(
        'topic: "One-line description of what this session accomplished"',
        f'topic: "{topic}"',
    )

    header = (
        f"# Knowledge Distillate — {today}\n"
        f"# Topic: {topic}\n"
        f"# Created by: python scripts/new_knowledge.py\n"
        f"# Update this file during/after the session, then run the script again for the next session.\n\n"
    )

    LATEST.write_text(header + body, encoding="utf-8")
    return LATEST


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python scripts/new_knowledge.py \"Topic description\"", file=sys.stderr)
        print("Example: python scripts/new_knowledge.py \"Auth module refactor\"", file=sys.stderr)
        return 1

    topic = " ".join(sys.argv[1:]).strip()
    if not topic:
        print("Error: topic cannot be empty", file=sys.stderr)
        return 1

    print(f"\nCreating knowledge distillate: \"{topic}\"\n")

    archive_latest(topic)
    new_path = create_new(topic)

    print(f"  Created:  {new_path.relative_to(ROOT)}")
    print(f"\nOpen and fill in: {new_path}")
    print("Focus on: cross_session_patterns and next_session_hints — these are the highest-value fields.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
