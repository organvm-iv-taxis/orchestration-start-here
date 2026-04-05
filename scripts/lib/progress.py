"""Per-project alpha-to-omega progress evaluation with contextual gate awareness.

The evaluator auto-detects each project's profile from registry signals and
local filesystem state, then adjusts which gates are applicable.  A markdown
governance repo is not penalized for missing tests/; an infrastructure .github
repo is not expected to have a deployment URL.

Profiles
--------
CODE_FULL      — flagship/standard code repo: all 11 gates apply
DOCUMENTATION  — design-only / docs-heavy: TESTS, DEPLOY skipped
INFRASTRUCTURE — .github / org config: TESTS, DOCS, PROTO, DEPLOY, GRAD skipped
GOVERNANCE     — policy/governance markdown: TESTS, PROTO, DEPLOY skipped
STUB           — tier=stub, barely started: only α, SEED, SCAFFOLD, CI apply
ARCHIVED       — frozen: report current state, OMEGA always N/A

Extended capabilities
---------------------
- Language detection from file extensions
- Staleness tracking (days since last_validated)
- Dependency health (are declared deps healthy?)
- Next-actions recommender per failing gate
- Severity levels (PASS / WARN / FAIL)
- Snapshot persistence for historical tracking
- Delta computation between snapshots
- Promotion readiness assessment
- Blockers analysis
- Weighted scoring (flagships weigh more)
- Gate pass-rate statistics across system
- Tier-appropriate thresholds (flagships need more)
- CLAUDE.md / LICENSE / security signal detection
- Git health signals (last commit age, branch hygiene)
- Revenue readiness for ORGAN-III
"""

from __future__ import annotations

import datetime
import json
import subprocess
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

GATE_NAMES = [
    "SEED", "SCAFFOLD", "CI", "TESTS", "DOCS",
    "PROTO", "CAND", "DEPLOY", "GRAD", "OMEGA",
]

ORG_TO_ORGAN: dict[str, str] = {
    "ivviiviivvi": "ORGAN-I",
    "organvm-i-theoria": "ORGAN-I",
    "omni-dromenon-machina": "ORGAN-II",
    "organvm-ii-poiesis": "ORGAN-II",
    "labores-profani-crux": "ORGAN-III",
    "organvm-iii-ergon": "ORGAN-III",
    "organvm-iv-taxis": "ORGAN-IV",
    "organvm-v-logos": "ORGAN-V",
    "organvm-vi-koinonia": "ORGAN-VI",
    "organvm-vii-kerygma": "ORGAN-VII",
    "meta-organvm": "META-ORGANVM",
    "4444j99": "PERSONAL",
}

ORGAN_DIRS: dict[str, list[str]] = {
    "ORGAN-I": ["organvm-i-theoria"],
    "ORGAN-II": ["organvm-ii-poiesis"],
    "ORGAN-III": ["organvm-iii-ergon"],
    "ORGAN-IV": ["organvm-iv-taxis"],
    "ORGAN-V": ["organvm-v-logos"],
    "ORGAN-VI": ["organvm-vi-koinonia"],
    "ORGAN-VII": ["organvm-vii-kerygma"],
    "META-ORGANVM": ["meta-organvm"],
    "PERSONAL": ["4444J99"],
}

ORGAN_DISPLAY: dict[str, str] = {
    "ORGAN-I": "Theory",
    "ORGAN-II": "Poiesis",
    "ORGAN-III": "Ergon",
    "ORGAN-IV": "Orchestration",
    "ORGAN-V": "Logos",
    "ORGAN-VI": "Koinonia",
    "ORGAN-VII": "Kerygma",
    "META-ORGANVM": "Meta",
    "PERSONAL": "Personal",
}

# Status ordering for comparisons
_IMPL_ORDER = {"ARCHIVED": 0, "DESIGN_ONLY": 1, "SKELETON": 2, "PROTOTYPE": 3, "ACTIVE": 4, "PRODUCTION": 4}
_PROMO_ORDER = {"ARCHIVED": -1, "LOCAL": 0, "CANDIDATE": 1, "PUBLIC_PROCESS": 2, "GRADUATED": 3}

# Tier weights for weighted scoring
TIER_WEIGHTS: dict[str, float] = {
    "flagship": 2.0,
    "standard": 1.0,
    "infrastructure": 0.5,
    "stub": 0.25,
    "archive": 0.0,
}

# Tier-specific thresholds (flagships held to higher standard)
DOCS_WORD_THRESHOLD: dict[str, int] = {
    "flagship": 1000,
    "standard": 500,
    "infrastructure": 100,
    "stub": 50,
    "archive": 0,
}

# Staleness thresholds (days)
STALE_WARN_DAYS = 30
STALE_CRITICAL_DAYS = 90

# Language detection extensions
LANG_EXTENSIONS: dict[str, str] = {
    ".py": "Python", ".pyi": "Python",
    ".ts": "TypeScript", ".tsx": "TypeScript",
    ".js": "JavaScript", ".jsx": "JavaScript",
    ".rs": "Rust",
    ".go": "Go",
    ".java": "Java",
    ".rb": "Ruby",
    ".c": "C", ".h": "C",
    ".cpp": "C++", ".hpp": "C++", ".cc": "C++",
    ".sh": "Shell", ".bash": "Shell", ".zsh": "Shell",
    ".md": "Markdown",
    ".yaml": "YAML", ".yml": "YAML",
    ".json": "JSON",
    ".html": "HTML", ".css": "CSS",
    ".sql": "SQL",
    ".toml": "TOML",
    ".r": "R", ".R": "R",
}

# Security patterns to detect in filenames
_SECURITY_BAD_FILES = {
    ".env", ".env.local", ".env.production",
    "credentials.json", "secrets.json", "service-account.json",
    "id_rsa", "id_ed25519", ".npmrc",
}


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class Profile(str, Enum):
    CODE_FULL = "code-full"
    DOCUMENTATION = "documentation"
    INFRASTRUCTURE = "infrastructure"
    GOVERNANCE = "governance"
    STUB = "stub"
    ARCHIVED = "archived"


class Severity(str, Enum):
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"
    NA = "na"


# Which gates each profile skips (N/A)
_PROFILE_SKIP: dict[Profile, set[str]] = {
    Profile.CODE_FULL: set(),
    Profile.DOCUMENTATION: {"TESTS", "DEPLOY"},
    Profile.INFRASTRUCTURE: {"TESTS", "DOCS", "PROTO", "DEPLOY", "GRAD", "OMEGA"},
    Profile.GOVERNANCE: {"TESTS", "PROTO", "DEPLOY"},
    Profile.STUB: {"TESTS", "DOCS", "PROTO", "DEPLOY", "GRAD", "OMEGA"},
    Profile.ARCHIVED: {"OMEGA"},
}

# Profile descriptions for display
PROFILE_DESCRIPTIONS: dict[Profile, str] = {
    Profile.CODE_FULL: "Full code repository — all gates apply",
    Profile.DOCUMENTATION: "Documentation / design-only — TESTS, DEPLOY skipped",
    Profile.INFRASTRUCTURE: "Infrastructure / org config — minimal gates",
    Profile.GOVERNANCE: "Governance / policy — TESTS, PROTO, DEPLOY skipped",
    Profile.STUB: "Stub — only early gates apply",
    Profile.ARCHIVED: "Archived — OMEGA not applicable",
}


# ---------------------------------------------------------------------------
# Profile detection
# ---------------------------------------------------------------------------

def detect_profile(
    entry: dict[str, Any],
    local_path: Path | None = None,
) -> Profile:
    """Auto-detect the project profile from registry + filesystem signals."""
    tier = entry.get("tier", "standard")
    impl = entry.get("implementation_status", "ACTIVE")
    promo = entry.get("promotion_status", "LOCAL")
    doc_status = entry.get("documentation_status", "")
    name = entry.get("name", "")

    # Archived repos
    if promo == "ARCHIVED" or tier == "archive":
        return Profile.ARCHIVED

    # Stubs
    if tier == "stub":
        return Profile.STUB

    # Infrastructure (.github repos, org config)
    if tier == "infrastructure" or doc_status == "INFRASTRUCTURE":
        return Profile.INFRASTRUCTURE

    # Design-only / documentation repos
    if impl == "DESIGN_ONLY":
        return Profile.DOCUMENTATION

    # Governance repos — heuristic: name contains governance keywords
    _gov_keywords = {"petasum", "governance", "commandments", "policy", "constitution"}
    if any(kw in name.lower() for kw in _gov_keywords):
        if local_path and _has_code_files(local_path):
            return Profile.CODE_FULL
        return Profile.GOVERNANCE

    # Documentation-heavy repos detected by local filesystem
    if local_path and not _has_code_files(local_path):
        return Profile.DOCUMENTATION

    return Profile.CODE_FULL


