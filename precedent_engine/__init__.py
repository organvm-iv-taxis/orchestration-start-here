"""Precedent search engine for the Protocol → Precedent → Constitutional framework.

Mechanizes Layer-3 (explicit precedent) search across action_ledger, feedback memories,
project artifact + session memories, originating plans, and git log. Returns a 3-of-4
rubric verdict per SOP-IV-PPC-001.

CLI entry: `python -m precedent_engine search --verb V --target T [--days N] [--show-trail]`
"""

__version__ = "0.1.0"
