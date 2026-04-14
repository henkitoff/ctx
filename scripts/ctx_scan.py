#!/usr/bin/env python3
"""
ctx_scan.py — AST-based module scanner for Python projects.

Reads configuration from .ctx/CTX_CONFIG.yaml (single source of truth).
Generates: CROSS_INDEX.json, CTX_IR.jsonl, ANOMALIES.json

This script is Python-specific. For other languages, replace the AST
analysis section with the appropriate parser.

Usage:
    python scripts/ctx_scan.py
"""
import ast
import json
import os
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

ROOT = Path(__file__).resolve().parents[1]
CTX_DIR = ROOT / ".ctx"
CONFIG_PATH = CTX_DIR / "CTX_CONFIG.yaml"


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------

def _load_config() -> dict:
    """Load build config from CTX_CONFIG.yaml with fallback defaults."""
    if CONFIG_PATH.exists():
        text = CONFIG_PATH.read_text(encoding="utf-8")
        if yaml is not None:
            return yaml.safe_load(text)
        print("NOTE: PyYAML not installed — using built-in parser", file=sys.stderr)
        return _parse_simple_yaml(text)
    print(f"NOTE: {CONFIG_PATH} not found — using defaults", file=sys.stderr)
    return {
        "source_dir": "src",
        "internal_packages": [],
        "services": {},
        "limits": {"max_classes_per_package": 30, "max_functions_per_module": 20},
    }


def _coerce_value(v: str) -> int | bool | str:
    if v.isdigit():
        return int(v)
    low = v.lower()
    if low == "true":
        return True
    if low == "false":
        return False
    if len(v) >= 2 and v[0] == v[-1] and v[0] in ('"', "'"):
        return v[1:-1]
    return v