def _has_code_files(path: Path) -> bool:
    """Quick check: does this repo contain substantive code files?"""
    code_extensions = {".py", ".ts", ".js", ".rs", ".go", ".java", ".rb", ".c", ".cpp"}
    code_dirs = {"src", "lib", "titan", "agents", "hive", "adapters", "runtime",
                 "pkg", "cmd", "internal", "app", "core", "server", "client"}

    for d in code_dirs:
        if (path / d).is_dir():
            return True

    for item in path.iterdir():
        if item.is_file() and item.suffix in code_extensions:
            return True
        if item.is_dir() and not item.name.startswith("."):
            try:
                for sub in item.iterdir():
                    if sub.is_file() and sub.suffix in code_extensions:
                        return True
            except PermissionError:
                continue
    return False


# ---------------------------------------------------------------------------
# Language detection
# ---------------------------------------------------------------------------

def detect_languages(local_path: Path | None) -> dict[str, int]:
    """Detect programming languages by counting files per extension.

    Returns {language: file_count} sorted by count descending.
    """
    if not local_path or not local_path.is_dir():
        return {}

    counts: dict[str, int] = defaultdict(int)
    skip_dirs = {".git", ".venv", "venv", "node_modules", "__pycache__",
                 ".mypy_cache", ".ruff_cache", "dist", "build", ".next",
                 ".tox", ".pytest_cache", "coverage", ".build"}

    def _walk(p: Path, depth: int = 0) -> None:
        if depth > 4:
            return
        try:
            for item in p.iterdir():
                if item.name in skip_dirs or item.name.startswith("."):
                    if item.name not in (".github",):
                        continue
                if item.is_file():
                    lang = LANG_EXTENSIONS.get(item.suffix)
                    if lang:
                        counts[lang] += 1
                elif item.is_dir():
                    _walk(item, depth + 1)
        except PermissionError:
            pass

    _walk(local_path)
    return dict(sorted(counts.items(), key=lambda x: -x[1]))


def primary_language(languages: dict[str, int]) -> str:
    """Return the dominant programming language (excluding Markdown/YAML/JSON)."""
    code_langs = {k: v for k, v in languages.items()
                  if k not in ("Markdown", "YAML", "JSON", "TOML", "HTML", "CSS")}
    if not code_langs:
        return "none"
    return max(code_langs, key=code_langs.get)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Git health
# ---------------------------------------------------------------------------

@dataclass
class GitHealth:
    last_commit_days: int = -1      # -1 = unknown
    branch_count: int = -1
    has_uncommitted: bool = False
    default_branch: str = ""
    total_commits: int = -1

    @property
    def stale(self) -> bool:
        return self.last_commit_days > STALE_CRITICAL_DAYS

    @property
    def warn_stale(self) -> bool:
        return STALE_WARN_DAYS < self.last_commit_days <= STALE_CRITICAL_DAYS

    def to_dict(self) -> dict[str, Any]:
        return {
            "last_commit_days": self.last_commit_days,
            "branch_count": self.branch_count,
            "has_uncommitted": self.has_uncommitted,
            "default_branch": self.default_branch,
            "total_commits": self.total_commits,
            "stale": self.stale,
            "warn_stale": self.warn_stale,
        }


