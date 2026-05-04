"""CLI for precedent_engine — `python -m precedent_engine search ...`"""
from __future__ import annotations

import argparse
import sys

from .search import fan_out_search


def _print_report(report, show_trail: bool) -> None:
    verdict = report.verdict
    print(f"\n=== Precedent Search: verb={report.verb!r} target={report.target!r} ===")
    print(f"  Stores queried: {len(report.stores_queried)} ({', '.join(report.stores_queried)})")
    for store, results in report.matches_by_store.items():
        print(f"    {store:20s}: {len(results):3d} match{'es' if len(results) != 1 else ''}")
    print()
    print(f"  Verdict: {verdict.verdict}")
    print(f"  Dimensions met: {verdict.dimensions_met}/4")
    for reason in verdict.reasons:
        print(f"    - {reason}")
    if verdict.most_recent_days is not None:
        print(f"  Most recent precedent: {verdict.most_recent_days} days ago")
    if verdict.sample_size > 0:
        print(f"  Sample size: {verdict.sample_size}")

    if show_trail:
        print("\n--- Search trail ---")
        for store, results in report.matches_by_store.items():
            if not results:
                continue
            print(f"\n  [{store}]")
            for m in results[:5]:
                ts = m.timestamp.strftime("%Y-%m-%d") if m.timestamp else "no-ts"
                print(f"    {ts}  {m.citation}")
                print(f"      → {m.excerpt[:140]}")
            if len(results) > 5:
                print(f"    ... and {len(results) - 5} more")
    print()


def _cmd_search(args) -> int:
    report = fan_out_search(verb=args.verb, target=args.target, days=args.days)
    _print_report(report, show_trail=args.show_trail)
    return 0 if report.verdict.verdict != "NO_PRECEDENT" else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="precedent_engine",
        description="L3 precedent search — fans out to action_ledger + feedback + plans + git per SOP-IV-PPC-001",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_search = sub.add_parser("search", help="Search for precedent matching verb+target")
    p_search.add_argument("--verb", required=True, help="Decision verb (e.g., merged, deleted, classified)")
    p_search.add_argument("--target", required=True, help="Decision target (e.g., PR_15, .bak_dir)")
    p_search.add_argument("--days", type=int, default=None, help="Restrict to last N days (default: no limit)")
    p_search.add_argument("--show-trail", action="store_true", help="Print full match list with citations")
    p_search.set_defaults(func=_cmd_search)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
