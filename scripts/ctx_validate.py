#!/usr/bin/env python3
"""
ctx_validate.py — Validate bidirectionality and CROSS_INDEX consistency.

Checks:
1. Bidirectionality: if A depends_on B, then B must list A in depended_by
2. CROSS_INDEX alignment: depends_on in .ctx.md must match CROSS_INDEX.json
3. Missing module: fields in frontmatter

Usage:
    python scripts/ctx_validate.py

Exit codes:
    0 — all checks passed
    1 — inconsistencies found
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _ctx_common import parse_frontmatter_field, parse_frontmatter_scalar

ROOT = Path(__file__).resolve().parents[1]
CTX_DIR = ROOT / ".ctx"


def _get_source_dir_name() -> str:
    """Read source_dir from CTX_CONFIG.yaml."""
    config_path = CTX_DIR / "CTX_CONFIG.yaml"
    if config_path.exists():
        for line in config_path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped.startswith("source_dir:"):
                return stripped.split(":", 1)[1].strip().strip("\"'")
    return "src"


def _pkg_from_module(text: str, source_dir_name: str) -> str | None:
    """Extract package name from 'module: src/...' frontmatter field."""
    module = parse_frontmatter_scalar(text, "module")
    if module and module.startswith(f"{source_dir_name}/"):
        rest = module[len(f"{source_dir_name}/"):]
        return rest.split("/")[0] if rest else None
    return None


def main() -> int:
    source_dir_name = _get_source_dir_name()
    errors: list[str] = []

    # 1. Load all .ctx.md files from modules/
    ctx_files = sorted((CTX_DIR / "modules").glob("*.ctx.md"))
    if not ctx_files:
        print(f"ERROR: No .ctx.md files found in {CTX_DIR / 'modules'}")
        return 1

    # 2. Load CROSS_INDEX.json
    cross_index_path = CTX_DIR / "CROSS_INDEX.json"
    if not cross_index_path.exists():
        print(f"ERROR: {cross_index_path} does not exist — run ctx_scan.py first")
        return 1

    try:
        cross_index: dict = json.loads(cross_index_path.read_text())
    except json.JSONDecodeError as e:
        print(f"ERROR: {cross_index_path} is not valid JSON: {e}")
        return 1

    # Build pkg → (Path, text) map
    pkg_map: dict[str, tuple[Path, str]] = {}
    for file in ctx_files:
        text = file.read_text()
        pkg = _pkg_from_module(text, source_dir_name)
        if pkg:
            pkg_map[pkg] = (file, text)

    # 3. Bidirectionality check
    for pkg, (file, text) in pkg_map.items():
        if "/" in pkg:
            continue  # skip sub-packages

        deps = parse_frontmatter_field(text, "depends_on")
        for dep in deps:
            dep_top = dep.split("/")[0]
            if dep_top not in pkg_map:
                continue
            _, dep_text = pkg_map[dep_top]
            dep_depended_by = parse_frontmatter_field(dep_text, "depended_by")
            if pkg not in dep_depended_by:
                errors.append(
                    f"BIDIRECTIONAL: {pkg} depends_on {dep}, "
                    f"but {dep_top} does not list {pkg} in depended_by"
                )

    # Check for missing module: fields
    for file in ctx_files:
        text = file.read_text()
        if not _pkg_from_module(text, source_dir_name):
            errors.append(f"FRONTMATTER: {file.name} missing 'module:' field")

    # 4. CROSS_INDEX alignment
    for file in ctx_files:
        text = file.read_text()
        pkg = _pkg_from_module(text, source_dir_name)
        if not pkg or "/" in pkg:
            continue  # already reported or sub-package

        ctx_deps = set(parse_frontmatter_field(text, "depends_on"))
        cross_deps = set(cross_index.get(pkg, {}).get("depends_on", []))

        if ctx_deps != cross_deps:
            errors.append(
                f"CROSS_INDEX: {pkg} — "
                f"ctx.md={sorted(ctx_deps)} vs cross_index={sorted(cross_deps)}"
            )

    # Report
    if errors:
        print(f"ERRORS: {len(errors)} inconsistencies found:\n")
        for e in errors:
            print(f"  {e}")
        return 1

    print(f"OK: {len(ctx_files)} .ctx.md files checked — all consistent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