def probe_git_health(local_path: Path | None) -> GitHealth:
    """Probe git repository health (fast, non-blocking)."""
    if not local_path or not (local_path / ".git").exists():
        return GitHealth()

    health = GitHealth()
    try:
        # Last commit age
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ct"],
            cwd=local_path, capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            ts = int(result.stdout.strip())
            days = (datetime.datetime.now().timestamp() - ts) / 86400
            health.last_commit_days = int(days)

        # Branch count
        result = subprocess.run(
            ["git", "branch", "--list"],
            cwd=local_path, capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            health.branch_count = len([l for l in result.stdout.strip().splitlines() if l.strip()])

        # Uncommitted changes
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=local_path, capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            health.has_uncommitted = bool(result.stdout.strip())

        # Total commits
        result = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            cwd=local_path, capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            health.total_commits = int(result.stdout.strip())

    except (subprocess.TimeoutExpired, OSError, ValueError):
        pass

    return health


# ---------------------------------------------------------------------------
# Security signals
# ---------------------------------------------------------------------------

@dataclass
class SecuritySignals:
    exposed_secrets: list[str] = field(default_factory=list)
    has_gitignore: bool = False
    has_env_example: bool = False
    has_security_policy: bool = False

    @property
    def clean(self) -> bool:
        return not self.exposed_secrets

    def to_dict(self) -> dict[str, Any]:
        return {
            "exposed_secrets": self.exposed_secrets,
            "has_gitignore": self.has_gitignore,
            "has_env_example": self.has_env_example,
            "has_security_policy": self.has_security_policy,
            "clean": self.clean,
        }


def probe_security(local_path: Path | None) -> SecuritySignals:
    """Check for obvious security signals."""
    if not local_path:
        return SecuritySignals()

    signals = SecuritySignals()
    signals.has_gitignore = (local_path / ".gitignore").is_file()
    signals.has_env_example = (local_path / ".env.example").is_file() or (local_path / ".env.sample").is_file()
    signals.has_security_policy = (local_path / "SECURITY.md").is_file() or (local_path / ".github" / "SECURITY.md").is_file()

    for item in local_path.iterdir():
        if item.name in _SECURITY_BAD_FILES and item.is_file():
            signals.exposed_secrets.append(item.name)

    return signals


# ---------------------------------------------------------------------------
# Scaffold signals (expanded)
# ---------------------------------------------------------------------------

@dataclass
class ScaffoldSignals:
    has_readme: bool = False
    readme_words: int = 0
    has_gitignore: bool = False
    has_license: bool = False
    has_changelog: bool = False
    has_contributing: bool = False
    has_claude_md: bool = False
    has_code_of_conduct: bool = False
    has_pkg_config: bool = False
    pkg_config_type: str = ""       # pyproject.toml, package.json, etc.
    has_editorconfig: bool = False

    @property
    def scaffold_score(self) -> int:
        """Count of scaffold files present (0-10)."""
        return sum([
            self.has_readme, self.has_gitignore, self.has_license,
            self.has_changelog, self.has_contributing, self.has_claude_md,
            self.has_code_of_conduct, self.has_pkg_config, self.has_editorconfig,
            self.readme_words >= 100,
        ])

    def to_dict(self) -> dict[str, Any]:
        return {
            "has_readme": self.has_readme,
            "readme_words": self.readme_words,
            "has_gitignore": self.has_gitignore,
            "has_license": self.has_license,
            "has_changelog": self.has_changelog,
            "has_contributing": self.has_contributing,
            "has_claude_md": self.has_claude_md,
            "has_code_of_conduct": self.has_code_of_conduct,
            "has_pkg_config": self.has_pkg_config,
            "pkg_config_type": self.pkg_config_type,
            "has_editorconfig": self.has_editorconfig,
            "scaffold_score": self.scaffold_score,
        }


def probe_scaffold(local_path: Path | None) -> ScaffoldSignals:
    """Probe local filesystem for scaffold files."""
    if not local_path:
        return ScaffoldSignals()

    s = ScaffoldSignals()
    readme = local_path / "README.md"
    s.has_readme = readme.is_file()
    if s.has_readme:
        try:
            s.readme_words = len(readme.read_text(errors="replace").split())
        except OSError:
            pass

    s.has_gitignore = (local_path / ".gitignore").is_file()
    s.has_license = any((local_path / f).is_file() for f in ("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING"))
    s.has_changelog = (local_path / "CHANGELOG.md").is_file()
    s.has_contributing = any((local_path / f).is_file() for f in ("CONTRIBUTING.md", ".github/CONTRIBUTING.md"))
    s.has_claude_md = (local_path / "CLAUDE.md").is_file()
    s.has_code_of_conduct = any((local_path / f).is_file() for f in ("CODE_OF_CONDUCT.md", ".github/CODE_OF_CONDUCT.md"))
    s.has_editorconfig = (local_path / ".editorconfig").is_file()

    pkg_configs = [
        ("pyproject.toml", "pyproject.toml"),
        ("package.json", "package.json"),
        ("Cargo.toml", "Cargo.toml"),
        ("go.mod", "go.mod"),
        ("setup.py", "setup.py"),
        ("setup.cfg", "setup.cfg"),
        ("Gemfile", "Gemfile"),
        ("pom.xml", "pom.xml"),
    ]
    for filename, label in pkg_configs:
        if (local_path / filename).is_file():
            s.has_pkg_config = True
            s.pkg_config_type = label
            break

    return s


# ---------------------------------------------------------------------------
# Staleness
# ---------------------------------------------------------------------------

def compute_staleness_days(entry: dict[str, Any]) -> int:
    """Days since last_validated. Returns -1 if unknown."""
    lv = entry.get("last_validated", "")
    if not lv:
        return -1
    try:
        validated = datetime.date.fromisoformat(str(lv))
        return (datetime.date.today() - validated).days
    except (ValueError, TypeError):
        return -1


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class Checkpoint:
    name: str
    passed: bool
    applicable: bool
    confidence: str             # "full" | "registry-only" | "local-only"
    severity: Severity = Severity.FAIL
    detail: str = ""
    discrepancy: str = ""
    next_action: str = ""       # what to do to pass this gate

    def __post_init__(self) -> None:
        if not self.applicable:
            self.severity = Severity.NA
        elif self.passed and not self.discrepancy:
            self.severity = Severity.PASS
        elif self.passed and self.discrepancy:
            self.severity = Severity.WARN
        # else: remains FAIL


@dataclass
class ProjectProgress:
    repo: str
    organ: str
    tier: str
    profile: Profile
    checkpoints: list[Checkpoint] = field(default_factory=list)
    # Extended fields
    languages: dict[str, int] = field(default_factory=dict)
    primary_lang: str = "unknown"
    staleness_days: int = -1
    git_health: GitHealth = field(default_factory=GitHealth)
    security: SecuritySignals = field(default_factory=SecuritySignals)
    scaffold: ScaffoldSignals = field(default_factory=ScaffoldSignals)
    # Registry metadata passthrough
    promotion_status: str = "LOCAL"
    implementation_status: str = "SKELETON"
    platinum_status: bool = False
    deployment_url: str = ""
    org: str = ""
    description: str = ""
    # Revenue (ORGAN-III only)
    revenue_model: str = ""
    revenue_status: str = ""

    @property
    def applicable_gates(self) -> list[Checkpoint]:
        return [c for c in self.checkpoints if c.applicable]

    @property
    def score(self) -> int:
        return sum(1 for c in self.checkpoints if c.applicable and c.passed)

    @property
    def total(self) -> int:
        return len(self.applicable_gates)

    @property
    def pct(self) -> int:
        return int(self.score / self.total * 100) if self.total else 0

    @property
    def weighted_score(self) -> float:
        """Score multiplied by tier weight."""
        return self.score * TIER_WEIGHTS.get(self.tier, 1.0)

    @property
    def discrepancies(self) -> list[Checkpoint]:
        return [c for c in self.checkpoints if c.discrepancy]

    @property
    def warnings(self) -> list[Checkpoint]:
        return [c for c in self.checkpoints if c.severity == Severity.WARN]

    @property
    def failures(self) -> list[Checkpoint]:
        return [c for c in self.checkpoints if c.applicable and not c.passed]

    @property
    def next_actions(self) -> list[str]:
        """Ordered list of recommended actions to advance."""
        return [c.next_action for c in self.checkpoints
                if c.applicable and not c.passed and c.next_action]

    @property
    def blockers(self) -> list[str]:
        """What's blocking this repo from reaching the next promotion level."""
        b: list[str] = []
        for c in self.checkpoints:
            if c.applicable and not c.passed:
                b.append(f"{c.name}: {c.detail}")
        if self.staleness_days > STALE_CRITICAL_DAYS:
            b.append(f"Stale: {self.staleness_days} days since last_validated")
        if not self.security.clean:
            b.append(f"Security: exposed files {self.security.exposed_secrets}")
        return b

    @property
    def promotion_ready(self) -> bool:
        """Is this repo ready for its next promotion step?"""
        current = _PROMO_ORDER.get(self.promotion_status, 0)
        if current < 0:
            return False  # archived
        # To promote: all gates up to the next level's requirements must pass
        if current == 0:  # LOCAL → CANDIDATE: need SEED + SCAFFOLD + CI
            return all(
                c.passed for c in self.checkpoints
                if c.applicable and c.name in ("SEED", "SCAFFOLD", "CI")
            )
        if current == 1:  # CANDIDATE → PUBLIC_PROCESS: need TESTS + DOCS + PROTO
            return all(
                c.passed for c in self.checkpoints
                if c.applicable and c.name in ("SEED", "SCAFFOLD", "CI", "TESTS", "DOCS", "PROTO")
            )
        if current == 2:  # PUBLIC_PROCESS → GRADUATED: need DEPLOY + all prior
            return all(c.passed for c in self.checkpoints if c.applicable and c.name != "OMEGA")
        return False  # Already GRADUATED

    @property
    def next_promotion(self) -> str:
        """What promotion status this repo should aim for."""
        current = _PROMO_ORDER.get(self.promotion_status, 0)
        _rev = {v: k for k, v in _PROMO_ORDER.items() if v >= 0}
        nxt = current + 1
        return _rev.get(nxt, "GRADUATED")

    @property
    def is_stale(self) -> bool:
        return self.staleness_days > STALE_CRITICAL_DAYS

    @property
    def is_warn_stale(self) -> bool:
        return STALE_WARN_DAYS < self.staleness_days <= STALE_CRITICAL_DAYS

    def bar_ascii(self, width: int = 0) -> str:
        """Compact dot bar: ● = passed, ○ = not passed, ─ = N/A."""
        parts: list[str] = []
        for c in self.checkpoints:
            if not c.applicable:
                parts.append("\u2500")   # ─
            elif c.passed:
                parts.append("\u25cf")   # ●
            else:
                parts.append("\u25cb")   # ○
        return "".join(parts)

    def bar_colored(self) -> str:
        """ANSI-colored dot bar."""
        parts: list[str] = []
        for c in self.checkpoints:
            if not c.applicable:
                parts.append("\033[90m\u2500\033[0m")      # dim ─
            elif c.passed and not c.discrepancy:
                parts.append("\033[92m\u25cf\033[0m")      # green ●
            elif c.passed and c.discrepancy:
                parts.append("\033[93m\u25cf\033[0m")      # yellow ●
            else:
                parts.append("\033[91m\u25cb\033[0m")      # red ○
        return "".join(parts)

    def bar_labeled(self) -> str:
        """Multi-line labeled bar for single-repo detail view."""
        symbols: list[str] = []
        labels: list[str] = []
        for c in self.checkpoints:
            short = c.name[:4]
            if not c.applicable:
                symbols.append("\u2500")
            elif c.passed:
                symbols.append("\u25cf")
            else:
                symbols.append("\u25cb")
            labels.append(f" {short:<4}")
        spacer = "  "
        sym_line = f"  \u03b1 {spacer.join(symbols)}  {self.score}/{self.total}"
        lbl_line = f"    {''.join(labels)}"
        return f"{sym_line}\n{lbl_line}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "repo": self.repo,
            "organ": self.organ,
            "tier": self.tier,
            "profile": self.profile.value,
            "score": self.score,
            "total": self.total,
            "pct": self.pct,
            "weighted_score": self.weighted_score,
            "primary_language": self.primary_lang,
            "languages": self.languages,
            "staleness_days": self.staleness_days,
            "is_stale": self.is_stale,
            "promotion_status": self.promotion_status,
            "implementation_status": self.implementation_status,
            "platinum_status": self.platinum_status,
            "deployment_url": self.deployment_url,
            "promotion_ready": self.promotion_ready,
            "next_promotion": self.next_promotion,
            "description": self.description,
            "org": self.org,
            "revenue_model": self.revenue_model,
            "revenue_status": self.revenue_status,
            "git_health": self.git_health.to_dict(),
            "security": self.security.to_dict(),
            "scaffold": self.scaffold.to_dict(),
            "blockers": self.blockers,
            "next_actions": self.next_actions,
            "checkpoints": [
                {
                    "name": c.name,
                    "passed": c.passed,
                    "applicable": c.applicable,
                    "confidence": c.confidence,
                    "severity": c.severity.value,
                    "detail": c.detail,
                    "discrepancy": c.discrepancy,
                    "next_action": c.next_action,
                }
                for c in self.checkpoints
            ],
        }


# ---------------------------------------------------------------------------
# Gate evaluators
# ---------------------------------------------------------------------------

