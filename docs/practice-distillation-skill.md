# Canonical Practice Distillation Skill — Design Document

> **Governance**: Feature Backlog F-49
> **Scope**: a-i--skills build pipeline, ORGAN-IV governance
> **Version**: 1.0

---

## Purpose

Design an AI skill (for the `a-i--skills` collection) that translates well-known external software practices into ORGANVM-native specifications. The skill ensures that any adopted practice is compatible with the registry, governance rules, and the no-back-edges invariant before it enters the system.

---

## Problem Statement

External practices (trunk-based development, DORA metrics, ADR conventions, etc.) are described in their own terminology and assume their own organizational models. Adopting them into ORGANVM requires manual translation work:

1. Understanding the practice's core principles
2. Mapping those principles to the right organ(s)
3. Checking for governance conflicts (back-edge violations, tier mismatches)
4. Generating the actual artifacts (docs, seed.yaml fragments, CI config)

This skill automates steps 2–4 and assists with step 1.

---

## Skill Specification

### Metadata (YAML frontmatter)

```yaml
name: practice-distillation
version: "1.0"
category: knowledge
description: Translates external practices into ORGANVM-native specifications
tags:
  - governance
  - onboarding
  - standards
  - architecture
requires:
  - governance-rules.json awareness
  - registry-v2.json schema knowledge
  - seed.yaml schema knowledge
```

### Input

A canonical practice description provided as natural language. Examples:

- "Trunk-based development: all developers commit to main, branches live < 24 hours"
- "DORA metrics: deployment frequency, lead time, change failure rate, MTTR"
- "Architecture Decision Records: lightweight docs capturing context, decision, consequences"

The input may also include:
- A URL to the practice's canonical documentation
- A specific organ or repo where the practice should apply
- Constraints ("only for Python repos", "flagship tier only")

### Output

The skill produces a **practice adoption package** containing:

1. **Practice summary** — 2-3 sentence description in ORGANVM terminology
2. **Organ mapping** — which organ(s) own this practice and why
3. **Governance compatibility report**:
   - Back-edge check: does this practice create dependencies that violate `I→II→III` flow?
   - Tier applicability: flagship only, standard+, or all?
   - Promotion impact: does adoption change promotion criteria?
4. **seed.yaml fragment** — produces/consumes edges this practice introduces
5. **Documentation stub** — markdown file ready for `docs/` with governance header
6. **Implementation checklist** — ordered steps to adopt the practice

### Process

```
┌─────────────────────┐
│ 1. IDENTIFY          │  Parse input, extract practice name, core principles,
│    Practice          │  and any constraints provided by the user.
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│ 2. MAP               │  Determine which organ(s) own this practice:
│    to Organ(s)       │  - Process/workflow → ORGAN-IV (Taxis)
│                      │  - Measurement/metrics → ORGAN-IV or META
│                      │  - Documentation → ORGAN-V (Logos)
│                      │  - Distribution → ORGAN-VII (Kerygma)
│                      │  - Implementation → organ of the target repo
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│ 3. CHECK             │  Validate against governance-rules.json:
│    Governance        │  - No back-edges introduced
│    Compatibility     │  - No state-machine skipping
│                      │  - Compatible with existing produces/consumes graph
│                      │  If conflict detected: report conflict, suggest modification
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│ 4. GENERATE          │  Produce artifacts:
│    Artifacts         │  - seed.yaml fragment (edges only, merge-ready)
│                      │  - docs/ markdown with governance header
│                      │  - Implementation checklist
│                      │  - Optional: CI workflow fragment
└─────────────────────┘
```

---

## Governance Compatibility Checks

The skill must validate these invariants:

### No Back-Edges (Article II)

If the practice introduces a dependency from a higher-numbered organ to a lower-numbered organ, it violates the unidirectional flow. The skill must:
- Detect the violation
- Explain why it's a violation
- Suggest an alternative routing (e.g., via ORGAN-IV orchestration)

### Promotion State Machine (Article VI)

If the practice requires capabilities only available at certain promotion levels (e.g., "requires CI" implies at least CANDIDATE), the skill must note the minimum promotion_status.

### Tier Appropriateness

Some practices are overhead for infrastructure repos but essential for flagships. The skill should recommend tier-based rollout:
- **Flagship**: full adoption
- **Standard**: adapted adoption (reduced ceremony)
- **Infrastructure**: exempt or minimal

---

## Example: Distilling "DORA Metrics"

**Input**: "DORA metrics — track deployment frequency, lead time for changes, change failure rate, and mean time to restore"

**Output**:

```markdown
## Practice Summary
DORA metrics measure software delivery performance through four key indicators.
In ORGANVM, these map to promotion velocity and CI health across the organ system.

## Organ Mapping
- Primary owner: ORGAN-IV (Taxis) — orchestration metrics
- Data source: META (organvm-engine) — registry and CI data
- Reporting: ORGAN-V (Logos) — dashboards and essays

## Governance Compatibility
✅ No back-edges: metrics flow from META → IV → V (downstream only)
✅ Promotion compatible: applicable at CANDIDATE+ (requires CI)
⚠️ Tier note: meaningful only for repos with regular releases (flagship, active standard)

## seed.yaml Fragment
produces:
  - type: dora-metrics
    consumers: [orchestration-start-here, system-dashboard]
consumes:
  - type: ci-status
    producer: github-actions
  - type: release-events
    producer: any

## Implementation Checklist
1. Define metric collection points in CI workflows
2. Add metrics aggregation to calculate-metrics.py
3. Create dashboard view in system-dashboard
4. Set baseline thresholds per tier
5. Document in orchestration-start-here/docs/
```

---

## Integration with a-i--skills Pipeline

### File Location

```
a-i--skills/skills/knowledge/practice-distillation/
├── SKILL.md          # Main skill instructions (this design, formatted as skill)
├── references/
│   ├── governance-rules-summary.md
│   └── organ-mapping-guide.md
└── assets/
    └── practice-template.md
```

### Build Pipeline

The skill follows the standard a-i--skills build process:
- `name` in YAML frontmatter matches directory name
- Included in `knowledge` collection
- SHA-256 hash tracked in lockfile
- Agent bundles generated for Claude/Codex/Gemini

### Validation

```bash
cd a-i--skills
python3 scripts/validate_skills.py --collection example --unique
python3 scripts/skill_health_check.py --skill practice-distillation
```

---

## References

- `a-i--skills/` build pipeline — Skill structure and validation
- `governance-rules.json` — Articles I, II, VI (invariants to check)
- `scripts/validate-deps.py` — Back-edge detection (reusable logic)
- [Conductor Playbook](conductor-playbook.md) — Session lifecycle the skill operates within
