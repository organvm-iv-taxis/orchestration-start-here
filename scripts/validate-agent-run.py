#!/usr/bin/env python3
"""Validate agent run directories against the F-57 logging standard.

Usage:
    python3 scripts/validate-agent-run.py /path/to/run-directory
    python3 scripts/validate-agent-run.py --all
    python3 scripts/validate-agent-run.py --all --agents-log /custom/path
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REQUIRED_FILES = ["manifest.json", "prompt.md", "session.log"]
OPTIONAL_FILES = ["patch.diff", "breadcrumb.md"]
MANIFEST_VERSION = "1.0"

REQUIRED_MANIFEST_FIELDS = [
    "version",
    "run_id",
    "session_id",
    "agent_name",
    "agent_type",
    "repo_path",
    "start_time",
    "end_time",
    "exit_status",
]

VALID_AGENT_TYPES = {"interactive", "non-interactive"}
VALID_EXIT_STATUSES = {"success", "failed", "rolled_back", "timeout", "cancelled"}

DEFAULT_AGENTS_LOG = Path.home() / ".local" / "share" / "organvm" / "agent-runs"


def validate_manifest(manifest_path: Path) -> list[str]:
    """Validate manifest.json against the schema. Returns list of errors."""
    errors: list[str] = []

    try:
        with open(manifest_path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return [f"manifest.json is not valid JSON: {e}"]
    except OSError as e:
        return [f"Cannot read manifest.json: {e}"]

    if not isinstance(data, dict):
        return ["manifest.json root must be an object"]

    # Check required fields
    for field in REQUIRED_MANIFEST_FIELDS:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    # Validate version
    if data.get("version") != MANIFEST_VERSION:
        errors.append(
            f"Expected version '{MANIFEST_VERSION}', got '{data.get('version')}'"
        )

    # Validate agent_type
    agent_type = data.get("agent_type")
    if agent_type and agent_type not in VALID_AGENT_TYPES:
        errors.append(
            f"Invalid agent_type '{agent_type}', must be one of: {VALID_AGENT_TYPES}"
        )

    # Validate exit_status
    exit_status = data.get("exit_status")
    if exit_status and exit_status not in VALID_EXIT_STATUSES:
        errors.append(
            f"Invalid exit_status '{exit_status}', must be one of: {VALID_EXIT_STATUSES}"
        )

    # Validate array fields are arrays
    for array_field in ["files_read", "files_written", "rollback_events"]:
        if array_field in data and not isinstance(data[array_field], list):
            errors.append(f"Field '{array_field}' must be an array")

    # Validate token_usage structure
    token_usage = data.get("token_usage")
    if token_usage is not None:
        if not isinstance(token_usage, dict):
            errors.append("Field 'token_usage' must be an object")
        else:
            for token_field in ["input_tokens", "output_tokens", "total_tokens"]:
                val = token_usage.get(token_field)
                if val is not None and not isinstance(val, int):
                    errors.append(
                        f"token_usage.{token_field} must be an integer"
                    )

    # Validate run_id matches directory name
    run_id = data.get("run_id")
    if run_id and run_id != manifest_path.parent.name:
        errors.append(
            f"run_id '{run_id}' does not match directory name "
            f"'{manifest_path.parent.name}'"
        )

    return errors


def validate_run_directory(run_dir: Path) -> tuple[list[str], list[str]]:
    """Validate a single run directory. Returns (errors, warnings)."""
    errors: list[str] = []
    warnings: list[str] = []

    if not run_dir.is_dir():
        return [f"Not a directory: {run_dir}"], []

    # Check required files
    for filename in REQUIRED_FILES:
        filepath = run_dir / filename
        if not filepath.exists():
            errors.append(f"Missing required file: {filename}")
        elif filepath.stat().st_size == 0:
            errors.append(f"Required file is empty: {filename}")

    # Check optional files
    for filename in OPTIONAL_FILES:
        filepath = run_dir / filename
        if filepath.exists() and filepath.stat().st_size == 0:
            warnings.append(f"Optional file exists but is empty: {filename}")

    # Validate manifest if it exists
    manifest_path = run_dir / "manifest.json"
    if manifest_path.exists():
        manifest_errors = validate_manifest(manifest_path)
        errors.extend(manifest_errors)

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate agent run directories against the F-57 logging standard."
    )
    parser.add_argument(
        "run_dir",
        nargs="?",
        type=Path,
        help="Path to a single run directory to validate",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Validate all run directories in $AGENTS_LOG",
    )
    parser.add_argument(
        "--agents-log",
        type=Path,
        default=None,
        help=f"Override $AGENTS_LOG path (default: {DEFAULT_AGENTS_LOG})",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results as JSON",
    )

    args = parser.parse_args()

    if not args.run_dir and not args.all:
        parser.error("Provide a run directory path or use --all")

    agents_log = args.agents_log or Path(
        __import__("os").environ.get("AGENTS_LOG", str(DEFAULT_AGENTS_LOG))
    )

    # Collect directories to validate
    dirs_to_validate: list[Path] = []

    if args.run_dir:
        dirs_to_validate.append(args.run_dir)
    elif args.all:
        if not agents_log.exists():
            print(f"AGENTS_LOG directory does not exist: {agents_log}")
            return 1
        dirs_to_validate = sorted(
            [d for d in agents_log.iterdir() if d.is_dir()],
            key=lambda p: p.name,
        )
        if not dirs_to_validate:
            print(f"No run directories found in {agents_log}")
            return 0

    # Validate
    total_errors = 0
    total_warnings = 0
    results: list[dict] = []

    for run_dir in dirs_to_validate:
        errors, warnings = validate_run_directory(run_dir)
        total_errors += len(errors)
        total_warnings += len(warnings)

        if args.json_output:
            results.append({
                "directory": str(run_dir),
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
            })
        else:
            status = "PASS" if not errors else "FAIL"
            print(f"{status}  {run_dir.name}")

            for error in errors:
                print(f"  ERROR: {error}")
            for warning in warnings:
                print(f"  WARN:  {warning}")

    if args.json_output:
        print(json.dumps({"results": results, "total_errors": total_errors}, indent=2))
    else:
        print(f"\n{'─' * 40}")
        print(
            f"Validated {len(dirs_to_validate)} run(s): "
            f"{total_errors} error(s), {total_warnings} warning(s)"
        )

    return 1 if total_errors > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
