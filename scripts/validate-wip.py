#!/usr/bin/env python3
"""WIP limit enforcement for the eight-organ system.

Checks work-in-progress counts against limits defined in governance-rules.json.
Reports per-organ summaries and warns when limits are exceeded.

Usage:
    python3 scripts/validate-wip.py
    python3 scripts/validate-wip.py --registry path/to/registry-v2.json
    python3 scripts/validate-wip.py --governance governance-rules.json
"""
import argparse
import json
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

ORG_TO_ORGAN = {
    "organvm-i-theoria": "ORGAN-I",
    "organvm-ii-poiesis": "ORGAN-II",
    "organvm-iii-ergon": "ORGAN-III",
    "organvm-iv-taxis": "ORGAN-IV",
    "organvm-v-logos": "ORGAN-V",
    "organvm-vi-koinonia": "ORGAN-VI",
    "organvm-vii-kerygma": "ORGAN-VII",
    "meta-organvm": "META-ORGANVM",
}

WORKSPACE = Path.home() / "Workspace"
SCRIPT_DIR = Path(__file__).resolve().parent
SCRIPT_WORKSPACE = SCRIPT_DIR.parents[2]
DEFAULT_REGISTRY_CANDIDATES = (
    WORKSPACE / "meta-organvm" / "organvm-corpvs-testamentvm" / "registry-v2.json",
    SCRIPT_WORKSPACE / "meta-organvm" / "organvm-corpvs-testamentvm" / "registry-v2.json",
)


def resolve_default_registry() -> Path | None:
    """Return first existing canonical registry path, if available."""
    for candidate in DEFAULT_REGISTRY_CANDIDATES:
        if candidate.is_file():
            return candidate.resolve()
    return None


def load_registry(path: str) -> dict:
    """Load registry with fallback to meta-organvm if needed."""
    requested_path = (Path.cwd() / path).resolve()
    resolved_path = requested_path

    if not requested_path.is_file():
        default_registry = resolve_default_registry()
        if default_registry is None:
            tried = ", ".join(str(p) for p in DEFAULT_REGISTRY_CANDIDATES)
            raise FileNotFoundError(
                f"Registry not found at {requested_path}; "
                f"no canonical registry found in [{tried}]"
            )
        print(f"Registry {requested_path} not found. Falling back to {default_registry}")
        resolved_path = default_registry

    with resolved_path.open(encoding="utf-8") as f:
        data = json.load(f)

    # Handle redirect files
    if "_redirect" in data and "organs" not in data:
        default_registry = resolve_default_registry()
        if default_registry is None:
            raise FileNotFoundError("Registry is a redirect but no canonical registry found")
        print(f"Registry {resolved_path} is a redirect. Following to {default_registry}")
        with default_registry.open(encoding="utf-8") as f:
            data = json.load(f)

    return data


def load_governance(path: str) -> dict:
    """Load governance rules."""
    governance_path = (Path.cwd() / path).resolve()
    with governance_path.open(encoding="utf-8") as f:
        return json.load(f)


def count_by_organ(registry: dict) -> dict:
    """Count repos per organ by promotion_status."""
    counts = {}
    for organ_id, organ in registry.get("organs", {}).items():
        organ_counts = {
            "total": 0,
            "LOCAL": 0,
            "CANDIDATE": 0,
            "PUBLIC_PROCESS": 0,
            "GRADUATED": 0,
            "ARCHIVED": 0,
            "active_recent": 0,
        }
        for repo in organ.get("repositories", []):
            status = repo.get("promotion_status", "LOCAL")
            organ_counts["total"] += 1
            organ_counts[status] = organ_counts.get(status, 0) + 1
        counts[organ_id] = organ_counts
    return counts


