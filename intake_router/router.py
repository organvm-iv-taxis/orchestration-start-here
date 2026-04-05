"""Keyword-based intake routing for cross-workspace dispatch."""

from __future__ import annotations

import re
from enum import StrEnum
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field

from action_ledger.emissions import emit_state_change
from action_ledger.ledger import (
    load_actions,
    load_param_registry,
    load_sequences,
    record,
    save_actions,
    save_param_registry,
    save_sequences,
)
from action_ledger.schemas import Action, ActionOrigin, RouteKind


class IntakeDomain(StrEnum):
    """Known intake domains for the orchestration router."""

    ORGANISM = "organism"
    TRANSMUTATION = "transmutation"
    EMISSION = "emission"
    HOUSEKEEPING = "housekeeping"
    PIPELINE = "pipeline"
    BILLING = "billing"
    CORRESPONDENCE = "correspondence"
    UNKNOWN = "unknown"


class IntakeItem(BaseModel):
    """Structured classification for a raw operator intake."""

    raw: str
    domain: IntakeDomain
    keywords: list[str] = Field(default_factory=list)
    tension: float
    suggested_archetype: str
    suggested_agent: str
    suggested_workspace: str
    prompt_fragment: str


class Dispatch(BaseModel):
    """Concrete execution recommendation derived from an intake item."""

    item: IntakeItem
    workspace: str
    archetype: str
    agent: str
    prompt: str
    token_budget: str


class PromptTemplate(BaseModel):
    """Prompt block parsed from the archetype plan."""

    title: str
    body: str


class RouteTarget(BaseModel):
    """Routing metadata for one intake domain."""

    workspace: str = ""
    archetype: str = ""
    agent: str
    token_budget: str = ""


ROUTER_SESSION = "ROUTER"
ARCHETYPE_PLAN = (
    Path(__file__).resolve().parents[1]
    / ".claude/plans/2026-03-31-hanging-task-archetypes.md"
)

DOMAIN_KEYWORDS: dict[IntakeDomain, tuple[str, ...]] = {
    IntakeDomain.ORGANISM: (
        "organism",
        "seed",
        "function",
        "gate",
        "signal",
        "axiom",
        "a-organvm",
    ),
    IntakeDomain.TRANSMUTATION: (
        "exit interview",
        "exit-interview",
        "testimony",
        "rectification",
        "governance",
        "counter-testimony",
    ),
    IntakeDomain.EMISSION: (
        "emission",
        "wire",
        "emit",
        "ledger",
        "action",
        "router",
    ),
    IntakeDomain.HOUSEKEEPING: (
        "irf",
        "concordance",
        "issue",
        "issues",
        "registry",
        "housekeeping",
    ),
    IntakeDomain.PIPELINE: (
        "pipeline",
        "application",
        "applications",
        "job",
        "jobs",
        "resume",
    ),
    IntakeDomain.BILLING: (
        "billing",
        "enterprise",
        "organization",
        "github org",
        "copilot",
    ),
    IntakeDomain.CORRESPONDENCE: (
        "correspondence",
        "email",
        "outbound",
        "inbound",
        "reply",
        "draft",
        "follow-up",
        "message",
        "contact",
    ),
}

ROUTING_TABLE: dict[IntakeDomain, RouteTarget] = {
    IntakeDomain.ORGANISM: RouteTarget(
        workspace="~/Workspace/a-organvm",
        archetype="I",
        agent="codex/gemini",
        token_budget="large",
    ),
    IntakeDomain.TRANSMUTATION: RouteTarget(
        workspace="~/Workspace/meta-organvm/organvm-engine",
        archetype="II",
        agent="codex/gemini",
        token_budget="large",
    ),
    IntakeDomain.EMISSION: RouteTarget(
        workspace="~/Workspace/organvm-iv-taxis/orchestration-start-here",
        archetype="III",
        agent="codex/gemini",
        token_budget="large",
    ),
    IntakeDomain.HOUSEKEEPING: RouteTarget(
        workspace="~/Workspace/meta-organvm/organvm-corpvs-testamentvm",
        archetype="IV",
        agent="codex/gemini",
        token_budget="large",
    ),
    IntakeDomain.PIPELINE: RouteTarget(
        workspace="~/Workspace/4444J99/application-pipeline",
        agent="codex/gemini",
        token_budget="large",
    ),
    IntakeDomain.BILLING: RouteTarget(agent="human"),
    IntakeDomain.CORRESPONDENCE: RouteTarget(
        workspace="~/Workspace/organvm-iv-taxis/orchestration-start-here",
        archetype="RELAY-CIRCUIT",
        agent="claude",
        token_budget="medium",
    ),
    IntakeDomain.UNKNOWN: RouteTarget(agent="claude", token_budget="small"),
}

