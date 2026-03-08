# Triple-Serving Project Template

> **Governance**: Feature Backlog F-52
> **Scope**: All repos targeting PUBLIC_PROCESS or GRADUATED status
> **Version**: 1.0

---

## Purpose

Every ORGANVM project can simultaneously serve three functions: a working product, a portfolio piece, and an academic output. This template provides the structure and checklists for achieving all three from a single codebase.

---

## The Three Serves

### 1. Product — Revenue or Utility

The project does something useful. It solves a problem, automates a workflow, or provides a tool that people (or other systems) consume.

**Requirements**:
- [ ] Clear value proposition in README (first paragraph)
- [ ] Installation/usage instructions that work for a stranger
- [ ] CI passing, tests covering core functionality
- [ ] Versioned releases with changelogs
- [ ] Error handling and user-facing messages are helpful

### 2. Portfolio — Demonstrable on GitHub

The project tells a professional story. A hiring manager, collaborator, or investor can understand the quality and intent within 60 seconds.

**Requirements**:
- [ ] README with architecture diagram or clear system description
- [ ] Social preview image using organ palette
- [ ] Clean commit history (conventional commits, no "fix typo" chains)
- [ ] GitHub topics set (organ, stack, domain keywords)
- [ ] Live demo or screenshot if applicable
- [ ] License file present

### 3. Academic Output — Citable Research

The project contributes to knowledge. It documents decisions, methodology, and findings in a way that can be referenced by others.

**Requirements**:
- [ ] Zenodo DOI via GitHub integration
- [ ] CITATION.cff file in repo root
- [ ] Architecture Decision Records (ADRs) for non-obvious choices
- [ ] References section linking to prior art and influences
- [ ] Abstract or extended description suitable for citation

---

## Research-Creation 4-Form Taxonomy

Every ORGANVM project maps to one (or more) of the four research-creation forms. This taxonomy connects the organ model to academic research methodology.

### Research-for-Creation → ORGAN-I (Theoria)

**Definition**: Research conducted to enable future creative or technical work.

**ORGANVM pattern**: Literature reviews, technology surveys, design explorations in `organvm-i-theoria/` that inform downstream organs.

**Example**: Investigating recursive symbolic systems to design the engine architecture.

**Artifacts**: Survey documents, annotated bibliographies, design space maps.

### Research-from-Creation → ORGAN-II (Poiesis)

**Definition**: Knowledge generated as a byproduct of creative practice.

**ORGANVM pattern**: Insights discovered while building generative art systems, performance tools, or creative coding projects in `organvm-ii-poiesis/`.

**Example**: Discovering emergent patterns in algorithmic composition that inform music theory.

**Artifacts**: Process journals, reflective documentation, pattern catalogs.

### Creation-as-Research → ORGAN-III (Ergon)

**Definition**: The act of building is itself the research method.

**ORGANVM pattern**: Products in `organvm-iii-ergon/` whose development process generates transferable knowledge about software architecture, AI orchestration, or developer tooling.

**Example**: Building a SaaS tool to test hypotheses about AI-conductor workflow patterns.

**Artifacts**: Working software, architecture documentation, performance benchmarks.

### Creative-Presentation-of-Research → ORGAN-V (Logos)

**Definition**: Research findings presented through creative or narrative means.

**ORGANVM pattern**: Essays, visualizations, and public discourse in `organvm-v-logos/` that translate technical findings into accessible narratives.

**Example**: An essay series explaining the eight-organ model through metaphor and case studies.

**Artifacts**: Published essays, talks, data visualizations, infographics.

---

## CITATION.cff Template

```yaml
cff-version: 1.2.0
message: "If you use this project, please cite it as below."
type: software
title: "<Project Name>"
abstract: "<One-paragraph description>"
authors:
  - family-names: "<Last Name>"
    given-names: "<First Name>"
    orcid: "https://orcid.org/<ORCID>"
repository-code: "https://github.com/<org>/<repo>"
license: "<SPDX identifier>"
version: "<current version>"
date-released: "<YYYY-MM-DD>"
keywords:
  - "<keyword1>"
  - "<keyword2>"
  - organvm
  - "<organ-name>"
```

---

## Zenodo Integration Steps

### Initial Setup

1. Link GitHub account to Zenodo at https://zenodo.org/account/settings/github/
2. Enable the specific repository in Zenodo settings
3. Create a GitHub Release (Zenodo auto-archives on release)
4. Copy the DOI badge from Zenodo and add to README

### Per-Release

1. Update `CITATION.cff` with new version and date
2. Create GitHub Release with release notes
3. Zenodo automatically creates a new version DOI
4. Parent DOI (concept DOI) always resolves to latest

### .zenodo.json (Optional Metadata)

```json
{
  "title": "<Project Name>",
  "upload_type": "software",
  "description": "<Abstract>",
  "creators": [
    {
      "name": "<Last, First>",
      "orcid": "<ORCID>"
    }
  ],
  "keywords": ["organvm", "<organ>", "<domain>"],
  "license": {"id": "<SPDX>"},
  "related_identifiers": [
    {
      "identifier": "https://github.com/<org>/<repo>",
      "relation": "isSupplementTo",
      "scheme": "url"
    }
  ]
}
```

---

## Funding Pipeline Guide

For projects that warrant external funding:

### Stage 1 — Internal Validation

- Project has all three serves operational
- At least PUBLIC_PROCESS promotion status
- Documented methodology and results

### Stage 2 — Grant Identification

- **Arts councils**: Creative coding, generative art projects (ORGAN-II)
- **Research grants**: Novel methodology, published findings (ORGAN-I, ORGAN-V)
- **Tech grants**: Open source tools, developer infrastructure (ORGAN-III)
- **GitHub Sponsors**: Any project with public users

### Stage 3 — Application Artifacts

- [ ] Abstract (250 words) — from CITATION.cff extended
- [ ] Project description (2 pages) — from README + architecture docs
- [ ] Budget justification — infrastructure costs, time allocation
- [ ] Prior work / preliminary results — from ADRs and changelogs
- [ ] Impact statement — from portfolio metrics and user data

### Stage 4 — Post-Award

- [ ] Zenodo DOI for deliverables
- [ ] Progress reports referencing git history
- [ ] Final report with DORA-style metrics

---

## References

- [Release Checklist](release-checklist.md) — Versioning and release process
- [30-Day Growth Plan](30-day-growth-plan.md) — Onboarding template for new repos
- [Conductor Playbook](conductor-playbook.md) — Session lifecycle
- Zenodo documentation: https://zenodo.org/
- CITATION.cff specification: https://citation-file-format.github.io/
