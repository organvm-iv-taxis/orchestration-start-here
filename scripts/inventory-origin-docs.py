#!/usr/bin/env python3
"""
Origin Document Inventory Scanner

Walks meta-organvm/ and organvm-iv-taxis/ to catalogue every origin document,
classify it by type, and output a structured markdown inventory.

Usage:
    python3 scripts/inventory-origin-docs.py [--output PATH]
"""

import os
import sys
import re
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict

WORKSPACE = Path(os.environ.get("ORGANVM_WORKSPACE_DIR", Path.home() / "Workspace"))
META = WORKSPACE / "meta-organvm"
TAXIS = WORKSPACE / "organvm-iv-taxis"

# Verify paths exist; fall back to ~/Workspace if env var is wrong
if not META.exists():
    WORKSPACE = Path.home() / "Workspace"
    META = WORKSPACE / "meta-organvm"
    TAXIS = WORKSPACE / "organvm-iv-taxis"

# Directories to skip entirely
SKIP_DIRS = {
    ".git", ".venv", "node_modules", ".ruff_cache", ".pytest_cache",
    ".mypy_cache", "__pycache__", ".hypothesis", ".atoms",
    "conductor.egg-info", "organvm_schema_definitions.egg-info",
    "vox_architectura_gubernatio.egg-info",
}

# Paths to exclude (relative to tree root)
EXCLUDE_PATTERNS = [
    "contrib--",           # External forks
    "materia-collider/bench/",  # Frozen archive
    "portfolio-site/",     # Generated Astro site
    "a-i--skills/skills/", # Curated skill content (not origin)
    "a-i--skills/.build/", # Generated build artifacts
    ".build/",             # Generated artifacts
    "ecosystem/pillar-dna/",
    "ecosystem/snapshots/",
    "ecosystem/intelligence/",
]

# File extensions to inventory
ORIGIN_EXTENSIONS = {".md", ".yaml", ".yml", ".json", ".txt", ".gdoc"}

# Classification rules: (path_pattern, category)
# Order matters — first match wins
CLASSIFICATION_RULES = [
    (r"\.claude/memory/", "memory"),
    (r"\.claude/plans/", "plan"),
    (r"\.gemini/plans/", "plan"),
    (r"\.codex/plans/", "plan"),
    (r"post-flood/", "post-flood"),
    (r"sessions/claude-artifacts/", "session-artifact"),
    (r"sessions/claude/", "session-export"),
    (r"sessions/gemini/", "session-export"),
    (r"sessions/2026-", "session-record"),
    (r"\.conductor/", "conductor-trace"),
    (r"prompt-corpus/dialogues/", "dialogue"),
    (r"prompt-corpus/", "prompt-corpus"),
    (r"content-pipeline/", "content-pipeline"),
    (r"research/", "research"),
    (r"standards/", "standard"),
    (r"governance/", "governance"),
    (r"constitution/", "governance"),
    (r"specs/SPEC-", "spec-numbered"),
    (r"specs/", "spec"),
    (r"specifications/", "spec"),
    (r"schemas/", "schema"),
    (r"schema-definitions/", "schema"),
    (r"worksheets/", "voice-worksheet"),
    (r"corpus/", "corpus"),
    (r"testament/", "corpus"),
    (r"intake/", "intake"),
    (r"archive/", "archive"),
    (r"docs/adr/", "adr"),
    (r"docs/essays/", "essay"),
    (r"docs/pitch/", "pitch"),
    (r"docs/governance/", "governance"),
    (r"docs/specs/", "spec"),
    (r"docs/strategy/", "strategy"),
    (r"docs/", "doc"),
    (r"sops/", "sop"),
    (r"runbooks/", "runbook"),
    (r"lessons/", "lesson"),
    (r"studies/", "study"),
    (r"templates/", "template"),
    (r"process/", "process"),
    (r"policies/", "policy"),
    (r"data/", "data"),
    (r"essays/", "essay"),
    (r"_posts/", "post"),
    (r"publications/", "publication"),
    (r"defenses/", "defense"),
    (r"commissions/", "commission"),
    (r"ecosystem\.yaml$", "ecosystem-meta"),
    (r"network-map\.yaml$", "ecosystem-meta"),
    (r"seed\.yaml$", "seed-contract"),
    (r"CLAUDE\.md$", "agent-config"),
    (r"AGENTS\.md$", "agent-config"),
    (r"GEMINI\.md$", "agent-config"),
    (r"COMMANDMENTS\.md$", "governance"),
    (r"LOGIC_FRAMEWORK\.md$", "governance"),
    (r"ARCHITECTURE\.md$", "architecture"),
    (r"README\.md$", "readme"),
    (r"CHANGELOG\.md$", "changelog"),
    (r"CONTRIBUTING\.md$", "contributing"),
    (r"LICENSE", "license"),
]