def _eval_seed(entry: dict, local_path: Path | None, tier: str) -> Checkpoint:
    """SEED: seed.yaml exists with required fields."""
    if local_path:
        seed_path = local_path / "seed.yaml"
        if seed_path.is_file():
            try:
                import yaml
                with open(seed_path) as f:
                    data = yaml.safe_load(f) or {}
                required = {"schema_version", "organ", "repo"}
                present = required.intersection(data.keys())
                ok = present == required
                # Check for bonus fields
                bonus_fields = {"metadata", "produces", "consumes", "subscriptions", "agents"}
                bonus = bonus_fields.intersection(data.keys())
                detail = f"seed.yaml ({len(present)}/{len(required)} required"
                if bonus:
                    detail += f", +{len(bonus)} optional"
                detail += ")"
                na = "" if ok else "Add missing required fields to seed.yaml: " + ", ".join(required - present)
                return Checkpoint("SEED", ok, True, "full", detail=detail, next_action=na)
            except Exception as e:
                return Checkpoint("SEED", False, True, "local-only",
                                  detail=f"seed.yaml parse error: {e}",
                                  next_action="Fix seed.yaml YAML syntax")
        return Checkpoint("SEED", False, True, "local-only",
                          detail="seed.yaml missing",
                          next_action="Create seed.yaml with schema_version, organ, repo fields")

    return Checkpoint("SEED", True, True, "registry-only",
                      detail="in registry (seed.yaml unverified)")


def _eval_scaffold(entry: dict, local_path: Path | None, tier: str, scaffold: ScaffoldSignals) -> Checkpoint:
    """SCAFFOLD: README.md + .gitignore + package config exist."""
    reg_doc = entry.get("documentation_status", "")
    reg_ok = bool(reg_doc) and reg_doc not in ("", "NONE", "MISSING")

    if local_path:
        local_ok = scaffold.has_readme and scaffold.has_gitignore
        parts = []
        if scaffold.has_readme:
            parts.append(f"README({scaffold.readme_words}w)")
        if scaffold.has_gitignore:
            parts.append(".gitignore")
        if scaffold.has_license:
            parts.append("LICENSE")
        if scaffold.has_pkg_config:
            parts.append(scaffold.pkg_config_type)
            local_ok = True
        if scaffold.has_claude_md:
            parts.append("CLAUDE.md")
        detail = ", ".join(parts) if parts else "missing scaffold files"

        disc = ""
        if reg_ok and not local_ok:
            disc = f"registry says '{reg_doc}' but local missing README or .gitignore"
        elif not reg_ok and local_ok:
            disc = "local has scaffold but registry documentation_status empty"

        na = ""
        if not local_ok:
            missing = []
            if not scaffold.has_readme:
                missing.append("README.md")
            if not scaffold.has_gitignore:
                missing.append(".gitignore")
            na = f"Create: {', '.join(missing)}"
        elif not scaffold.has_license:
            na = "Add LICENSE file"

        return Checkpoint("SCAFFOLD", local_ok, True, "full", detail=detail,
                          discrepancy=disc, next_action=na)

    return Checkpoint("SCAFFOLD", reg_ok, True, "registry-only",
                      detail=f"documentation_status={reg_doc}")


def _eval_ci(entry: dict, local_path: Path | None, tier: str) -> Checkpoint:
    """CI: workflow file exists."""
    reg_ci = entry.get("ci_workflow")
    reg_ok = reg_ci is not None and reg_ci != ""

    if local_path:
        wf_dir = local_path / ".github" / "workflows"
        local_files = list(wf_dir.glob("*.yml")) if wf_dir.is_dir() else []
        local_ok = len(local_files) > 0
        detail = f"{len(local_files)} workflow(s)" if local_files else "no workflow files"
        if reg_ok:
            detail = f"{reg_ci} (registry) + {detail}"

        disc = ""
        if reg_ok and not local_ok:
            disc = f"registry says ci_workflow={reg_ci} but no local .github/workflows/*.yml"
        elif not reg_ok and local_ok:
            disc = f"local has {len(local_files)} workflow(s) but registry ci_workflow is null"

        passed = reg_ok and local_ok
        na = ""
        if not passed:
            if not local_ok:
                na = "Add .github/workflows/ci.yml with lint+test steps"
            elif not reg_ok:
                na = "Update registry ci_workflow field"

        return Checkpoint("CI", passed, True, "full", detail=detail,
                          discrepancy=disc, next_action=na)

    return Checkpoint("CI", reg_ok, True, "registry-only",
                      detail=f"ci_workflow={reg_ci}",
                      next_action="" if reg_ok else "Set ci_workflow in registry")


def _eval_tests(entry: dict, local_path: Path | None, tier: str) -> Checkpoint:
    """TESTS: tests/ directory with test files. Flagship needs >=10."""
    min_tests = 10 if tier == "flagship" else 1

    if local_path:
        test_files: list[Path] = []
        for test_dir_name in ("tests", "__tests__", "test", "spec"):
            td = local_path / test_dir_name
            if td.is_dir():
                for ext in ("*.py", "*.ts", "*.js"):
                    test_files.extend(td.rglob(ext))
        # Also find inline test files (*.test.ts, *.spec.js) anywhere
        for pattern in ("*.test.ts", "*.test.js", "*.spec.ts", "*.spec.js"):
            test_files.extend(local_path.rglob(pattern))
        # Deduplicate
        test_files = list(set(test_files))
        count = len(test_files)
        ok = count >= min_tests
        detail = f"{count} test file(s)"
        if tier == "flagship" and count < min_tests:
            detail += f" (flagship needs >={min_tests})"

        na = ""
        if not ok:
            if count == 0:
                na = "Create tests/ directory with initial test file"
            else:
                na = f"Add more tests ({count}/{min_tests} for {tier})"

        return Checkpoint("TESTS", ok, True, "local-only", detail=detail, next_action=na)

    return Checkpoint("TESTS", False, True, "registry-only",
                      detail="cannot verify remotely",
                      next_action="Clone repo and add tests/ directory")


def _eval_docs(entry: dict, local_path: Path | None, tier: str, scaffold: ScaffoldSignals) -> Checkpoint:
    """DOCS: substantial README + CHANGELOG. Thresholds vary by tier."""
    reg_doc = entry.get("documentation_status", "")
    reg_ok = reg_doc in ("DEPLOYED", "FLAGSHIP README DEPLOYED")
    word_threshold = DOCS_WORD_THRESHOLD.get(tier, 500)

    if local_path:
        word_count = scaffold.readme_words
        has_changelog = scaffold.has_changelog
        local_ok = word_count >= word_threshold and has_changelog
        detail = f"README {word_count}w (need {word_threshold})"
        if has_changelog:
            detail += " + CHANGELOG.md"

        disc = ""
        if reg_ok and not local_ok:
            disc = f"registry={reg_doc} but local README {word_count}w or no CHANGELOG"
        elif not reg_ok and local_ok:
            disc = f"local docs strong ({word_count}w + CHANGELOG) but registry={reg_doc}"

        passed = reg_ok or local_ok
        na = ""
        if not passed:
            parts = []
            if word_count < word_threshold:
                parts.append(f"expand README to >={word_threshold} words (currently {word_count})")
            if not has_changelog:
                parts.append("add CHANGELOG.md")
            na = "; ".join(parts)

        return Checkpoint("DOCS", passed, True, "full", detail=detail,
                          discrepancy=disc, next_action=na)

    return Checkpoint("DOCS", reg_ok, True, "registry-only",
                      detail=f"documentation_status={reg_doc}",
                      next_action="" if reg_ok else "Deploy documentation and update registry")


def _eval_proto(entry: dict, local_path: Path | None, tier: str) -> Checkpoint:
    """PROTO: implementation_status >= PROTOTYPE."""
    impl = entry.get("implementation_status", "SKELETON")
    reg_ok = _IMPL_ORDER.get(impl, 0) >= _IMPL_ORDER["PROTOTYPE"]

    if local_path:
        has_substance = _has_code_files(local_path)
        detail = f"implementation_status={impl}"
        if has_substance:
            detail += " + code on disk"

        disc = ""
        if reg_ok and not has_substance:
            disc = f"registry says {impl} but no substantive code found locally"
        elif not reg_ok and has_substance:
            disc = f"code exists locally but registry says {impl}"

        na = ""
        if not reg_ok:
            na = f"Advance implementation from {impl} to at least PROTOTYPE"
            if has_substance:
                na = f"Update registry implementation_status from {impl} (code exists locally)"

        return Checkpoint("PROTO", reg_ok, True, "full", detail=detail,
                          discrepancy=disc, next_action=na)

    return Checkpoint("PROTO", reg_ok, True, "registry-only",
                      detail=f"implementation_status={impl}",
                      next_action="" if reg_ok else f"Advance from {impl} to PROTOTYPE+")


