#!/usr/bin/env python3
"""
build_distilled.py — Tier Distillation Builder

Reads all .ctx.md files from modules/ and architecture/,
filters sections by tier tag, writes to .distilled/{tier}/,
and updates .distilled/MANIFEST.json with token counts.

Tiers:
    haiku   — fast workers (~25k tokens) — signatures + invariants
    sonnet  — manager agents (~50k tokens) — full API + patterns
    opus    — architect tasks (~90k tokens) — everything incl. rationale

Tier tags in .ctx.md section headers:
    <!-- all-tiers -->   Included in: haiku, sonnet, opus
    <!-- sonnet+ -->     Included in: sonnet, opus
    <!-- opus-only -->   Included in: opus only
    (no tag)             Treated as: opus-only (always included in opus)

Usage:
    # Build root project (modules/ + architecture/)
    python scripts/build_distilled.py

    # Build a named example project (examples/<name>/modules/ + architecture/)
    python scripts/build_distilled.py --project openclaw
"""

import argparse
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from itertools import chain
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

ROOT = Path(__file__).parent.parent

TIER_HAIKU = "haiku"
TIER_SONNET = "sonnet"
TIER_OPUS = "opus"
ALL_TIERS = [TIER_HAIKU, TIER_SONNET, TIER_OPUS]

TAG_ALL_TIERS = "<!-- all-tiers -->"
TAG_SONNET_PLUS = "<!-- sonnet+ -->"
TAG_OPUS_ONLY = "<!-- opus-only -->"

# Compiled once
_SECTION_RE = re.compile(r"^(#{1,6}\s+.*)$", re.MULTILINE)
_HEADER_PREFIX_RE = re.compile(r"^#{1,6}\s+")
_TAG_STRIP_RE = re.compile(r"\s*<!--\s*[\w+\-]+\s*-->")

# Globals, resolved in main()
SOURCES: list[Path] = []
DISTILLED_DIR: Path = ROOT / ".distilled"
MANIFEST_PATH: Path = DISTILLED_DIR / "MANIFEST.json"


def resolve_paths(project: str | None) -> tuple[list[Path], Path, Path]:
    """Return (source_dirs, distilled_dir, manifest_path) for root or a named project."""
    if project:
        base = ROOT / "examples" / project
        sources = [base / "modules", base / "architecture"]
        distilled_dir = base / ".distilled"
    else:
        base = ROOT
        sources = [base / "modules", base / "architecture"]
        distilled_dir = base / ".distilled"
    return sources, distilled_dir, distilled_dir / "MANIFEST.json"


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

def _split_frontmatter(text: str) -> tuple[str, str]:
    """Split YAML frontmatter (--- ... ---) from body. Returns (frontmatter, body)."""
    stripped = text.lstrip("\ufeff")
    if not stripped.startswith("---"):
        return "", stripped
    end = stripped.find("\n---", 3)
    if end == -1:
        return "", stripped
    end_pos = end + 4
    if end_pos < len(stripped) and stripped[end_pos] in ("\n", "\r"):
        end_pos += 1
    return stripped[:end_pos], stripped[end_pos:]


def _extract_tag(header: str) -> str | None:
    """Extract tier tag from a section header."""
    if TAG_ALL_TIERS in header:
        return TAG_ALL_TIERS
    if TAG_SONNET_PLUS in header:
        return TAG_SONNET_PLUS
    if TAG_OPUS_ONLY in header:
        return TAG_OPUS_ONLY
    return None  # no tag → implicitly opus-only


def _is_for_haiku(tag: str | None) -> bool:
    return tag == TAG_ALL_TIERS


def _is_for_sonnet(tag: str | None) -> bool:
    return tag in (TAG_ALL_TIERS, TAG_SONNET_PLUS)


def _is_for_opus(tag: str | None) -> bool:
    return tag != "__detail_only__"  # opus sees everything except explicit detail-only


def _parse_sections(body: str) -> list[dict]:
    """Split body into sections, each with header, tag, and content."""
    parts = _SECTION_RE.split(body)
    sections = []

    if parts[0].strip():
        sections.append({"header": None, "tag": None, "content": parts[0]})

    i = 1
    while i < len(parts) - 1:
        header = parts[i]
        content = parts[i + 1] if i + 1 < len(parts) else ""
        tag = _extract_tag(header)
        sections.append({"header": header, "tag": tag, "content": content})
        i += 2

    return sections


def _clean_header(header: str) -> str:
    """Remove ## prefix and tier-tag comments from a header."""
    name = _HEADER_PREFIX_RE.sub("", header)
    for tag in (TAG_ALL_TIERS, TAG_SONNET_PLUS, TAG_OPUS_ONLY):
        name = name.replace(tag, "")
    return name.strip()


def count_tokens(text: str) -> int:
    """Token estimate: ~4 chars/token."""
    return max(0, int(len(text) / 4.0))


# ---------------------------------------------------------------------------
# Distillation
# ---------------------------------------------------------------------------

