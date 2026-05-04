"""Search orchestrator — fans out to all stores per SOP-IV-PPC-001 §2 Phase L3."""
from __future__ import annotations

from dataclasses import dataclass, field

from . import stores
from .rubric import RubricVerdict, evaluate
from .stores import Match


@dataclass
class SearchReport:
    verb: str
    target: str
    days: int | None
    matches_by_store: dict[str, list[Match]] = field(default_factory=dict)
    verdict: RubricVerdict | None = None
    stores_queried: list[str] = field(default_factory=list)


def fan_out_search(verb: str, target: str, days: int | None = None) -> SearchReport:
    """Run all L3 store queries, evaluate rubric, return report."""
    report = SearchReport(verb=verb, target=target, days=days)
    keywords = [verb, target] if verb and target else [verb or target]

    queries = [
        ("action_ledger", lambda: stores.query_action_ledger(verb, target)),
        ("feedback", lambda: stores.query_feedback_memories(keywords)),
        ("project_artifact", lambda: stores.query_project_artifacts(keywords)),
        ("project_session", lambda: stores.query_project_sessions(keywords)),
        ("plans", lambda: stores.query_originating_plans(keywords, days=days)),
        ("git", lambda: stores.query_git_log(verb, target, days=days or 30)),
    ]

    all_matches: list[Match] = []
    for store_name, query_fn in queries:
        report.stores_queried.append(store_name)
        try:
            results = query_fn()
        except Exception as exc:
            results = []
            report.matches_by_store[store_name] = []
            print(f"  [warning] {store_name} query failed: {exc}")
            continue
        report.matches_by_store[store_name] = results
        all_matches.extend(results)

    feedback_n = len(report.matches_by_store.get("feedback", []))
    report.verdict = evaluate(all_matches, verb, target, feedback_match_count=feedback_n)
    return report