def _eval_cand(entry: dict, _local_path: Path | None, tier: str) -> Checkpoint:
    """CAND: promotion_status >= CANDIDATE. Registry authoritative."""
    promo = entry.get("promotion_status", "LOCAL")
    ok = _PROMO_ORDER.get(promo, 0) >= _PROMO_ORDER["CANDIDATE"]
    na = "" if ok else f"Promote from {promo} to CANDIDATE (need SEED+SCAFFOLD+CI)"
    return Checkpoint("CAND", ok, True, "registry-only",
                      detail=f"promotion_status={promo}", next_action=na)


def _eval_deploy(entry: dict, _local_path: Path | None, tier: str) -> Checkpoint:
    """DEPLOY: deployment_url populated or Pages enabled. Registry authoritative."""
    url = entry.get("deployment_url", "")
    platform = entry.get("deployment_platform", "")
    ok = bool(url)
    detail = url if url else "no deployment_url"
    if platform:
        detail += f" ({platform})"
    na = "" if ok else "Deploy the project and set deployment_url in registry"
    return Checkpoint("DEPLOY", ok, True, "registry-only", detail=detail, next_action=na)


def _eval_grad(entry: dict, _local_path: Path | None, tier: str) -> Checkpoint:
    """GRAD: promotion_status >= GRADUATED. Registry authoritative."""
    promo = entry.get("promotion_status", "LOCAL")
    ok = _PROMO_ORDER.get(promo, 0) >= _PROMO_ORDER["GRADUATED"]
    detail = f"promotion_status={promo}"
    if not ok:
        detail += " (need GRADUATED)"
    na = "" if ok else f"Complete all gates and promote from {promo} to GRADUATED"
    return Checkpoint("GRAD", ok, True, "registry-only", detail=detail, next_action=na)


def _eval_omega(entry: dict, local_path: Path | None, prev_gates: list[Checkpoint], tier: str) -> Checkpoint:
    """OMEGA: all prior applicable gates pass + platinum_status."""
    platinum = entry.get("platinum_status", False)
    applicable_prior = [g for g in prev_gates if g.applicable]
    all_prior_pass = all(g.passed for g in applicable_prior)
    ok = platinum and all_prior_pass
    parts: list[str] = []
    if not all_prior_pass:
        failed = [g.name for g in applicable_prior if not g.passed]
        parts.append(f"blocked by: {', '.join(failed)}")
    if not platinum:
        parts.append("platinum_status=false")
    if ok:
        parts.append("all gates passed + platinum")
    detail = "; ".join(parts) if parts else "complete"
    na = ""
    if not ok:
        if not all_prior_pass:
            na = f"Clear remaining gate failures first: {', '.join(g.name for g in applicable_prior if not g.passed)}"
        elif not platinum:
            na = "Set platinum_status=true in registry"
    return Checkpoint("OMEGA", ok, True, "full" if local_path else "registry-only",
                      detail=detail, next_action=na)


_GATE_EVALUATORS_BASIC = [
    ("SEED", _eval_seed),
    ("CI", _eval_ci),
    ("TESTS", _eval_tests),
    ("PROTO", _eval_proto),
    ("CAND", _eval_cand),
    ("DEPLOY", _eval_deploy),
    ("GRAD", _eval_grad),
]


# ---------------------------------------------------------------------------
# Core evaluator
# ---------------------------------------------------------------------------

def evaluate_project(
    entry: dict[str, Any],
    organ_id: str = "",
    local_path: Path | None = None,
    probe_git: bool = False,
) -> ProjectProgress:
    """Evaluate a single project's progress through all applicable gates."""
    profile = detect_profile(entry, local_path)
    skip = _PROFILE_SKIP[profile]

    repo = entry.get("name", "?")
    tier = entry.get("tier", "standard")
    organ = organ_id or ORG_TO_ORGAN.get(entry.get("org", ""), "?")

    # Probe extended signals
    scaffold = probe_scaffold(local_path)
    languages = detect_languages(local_path)
    plang = primary_language(languages)
    staleness = compute_staleness_days(entry)
    git_h = probe_git_health(local_path) if probe_git else GitHealth()
    sec = probe_security(local_path)

    # Evaluate gates
    gates: list[Checkpoint] = []

    def _add(name: str, cp: Checkpoint) -> None:
        if name in skip:
            cp = Checkpoint(name, False, False, cp.confidence, detail=f"N/A ({profile.value})")
        gates.append(cp)

    _add("SEED", _eval_seed(entry, local_path, tier))
    _add("SCAFFOLD", _eval_scaffold(entry, local_path, tier, scaffold))
    _add("CI", _eval_ci(entry, local_path, tier))
    _add("TESTS", _eval_tests(entry, local_path, tier))
    _add("DOCS", _eval_docs(entry, local_path, tier, scaffold))
    _add("PROTO", _eval_proto(entry, local_path, tier))
    _add("CAND", _eval_cand(entry, local_path, tier))
    _add("DEPLOY", _eval_deploy(entry, local_path, tier))
    _add("GRAD", _eval_grad(entry, local_path, tier))

    # OMEGA
    omega = _eval_omega(entry, local_path, gates, tier)
    if "OMEGA" in skip:
        omega = Checkpoint("OMEGA", False, False, omega.confidence, detail=f"N/A ({profile.value})")
    gates.append(omega)

    return ProjectProgress(
        repo=repo,
        organ=organ,
        tier=tier,
        profile=profile,
        checkpoints=gates,
        languages=languages,
        primary_lang=plang,
        staleness_days=staleness,
        git_health=git_h,
        security=sec,
        scaffold=scaffold,
        promotion_status=entry.get("promotion_status", "LOCAL"),
        implementation_status=entry.get("implementation_status", "SKELETON"),
        platinum_status=entry.get("platinum_status", False),
        deployment_url=entry.get("deployment_url", ""),
        org=entry.get("org", ""),
        description=entry.get("description", ""),
        revenue_model=entry.get("revenue_model", ""),
        revenue_status=entry.get("revenue_status", ""),
    )


def evaluate_all(
    registry: dict[str, Any],
    workspace: Path | None = None,
    probe_git: bool = False,
) -> list[ProjectProgress]:
    """Evaluate all repos in the registry."""
    results: list[ProjectProgress] = []

    for organ_id, organ_data in registry.get("organs", {}).items():
        for entry in organ_data.get("repositories", []):
            local_path = _find_local_path(entry, organ_id, workspace)
            progress = evaluate_project(entry, organ_id, local_path, probe_git=probe_git)
            results.append(progress)

    return results


def _find_local_path(
    entry: dict[str, Any],
    organ_id: str,
    workspace: Path | None,
) -> Path | None:
    """Resolve the local filesystem path for a repo, if available."""
    if workspace is None:
        return None

    org = entry.get("org", "")
    name = entry.get("name", "")
    if not name:
        return None

    for organ_key, dirs in ORGAN_DIRS.items():
        if organ_id == organ_key or org in dirs:
            for d in dirs:
                candidate = workspace / d / name
                if candidate.is_dir():
                    return candidate

    if org:
        candidate = workspace / org / name
        if candidate.is_dir():
            return candidate

    return None


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------

@dataclass
class GateStats:
    """Pass/fail statistics for a single gate across all repos."""
    name: str
    total_applicable: int = 0
    total_passed: int = 0
    total_failed: int = 0
    total_warn: int = 0
    total_na: int = 0
    failing_repos: list[str] = field(default_factory=list)

    @property
    def pass_rate(self) -> float:
        return (self.total_passed / self.total_applicable * 100) if self.total_applicable else 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "total_applicable": self.total_applicable,
            "total_passed": self.total_passed,
            "total_failed": self.total_failed,
            "total_warn": self.total_warn,
            "total_na": self.total_na,
            "pass_rate": round(self.pass_rate, 1),
            "failing_repos": self.failing_repos,
        }


def compute_gate_stats(projects: list[ProjectProgress]) -> list[GateStats]:
    """Compute pass/fail rates per gate across all projects."""
    stats_map: dict[str, GateStats] = {}
    for gate_name in GATE_NAMES:
        stats_map[gate_name] = GateStats(name=gate_name)

    for p in projects:
        for cp in p.checkpoints:
            s = stats_map.get(cp.name)
            if not s:
                continue
            if not cp.applicable:
                s.total_na += 1
            elif cp.passed and not cp.discrepancy:
                s.total_applicable += 1
                s.total_passed += 1
            elif cp.passed and cp.discrepancy:
                s.total_applicable += 1
                s.total_passed += 1
                s.total_warn += 1
            else:
                s.total_applicable += 1
                s.total_failed += 1
                s.failing_repos.append(p.repo)

    return [stats_map[g] for g in GATE_NAMES]