@dataclass
class DocEntry:
    path: str
    relative_path: str
    tree: str  # "META" or "TAXIS"
    category: str
    extension: str
    size_bytes: int
    modified: str
    word_count: int
    has_frontmatter: bool
    title: str = ""


def should_skip_dir(name: str) -> bool:
    return name in SKIP_DIRS


def should_exclude(rel_path: str) -> bool:
    for pattern in EXCLUDE_PATTERNS:
        if pattern in rel_path:
            return True
    return False


def classify(rel_path: str, filename: str) -> str:
    full = rel_path + "/" + filename
    for pattern, category in CLASSIFICATION_RULES:
        if re.search(pattern, full):
            return category
    return "unclassified"


def extract_title(content: str) -> str:
    """Extract first heading or frontmatter name."""
    # Try frontmatter name
    fm_match = re.match(r"^---\n.*?^name:\s*(.+?)$.*?^---", content, re.MULTILINE | re.DOTALL)
    if fm_match:
        return fm_match.group(1).strip()
    # Try first heading
    h_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if h_match:
        return h_match.group(1).strip()
    return ""


def scan_tree(root: Path, tree_name: str) -> list[DocEntry]:
    entries = []
    for dirpath, dirnames, filenames in os.walk(root):
        # Prune skip dirs in-place
        dirnames[:] = [d for d in dirnames if not should_skip_dir(d)]

        rel_dir = str(Path(dirpath).relative_to(root))
        if should_exclude(rel_dir + "/"):
            dirnames.clear()
            continue

        for fname in filenames:
            ext = Path(fname).suffix.lower()
            if ext not in ORIGIN_EXTENSIONS:
                continue
            if fname.startswith(".DS_Store"):
                continue
            if fname in ("package-lock.json", "yarn.lock", "pnpm-lock.yaml"):
                continue

            full_path = Path(dirpath) / fname
            rel_path = str(full_path.relative_to(root))

            if should_exclude(rel_path):
                continue

            try:
                stat = full_path.stat()
                size = stat.st_size
                mtime = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d")
            except OSError:
                size = 0
                mtime = "unknown"

            # Read content for word count and frontmatter detection
            content = ""
            word_count = 0
            has_fm = False
            title = ""
            if ext in (".md", ".txt") and size < 500_000:  # Skip huge files
                try:
                    content = full_path.read_text(errors="ignore")
                    word_count = len(content.split())
                    has_fm = content.startswith("---")
                    title = extract_title(content)
                except Exception:
                    pass
            elif ext in (".yaml", ".yml", ".json"):
                try:
                    content = full_path.read_text(errors="ignore")
                    word_count = len(content.split())
                except Exception:
                    pass

            category = classify(rel_dir, fname)

            entries.append(DocEntry(
                path=str(full_path),
                relative_path=rel_path,
                tree=tree_name,
                category=category,
                extension=ext,
                size_bytes=size,
                modified=mtime,
                word_count=word_count,
                has_frontmatter=has_fm,
                title=title,
            ))

    return entries


