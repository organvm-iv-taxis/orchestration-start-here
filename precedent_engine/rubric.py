"""3-of-4 rubric evaluator per SOP-IV-PPC-001 §2 Phase L3."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Iterable

from .stores import Match


@dataclass
class RubricVerdict:
    verdict: str  # "DICTATES" | "SUGGESTS" | "NO_PRECEDENT"
    reasons: list[str]
    sample_size: int
    most_recent_days: int | None
    coherence_pct: float | None
    domain_match: bool
    dimensions_met: int


def _days_since(ts: datetime | None) -> int | None:
    if ts is None:
        return None
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    delta = datetime.now(timezone.utc) - ts
    return delta.days


def evaluate(matches: Iterable[Match], verb: str, target: str,
             feedback_match_count: int = 0) -> RubricVerdict:
    """Apply 3-of-4 rubric:
    1. sample_size: n>=5 ledger OR >=2 feedback OR n=1 exact-match within 30 days
    2. recency: most recent within 30 days
    3. coherence: >=80% directional agreement (heuristic — same verb/target = agreement)
    4. domain_match: verb+target both present in the precedent (not analogous-only)
    """
    matches_list = list(matches)
    n = len(matches_list)
    if n == 0:
        return RubricVerdict(
            verdict="NO_PRECEDENT",
            reasons=["No matches found across all queried stores"],
            sample_size=0, most_recent_days=None, coherence_pct=None,
            domain_match=False, dimensions_met=0,
        )

    timestamps = [m.timestamp for m in matches_list if m.timestamp is not None]
    most_recent = max(timestamps) if timestamps else None
    days_recent = _days_since(most_recent)

    domain_match = all(
        (verb.lower() in m.excerpt.lower() and target.lower() in m.excerpt.lower())
        or (m.verb == verb and m.target == target)
        for m in matches_list
    )
    coherence_pct = 100.0 if domain_match else (
        sum(1 for m in matches_list if verb.lower() in m.excerpt.lower()
            or target.lower() in m.excerpt.lower()) / max(n, 1) * 100
    )

    sample_dim = (
        n >= 5
        or feedback_match_count >= 2
        or (n == 1 and domain_match and days_recent is not None and days_recent <= 30)
    )
    recency_dim = days_recent is not None and days_recent <= 30
    coherence_dim = coherence_pct >= 80
    domain_dim = domain_match

    dimensions_met = sum([sample_dim, recency_dim, coherence_dim, domain_dim])
    reasons = []
    if sample_dim:
        reasons.append(f"sample_size_OK (n={n}, feedback_n={feedback_match_count})")
    else:
        reasons.append(f"sample_size_below_threshold (n={n}, feedback_n={feedback_match_count})")
    if recency_dim:
        reasons.append(f"recency_OK ({days_recent}d)")
    else:
        reasons.append(f"recency_stale ({days_recent}d)" if days_recent is not None else "recency_unknown")
    if coherence_dim:
        reasons.append(f"coherence_OK ({coherence_pct:.0f}%)")
    else:
        reasons.append(f"coherence_low ({coherence_pct:.0f}%)")
    if domain_dim:
        reasons.append("domain_match_exact")
    else:
        reasons.append("domain_match_partial")

    verdict = "DICTATES" if dimensions_met >= 3 else "SUGGESTS"
    return RubricVerdict(
        verdict=verdict,
        reasons=reasons,
        sample_size=n,
        most_recent_days=days_recent,
        coherence_pct=coherence_pct,
        domain_match=domain_match,
        dimensions_met=dimensions_met,
    )