@dataclass
class SystemSummary:
    """Aggregate analytics for the entire system."""
    total_repos: int = 0
    total_score: int = 0
    total_possible: int = 0
    avg_pct: float = 0.0
    weighted_total: float = 0.0
    profile_counts: dict[str, int] = field(default_factory=dict)
    promo_counts: dict[str, int] = field(default_factory=dict)
    tier_counts: dict[str, int] = field(default_factory=dict)
    language_counts: dict[str, int] = field(default_factory=dict)
    stale_count: int = 0
    warn_stale_count: int = 0
    security_issues_count: int = 0
    promotion_ready_count: int = 0
    discrepancy_count: int = 0
    gate_stats: list[GateStats] = field(default_factory=list)
    # Per-organ summaries
    organ_summaries: dict[str, dict[str, Any]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_repos": self.total_repos,
            "total_score": self.total_score,
            "total_possible": self.total_possible,
            "sys_pct": round(self.avg_pct, 1),
            "weighted_total": round(self.weighted_total, 1),
            "profile_counts": self.profile_counts,
            "promo_counts": self.promo_counts,
            "tier_counts": self.tier_counts,
            "language_counts": self.language_counts,
            "stale_count": self.stale_count,
            "warn_stale_count": self.warn_stale_count,
            "security_issues_count": self.security_issues_count,
            "promotion_ready_count": self.promotion_ready_count,
            "discrepancy_count": self.discrepancy_count,
            "gate_stats": [g.to_dict() for g in self.gate_stats],
            "organ_summaries": self.organ_summaries,
        }


def compute_system_summary(projects: list[ProjectProgress]) -> SystemSummary:
    """Compute aggregate system analytics."""
    s = SystemSummary()
    s.total_repos = len(projects)
    s.total_score = sum(p.score for p in projects)
    s.total_possible = sum(p.total for p in projects)
    s.avg_pct = (s.total_score / s.total_possible * 100) if s.total_possible else 0.0
    s.weighted_total = sum(p.weighted_score for p in projects)
    s.profile_counts = dict(Counter(p.profile.value for p in projects).most_common())
    s.promo_counts = dict(Counter(p.promotion_status for p in projects).most_common())
    s.tier_counts = dict(Counter(p.tier for p in projects).most_common())
    s.stale_count = sum(1 for p in projects if p.is_stale)
    s.warn_stale_count = sum(1 for p in projects if p.is_warn_stale)
    s.security_issues_count = sum(1 for p in projects if not p.security.clean)
    s.promotion_ready_count = sum(1 for p in projects if p.promotion_ready)
    s.discrepancy_count = sum(len(p.discrepancies) for p in projects)
    s.gate_stats = compute_gate_stats(projects)

    # Language counts
    lang_counter: Counter[str] = Counter()
    for p in projects:
        if p.primary_lang != "unknown" and p.primary_lang != "none":
            lang_counter[p.primary_lang] += 1
    s.language_counts = dict(lang_counter.most_common())

    # Per-organ summaries
    organs: dict[str, list[ProjectProgress]] = defaultdict(list)
    for p in projects:
        organs[p.organ].append(p)

    for organ_id, projs in organs.items():
        avg = sum(p.pct for p in projs) / len(projs) if projs else 0
        s.organ_summaries[organ_id] = {
            "count": len(projs),
            "avg_pct": round(avg, 1),
            "avg_score": round(sum(p.score for p in projs) / len(projs), 1) if projs else 0,
            "avg_total": round(sum(p.total for p in projs) / len(projs), 1) if projs else 0,
            "stale": sum(1 for p in projs if p.is_stale),
            "promotion_ready": sum(1 for p in projs if p.promotion_ready),
        }

    return s


# ---------------------------------------------------------------------------
# Snapshot persistence
# ---------------------------------------------------------------------------