def distill_file(ctx_path: Path) -> dict:
    """Process one .ctx.md file and return haiku/sonnet/opus versions."""
    try:
        raw = ctx_path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"  WARNING: Cannot read {ctx_path}: {exc}", file=sys.stderr)
        return {}

    frontmatter, body = _split_frontmatter(raw)
    sections = _parse_sections(body)

    haiku_parts = [frontmatter] if frontmatter else []
    sonnet_parts = [frontmatter] if frontmatter else []
    opus_parts = [frontmatter] if frontmatter else []
    haiku_sections: list[str] = []
    sonnet_sections: list[str] = []
    opus_sections: list[str] = []

    for sec in sections:
        has_content = bool(sec["content"].strip())
        header = sec["header"] or ""
        tag = sec["tag"]
        clean = _clean_header(header) if header else ""
        clean_header_line = (_TAG_STRIP_RE.sub("", header) if header else "")

        # Build part: header line (stripped of tag) + content
        part = (clean_header_line + "\n" + sec["content"]) if header else sec["content"]

        if _is_for_haiku(tag) and (has_content or header):
            haiku_parts.append(part)
            sonnet_parts.append(part)
            opus_parts.append(part)
            haiku_sections.append(clean)
            sonnet_sections.append(clean)
            opus_sections.append(clean)

        elif _is_for_sonnet(tag) and not _is_for_haiku(tag) and (has_content or header):
            sonnet_parts.append(part)
            opus_parts.append(part)
            sonnet_sections.append(clean)
            opus_sections.append(clean)

        elif _is_for_opus(tag) and not _is_for_sonnet(tag) and (has_content or header):
            opus_parts.append(part)
            opus_sections.append(clean)

    haiku_text = "\n".join(haiku_parts).rstrip() + "\n"
    sonnet_text = "\n".join(sonnet_parts).rstrip() + "\n"
    opus_text = "\n".join(opus_parts).rstrip() + "\n"

    return {
        TIER_HAIKU:  {"content": haiku_text,  "tokens": count_tokens(haiku_text),  "sections": haiku_sections},
        TIER_SONNET: {"content": sonnet_text, "tokens": count_tokens(sonnet_text), "sections": sonnet_sections},
        TIER_OPUS:   {"content": opus_text,   "tokens": count_tokens(opus_text),   "sections": opus_sections},
    }


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def collect_source_files() -> list[Path]:
    return sorted(
        chain.from_iterable(d.glob("*.ctx.md") for d in SOURCES if d.exists())
    )


def relative_key(path: Path) -> str:
    for source_dir in SOURCES:
        try:
            rel = path.relative_to(source_dir)
            return f"{source_dir.name}/{rel.stem.replace('.ctx', '')}"
        except ValueError:
            continue
    return path.stem


def build_all() -> dict | None:
    source_files = collect_source_files()
    if not source_files:
        print("No .ctx.md files found in modules/ or architecture/", file=sys.stderr)
        return None

    # Ensure output dirs exist
    for tier in ALL_TIERS:
        (DISTILLED_DIR / tier).mkdir(parents=True, exist_ok=True)

    manifest: dict = {
        "_comment": "Auto-generated by scripts/build_distilled.py. Do not edit manually.",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "tiers": {
            t: {"files": 0, "total_tokens": 0, "files_detail": {}}
            for t in ALL_TIERS
        },
    }

    print(f"Distilling {len(source_files)} files...\n")

    # Parallel distillation
    file_results: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=min(8, len(source_files))) as executor:
        futures = {executor.submit(distill_file, p): p for p in source_files}
        for future in as_completed(futures):
            ctx_path = futures[future]
            try:
                result = future.result()
            except Exception as exc:
                print(f"  -> {ctx_path.name} [ERROR: {exc}]", file=sys.stderr)
                continue
            if result:
                file_results[ctx_path.name] = result

    # Write results (sequential for consistent output)
    tier_dirs = {t: DISTILLED_DIR / t for t in ALL_TIERS}
    for filename in sorted(file_results):
        result = file_results[filename]
        h = result[TIER_HAIKU]["tokens"]
        s = result[TIER_SONNET]["tokens"]
        o = result[TIER_OPUS]["tokens"]
        print(f"  {filename:45s} haiku={h:5d}  sonnet={s:5d}  opus={o:5d}")

        for tier, tier_dir in tier_dirs.items():
            data = result[tier]
            (tier_dir / filename).write_text(data["content"], encoding="utf-8")
            m = manifest["tiers"][tier]
            m["files"] += 1
            m["total_tokens"] += data["tokens"]
            m["files_detail"][filename] = {
                "tokens": data["tokens"],
                "sections": data["sections"],
            }

    return manifest


def write_manifest(manifest: dict) -> None:
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Build .ctx tier distillates")
    parser.add_argument(
        "--project",
        metavar="NAME",
        default=None,
        help="Build a named example project under examples/<NAME>/ (default: root project)",
    )
    args = parser.parse_args()

    global SOURCES, DISTILLED_DIR, MANIFEST_PATH
    SOURCES, DISTILLED_DIR, MANIFEST_PATH = resolve_paths(args.project)

    label = f"examples/{args.project}" if args.project else "root"
    print(f"Building .ctx distillates ({label})...\n")

    manifest = build_all()
    if not manifest:
        return 1

    write_manifest(manifest)

    print(f"\nManifest: {MANIFEST_PATH.relative_to(ROOT)}")
    print("\nSummary:")
    for tier in ALL_TIERS:
        data = manifest["tiers"][tier]
        print(f"  {tier:6s}  {data['files']:2d} files  ~{data['total_tokens']:6d} tokens")

    return 0


if __name__ == "__main__":
    sys.exit(main())
