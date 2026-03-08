# Repo Templates per Organ Archetype

> **Governance**: Feature Backlog F-55
> **Scope**: All new repository creation across the eight-organ system
> **Version**: 1.0

---

## Purpose

GitHub template repositories for each organ type, ensuring every new repo starts with the correct directory structure, pre-filled `seed.yaml`, and organ-appropriate scaffolding. Templates eliminate the "blank page" problem and enforce structural consistency from day one.

---

## Template: Research (ORGAN-I — Theoria)

**Use for**: Literature surveys, theoretical explorations, symbolic computing experiments, knowledge bases.

```
<repo-name>/
├── .github/
│   └── workflows/
│       └── ci.yml              # Markdown lint + link check
├── docs/
│   ├── bibliography.md         # Annotated bibliography
│   └── methodology.md          # Research approach
├── references/
│   └── .gitkeep                # External sources, papers, notes
├── CLAUDE.md                   # AI agent context
├── CITATION.cff                # Academic citation metadata
├── LICENSE                     # Default: MIT or CC-BY-4.0
├── README.md                   # Project overview + research question
└── seed.yaml                   # ORGANVM metadata
```

**Pre-filled seed.yaml**:

```yaml
schema: "1.0"
organ: I
organ_name: Theoria
tier: standard
promotion_status: LOCAL
produces:
  - type: research-output
    consumers: [organvm-ii-poiesis]
consumes: []
subscriptions: []
ci_agent: markdown-lint
```

**README template focus**: Research question, methodology, current findings, references.

---

## Template: Creative System (ORGAN-II — Poiesis)

**Use for**: Generative art, music systems, performance tools, creative coding, interactive installations.

```
<repo-name>/
├── .github/
│   └── workflows/
│       └── ci.yml              # Lint + test (language-dependent)
├── src/
│   └── .gitkeep                # Core creative engine code
├── assets/
│   └── .gitkeep                # Media, textures, samples, presets
├── examples/
│   └── .gitkeep                # Example outputs, demos, sketches
├── tests/
│   └── .gitkeep                # Unit/integration tests
├── CLAUDE.md                   # AI agent context
├── LICENSE                     # Default: MIT or GPL-3.0
├── README.md                   # Project overview + examples
└── seed.yaml                   # ORGANVM metadata
```

**Pre-filled seed.yaml**:

```yaml
schema: "1.0"
organ: II
organ_name: Poiesis
tier: standard
promotion_status: LOCAL
produces:
  - type: creative-output
    consumers: [organvm-iii-ergon]
consumes:
  - type: research-output
    producer: organvm-i-theoria
subscriptions:
  - event: research.published
    source: organvm-i-theoria
ci_agent: lint-and-test
```

**README template focus**: What it creates, how to run it, example outputs (screenshots/audio/video links).

---

## Template: Product (ORGAN-III — Ergon)

**Use for**: SaaS tools, CLI utilities, libraries, APIs, developer products.

```
<repo-name>/
├── .github/
│   └── workflows/
│       └── ci.yml              # Lint + typecheck + test + coverage
├── src/
│   └── <package_name>/
│       ├── __init__.py         # (Python) or index.ts (TypeScript)
│       └── .gitkeep
├── tests/
│   ├── unit/
│   │   └── .gitkeep
│   ├── integration/
│   │   └── .gitkeep
│   └── conftest.py             # (Python) or setup.ts (TypeScript)
├── docs/
│   └── .gitkeep                # API docs, architecture
├── CLAUDE.md                   # AI agent context
├── CHANGELOG.md                # Keep a Changelog format
├── LICENSE                     # Default: MIT
├── README.md                   # Project overview + install + usage
├── pyproject.toml              # (Python) or package.json (TypeScript)
└── seed.yaml                   # ORGANVM metadata
```

**Pre-filled seed.yaml**:

```yaml
schema: "1.0"
organ: III
organ_name: Ergon
tier: standard
promotion_status: LOCAL
produces:
  - type: product
    consumers: [any]
  - type: community_signal
    consumers: [organvm-vi-koinonia]
  - type: distribution_signal
    consumers: [organvm-vii-kerygma]
consumes:
  - type: creative-output
    producer: organvm-ii-poiesis
subscriptions:
  - event: community.event_created
    source: organvm-vi-koinonia
  - event: distribution.dispatched
    source: organvm-vii-kerygma
ci_agent: full-pipeline
```