_ORGANISM_SECOND_PROMPT = {
    "signal",
    "gate",
    "query",
    "aesthetic",
    "teaching",
    "triptych",
}
_TRANSMUTATION_BUILD_PROMPT = {
    "build",
    "implement",
    "parser",
    "generator",
    "rectification",
    "cli",
}
_URGENCY_TERMS = ("p0", "p1", "urgent", "critical", "blocker", "tonight", "asap", "now")


def classify(raw_input: str) -> IntakeItem:
    """Classify raw operator text into a structured intake item."""

    raw = raw_input.strip()
    lowered = raw.lower()
    matches = {
        domain: [keyword for keyword in keywords if keyword in lowered]
        for domain, keywords in DOMAIN_KEYWORDS.items()
    }
    domain = _pick_domain(matches)
    target = ROUTING_TABLE[domain]
    keywords = matches.get(domain, [])
    tension = _estimate_tension(lowered, len(keywords))
    workspace = _expand_workspace(target.workspace)
    prompt_fragment = "\n".join(
        [
            "# Intake Router Fragment",
            f"Domain: {domain.value}",
            f"Keywords: {', '.join(keywords) or 'none'}",
            f"Workspace: {workspace or 'operator decision required'}",
            f"Agent: {target.agent}",
            f"Raw intake: {raw}",
        ]
    )
    return IntakeItem(
        raw=raw,
        domain=domain,
        keywords=keywords,
        tension=tension,
        suggested_archetype=target.archetype or "new",
        suggested_agent=target.agent,
        suggested_workspace=workspace,
        prompt_fragment=prompt_fragment,
    )


def route(item: IntakeItem) -> Dispatch:
    """Turn a classified intake into a dispatch recommendation."""

    target = ROUTING_TABLE[item.domain]
    workspace = _expand_workspace(target.workspace)
    prompt_template = _select_prompt(item, target.archetype)
    prompt = _build_prompt(item, workspace, target, prompt_template)
    return Dispatch(
        item=item,
        workspace=workspace,
        archetype=target.archetype or "new",
        agent=target.agent,
        prompt=prompt,
        token_budget=target.token_budget or "none",
    )


def emit_routing(dispatch: Dispatch) -> None:
    """Persist both the operator intake and the routed follow-up to the ledger."""

    actions = load_actions()
    sequences = load_sequences()
    registry = load_param_registry()

    manual_action = record(
        actions,
        sequences,
        registry,
        session=ROUTER_SESSION,
        verb="received_intake",
        target=f"intake:{dispatch.item.domain.value}",
        context=dispatch.item.raw,
        params=_dispatch_params(dispatch, include_subsystem=True),
        routes=_manual_routes(dispatch),
        origin=ActionOrigin.MANUAL,
    )

    save_actions(actions)
    save_sequences(sequences)
    save_param_registry(registry)

    emit_state_change(
        subsystem="intake_router",
        verb="routed_intake",
        target=f"intake_router:{dispatch.item.domain.value}",
        from_state="received",
        to_state="dispatched",
        session=ROUTER_SESSION,
        params=_dispatch_params(dispatch, include_subsystem=False)
        | {"intake_action_id": manual_action.id},
        routes=_emitted_routes(dispatch, manual_action.id),
    )


def recent_dispatches(
    domain: IntakeDomain | None = None,
    limit: int = 10,
) -> list[Action]:
    """Return the most recent emitted intake-router dispatches."""

    actions = [
        action
        for action in load_actions().actions
        if action.origin == ActionOrigin.EMITTED
        and action.params.get("subsystem") == "intake_router"
        and (domain is None or action.params.get("domain") == domain.value)
    ]
    return list(reversed(actions[-limit:]))


def routing_table_rows() -> list[dict[str, str]]:
    """Expose the routing map in a CLI-friendly tabular shape."""

    prompts = _load_prompt_templates()
    rows: list[dict[str, str]] = []
    for domain, target in ROUTING_TABLE.items():
        prompt_title = ""
        if target.archetype and prompts.get(target.archetype):
            prompt_title = prompts[target.archetype][0].title
        rows.append(
            {
                "domain": domain.value,
                "workspace": _expand_workspace(target.workspace) or "—",
                "archetype": target.archetype or "—",
                "agent": target.agent,
                "token_budget": target.token_budget or "—",
                "prompt": prompt_title or "manual follow-up",
            }
        )
    return rows


def _pick_domain(matches: dict[IntakeDomain, list[str]]) -> IntakeDomain:
    best = IntakeDomain.UNKNOWN
    best_count = 0
    for domain in DOMAIN_KEYWORDS:
        count = len(matches.get(domain, []))
        if count > best_count:
            best = domain
            best_count = count
    return best if best_count else IntakeDomain.UNKNOWN


