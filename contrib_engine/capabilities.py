"""ORGANVM capability map — what the system can contribute to open-source projects.

Each capability maps ORGANVM patterns to the kinds of open-source issues
they solve. The scanner uses this to score domain overlap.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Capability:
    """A contribution capability derived from ORGANVM patterns."""

    id: str
    name: str
    description: str
    source_repos: list[str]  # ORGANVM repos that embody this pattern
    issue_keywords: list[str]  # Keywords that signal matching issues
    languages: list[str] = field(default_factory=lambda: ["python"])


# The canonical capability map
CAPABILITIES: list[Capability] = [
    Capability(
        id="governance-lifecycle",
        name="Governance & Lifecycle State Machines",
        description=(
            "Forward-only promotion states with quality gates. "
            "Versioning with integrity checksums. Audit trails."
        ),
        source_repos=["orchestration-start-here", "agentic-titan"],
        issue_keywords=[
            "version", "versioning", "reproducibility", "rollback",
            "snapshot", "checkpoint", "lifecycle", "state machine",
            "promotion", "governance", "audit", "history",
        ],
    ),
    Capability(
        id="multi-agent-orchestration",
        name="Multi-Agent Orchestration",
        description=(
            "9 topology patterns, 22 agent archetypes, model-agnostic LLM adapters. "
            "Fission-fusion dynamics, assembly states, coordinator patterns."
        ),
        source_repos=["agentic-titan"],
        issue_keywords=[
            "multi-agent", "orchestration", "coordinator", "swarm",
            "agent communication", "delegation", "topology", "parallel agents",
            "agent coordination", "distributed agents",
        ],
    ),
    Capability(
        id="testing-infrastructure",
        name="Testing Infrastructure",
        description=(
            "23,470 tests across 118 repos. pytest patterns, parallel execution, "
            "CI/CD pipelines, coverage enforcement, fixture design."
        ),
        source_repos=["orchestration-start-here", "agentic-titan", "agent--claude-smith"],
        issue_keywords=[
            "test", "testing", "pytest", "coverage", "ci/cd", "parallel test",
            "test infrastructure", "fixture", "mock", "integration test",
            "xdist", "test isolation",
        ],
    ),
    Capability(
        id="dependency-validation",
        name="Dependency Graph Validation",
        description=(
            "Unidirectional dependency enforcement across 118 repos. "
            "Automated back-edge detection. Graph-level governance."
        ),
        source_repos=["orchestration-start-here"],
        issue_keywords=[
            "dependency", "circular dependency", "dependency graph",
            "import cycle", "module dependency", "dependency validation",
        ],
    ),
    Capability(
        id="mcp-integration",
        name="MCP Server Integration",
        description=(
            "Model Context Protocol servers for filesystem, memory, sequential thinking. "
            "Tool registration, transport configuration."
        ),
        source_repos=["agentic-titan", "agent--claude-smith"],
        issue_keywords=[
            "mcp", "model context protocol", "tool server", "tool integration",
            "mcp server", "tool registration",
        ],
    ),
    Capability(
        id="documentation-governance",
        name="Documentation Governance",
        description=(
            "739K words across 118 repos. CLAUDE.md, AGENTS.md, seed.yaml contracts. "
            "Stranger testing, README standards, pre-commit validation."
        ),
        source_repos=["orchestration-start-here", "petasum-super-petasum"],
        issue_keywords=[
            "documentation", "docs", "readme", "contributing guide",
            "onboarding", "developer experience", "dx",
        ],
    ),
    Capability(
        id="security-patterns",
        name="Security Implementation",
        description=(
            "Authentication, authorization, input validation. "
            "Secret scanning, credential management, OWASP patterns."
        ),
        source_repos=["agent--claude-smith"],
        issue_keywords=[
            "security", "authentication", "auth", "authorization",
            "credential", "secret", "vulnerability", "owasp",
            "input validation", "injection",
        ],
    ),
    Capability(
        id="cli-tooling",
        name="CLI Tool Design",
        description=(
            "argparse/click patterns, subcommand architecture, "
            "shell completion, structured output."
        ),
        source_repos=["orchestration-start-here", "agentic-titan"],
        issue_keywords=[
            "cli", "command line", "terminal", "argparse", "click",
            "shell", "completion", "subcommand",
        ],
    ),
]


def match_capabilities(issue_text: str) -> list[Capability]:
    """Return capabilities matching keywords in issue text."""
    text_lower = issue_text.lower()
    matches = []
    for cap in CAPABILITIES:
        score = sum(1 for kw in cap.issue_keywords if kw in text_lower)
        if score > 0:
            matches.append(cap)
    return sorted(matches, key=lambda c: -sum(1 for kw in c.issue_keywords if kw in text_lower))


def get_capability(cap_id: str) -> Capability | None:
    """Get capability by ID."""
    for cap in CAPABILITIES:
        if cap.id == cap_id:
            return cap
    return None