def _parse_simple_yaml(text: str) -> dict:
    """Minimal YAML parser for CTX_CONFIG.yaml (no PyYAML required).

    Supports only the structures that appear in CTX_CONFIG.yaml:
    top-level keys with nested lists and dicts.
    """
    result: dict = {}
    current_key = ""
    current_list: list | None = None
    current_dict: dict | None = None
    sub_dict: dict | None = None

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())

        if indent == 0 and ":" in stripped:
            key_part, _, val_part = stripped.partition(":")
            val_part = val_part.strip()
            if val_part:
                result[key_part] = _coerce_value(val_part)
                current_key = current_list = current_dict = sub_dict = None  # type: ignore[assignment]
                continue
            current_key = key_part
            current_list = current_dict = sub_dict = None  # type: ignore[assignment]
            continue

        if indent == 2 and stripped.startswith("- "):
            if current_list is None:
                current_list = []
                result[current_key] = current_list
            current_list.append(_coerce_value(stripped[2:]))
            continue

        if indent == 2 and stripped.endswith(":"):
            if current_dict is None:
                current_dict = {}
                result[current_key] = current_dict
            sub_dict = {}
            current_dict[stripped[:-1]] = sub_dict
            continue

        if indent == 4 and ":" in stripped and sub_dict is not None:
            k, v = stripped.split(":", 1)
            sub_dict[k.strip()] = _coerce_value(v.strip())

    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    CTX_DIR.mkdir(exist_ok=True)

    config = _load_config()
    source_dir_name = config.get("source_dir", "src")
    source_root = ROOT / source_dir_name
    internal_packages = set(config.get("internal_packages", []))
    service_metadata = config.get("services", {})
    limits = config.get("limits", {})
    max_classes = limits.get("max_classes_per_package", 30)
    max_functions = limits.get("max_functions_per_module", 20)

    if not source_root.exists():
        print(f"ERROR: source_dir '{source_dir_name}' not found at {source_root}", file=sys.stderr)
        print("Set 'source_dir' in .ctx/CTX_CONFIG.yaml to your source directory.", file=sys.stderr)
        sys.exit(1)

    # --- Analyze Python modules ---
    modules: dict = {}
    for pyfile in sorted(source_root.rglob("*.py")):
        if "__pycache__" in str(pyfile):
            continue
        rel = str(pyfile.relative_to(ROOT)).replace(os.sep, "/")
        source = pyfile.read_text(encoding="utf-8", errors="ignore")
        try:
            tree = ast.parse(source)
        except SyntaxError:
            modules[rel] = {"error": "SyntaxError"}
            continue

        # Walk AST for imports (can appear inside if-blocks, try-except, etc.)
        imports_from: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                imports_from.add(node.module.split(".")[0])
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    imports_from.add(alias.name.split(".")[0])

        # Top-level classes and public functions only
        classes = []
        functions = []
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith("_"):
                    functions.append(node.name)

        modules[rel] = {
            "imports": sorted(imports_from & internal_packages),
            "classes": classes[:max_classes],
            "functions": functions[:max_functions],
            "lines": source.count("\n") + (1 if source and not source.endswith("\n") else 0),
        }

    # --- Build package-level cross-index ---
    pkg_deps: dict = {}
    for path, info in modules.items():
        parts = path.replace(f"{source_dir_name}/", "").split("/")
        pkg = parts[0] if len(parts) > 1 else "root"
        if pkg not in pkg_deps:
            pkg_deps[pkg] = {"files": 0, "lines": 0, "depends_on": set(), "classes": []}
        pkg_deps[pkg]["files"] += 1
        pkg_deps[pkg]["lines"] += info.get("lines", 0)
        pkg_deps[pkg]["classes"].extend(info.get("classes", []))
        for dep in info.get("imports", []):
            if dep != pkg:
                pkg_deps[pkg]["depends_on"].add(dep)

    for k in pkg_deps:
        pkg_deps[k]["depends_on"] = sorted(pkg_deps[k]["depends_on"])
        pkg_deps[k]["classes"] = sorted(set(pkg_deps[k]["classes"]))[:max_classes]
        if k in service_metadata:
            pkg_deps[k]["service"] = service_metadata[k]

    with open(CTX_DIR / "CROSS_INDEX.json", "w", encoding="utf-8") as f:
        json.dump(pkg_deps, f, indent=2)

    with open(CTX_DIR / "CTX_IR.jsonl", "w", encoding="utf-8") as f:
        for path, info in sorted(modules.items()):
            f.write(json.dumps({"module": path, **info}) + "\n")

    # --- Anomaly detection ---
    anomalies: list[dict] = []

    # Circular dependency check
    for pkg, info in pkg_deps.items():
        for dep in info["depends_on"]:
            if dep in pkg_deps and pkg in pkg_deps[dep]["depends_on"]:
                anomalies.append({
                    "type": "circular_dependency",
                    "packages": sorted([pkg, dep]),
                    "severity": "warning",
                })

    # Orphan package check (1 file, no deps, no reverse deps)
    imported_by: dict[str, list] = {}
    for path, info in modules.items():
        for dep in info.get("imports", []):
            imported_by.setdefault(dep, []).append(path)

    for pkg, info in pkg_deps.items():
        if info["files"] == 1 and not info["depends_on"] and pkg not in imported_by:
            anomalies.append({"type": "orphan_package", "package": pkg, "severity": "info"})

    # Deduplicate
    seen: set[str] = set()
    deduped = []
    for a in anomalies:
        key = json.dumps(a, sort_keys=True)
        if key not in seen:
            seen.add(key)
            deduped.append(a)

    with open(CTX_DIR / "ANOMALIES.json", "w", encoding="utf-8") as f:
        json.dump(deduped, f, indent=2)

    # --- Report ---
    config_label = str(CONFIG_PATH) if CONFIG_PATH.exists() else "defaults"
    print(f"Config:    {config_label}")
    print(f"Source:    {source_root}")
    print(f"Analyzed:  {len(modules)} modules")
    print(f"Packages:  {len(pkg_deps)}")
    print(f"Anomalies: {len(deduped)}")
    print()
    for pkg, info in sorted(pkg_deps.items(), key=lambda x: -x[1]["lines"]):
        print(f"  {pkg:25s}  {info['files']:3d} files  {info['lines']:6d} LOC  deps: {info['depends_on']}")
    if deduped:
        print("\nAnomalies:")
        for a in deduped:
            print(f"  [{a['severity']}] {a['type']}: {a.get('packages', a.get('package', ''))}")


if __name__ == "__main__":
    main()