def generate_inventory(entries: list[DocEntry]) -> str:
    """Generate the full inventory markdown."""
    lines = []
    lines.append("# Origin Document Inventory")
    lines.append(f"\n*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    lines.append(f"*Scanner: inventory-origin-docs.py*\n")

    # Grand summary
    meta_entries = [e for e in entries if e.tree == "META"]
    taxis_entries = [e for e in entries if e.tree == "TAXIS"]

    lines.append("## Summary\n")
    lines.append(f"| Domain | Files | Words | Categories |")
    lines.append(f"|--------|------:|------:|------------|")

    meta_cats = len(set(e.category for e in meta_entries))
    taxis_cats = len(set(e.category for e in taxis_entries))
    all_cats = len(set(e.category for e in entries))

    lines.append(f"| META-ORGANVM | {len(meta_entries):,} | {sum(e.word_count for e in meta_entries):,} | {meta_cats} |")
    lines.append(f"| ORGANVM-IV-TAXIS | {len(taxis_entries):,} | {sum(e.word_count for e in taxis_entries):,} | {taxis_cats} |")
    lines.append(f"| **Total** | **{len(entries):,}** | **{sum(e.word_count for e in entries):,}** | **{all_cats}** |")

    # Category breakdown
    lines.append("\n## By Category\n")
    cat_counts = defaultdict(lambda: {"count": 0, "words": 0, "meta": 0, "taxis": 0})
    for e in entries:
        cat_counts[e.category]["count"] += 1
        cat_counts[e.category]["words"] += e.word_count
        if e.tree == "META":
            cat_counts[e.category]["meta"] += 1
        else:
            cat_counts[e.category]["taxis"] += 1

    lines.append("| Category | Total | META | TAXIS | Words |")
    lines.append("|----------|------:|-----:|------:|------:|")
    for cat in sorted(cat_counts.keys(), key=lambda c: -cat_counts[c]["count"]):
        d = cat_counts[cat]
        lines.append(f"| {cat} | {d['count']:,} | {d['meta']:,} | {d['taxis']:,} | {d['words']:,} |")

    # Atomization readiness
    HIGH_READY = {"plan", "memory", "governance", "dialogue", "voice-worksheet",
                  "adr", "seed-contract", "agent-config", "sop", "standard"}
    MEDIUM_READY = {"post-flood", "research", "spec", "spec-numbered", "doc",
                    "schema", "corpus", "essay", "architecture", "strategy",
                    "process", "runbook", "pitch", "study", "lesson"}
    LOW_READY = {"session-export", "session-artifact", "session-record",
                 "conductor-trace", "intake", "content-pipeline"}

    lines.append("\n## Atomization Readiness\n")
    lines.append("| Readiness | Categories | Files |")
    lines.append("|-----------|-----------|------:|")

    high_count = sum(d["count"] for c, d in cat_counts.items() if c in HIGH_READY)
    med_count = sum(d["count"] for c, d in cat_counts.items() if c in MEDIUM_READY)
    low_count = sum(d["count"] for c, d in cat_counts.items() if c in LOW_READY)
    other_count = sum(d["count"] for c, d in cat_counts.items()
                      if c not in HIGH_READY and c not in MEDIUM_READY and c not in LOW_READY)

    lines.append(f"| HIGH | {', '.join(sorted(HIGH_READY & cat_counts.keys()))} | {high_count:,} |")
    lines.append(f"| MEDIUM | {', '.join(sorted(MEDIUM_READY & cat_counts.keys()))} | {med_count:,} |")
    lines.append(f"| LOW | {', '.join(sorted(LOW_READY & cat_counts.keys()))} | {low_count:,} |")
    if other_count:
        other_cats = sorted(set(cat_counts.keys()) - HIGH_READY - MEDIUM_READY - LOW_READY)
        lines.append(f"| UNCLASSIFIED | {', '.join(other_cats)} | {other_count:,} |")

    # Detailed file listing by category
    lines.append("\n---\n")
    lines.append("## Detailed Inventory\n")

    by_category = defaultdict(list)
    for e in entries:
        by_category[e.category].append(e)

    for cat in sorted(by_category.keys(), key=lambda c: -len(by_category[c])):
        cat_entries = by_category[cat]
        lines.append(f"\n### {cat} ({len(cat_entries):,} files)\n")
        lines.append("| Tree | Path | Words | Modified | FM |")
        lines.append("|------|------|------:|---------:|---:|")

        # Sort by tree then path
        for e in sorted(cat_entries, key=lambda x: (x.tree, x.relative_path)):
            fm = "Y" if e.has_frontmatter else ""
            # Truncate long paths
            display_path = e.relative_path
            if len(display_path) > 90:
                display_path = "..." + display_path[-87:]
            lines.append(f"| {e.tree} | `{display_path}` | {e.word_count:,} | {e.modified} | {fm} |")

    return "\n".join(lines) + "\n"


def main():
    if len(sys.argv) > 1:
        output_path = Path(sys.argv[1])
    else:
        output_path = TAXIS / "orchestration-start-here" / "ORIGIN-DOCUMENT-INVENTORY.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Scanning META-ORGANVM: {META}")
    meta_entries = scan_tree(META, "META")
    print(f"  Found {len(meta_entries):,} origin documents")

    print(f"Scanning ORGANVM-IV-TAXIS: {TAXIS}")
    taxis_entries = scan_tree(TAXIS, "TAXIS")
    print(f"  Found {len(taxis_entries):,} origin documents")

    all_entries = meta_entries + taxis_entries
    print(f"\nTotal: {len(all_entries):,} origin documents")

    inventory = generate_inventory(all_entries)
    output_path.write_text(inventory)
    print(f"\nInventory written to: {output_path}")

    # Print category summary to stdout
    cat_counts = defaultdict(int)
    for e in all_entries:
        cat_counts[e.category] += 1
    print("\nCategory breakdown:")
    for cat in sorted(cat_counts.keys(), key=lambda c: -cat_counts[c]):
        print(f"  {cat_counts[cat]:>6,}  {cat}")


if __name__ == "__main__":
    main()
