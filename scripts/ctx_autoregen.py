#!/usr/bin/env python3
"""
ctx_autoregen.py — Incremental .ctx.md regeneration.

Updates ONLY stale .ctx.md files:
- Frontmatter fields (lines, modules, depends_on, provides) from CROSS_INDEX.json
- Leaves tier-tags and manual content intact
- Runs build_distilled.py at the end

Staleness = .ctx.md mtime older than newest source file in the package.

Usage:
    python scripts/ctx_autoregen.py

    # Source directory is read from .ctx/CTX_CONFIG.yaml (source_dir key).
    # Falls back to 'src' if not configured.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CTX_DIR = ROOT / ".ctx"
CTX_MODULES = CTX_DIR / "modules"
CROSS_INDEX = CTX_DIR / "CROSS_INDEX.json"
SCRIPTS_DIR = ROOT / "scripts"


def _get_source_dir() -> Path:
    """Read source_dir from CTX_CONFIG.yaml, fall back to 'src'."""
    config_path = CTX_DIR / "CTX_CONFIG.yaml"
    if config_path.exists():
        for line in config_path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped.startswith("source_dir:"):
                value = stripped.split(":", 1)[1].strip().strip("\"'")
                return ROOT / value
    return ROOT / "src"


def _run_script(name: str) -> bool:
    """Run a script in scripts/. Returns True on success."""
    script = SCRIPTS_DIR / name
    if not script.exists():
        print(f"ERROR: {script} not found", file=sys.stderr)
        return False
    print(f">>> Running {name} ...")
    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"ERROR in {name}:", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        return False
    for line in result.stdout.strip().splitlines():
        print(f"  {line}")
    return True


def _newest_source_mtime(source_dir: Path) -> float:
    """Newest mtime of source files under source_dir. Returns 0.0 if empty."""
    best = 0.0
    if not source_dir.is_dir():
        return best
    # Check .py files; add other extensions here if needed
    for f in source_dir.rglob("*.py"):
        if "__pycache__" in str(f):
            continue
        mt = f.stat().st_mtime
        if mt > best:
            best = mt
    return best


def _extract_frontmatter(text: str) -> tuple[str, str]:
    """Split frontmatter from body. Returns (frontmatter, body)."""
    m = re.match(r"(---\n.*?\n---)\n?(.*)", text, re.DOTALL)
    if not m:
        return "", text
    return m.group(1), m.group(2)


def _format_yaml_list(items: list[str]) -> str:
    return "[" + ", ".join(items) + "]"


def _update_frontmatter_field(fm: str, key: str, value: str) -> str:
    """Replace a single-line key: value entry in frontmatter."""
    pattern = re.compile(r"^(" + re.escape(key) + r":)\s*.*$", re.MULTILINE)
    return pattern.sub(f"{key}: {value}", fm, count=1)


def _module_from_frontmatter(fm: str) -> str | None:
    m = re.search(r"^module:\s*(.+)$", fm, re.MULTILINE)
    return m.group(1).strip() if m else None


def _source_from_frontmatter(fm: str) -> str | None:
    m = re.search(r"^source:\s*(.+)$", fm, re.MULTILINE)
    return m.group(1).strip() if m else None


def _pkg_key_from_module(module_field: str, source_dir_name: str) -> str | None:
    """Extract CROSS_INDEX key from module: field.

    'src/agents'        -> 'agents'
    'src/training/core' -> 'training'  (top-level package)
    """
    prefix = f"{source_dir_name}/"
    if not module_field.startswith(prefix):
        return None
    rest = module_field[len(prefix):]
    return rest.split("/")[0] if rest else None


def main() -> None:
    # Step 1: refresh CROSS_INDEX.json
    if not _run_script("ctx_scan.py"):
        print("ABORT: ctx_scan.py failed", file=sys.stderr)
        sys.exit(1)
    print()

    if not CROSS_INDEX.exists():
        print(f"ERROR: {CROSS_INDEX} not found", file=sys.stderr)
        sys.exit(1)

    with open(CROSS_INDEX, encoding="utf-8") as f:
        cross_index: dict = json.load(f)

    source_dir = _get_source_dir()
    source_dir_name = source_dir.name

    # Step 2: find stale .ctx.md files and update them
    ctx_files = sorted(CTX_MODULES.glob("*.ctx.md"))
    if not ctx_files:
        print(f"No .ctx.md files found in {CTX_MODULES}")
        sys.exit(0)

    updated: list[str] = []
    skipped_fresh: list[str] = []
    skipped_no_index: list[str] = []
    errors: list[str] = []

    for ctx_path in ctx_files:
        fname = ctx_path.name
        text = ctx_path.read_text(encoding="utf-8")
        frontmatter, body = _extract_frontmatter(text)
        if not frontmatter:
            errors.append(f"{fname}: No frontmatter found")
            continue

        module_field = _module_from_frontmatter(frontmatter)
        source_field = _source_from_frontmatter(frontmatter)
        if not module_field or not source_field:
            errors.append(f"{fname}: Missing 'module:' or 'source:' in frontmatter")
            continue

        # Staleness check
        source_path = ROOT / source_field.rstrip("/")
        newest = _newest_source_mtime(source_path)
        ctx_mtime = ctx_path.stat().st_mtime

        if newest <= ctx_mtime:
            skipped_fresh.append(fname)
            continue

        pkg_key = _pkg_key_from_module(module_field, source_dir_name)
        if not pkg_key or pkg_key not in cross_index:
            skipped_no_index.append(fname)
            continue

        entry = cross_index[pkg_key]
        new_fm = frontmatter
        new_fm = _update_frontmatter_field(new_fm, "lines", str(entry.get("lines", 0)))
        new_fm = _update_frontmatter_field(new_fm, "modules", str(entry.get("files", 0)))
        new_fm = _update_frontmatter_field(new_fm, "depends_on", _format_yaml_list(entry.get("depends_on", [])))
        new_fm = _update_frontmatter_field(new_fm, "provides", _format_yaml_list(entry.get("classes", [])))

        ctx_path.write_text(new_fm + "\n" + body, encoding="utf-8")
        updated.append(fname)

    # Step 3: rebuild distillates
    print()
    if not _run_script("build_distilled.py"):
        print("WARNING: build_distilled.py failed", file=sys.stderr)

    # Summary
    print()
    print("=" * 60)
    print("ctx_autoregen — Summary")
    print("=" * 60)
    print(f"  Total .ctx.md files:  {len(ctx_files)}")
    print(f"  Updated (stale):      {len(updated)}")
    print(f"  Skipped (fresh):      {len(skipped_fresh)}")
    print(f"  Skipped (no index):   {len(skipped_no_index)}")
    if errors:
        print(f"  Errors:               {len(errors)}")

    if updated:
        print("\nUpdated:")
        for name in updated:
            print(f"  - {name}")
    if skipped_no_index:
        print("\nNo CROSS_INDEX entry (sub-packages?):")
        for name in skipped_no_index:
            print(f"  - {name}")
    if errors:
        print("\nErrors:")
        for msg in errors:
            print(f"  ! {msg}")


if __name__ == "__main__":
    main()