**README template focus**: Problem statement, installation, usage examples, API reference link, contributing guide.

---

## Template: Orchestration (ORGAN-IV — Taxis)

**Use for**: Governance tools, orchestration scripts, registry management, automation infrastructure.

```
<repo-name>/
├── .github/
│   └── workflows/
│       └── ci.yml              # Lint + validate + test
├── scripts/
│   └── .gitkeep                # Automation scripts
├── docs/
│   └── .gitkeep                # Governance docs, SOPs, playbooks
├── tests/
│   └── .gitkeep
├── CLAUDE.md                   # AI agent context
├── LICENSE                     # Default: MIT
├── README.md                   # Project overview + governance context
└── seed.yaml                   # ORGANVM metadata
```

**Pre-filled seed.yaml**:

```yaml
schema: "1.0"
organ: IV
organ_name: Taxis
tier: standard
promotion_status: LOCAL
produces:
  - type: governance-rules
    consumers: [all]
  - type: health-reports
    consumers: [all]
consumes:
  - type: registry-updates
    producer: any
subscriptions: []
ci_agent: validate-and-test
```

**README template focus**: What this orchestrates, governance context, how to run scripts.

---

## Template: Narrative (ORGAN-VII — Kerygma)

**Use for**: Distribution profiles, social automation, announcement templates, POSSE infrastructure.

```
<repo-name>/
├── .github/
│   └── workflows/
│       └── ci.yml              # YAML lint + schema validation
├── content/
│   └── .gitkeep                # Announcement drafts, social posts
├── templates/
│   └── .gitkeep                # Distribution templates (per-platform)
├── config/
│   └── distribution.yaml       # Platform configuration
├── CLAUDE.md                   # AI agent context
├── LICENSE                     # Default: MIT
├── README.md                   # Project overview + distribution strategy
└── seed.yaml                   # ORGANVM metadata
```

**Pre-filled seed.yaml**:

```yaml
schema: "1.0"
organ: VII
organ_name: Kerygma
tier: standard
promotion_status: LOCAL
produces: []
consumes:
  - type: distribution_signal
    producer: organvm-iii-ergon
  - type: essay-notifications
    producer: organvm-v-logos
subscriptions:
  - event: product.release
    source: organvm-iii-ergon
  - event: essay.published
    source: organvm-v-logos
ci_agent: yaml-lint
```

**README template focus**: What gets distributed, to which platforms, how templates work.

---

## Common Elements (All Templates)

Every template includes these files with organ-specific content:

### CLAUDE.md Structure

```markdown
# CLAUDE.md — <repo-name>

**ORGAN <N>** (<organ-name>) · `<github-org>/<repo-name>`
**Status:** <promotion_status>

## What This Repo Is
<one paragraph>

## Stack
<language, framework, key dependencies>

## Directory Structure
<tree output>

## Key Commands
<build, test, lint, run>

<!-- ORGANVM:AUTO:START -->
## System Context (auto-generated — do not edit)
<!-- filled by automation -->
<!-- ORGANVM:AUTO:END -->
```

### seed.yaml Schema

All templates use schema version 1.0. See `orchestration-start-here/docs/seed-schema/` for the full schema definition and validation rules.

---

## Implementation

### Creating GitHub Template Repos

```bash
# Create template repo on GitHub
gh repo create organvm-iv-taxis/template-<organ> \
  --template \
  --public \
  --description "ORGANVM template for ORGAN-<N> (<organ-name>) repositories"

# Push template content
cd template-<organ>
git add -A
git commit -m "chore: initial template for ORGAN-<N> repos"
git push origin main
```

### Using a Template

```bash
# Create new repo from template
gh repo create <org>/<new-repo> \
  --template organvm-iv-taxis/template-<organ> \
  --public

# Clone and customize
git clone git@github.com:<org>/<new-repo>.git
cd <new-repo>
# Edit seed.yaml, README.md, CLAUDE.md with repo-specific content
```

---

## References

- [30-Day Growth Plan](30-day-growth-plan.md) — Uses these templates in Week 1
- [CI Templates](ci-templates.md) — Workflow configurations included in each template
- `seed-schema/` — Canonical seed.yaml schema and validation
- `governance-rules.json` — Organ definitions and tier requirements