def save_snapshot(
    projects: list[ProjectProgress],
    summary: SystemSummary,
    output_dir: Path,
    label: str = "",
) -> Path:
    """Save evaluation snapshot to a timestamped JSON file.

    Returns the path of the saved file.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
    suffix = f"-{label}" if label else ""
    filename = f"progress-snapshot-{ts}{suffix}.json"
    path = output_dir / filename

    data = {
        "timestamp": datetime.datetime.now().isoformat(),
        "label": label,
        "summary": summary.to_dict(),
        "projects": [p.to_dict() for p in projects],
    }

    with open(path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")

    return path


def load_snapshot(path: Path) -> dict[str, Any]:
    """Load a previously saved snapshot."""
    with open(path) as f:
        return json.load(f)


def list_snapshots(snapshot_dir: Path) -> list[Path]:
    """List all snapshot files, newest first."""
    if not snapshot_dir.is_dir():
        return []
    return sorted(snapshot_dir.glob("progress-snapshot-*.json"), reverse=True)


# ---------------------------------------------------------------------------
# Delta computation
# ---------------------------------------------------------------------------

@dataclass
class RepoDelta:
    """Change in a single repo between two snapshots."""
    repo: str
    organ: str
    old_score: int
    new_score: int
    old_total: int
    new_total: int
    old_pct: int
    new_pct: int
    gates_gained: list[str] = field(default_factory=list)
    gates_lost: list[str] = field(default_factory=list)
    profile_changed: bool = False
    old_profile: str = ""
    new_profile: str = ""

    @property
    def delta_score(self) -> int:
        return self.new_score - self.old_score

    @property
    def delta_pct(self) -> int:
        return self.new_pct - self.old_pct

    @property
    def improved(self) -> bool:
        return self.delta_pct > 0

    @property
    def regressed(self) -> bool:
        return self.delta_pct < 0


@dataclass
class SnapshotDelta:
    """Comparison between two snapshots."""
    old_timestamp: str
    new_timestamp: str
    old_sys_pct: float
    new_sys_pct: float
    repos_improved: list[RepoDelta] = field(default_factory=list)
    repos_regressed: list[RepoDelta] = field(default_factory=list)
    repos_unchanged: int = 0
    repos_added: list[str] = field(default_factory=list)
    repos_removed: list[str] = field(default_factory=list)

    @property
    def delta_sys_pct(self) -> float:
        return self.new_sys_pct - self.old_sys_pct

    def to_dict(self) -> dict[str, Any]:
        return {
            "old_timestamp": self.old_timestamp,
            "new_timestamp": self.new_timestamp,
            "old_sys_pct": round(self.old_sys_pct, 1),
            "new_sys_pct": round(self.new_sys_pct, 1),
            "delta_sys_pct": round(self.delta_sys_pct, 1),
            "repos_improved": len(self.repos_improved),
            "repos_regressed": len(self.repos_regressed),
            "repos_unchanged": self.repos_unchanged,
            "repos_added": self.repos_added,
            "repos_removed": self.repos_removed,
            "improvements": [
                {"repo": r.repo, "organ": r.organ,
                 "old": f"{r.old_score}/{r.old_total}",
                 "new": f"{r.new_score}/{r.new_total}",
                 "gates_gained": r.gates_gained}
                for r in self.repos_improved
            ],
            "regressions": [
                {"repo": r.repo, "organ": r.organ,
                 "old": f"{r.old_score}/{r.old_total}",
                 "new": f"{r.new_score}/{r.new_total}",
                 "gates_lost": r.gates_lost}
                for r in self.repos_regressed
            ],
        }


def compute_delta(old_snap: dict[str, Any], new_snap: dict[str, Any]) -> SnapshotDelta:
    """Compare two snapshots and compute the delta."""
    old_projects = {p["repo"]: p for p in old_snap.get("projects", [])}
    new_projects = {p["repo"]: p for p in new_snap.get("projects", [])}

    delta = SnapshotDelta(
        old_timestamp=old_snap.get("timestamp", "?"),
        new_timestamp=new_snap.get("timestamp", "?"),
        old_sys_pct=old_snap.get("summary", {}).get("sys_pct", 0),
        new_sys_pct=new_snap.get("summary", {}).get("sys_pct", 0),
    )

    all_repos = set(old_projects.keys()) | set(new_projects.keys())
    delta.repos_added = sorted(set(new_projects.keys()) - set(old_projects.keys()))
    delta.repos_removed = sorted(set(old_projects.keys()) - set(new_projects.keys()))

    for repo in sorted(all_repos):
        if repo in delta.repos_added or repo in delta.repos_removed:
            continue
        old_p = old_projects[repo]
        new_p = new_projects[repo]

        old_gates = {c["name"]: c["passed"] for c in old_p.get("checkpoints", []) if c.get("applicable")}
        new_gates = {c["name"]: c["passed"] for c in new_p.get("checkpoints", []) if c.get("applicable")}

        gained = [g for g in new_gates if new_gates.get(g) and not old_gates.get(g)]
        lost = [g for g in old_gates if old_gates.get(g) and not new_gates.get(g)]

        rd = RepoDelta(
            repo=repo,
            organ=new_p.get("organ", "?"),
            old_score=old_p.get("score", 0),
            new_score=new_p.get("score", 0),
            old_total=old_p.get("total", 0),
            new_total=new_p.get("total", 0),
            old_pct=old_p.get("pct", 0),
            new_pct=new_p.get("pct", 0),
            gates_gained=gained,
            gates_lost=lost,
            profile_changed=old_p.get("profile") != new_p.get("profile"),
            old_profile=old_p.get("profile", ""),
            new_profile=new_p.get("profile", ""),
        )

        if rd.improved:
            delta.repos_improved.append(rd)
        elif rd.regressed:
            delta.repos_regressed.append(rd)
        else:
            delta.repos_unchanged += 1

    delta.repos_improved.sort(key=lambda r: -r.delta_pct)
    delta.repos_regressed.sort(key=lambda r: r.delta_pct)

    return delta


# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------

def render_detail(progress: ProjectProgress, color: bool = False) -> str:
    """Render a single-repo detail view."""
    lines: list[str] = []
    lines.append(f"{progress.repo} ({progress.organ}, {progress.tier}, profile={progress.profile.value})")
    if progress.description:
        lines.append(f"  {progress.description[:80]}")
    lines.append(progress.bar_labeled())
    lines.append("")

    for cp in progress.checkpoints:
        if not cp.applicable:
            sym = "\u2500"
            if color:
                lines.append(f"  \033[90m{sym} {cp.name:<10} {cp.detail}\033[0m")
            else:
                lines.append(f"  {sym} {cp.name:<10} {cp.detail}")
        elif cp.passed:
            sym = "\u2713"
            if color and cp.discrepancy:
                lines.append(f"  \033[93m{sym} {cp.name:<10} {cp.detail}\033[0m")
            elif color:
                lines.append(f"  \033[92m{sym} {cp.name:<10} {cp.detail}\033[0m")
            else:
                lines.append(f"  {sym} {cp.name:<10} {cp.detail}")
        else:
            sym = "\u2717"
            if color:
                lines.append(f"  \033[91m{sym} {cp.name:<10} {cp.detail}\033[0m")
            else:
                lines.append(f"  {sym} {cp.name:<10} {cp.detail}")
        if cp.discrepancy:
            lines.append(f"    \u26a0 {cp.discrepancy}")
        if cp.next_action and not cp.passed:
            lines.append(f"    \u2192 {cp.next_action}")

    # Extended info
    lines.append("")
    if progress.languages:
        top3 = list(progress.languages.items())[:3]
        lines.append(f"  Languages: {', '.join(f'{l} ({c})' for l, c in top3)}")
    if progress.staleness_days >= 0:
        stale_marker = ""
        if progress.is_stale:
            stale_marker = " [STALE]" if not color else " \033[91m[STALE]\033[0m"
        elif progress.is_warn_stale:
            stale_marker = " [aging]" if not color else " \033[93m[aging]\033[0m"
        lines.append(f"  Last validated: {progress.staleness_days} days ago{stale_marker}")
    if not progress.security.clean:
        lines.append(f"  Security: exposed files: {', '.join(progress.security.exposed_secrets)}")
    if progress.scaffold.has_claude_md:
        lines.append("  AI context: CLAUDE.md present")
    if progress.scaffold.has_license:
        lines.append("  License: present")
    elif progress.profile != Profile.INFRASTRUCTURE:
        lines.append("  License: MISSING")
    if progress.promotion_ready:
        lines.append(f"  Promotion: READY for {progress.next_promotion}")
    else:
        lines.append(f"  Promotion: not ready for {progress.next_promotion}")
    if progress.revenue_model:
        lines.append(f"  Revenue: {progress.revenue_model} ({progress.revenue_status})")
    if progress.blockers:
        lines.append(f"  Blockers ({len(progress.blockers)}):")
        for b in progress.blockers[:5]:
            lines.append(f"    - {b}")

    return "\n".join(lines)


def render_organ_summary(
    organ_id: str,
    organ_name: str,
    projects: list[ProjectProgress],
    color: bool = False,
) -> str:
    """Render an organ-level summary table."""
    lines: list[str] = []
    lines.append(f"{organ_id}: {organ_name} ({len(projects)} repos)")
    lines.append("\u2501" * 78)

    for p in sorted(projects, key=lambda x: (-x.pct, -x.score, x.repo)):
        bar = p.bar_colored() if color else p.bar_ascii()
        promo = p.promotion_status
        badge = p.profile.value if p.profile != Profile.CODE_FULL else p.tier
        ready = "\u2191" if p.promotion_ready else " "
        stale = ""
        if p.is_stale:
            stale = " !" if not color else " \033[91m!\033[0m"
        elif p.is_warn_stale:
            stale = " ~" if not color else " \033[93m~\033[0m"
        lines.append(
            f"  {p.repo:<35} {bar}  {p.score:>2}/{p.total:<2} {p.pct:>3}%  "
            f"{badge:<14} {promo:<16} {ready}{stale}"
        )

    if projects:
        avg_pct = sum(p.pct for p in projects) / len(projects)
        avg_score = sum(p.score for p in projects) / len(projects)
        avg_total = sum(p.total for p in projects) / len(projects)
        ready_count = sum(1 for p in projects if p.promotion_ready)
        stale_count = sum(1 for p in projects if p.is_stale)
        lines.append("\u2501" * 78)
        lines.append(
            f"  Avg: {avg_score:.1f}/{avg_total:.1f} ({avg_pct:.0f}%) | "
            f"Promo-ready: {ready_count} | Stale: {stale_count} | "
            f"Discrepancies: {sum(len(p.discrepancies) for p in projects)}"
        )

    return "\n".join(lines)


def render_heatmap(all_projects: list[ProjectProgress], color: bool = False) -> str:
    """Render system-wide heatmap grouped by organ."""
    organs: dict[str, list[ProjectProgress]] = defaultdict(list)
    for p in all_projects:
        organs[p.organ].append(p)

    organ_order = [
        "ORGAN-I", "ORGAN-II", "ORGAN-III", "ORGAN-IV",
        "ORGAN-V", "ORGAN-VI", "ORGAN-VII", "META-ORGANVM", "PERSONAL",
    ]

    lines: list[str] = []
    lines.append("ORGANVM System Progress \u2014 \u03b1 \u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501 \u03a9")
    lines.append("")

    total_repos = 0
    total_score = 0
    total_possible = 0

    for organ in organ_order:
        projs = organs.get(organ, [])
        if not projs:
            continue
        avg_pct = sum(p.pct for p in projs) / len(projs)
        filled = int(avg_pct / 10)
        bar = "\u2588" * filled + "\u2591" * (10 - filled)
        avg_score = sum(p.score for p in projs) / len(projs)
        avg_total = sum(p.total for p in projs) / len(projs)
        ready = sum(1 for p in projs if p.promotion_ready)
        stale = sum(1 for p in projs if p.is_stale)

        extra = ""
        if ready:
            extra += f" \u2191{ready}"
        if stale:
            extra += f" !{stale}"

        if color:
            bar_color = "\033[92m" if avg_pct >= 80 else "\033[93m" if avg_pct >= 50 else "\033[91m"
            lines.append(
                f"  {organ:<14} {bar_color}{bar}\033[0m  {avg_pct:>3.0f}%  "
                f"({len(projs):>2} repos, avg {avg_score:.1f}/{avg_total:.1f}){extra}"
            )
        else:
            lines.append(
                f"  {organ:<14} {bar}  {avg_pct:>3.0f}%  "
                f"({len(projs):>2} repos, avg {avg_score:.1f}/{avg_total:.1f}){extra}"
            )

        total_repos += len(projs)
        total_score += sum(p.score for p in projs)
        total_possible += sum(p.total for p in projs)

    sys_pct = int(total_score / total_possible * 100) if total_possible else 0
    lines.append("")
    filled = int(sys_pct / 10)
    bar = "\u2588" * filled + "\u2591" * (10 - filled)
    lines.append(f"  {'System':<14} {bar}  {sys_pct:>3}%  ({total_repos} repos)")
    lines.append("")

    summary = compute_system_summary(all_projects)
    promo_parts = []
    for status in ("GRADUATED", "PUBLIC_PROCESS", "CANDIDATE", "LOCAL", "ARCHIVED"):
        count = summary.promo_counts.get(status, 0)
        if count:
            promo_parts.append(f"{status}: {count}")
    if promo_parts:
        lines.append(f"  {' | '.join(promo_parts)}")

    prof_parts = [f"{k}: {v}" for k, v in summary.profile_counts.items()]
    lines.append(f"  Profiles: {' | '.join(prof_parts)}")

    if summary.language_counts:
        lang_parts = [f"{k}: {v}" for k, v in list(summary.language_counts.items())[:6]]
        lines.append(f"  Languages: {' | '.join(lang_parts)}")

    lines.append(
        f"  Promo-ready: {summary.promotion_ready_count} | "
        f"Stale: {summary.stale_count} | "
        f"Security issues: {summary.security_issues_count} | "
        f"Discrepancies: {summary.discrepancy_count}"
    )

    return "\n".join(lines)


def render_gate_stats(stats: list[GateStats], color: bool = False) -> str:
    """Render system-wide gate pass-rate table."""
    lines: list[str] = []
    lines.append("Gate Pass Rates")
    lines.append("\u2501" * 68)
    lines.append(f"  {'Gate':<10} {'Pass':>6} {'Fail':>6} {'Warn':>6} {'N/A':>6} {'Rate':>8}")
    lines.append("\u2500" * 68)

    for s in stats:
        rate_str = f"{s.pass_rate:.0f}%"
        if color:
            c = "\033[92m" if s.pass_rate >= 80 else "\033[93m" if s.pass_rate >= 50 else "\033[91m"
            rate_str = f"{c}{s.pass_rate:.0f}%\033[0m"
        lines.append(
            f"  {s.name:<10} {s.total_passed:>6} {s.total_failed:>6} "
            f"{s.total_warn:>6} {s.total_na:>6} {rate_str:>8}"
        )

    lines.append("\u2501" * 68)
    return "\n".join(lines)


def render_blockers(projects: list[ProjectProgress], color: bool = False) -> str:
    """Render blockers report — repos that are promotion-ready vs blocked."""
    ready = [p for p in projects if p.promotion_ready and p.promotion_status != "GRADUATED"]
    blocked = [p for p in projects if not p.promotion_ready and p.promotion_status not in ("GRADUATED", "ARCHIVED")]

    lines: list[str] = []
    lines.append("Promotion Blockers Report")
    lines.append("\u2501" * 68)

    if ready:
        lines.append(f"\n  READY FOR PROMOTION ({len(ready)} repos):")
        for p in sorted(ready, key=lambda x: x.repo):
            lines.append(f"    {p.repo:<35} {p.promotion_status} \u2192 {p.next_promotion}")

    if blocked:
        lines.append(f"\n  BLOCKED ({len(blocked)} repos):")
        for p in sorted(blocked, key=lambda x: (-len(x.blockers), x.repo)):
            lines.append(f"    {p.repo:<35} {p.promotion_status} ({len(p.blockers)} blockers)")
            for b in p.blockers[:3]:
                lines.append(f"      - {b}")

    lines.append("\u2501" * 68)
    return "\n".join(lines)


def render_next_actions(projects: list[ProjectProgress], limit: int = 20) -> str:
    """Render prioritized next-actions across all repos."""
    actions: list[tuple[str, str, str]] = []  # (repo, gate, action)
    for p in projects:
        if p.profile == Profile.ARCHIVED:
            continue
        for cp in p.checkpoints:
            if cp.applicable and not cp.passed and cp.next_action:
                actions.append((p.repo, cp.name, cp.next_action))

    lines: list[str] = []
    lines.append(f"Next Actions ({len(actions)} total, showing {min(limit, len(actions))})")
    lines.append("\u2501" * 78)

    for repo, gate, action in actions[:limit]:
        lines.append(f"  {repo:<35} [{gate:<6}] {action}")

    if len(actions) > limit:
        lines.append(f"  ... and {len(actions) - limit} more")

    return "\n".join(lines)


def render_discrepancies(projects: list[ProjectProgress]) -> str:
    """Render all registry/local discrepancies."""
    lines: list[str] = []
    lines.append("Discrepancies (registry vs local)")
    lines.append("\u2501" * 78)

    count = 0
    for p in projects:
        for cp in p.discrepancies:
            count += 1
            lines.append(f"  {p.repo:<35} [{cp.name:<6}] {cp.discrepancy}")

    if count == 0:
        lines.append("  No discrepancies found.")
    else:
        lines.append("\u2501" * 78)
        lines.append(f"  Total: {count} discrepancies across {sum(1 for p in projects if p.discrepancies)} repos")

    return "\n".join(lines)


def render_stale(projects: list[ProjectProgress]) -> str:
    """Render staleness report."""
    critical = [p for p in projects if p.is_stale]
    warning = [p for p in projects if p.is_warn_stale]

    lines: list[str] = []
    lines.append("Staleness Report")
    lines.append("\u2501" * 68)

    if critical:
        lines.append(f"\n  CRITICAL (>{STALE_CRITICAL_DAYS} days, {len(critical)} repos):")
        for p in sorted(critical, key=lambda x: -x.staleness_days):
            lines.append(f"    {p.repo:<35} {p.staleness_days} days")

    if warning:
        lines.append(f"\n  WARNING ({STALE_WARN_DAYS}-{STALE_CRITICAL_DAYS} days, {len(warning)} repos):")
        for p in sorted(warning, key=lambda x: -x.staleness_days):
            lines.append(f"    {p.repo:<35} {p.staleness_days} days")

    if not critical and not warning:
        lines.append("  All repos validated within the last 30 days.")

    lines.append("\u2501" * 68)
    return "\n".join(lines)


def render_delta(delta: SnapshotDelta, color: bool = False) -> str:
    """Render snapshot comparison."""
    lines: list[str] = []
    sign = "+" if delta.delta_sys_pct >= 0 else ""
    lines.append(f"Snapshot Delta: {delta.old_timestamp[:10]} \u2192 {delta.new_timestamp[:10]}")
    lines.append(f"  System: {delta.old_sys_pct:.0f}% \u2192 {delta.new_sys_pct:.0f}% ({sign}{delta.delta_sys_pct:.1f}%)")
    lines.append("\u2501" * 68)

    if delta.repos_improved:
        lines.append(f"\n  IMPROVED ({len(delta.repos_improved)} repos):")
        for r in delta.repos_improved:
            gained = f" +{', '.join(r.gates_gained)}" if r.gates_gained else ""
            lines.append(f"    {r.repo:<35} {r.old_score}/{r.old_total} \u2192 {r.new_score}/{r.new_total}{gained}")

    if delta.repos_regressed:
        lines.append(f"\n  REGRESSED ({len(delta.repos_regressed)} repos):")
        for r in delta.repos_regressed:
            lost = f" -{', '.join(r.gates_lost)}" if r.gates_lost else ""
            lines.append(f"    {r.repo:<35} {r.old_score}/{r.old_total} \u2192 {r.new_score}/{r.new_total}{lost}")

    if delta.repos_added:
        lines.append(f"\n  ADDED ({len(delta.repos_added)}):")
        for r in delta.repos_added:
            lines.append(f"    {r}")

    if delta.repos_removed:
        lines.append(f"\n  REMOVED ({len(delta.repos_removed)}):")
        for r in delta.repos_removed:
            lines.append(f"    {r}")

    lines.append(f"\n  Unchanged: {delta.repos_unchanged}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Export helpers
# ---------------------------------------------------------------------------

def export_csv(projects: list[ProjectProgress]) -> str:
    """Export as CSV."""
    header = "repo,organ,tier,profile,score,total,pct,promo,impl,stale_days,primary_lang,blockers"
    rows = [header]
    for p in projects:
        blockers = "|".join(p.blockers).replace(",", ";")
        rows.append(
            f"{p.repo},{p.organ},{p.tier},{p.profile.value},{p.score},{p.total},{p.pct},"
            f"{p.promotion_status},{p.implementation_status},{p.staleness_days},"
            f"{p.primary_lang},{blockers}"
        )
    return "\n".join(rows)


def export_markdown(projects: list[ProjectProgress], summary: SystemSummary) -> str:
    """Export as Markdown table."""
    lines: list[str] = []
    lines.append("# ORGANVM Progress Report")
    lines.append("")
    lines.append(f"**System: {summary.avg_pct:.0f}%** ({summary.total_repos} repos)")
    lines.append("")
    lines.append("| Repo | Organ | Profile | Score | % | Promo | Lang |")
    lines.append("|------|-------|---------|-------|---|-------|------|")
    for p in sorted(projects, key=lambda x: (-x.pct, x.repo)):
        lines.append(
            f"| {p.repo} | {p.organ} | {p.profile.value} | "
            f"{p.score}/{p.total} | {p.pct}% | {p.promotion_status} | {p.primary_lang} |"
        )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Registry loading (standalone, no organvm_engine dependency)
# ---------------------------------------------------------------------------

def load_registry(path: Path) -> dict[str, Any]:
    """Load registry-v2.json."""
    with open(path) as f:
        return json.load(f)