def count_active_work(registry: dict, window_days: int) -> dict:
    """Count repos with last_validated within the active work window."""
    cutoff = datetime.now(UTC) - timedelta(days=window_days)
    active = {}
    for organ_id, organ in registry.get("organs", {}).items():
        count = 0
        for repo in organ.get("repositories", []):
            last_validated = repo.get("last_validated")
            if not last_validated:
                continue
            try:
                validated_dt = datetime.fromisoformat(
                    last_validated.replace("Z", "+00:00")
                )
                if validated_dt >= cutoff:
                    count += 1
            except (ValueError, TypeError):
                continue
        active[organ_id] = count
    return active


def validate_wip(registry_path: str, governance_path: str) -> int:
    """Validate WIP limits. Returns count of over-limit warnings."""
    registry = load_registry(registry_path)
    governance = load_governance(governance_path)

    wip_limits = governance.get("wip_limits")
    if not wip_limits:
        print("No wip_limits section found in governance-rules.json.")
        print("Add wip_limits to enable WIP enforcement.")
        return 0

    enforcement = wip_limits.get("enforcement", "warn")
    window_days = wip_limits.get("active_work_window_days", 14)
    max_pp_per_organ = wip_limits.get("public_process_per_organ", 5)
    max_active_per_organ = wip_limits.get("active_work_per_organ", 3)
    max_promotions = wip_limits.get("active_promotions_system_wide", 3)

    counts = count_by_organ(registry)
    active = count_active_work(registry, window_days)

    version = registry.get("version", "unknown")
    print(f"WIP Limit Report (Registry v{version})")
    print(f"{'=' * 65}")
    print(f"Enforcement: {enforcement}")
    print(f"Active work window: {window_days} days")
    print()

    # Per-organ summary table
    header = f"{'Organ':<16} {'Total':>5} {'LOC':>4} {'CAN':>4} {'PUB':>4} {'GRD':>4} {'ARC':>4} {'Active':>6}"
    print(header)
    print("-" * len(header))

    warnings = []
    total_pp = 0

    for organ_id in sorted(counts.keys()):
        c = counts[organ_id]
        a = active.get(organ_id, 0)
        total_pp += c["PUBLIC_PROCESS"]

        print(
            f"{organ_id:<16} {c['total']:>5} "
            f"{c['LOCAL']:>4} {c['CANDIDATE']:>4} {c['PUBLIC_PROCESS']:>4} "
            f"{c['GRADUATED']:>4} {c['ARCHIVED']:>4} {a:>6}"
        )

        if c["PUBLIC_PROCESS"] > max_pp_per_organ:
            warnings.append(
                f"  {organ_id}: {c['PUBLIC_PROCESS']} PUBLIC_PROCESS repos "
                f"(limit: {max_pp_per_organ})"
            )
        if a > max_active_per_organ:
            warnings.append(
                f"  {organ_id}: {a} actively worked repos in last {window_days} days "
                f"(limit: {max_active_per_organ})"
            )

    print()

    # System-wide checks
    if total_pp > max_promotions:
        warnings.append(
            f"  System-wide: {total_pp} total PUBLIC_PROCESS repos "
            f"(promotion limit: {max_promotions})"
        )

    # Report warnings
    if warnings:
        print(f"OVER-LIMIT WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(w)
        print()
        if enforcement == "warn":
            print("Enforcement is 'warn' — these are advisory. Finish existing work first.")
        else:
            print("Enforcement is 'block' — resolve over-limit conditions before new work.")
    else:
        print("All WIP limits within bounds.")

    print()

    # Exit code depends on enforcement mode
    if enforcement == "block" and warnings:
        return len(warnings)
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Validate work-in-progress limits across the eight-organ system"
    )
    parser.add_argument(
        "--registry",
        default="registry.json",
        help="Path to registry JSON (default: registry.json, falls back to canonical)",
    )
    parser.add_argument(
        "--governance",
        default="governance-rules.json",
        help="Path to governance-rules.json (default: governance-rules.json)",
    )
    args = parser.parse_args()

    warning_count = validate_wip(args.registry, args.governance)
    sys.exit(1 if warning_count > 0 else 0)


if __name__ == "__main__":
    main()
