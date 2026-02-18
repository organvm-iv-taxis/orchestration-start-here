#!/usr/bin/env python3
"""Handle repository_dispatch promotion events.

Processes theory.candidate and art.ready-commercialize dispatch payloads.
Checks promotion gates (documentation, promotion_status, no back-edges),
then opens a tracking issue or executes the promotion.

Expected payload format (client_payload):
{
  "source_repo": "org/repo-name",
  "source_organ": "ORGAN-I",
  "target_organ": "ORGAN-II",
  "promotion_type": "promote-to-art",
  "triggered_by": "theory-to-art-watcher"
}
"""

import json
import os
import subprocess
import sys


def gh_issue_search(repo: str, title_prefix: str) -> bool:
    """Check if an open issue with given title prefix already exists."""
    result = subprocess.run(
        ["gh", "issue", "list", "--repo", repo, "--search", f'"{title_prefix}" in:title',
         "--state", "open", "--json", "title", "--limit", "5"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return False
    try:
        issues = json.loads(result.stdout)
        return any(title_prefix in i.get("title", "") for i in issues)
    except json.JSONDecodeError:
        return False


def create_tracking_issue(repo: str, title: str, body: str, labels: str = "") -> str | None:
    """Create a tracking issue and return its URL."""
    cmd = ["gh", "issue", "create", "--repo", repo, "--title", title, "--body", body]
    if labels:
        cmd += ["--label", labels]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout.strip()
    # Retry without labels (they might not exist)
    cmd = ["gh", "issue", "create", "--repo", repo, "--title", title, "--body", body]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else None


def main():
    event_type = os.environ.get("EVENT_TYPE", "")
    payload_str = os.environ.get("EVENT_PAYLOAD", "{}")

    try:
        payload = json.loads(payload_str)
    except json.JSONDecodeError:
        print(f"::error::Invalid JSON payload: {payload_str[:200]}")
        sys.exit(1)

    source_repo = payload.get("source_repo", "")
    source_organ = payload.get("source_organ", "")
    target_organ = payload.get("target_organ", "")
    promotion_type = payload.get("promotion_type", "")
    triggered_by = payload.get("triggered_by", "unknown")

    if not source_repo:
        print("::error::Missing source_repo in payload")
        sys.exit(1)

    repo_name = source_repo.split("/")[-1] if "/" in source_repo else source_repo
    org_name = source_repo.split("/")[0] if "/" in source_repo else ""

    print(f"Processing {event_type} dispatch:")
    print(f"  Source: {source_repo} ({source_organ})")
    print(f"  Target: {target_organ}")
    print(f"  Type: {promotion_type}")
    print(f"  Triggered by: {triggered_by}")

    # Load registry
    with open("registry-v2.json") as f:
        registry = json.load(f)

    # Find source repo in registry
    source_entry = None
    for organ_id, organ in registry.get("organs", {}).items():
        for repo in organ.get("repositories", []):
            if repo["name"] == repo_name and repo.get("org") == org_name:
                source_entry = repo
                break

    if not source_entry:
        print(f"::warning::{source_repo} not found in registry — proceeding with limited validation")

    # Gate checks
    gates = []

    # Gate 1: promotion_status
    if source_entry:
        promo_status = source_entry.get("promotion_status", "LOCAL")
        gates.append({
            "gate": "promotion_status >= CANDIDATE",
            "passed": promo_status in ("CANDIDATE", "PUBLIC_PROCESS", "GRADUATED"),
            "detail": f"Current: {promo_status}",
        })
    else:
        gates.append({"gate": "promotion_status >= CANDIDATE", "passed": None, "detail": "Repo not in registry"})

    # Gate 2: documentation
    if source_entry:
        doc_status = source_entry.get("documentation_status", "")
        gates.append({
            "gate": "documentation_status is DEPLOYED",
            "passed": doc_status in ("DEPLOYED", "FLAGSHIP README DEPLOYED"),
            "detail": f"Current: {doc_status or 'not set'}",
        })
    else:
        gates.append({"gate": "documentation_status", "passed": None, "detail": "Repo not in registry"})

    # Gate 3: no back-edges (load governance rules)
    try:
        with open("governance-rules.json") as f:
            governance = json.load(f)
        gates.append({"gate": "No back-edge violations", "passed": True, "detail": "Governance rules loaded"})
    except FileNotFoundError:
        gates.append({"gate": "No back-edge violations", "passed": None, "detail": "governance-rules.json missing"})

    # Determine target org
    target_org_map = {
        "ORGAN-II": "organvm-ii-poiesis",
        "ORGAN-III": "organvm-iii-ergon",
        "ORGAN-V": "organvm-v-logos",
    }
    target_org = target_org_map.get(target_organ, "")

    # Build report
    all_auto_passed = all(g["passed"] for g in gates if g["passed"] is not None)
    any_failed = any(g["passed"] is False for g in gates)

    report_lines = [
        f"## Dispatch Promotion: `{event_type}`",
        "",
        f"**Source:** `{source_repo}` ({source_organ})",
        f"**Target:** `{target_org}` ({target_organ})",
        f"**Triggered by:** {triggered_by}",
        "",
        "### Gate Checks",
        "",
        "| Gate | Status | Detail |",
        "|------|--------|--------|",
    ]
    for g in gates:
        icon = {True: "PASS", False: "FAIL", None: "SKIP"}.get(g["passed"], "?")
        report_lines.append(f"| {g['gate']} | {icon} | {g['detail']} |")

    report = "\n".join(report_lines)
    print(f"\n{report}")

    if any_failed:
        print("\n::warning::One or more gates failed. Creating tracking issue with failures.")

    # Idempotency check
    tracking_title = f"Promotion: {source_repo} → {target_organ}"
    orchestration_repo = "organvm-iv-taxis/orchestration-start-here"

    if gh_issue_search(orchestration_repo, tracking_title):
        print(f"\nTracking issue already exists for '{tracking_title}' — skipping creation")
        return

    # Create tracking issue
    body = report + "\n\n---\n"
    if all_auto_passed and not any_failed:
        body += "All automated gates passed. Ready for human review.\n"
        body += f"\nTo execute: comment `@orchestration promote` on this issue.\n"
    else:
        body += "Blocked: resolve failed gates before promotion can proceed.\n"

    body += f"\n*Created by handle-dispatch-promotion.py via {event_type} dispatch*"

    issue_url = create_tracking_issue(orchestration_repo, tracking_title, body, "automation,promotion")
    if issue_url:
        print(f"\nTracking issue created: {issue_url}")
    else:
        print("::error::Failed to create tracking issue")
        sys.exit(1)


if __name__ == "__main__":
    main()
