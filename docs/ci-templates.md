# CI Templates Per Stack

> **Governance**: Article IV (Documentation Precedes Deployment)
> **Scope**: All repositories across the eight-organ system
> **Version**: 1.0

---

## Why This Exists

105 repos across 8 organs use different stacks (Python, TypeScript, Markdown-only).
Without reusable CI templates, each repo invents its own workflow, leading to
inconsistent quality gates and maintenance burden.

This document defines 3 canonical CI template tiers matching the `ci_workflow`
enumerations in registry-v2.json.

---

## Template Tiers

### ci-python.yml — Python Projects

**Used by**: agentic-titan, orchestration-start-here scripts, most ORGAN-I/II/III repos

```yaml
name: CI — Python

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install ruff
      - run: ruff check .

  typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -e ".[dev]"
      - run: mypy .

  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -e ".[dev]"
      - run: pytest --cov=. --cov-report=term -v

  governance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Validate seed.yaml
        run: python3 -c "import yaml; yaml.safe_load(open('seed.yaml'))"
      - name: Secret scan
        run: |
          if grep -rn 'sk-[a-zA-Z0-9]\{20,\}\|ghp_[a-zA-Z0-9]\{36\}\|AKIA[A-Z0-9]\{16\}' \
            --include='*.py' --include='*.yml' --include='*.yaml' --include='*.json' \
            --include='*.md' --include='*.ts' --include='*.js' .; then
            echo "::error::Potential secrets detected"
            exit 1
          fi
```

**Ruff rules**: `["E", "F", "I", "N", "W", "UP"]` (errors, pyflakes, isort, naming, warnings, pyupgrade)

**Tier-specific additions**:
- **Flagship**: Add coverage thresholds (`--cov-fail-under=80`), add `validate-deps.py` job
- **Standard**: Matrix can be single Python version
- **Infrastructure**: Skip typecheck, test with smoke tests only

---

### ci-typescript.yml — TypeScript Projects

**Used by**: agent--claude-smith, portfolio, some ORGAN-II packages

```yaml
name: CI — TypeScript

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "22"
      - run: npm ci
      - run: npm run typecheck

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "22"
      - run: npm ci
      - run: npm test

  governance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Validate seed.yaml
        run: |
          node -e "const yaml = require('js-yaml'); \
            const fs = require('fs'); \
            yaml.load(fs.readFileSync('seed.yaml', 'utf8'));"
      - name: Secret scan
        run: |
          if grep -rn 'sk-[a-zA-Z0-9]\{20,\}\|ghp_[a-zA-Z0-9]\{36\}\|AKIA[A-Z0-9]\{16\}' \
            --include='*.ts' --include='*.js' --include='*.yml' --include='*.yaml' \
            --include='*.json' --include='*.md' .; then
            echo "::error::Potential secrets detected"
            exit 1
          fi
```

**Tier-specific additions**:
- **Flagship**: Add coverage thresholds, add security tests
- **Standard**: Single node version, basic test suite

---

### ci-minimal.yml — Documentation & Infrastructure

**Used by**: org-dotgithub, ORGAN-VII repos, doc-only repos, stubs

```yaml
name: CI — Minimal

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: README check
        run: |
          if [ -f "README.md" ]; then
            WORDS=$(wc -w < README.md)
            echo "README.md: $WORDS words"
            if [ "$WORDS" -lt 50 ]; then
              echo "::warning::README.md is very short ($WORDS words)"
            fi
          else
            echo "::error::No README.md found"
            exit 1
          fi

      - name: Validate seed.yaml
        run: python3 -c "import yaml; yaml.safe_load(open('seed.yaml'))"

      - name: Secret scan
        run: |
          if grep -rn 'sk-[a-zA-Z0-9]\{20,\}\|ghp_[a-zA-Z0-9]\{36\}\|AKIA[A-Z0-9]\{16\}' \
            --include='*.py' --include='*.yml' --include='*.yaml' --include='*.json' \
            --include='*.md' --include='*.ts' --include='*.js' .; then
            echo "::error::Potential secrets detected"
            exit 1
          fi
```

---

## Governance Job

All three templates include a `governance` (or `validate`) job that runs:

1. **seed.yaml validation**: Ensures the automation contract parses correctly
2. **Secret scanning**: Detects leaked API keys (`sk-*`, `ghp_*`, `AKIA*`)

Flagship repos add:
3. **Dependency validation**: `python3 scripts/validate-deps.py` (no back-edges)
4. **Registry consistency**: Verify registry.json matches reality

---

## Mapping to Registry

The `ci_workflow` field in registry-v2.json maps repos to templates:

| `ci_workflow` Value | Template | Description |
|---------------------|----------|-------------|
| `ci-python` | ci-python.yml | Python projects with ruff + mypy + pytest |
| `ci-typescript` | ci-typescript.yml | TypeScript projects with tsc + vitest |
| `ci-minimal` | ci-minimal.yml | Doc-only, infrastructure, stubs |
| `none` | — | No CI (only for ARCHIVED repos) |

---

## Tier-Based Testing Matrix

| Tier | Lint | Typecheck | Unit Tests | Coverage | Contract Tests | Matrix CI |
|------|------|-----------|------------|----------|----------------|-----------|
| **Flagship** | Required | Required | Required | ≥80% | Required | Multi-version |
| **Standard** | Required | Recommended | Required | Tracked | Optional | Single-version |
| **Infrastructure** | Recommended | Optional | Smoke only | Optional | Optional | Single-version |
| **Stub** | Optional | N/A | Schema only | N/A | N/A | N/A |

---

## Adopting a Template

1. Copy the appropriate template to your repo's `.github/workflows/ci.yml`
2. Adjust the Python/Node version to match your `pyproject.toml` or `package.json`
3. Update the `ci_workflow` field in registry-v2.json
4. Run the workflow locally first: `act -j lint` (if using `act`)
5. Push and verify CI passes on the PR

---

## References

- **Branching Strategy**: `docs/branching-strategy.md` — branch naming and lifecycle
- **PR Template**: `.github/PULL_REQUEST_TEMPLATE.md` — governance checklist
- **Registry**: `registry.json` — `ci_workflow` field per repo
- **Governance Rules**: `governance-rules.json` — Article IV
