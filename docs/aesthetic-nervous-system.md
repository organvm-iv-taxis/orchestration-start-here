# Aesthetic Nervous System

> **Governance**: Feature Backlog F-80
> **Scope**: All public-facing repositories across the eight-organ system
> **Version**: 1.0

---

## Purpose

Enforce visual identity consistency across ORGANVM organs through `organ-aesthetic.yaml` definitions and automated CI validation. Each organ has a distinct aesthetic identity — palette, typography, tone, layout — that should be consistently applied to READMEs, social previews, documentation, and public interfaces.

---

## organ-aesthetic.yaml Schema

Each organ's `.github/` repository (e.g., `org-dotgithub`) defines the organ's visual identity:

```yaml
# organ-aesthetic.yaml
organ: IV
organ_name: Taxis
aesthetic:
  palette:
    primary: "#2563EB"       # Blue — orchestration, systems
    secondary: "#1E40AF"     # Dark blue — authority, governance
    accent: "#60A5FA"        # Light blue — clarity, precision
    background: "#0F172A"    # Near-black — infrastructure
    text: "#F8FAFC"          # Near-white — readability
  typography:
    heading: "JetBrains Mono"    # Monospace — technical precision
    body: "Inter"                # Sans-serif — clean readability
    code: "JetBrains Mono"      # Consistent code blocks
  tone:
    formality: formal            # formal | conversational | technical
    voice: authoritative         # authoritative | exploratory | playful
    pronouns: we                 # we | I | impersonal
  layout:
    badge_style: flat-square     # flat | flat-square | for-the-badge
    social_preview: required     # required | optional
    readme_sections:             # Required README sections
      - Overview
      - Installation
      - Usage
      - Architecture
      - Contributing
      - License
```

---

## Validation Checks

### Level 1 — Badge Compliance

Verify that README badges use the organ's palette colors.

```python
import re
import yaml

def check_badge_colors(readme_path: str, aesthetic: dict) -> list[str]:
    """Check that shields.io badges use organ palette colors."""
    violations = []
    palette = aesthetic["palette"]
    allowed_colors = {v.lstrip("#").lower() for v in palette.values()}

    with open(readme_path) as f:
        content = f.read()

    # Match shields.io color parameters
    badge_colors = re.findall(r'shields\.io/.*?(?:color|labelColor)=([a-fA-F0-9]{6})', content)
    for color in badge_colors:
        if color.lower() not in allowed_colors:
            violations.append(f"Badge color #{color} not in organ palette")

    return violations
```

### Level 2 — Social Preview Existence

Check that repos with `social_preview: required` have a social preview image set.

```bash
# Check if social preview is set
gh api /repos/<org>/<repo> --jq '.has_pages, .social_media_preview'

# Or check for a local social preview image
test -f .github/social-preview.png || echo "Missing social preview"
```

### Level 3 — Documentation Tone

Validate that documentation tone matches the organ's voice definition. This is advisory (heuristic-based), not blocking.

**Heuristics**:
- `formal`: No contractions ("don't" → "do not"), no emoji, no first-person singular
- `conversational`: Contractions allowed, second-person ("you") preferred
- `technical`: Passive voice acceptable, jargon expected, precision over readability

### Level 4 — README Section Compliance

Verify that required README sections exist:

```python
def check_readme_sections(readme_path: str, required_sections: list[str]) -> list[str]:
    """Check that README contains all required sections."""
    violations = []
    with open(readme_path) as f:
        content = f.read()

    headings = re.findall(r'^#{1,3}\s+(.+)$', content, re.MULTILINE)
    heading_lower = {h.strip().lower() for h in headings}

    for section in required_sections:
        if section.lower() not in heading_lower:
            violations.append(f"Missing required section: {section}")

    return violations
```

---

## CI Implementation

### GitHub Action: Aesthetic Validator

```yaml
name: Aesthetic Compliance
on:
  pull_request:
    paths:
      - 'README.md'
      - '.github/social-preview.*'
      - 'docs/**'

jobs:
  aesthetic-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Fetch organ-aesthetic.yaml
        run: |
          # Fetch from org .github repo
          curl -sL "https://raw.githubusercontent.com/${{ github.repository_owner }}/.github/main/organ-aesthetic.yaml" \
            -o organ-aesthetic.yaml || echo "No organ-aesthetic.yaml found"

      - name: Run aesthetic checks
        if: hashFiles('organ-aesthetic.yaml') != ''
        run: |
          python3 scripts/aesthetic-validator.py \
            --aesthetic organ-aesthetic.yaml \
            --readme README.md \
            --phase ${{ vars.AESTHETIC_PHASE || '1' }}
```

### Phase Rollout

| Phase | Behavior | Target |
|---|---|---|
| **Phase 1** | Advisory warnings only | All repos |
| **Phase 2** | Blocking for GRADUATED repos, advisory for others | GRADUATED + PUBLIC_PROCESS |
| **Phase 3** | Blocking for all PUBLIC_PROCESS and above | PUBLIC_PROCESS + GRADUATED |

Configure phase per-org using GitHub Variables:
```bash
gh variable set AESTHETIC_PHASE --body "1" --org organvm-iv-taxis
```

---

## Per-Organ Aesthetic Summaries

| Organ | Primary Color | Tone | Typography | Badge Style |
|---|---|---|---|---|
| I (Theoria) | Deep purple | Formal, scholarly | Serif headings | flat |
| II (Poiesis) | Warm gold | Exploratory, creative | Display fonts | for-the-badge |
| III (Ergon) | Forest green | Technical, practical | Sans-serif | flat-square |
| IV (Taxis) | System blue | Formal, authoritative | Monospace | flat-square |
| V (Logos) | Warm gray | Conversational, editorial | Serif body | flat |
| VI (Koinonia) | Coral | Conversational, inclusive | Rounded sans | for-the-badge |
| VII (Kerygma) | Signal red | Punchy, promotional | Bold sans | for-the-badge |
| META | Neutral slate | Technical, reference | Monospace | flat-square |

These are guidelines — exact values are defined in each org's `organ-aesthetic.yaml`.

---

## Social Preview Generation

For repos without a custom social preview, generate one from the organ palette:

```bash
# Using ImageMagick (available via Homebrew)
convert -size 1280x640 \
  xc:"#0F172A" \
  -font "JetBrains-Mono-Bold" \
  -pointsize 64 \
  -fill "#F8FAFC" \
  -gravity center \
  -annotate +0-40 "<Repo Name>" \
  -pointsize 28 \
  -fill "#60A5FA" \
  -annotate +0+40 "ORGAN-IV · Taxis · Orchestration" \
  .github/social-preview.png
```

---

## References

- `org-dotgithub/` — Contains `organ-aesthetic.yaml` for ORGAN-IV
- [Repository Rulesets](repository-rulesets.md) — Can enforce aesthetic checks as required status
- [Repo Templates](repo-templates.md) — Templates include organ-appropriate README structure
- [CODEOWNERS Strategy](codeowners-strategy.md) — Aesthetic files routed to appropriate reviewers