def _estimate_tension(lowered: str, keyword_count: int) -> float:
    tension = 0.15 + min(keyword_count * 0.12, 0.36)
    if any(term in lowered for term in _URGENCY_TERMS):
        tension += 0.3
    if "?" in lowered:
        tension += 0.05
    return round(min(tension, 1.0), 2)


def _expand_workspace(workspace: str) -> str:
    if not workspace:
        return ""
    return str(Path(workspace).expanduser().resolve())


def _build_prompt(
    item: IntakeItem,
    workspace: str,
    target: RouteTarget,
    prompt_template: PromptTemplate | None,
) -> str:
    lines = [
        "# Intake Router Dispatch",
        f"# Domain: {item.domain.value}",
        f"# Archetype: {target.archetype or 'new'}",
        f"# Suggested agent: {target.agent}",
        f"# Token budget: {target.token_budget or 'none'}",
        f"# Workspace: {workspace or 'operator decision required'}",
        "",
        "Operator intake:",
        item.raw,
        "",
        f"Routing signals: {', '.join(item.keywords) or 'none'}",
        f"Tension: {item.tension:.2f}",
        "",
    ]
    if prompt_template:
        lines.extend(
            [
                f"# Archetype prompt: {prompt_template.title}",
                "",
                prompt_template.body,
            ]
        )
    elif workspace:
        lines.extend(
            [
                f"cd {workspace}",
                "",
                f"# Follow this intake directly in {workspace}",
            ]
        )
    else:
        lines.extend(
            [
                "# Manual routing required",
                f"# Suggested next actor: {target.agent}",
            ]
        )
    return "\n".join(lines).strip()


def _dispatch_params(
    dispatch: Dispatch, include_subsystem: bool
) -> dict[str, float | str]:
    params: dict[str, float | str] = {
        "domain": dispatch.item.domain.value,
        "keywords": ", ".join(dispatch.item.keywords) or "none",
        "tension": dispatch.item.tension,
        "archetype": dispatch.archetype,
        "agent": dispatch.agent,
        "workspace": dispatch.workspace or "none",
        "token_budget": dispatch.token_budget,
    }
    if include_subsystem:
        params["subsystem"] = "intake_router"
    return params


def _manual_routes(dispatch: Dispatch) -> list[dict[str, str]]:
    routes = [{"kind": RouteKind.FEEDS.value, "target": _route_target(dispatch)}]
    if dispatch.archetype != "new":
        routes.append(
            {"kind": RouteKind.FEEDS.value, "target": f"archetype:{dispatch.archetype}"}
        )
    return routes


def _emitted_routes(dispatch: Dispatch, intake_action_id: str) -> list[dict[str, str]]:
    routes = [{"kind": RouteKind.INFORMED_BY.value, "target": intake_action_id}]
    routes.extend(_manual_routes(dispatch))
    return routes


def _route_target(dispatch: Dispatch) -> str:
    return dispatch.workspace or f"agent:{dispatch.agent}"


def _select_prompt(item: IntakeItem, archetype: str) -> PromptTemplate | None:
    prompts = _load_prompt_templates().get(archetype, [])
    if not prompts:
        return None
    lowered = item.raw.lower()
    if (
        archetype == "I"
        and len(prompts) > 1
        and _ORGANISM_SECOND_PROMPT.intersection(item.keywords)
    ):
        return prompts[1]
    if (
        archetype == "II"
        and len(prompts) > 1
        and any(term in lowered for term in _TRANSMUTATION_BUILD_PROMPT)
    ):
        return prompts[1]
    return prompts[0]


@lru_cache(maxsize=1)
def _load_prompt_templates() -> dict[str, list[PromptTemplate]]:
    if not ARCHETYPE_PLAN.exists():
        return {}
    text = ARCHETYPE_PLAN.read_text(encoding="utf-8")
    sections = list(
        re.finditer(r"^## Archetype (?P<id>[IVX]+):.*$", text, flags=re.MULTILINE)
    )
    prompts: dict[str, list[PromptTemplate]] = {}
    for index, match in enumerate(sections):
        start = match.end()
        end = sections[index + 1].start() if index + 1 < len(sections) else len(text)
        archetype = match.group("id")
        section_text = text[start:end]
        prompts[archetype] = [
            PromptTemplate(
                title=prompt.group("title").strip(), body=prompt.group("body").strip()
            )
            for prompt in re.finditer(
                r"^### Prompt: (?P<title>.+?)\n\n```(?:\w+)?\n(?P<body>.*?)\n```",
                section_text,
                flags=re.MULTILINE | re.DOTALL,
            )
        ]
    return prompts
