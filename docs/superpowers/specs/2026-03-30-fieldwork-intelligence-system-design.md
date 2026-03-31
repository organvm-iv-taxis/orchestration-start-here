# Fieldwork Intelligence System — Design Spec

**Date:** 2026-03-30
**Status:** APPROVED
**Module:** `contrib_engine/fieldwork.py`
**Data:** `contrib_engine/data/fieldwork.yaml`, `contrib_engine/data/dossiers/`

---

## 1. Purpose

Every contribution is a research expedition. The Fieldwork Intelligence System captures process observations about external projects during contribution — their merge protocols, review culture, CI architecture, repo layout, tooling choices, communication patterns — and distills them into actionable intelligence on three simultaneous axes (§2). The system closes three recursive loops (§12): self-targeting, knowledge refinement, and inbound attraction.

## 2. The Three Axes

Every observation is evaluated on three simultaneous axes:

1. **Self-directed (avoid ↔ absorb):** What should ORGANVM adopt, study, or reject?
2. **Strategic (shatterpoint ↔ fortress):** Where are their gaps and strengths?
3. **Knowledge output (what can this become?):** Tutorial, essay, tool, curriculum module, comparison data point, community seed, distribution hook?

The third axis is the professor's trick. A tenured professor hands a syllabus to a room of undergrads — the reading list is the bibliography for their next publication. The students think they're learning; they're doing literature review. The classroom is a refinement engine where the act of making knowledge reproducible forces the knowledge to become more precise.

The contribution engine operates the same model:
- **Agents** (students) do the fieldwork via PRs
- **Campaign** (syllabus) determines what they study
- **PRs** (assignments) produce both deliverables AND research data
- **Orchestrator** (professor) synthesizes across all agents' work
- **Synthesis** (paper) becomes publishable analysis
- **Publication** (next semester's reading list) attracts new contributors, which generates more observations

Publishing the analysis IS itself a contribution to the ecosystem. The essay "How 24 open-source projects handle contributor onboarding" demonstrates engagement depth, attracts inbound, positions ORGANVM as institutional actor, forces data refinement, and creates citable material. The output feeds the input.

## 3. Architecture — Four Layers

### Layer 1: Observation Stream (`data/fieldwork.yaml`) — MICRO

Append-only log of timestamped observations. Captured inline during contribution work. Cheap to write — one entry per observation. This is the micro layer.

```yaml
observations:
- id: fo-dapr-0328-001
  workspace: contrib--dapr-dapr
  timestamp: "2026-03-28T22:15:00"
  category: merge_protocol
  signal: "DCO signing required — bot blocks PR until signed-off-by present in commit message"
  spectrum: +1           # -2 avoid, -1 caution, 0 note, +1 study, +2 absorb
  strategic: null        # shatterpoint | missing_shield | friction_point | fortress | competitive_edge | competitive_gap
  source: pr_submission  # pr_submission | review_response | ci_run | repo_exploration | phase_transition
  evidence: "PR #9719 blocked by DCO bot check"
  scored_by: agent       # agent (inline) | orchestrator (phase transition review)
  related_absorption_ids: []  # Cross-ref to AbsorptionItem.id when both systems observe the same interaction
```

**Capture triggers:**
- **pr_submission** — friction encountered submitting the PR (CLA, DCO, changeset files, CI gates)
- **review_response** — maintainer responds (review depth, tone, response time, specificity)
- **ci_run** — CI behavior observed (speed, flakiness, coverage requirements, lint strictness)
- **repo_exploration** — structural observations while reading the codebase (layout, tooling, patterns)
- **phase_transition** — deliberate assessment at campaign phase boundaries
- **automated** — scraped repo metadata (branch protection, label taxonomy, contributor stats)

**Stream retention policy:** The observation stream is append-only but not unbounded. After dossier compilation, raw observations remain in the stream as audit trail and knowledge output source material. At 500 observations, the stream is rotated: observations older than 90 days that have been compiled into dossiers move to `data/fieldwork_archive/YYYY-QN.yaml`. The archive preserves source provenance for knowledge outputs without bloating the active stream.

**Scoring protocol:** Observations receive an initial spectrum score from the contributing agent inline (`scored_by: agent`). At phase transitions, the orchestrator reviews agent-scored observations and may re-score (`scored_by: orchestrator`). Agent scores are fast but noisy; orchestrator scores are delayed but calibrated. When both exist, the orchestrator score takes precedence. Strategic tags (`shatterpoint`, `missing_shield`) are always assigned by the orchestrator at phase transition — they require cross-repo context the inline agent doesn't have.

### Layer 2: Repo Dossier (`data/dossiers/{workspace}.yaml`) — STRUCTURED

Structured per-repo intelligence compiled from the observation stream + automated metadata scraping. One file per target repo. This is the structured view.

```yaml
workspace: contrib--dapr-dapr
target: dapr/dapr
stars: 25600
last_updated: "2026-03-30"

# --- Automated metadata (scraped) ---
metadata:
  default_branch: master
  branch_protection: true
  required_reviews: 2
  ci_platform: github_actions
  ci_avg_duration_minutes: 12
  label_count: 45
  contributor_count: 800
  license: Apache-2.0
  languages:
    Go: 95
    Shell: 3
    Makefile: 2
  has_contributing_md: true
  has_cla: false
  has_dco: true
  has_changelog: true
  has_security_policy: true

# --- Verdicts (compiled from observation stream, one per observed category) ---
verdicts:
- category: merge_protocol
  spectrum: +1
  summary: "DCO required, squash-merge enforced, 2 reviewers minimum"
  observation_count: 3
  provenance: synthesized
  first_observed: "2026-03-28"
  last_observed: "2026-03-30"
  trend: stable
  confidence: 0.6
- category: review_culture
  spectrum: null
  summary: ""
  observation_count: 1
  provenance: compiled
  first_observed: "2026-03-28"
  last_observed: "2026-03-28"
  trend: insufficient
  confidence: 0.2

# --- Strategic assessment ---
shatterpoints: []         # Identified gaps → potential contribution targets
missing_shields: []       # Defensive gaps → trust-building opportunities
competitive_notes: []     # Provenance: FREEFORM — survives dossier regeneration
compatibility_score: 0.45 # Different from ORGANVM practices → high learning value
outreach_workspace: contrib--dapr-dapr  # Cross-ref to outreach.yaml relationship
```

**Dossier compilation** runs on two triggers:
1. **On observation append** — new observation slots into the relevant category
2. **On phase transition** — full re-synthesis, verdict updates, shatterpoint detection

### Layer 3: Cross-Repo Synthesis (`data/fieldwork_synthesis.yaml`) — MACRO

Macro patterns that emerge across repos. Generated at phase transitions or on demand. This is where 24 individual dossiers become institutional knowledge.

```yaml
generated: "2026-03-30"
patterns:
- pattern: "DCO signing correlates with CNCF membership"
  repos: [contrib--dapr-dapr, contrib--grafana-k6]
  spectrum: 0
  category: merge_protocol

- pattern: "MCP ecosystem projects review 3x faster than agent frameworks"
  repos: [contrib--mcp-python-sdk, contrib--mcp-typescript-sdk, contrib--fastmcp, contrib--pydantic-ai, contrib--camel-ai-camel]
  spectrum: +1
  category: review_culture

- pattern: "4 of 7 Wave 2 projects lack security scanning CI"
  repos: [...]
  spectrum: null
  strategic: missing_shield
  category: ci_architecture
  action: "Batch security-scanning PRs across 4 repos — high-trust contribution pattern"

cross_repo_verdicts:
  merge_protocol: "Most mature projects (>10K stars) require DCO or CLA. Absorb: automated DCO for ORGANVM repos."
  review_culture: "Protocol projects (MCP) have faster review cycles than application frameworks. Target protocol repos for velocity."
  ci_architecture: "Go projects have stricter CI than Python. Absorb: adopt golangci-lint patterns for agentic-titan Go components."
```

### Layer 4: Knowledge Output Pipeline (`data/knowledge_outputs.yaml`) — PRODUCTION

The refinement engine. Every observation, dossier, and synthesis pattern is evaluated for what it can become. Knowledge outputs are routed to organs for production, and the act of production refines the source intelligence.

```yaml
outputs:
- id: ko-2026-03-30-001
  title: "Merge Protocol Taxonomy: CLA vs DCO vs None Across 24 Projects"
  output_type: comparison_study
  organ: V                           # Logos — essays, analysis
  source_observations: [fo-dapr-0328-001, fo-k6-0328-003, fo-temporal-0321-002]  # Stable observation IDs
  source_dossiers: [contrib--dapr-dapr, contrib--grafana-k6, contrib--temporal-sdk-python]
  status: candidate                  # candidate | drafting | published | archived
  refinement_notes: ""               # What producing this taught us about the source data

- id: ko-2026-03-30-002
  title: "Contributing to CNCF Projects: DCO, CI Gates, Review Culture"
  output_type: tutorial
  organ: VI                          # Koinonia — community, learning
  source_observations: [fo-dapr-0328-001, fo-dapr-0328-004, fo-k6-0328-002]
  source_dossiers: [contrib--dapr-dapr, contrib--grafana-k6]
  status: candidate
  refinement_notes: ""

- id: ko-2026-03-30-003
  title: "Automated Repo Contribution-Readiness Assessment"
  output_type: tool
  organ: III                         # Ergon — commercial products, dev utilities
  source_observations: []
  source_dossiers: []                # Drawn from all dossier metadata patterns
  status: candidate
  refinement_notes: ""
```

**Output types and their organ routing:**

| Output Type | Description | Target Organ | Refinement Effect |
|-------------|-------------|-------------|-------------------|
| `comparison_study` | Cross-repo analysis on a single dimension | V (Logos) | Forces data normalization across dossiers |
| `tutorial` | Step-by-step guide from contribution experience | VI (Koinonia) | Forces process articulation — gaps in the guide reveal gaps in understanding |
| `curriculum_module` | Structured teaching unit with exercises | VI (Koinonia) | Forces prerequisite identification and learning-path design |
| `essay` | Analytical/argumentative piece from synthesis patterns | V (Logos) | Forces thesis articulation — the claim must survive scrutiny |
| `tool` | Automatable pattern extracted from manual process | III (Ergon) | Forces algorithmic precision — you can't code what you can't specify |
| `pattern_catalog` | Named, reusable pattern with formal properties | I (Theoria) | Forces abstraction — the pattern must generalize beyond its origin |
| `community_seed` | Discussion topic or reading group material | VI (Koinonia) | Forces question formulation — the seed must be generative, not conclusory |
| `distribution_hook` | Thread, post, or content that attracts inbound | VII (Kerygma) | Forces audience modeling — what would make someone come to us? |
| `contribution_playbook` | Dossier → public "How to Contribute to X" guide | V + VII | Forces verification of every claim. One artifact serves internal intelligence AND external distribution. |

**The refinement loop:**

```
observe → record (fieldwork stream)
    → compile (dossier)
        → synthesize (cross-repo patterns)
            → identify knowledge output (what can this become?)
                → produce the output (essay, tutorial, tool)
                    → production reveals gaps in source data
                        → new targeted observations fill gaps
                            → source data is now more precise
                                → the output improves
                                    → publication attracts inbound
                                        → inbound generates new observations
```

Each production cycle makes the underlying intelligence more precise. Writing the tutorial "Contributing to CNCF Projects" forces you to verify: did dapr actually require 2 reviewers or was it 1? Was the CI 12 minutes or 8? The act of teaching audits the data.

**Automatic output detection:**

When the synthesis layer identifies a pattern spanning 3+ repos in the same category, it auto-generates a `candidate` knowledge output. The system proposes what to write based on what it's observed:

- 3+ repos with `merge_protocol` observations → comparison study candidate
- A dossier with 5+ observations in `contributor_experience` → tutorial candidate
- A cross-repo verdict with a strong spectrum signal → essay candidate
- A repeated manual process across repos → tool candidate

## 5. Spectrum Scales

### Self-Directed Spectrum (avoid ↔ absorb)

| Score | Label | Meaning | System Action |
|-------|-------|---------|---------------|
| -2 | **avoid** | Anti-pattern. Actively harmful. Do the opposite. | Log as anti-pattern in synthesis |
| -1 | **caution** | Suboptimal but not dangerous. Note for awareness. | No action |
| 0 | **note** | Neutral observation. Context without judgment. | Archive in dossier |
| +1 | **study** | Interesting. Worth deeper investigation. | Flag for review |
| +2 | **absorb** | Adopt into ORGANVM. Create backflow item. | **Auto-generate BackflowItem** |

### Strategic Value Tags

| Tag | Meaning | System Action |
|-----|---------|---------------|
| `shatterpoint` | Structural weakness — brittle CI, missing tests, unhandled edge cases | **Auto-generate CampaignAction** |
| `missing_shield` | Defensive gap — no security scanning, no branch protection, no CLA | **Auto-generate CampaignAction** (high trust) |
| `friction_point` | Contributor experience pain — unclear docs, broken dev setup | Generate candidate contribution |
| `fortress` | Well-defended — they've solved this thoroughly | Study and absorb only |
| `competitive_edge` | Something they do better than us | Absorb or note |
| `competitive_gap` | Something we do better than them | Note for positioning |

## 6. Observation Categories

| Category | What It Captures |
|----------|-----------------|
| `merge_protocol` | Squash/rebase/merge-commit policy, required checks, CLA/DCO, changeset requirements |
| `review_culture` | Response time, review depth, tone, number of reviewers, iteration rounds |
| `ci_architecture` | CI platform, speed, required checks, lint rules, coverage thresholds, flakiness |
| `repo_layout` | Source layout (src/ vs flat), test structure, config patterns, monorepo vs single |
| `tooling` | Dependency management, build tools, formatters, linters, changelog tools |
| `contributor_experience` | CONTRIBUTING.md quality, issue templates, label taxonomy, bot automation |
| `communication_style` | Maintainer tone, feedback specificity, community warmth, response cadence |
| `governance` | Decision-making visibility, roadmap transparency, release process, maintainer hierarchy |
| `documentation` | Doc quality, API docs, architecture docs, onboarding docs |
| `security_posture` | Security policy, vulnerability handling, dependency scanning, SAST/DAST |

## 7. Data Model (Pydantic)

```python
class SpectrumScore(IntEnum):
    AVOID = -2
    CAUTION = -1
    NOTE = 0
    STUDY = 1
    ABSORB = 2

class StrategicTag(StrEnum):
    SHATTERPOINT = "shatterpoint"
    MISSING_SHIELD = "missing_shield"
    FRICTION_POINT = "friction_point"
    FORTRESS = "fortress"
    COMPETITIVE_EDGE = "competitive_edge"
    COMPETITIVE_GAP = "competitive_gap"

class ObservationCategory(StrEnum):
    MERGE_PROTOCOL = "merge_protocol"
    REVIEW_CULTURE = "review_culture"
    CI_ARCHITECTURE = "ci_architecture"
    REPO_LAYOUT = "repo_layout"
    TOOLING = "tooling"
    CONTRIBUTOR_EXPERIENCE = "contributor_experience"
    COMMUNICATION_STYLE = "communication_style"
    GOVERNANCE = "governance"
    DOCUMENTATION = "documentation"
    SECURITY_POSTURE = "security_posture"

class ObservationSource(StrEnum):
    PR_SUBMISSION = "pr_submission"
    REVIEW_RESPONSE = "review_response"
    CI_RUN = "ci_run"
    REPO_EXPLORATION = "repo_exploration"
    PHASE_TRANSITION = "phase_transition"
    AUTOMATED = "automated"

class FieldObservation(BaseModel):
    id: str                                  # Stable ID: "fo-{workspace}-{timestamp_short}-{seq}"
    workspace: str
    timestamp: str
    category: ObservationCategory
    signal: str                              # The observation itself
    spectrum: SpectrumScore = SpectrumScore.NOTE
    strategic: StrategicTag | None = None
    source: ObservationSource
    evidence: str = ""                       # PR URL, commit, screenshot ref
    scored_by: str = "agent"                 # "agent" (inline) | "orchestrator" (phase transition)
    related_absorption_ids: list[str] = Field(default_factory=list)  # Cross-ref to AbsorptionItem.id

class FieldworkIndex(BaseModel):
    generated: str = ""
    observations: list[FieldObservation] = Field(default_factory=list)

class VerdictProvenance(StrEnum):
    """How a dossier field was produced."""
    COMPILED = "compiled"           # Filtered from observation stream (deterministic)
    SCRAPED = "scraped"             # GitHub API metadata (automated)
    SYNTHESIZED = "synthesized"     # Requires judgment (agent or orchestrator)
    FREEFORM = "freeform"           # Human-written, survives regeneration

class Trend(StrEnum):
    IMPROVING = "improving"
    STABLE = "stable"
    DEGRADING = "degrading"
    INSUFFICIENT = "insufficient"   # Not enough data points for trend

class DossierVerdict(BaseModel):
    category: ObservationCategory
    spectrum: SpectrumScore | None = None
    summary: str = ""
    observation_count: int = 0
    provenance: VerdictProvenance = VerdictProvenance.SYNTHESIZED
    first_observed: str = ""        # ISO date of earliest observation in this category
    last_observed: str = ""         # ISO date of most recent observation
    trend: Trend = Trend.INSUFFICIENT  # Temporal trajectory — the trajectory IS the intelligence
    confidence: float = 0.0            # 0.0-1.0 from observation_count × source_diversity × temporal_span

class RepoMetadata(BaseModel):
    default_branch: str = ""
    branch_protection: bool = False
    required_reviews: int = 0
    ci_platform: str = ""
    ci_avg_duration_minutes: float = 0
    label_count: int = 0
    contributor_count: int = 0
    license: str = ""
    languages: dict[str, int] = Field(default_factory=dict)
    has_contributing_md: bool = False
    has_cla: bool = False
    has_dco: bool = False
    has_changelog: bool = False
    has_security_policy: bool = False

class Shatterpoint(BaseModel):
    category: ObservationCategory
    description: str
    contribution_opportunity: str
    campaign_action_id: str = ""             # If a CampaignAction was generated

class RepoDossier(BaseModel):
    workspace: str
    target: str
    stars: int = 0
    last_updated: str = ""
    metadata: RepoMetadata = Field(default_factory=RepoMetadata)
    verdicts: list[DossierVerdict] = Field(default_factory=list)  # Keyed by category, not hardcoded sections
    shatterpoints: list[Shatterpoint] = Field(default_factory=list)
    missing_shields: list[Shatterpoint] = Field(default_factory=list)
    competitive_notes: list[str] = Field(default_factory=list)    # Provenance: FREEFORM — survives regen
    compatibility_score: float = 0.0  # 0.0-1.0 similarity to ORGANVM practices. High = easy contrib, low = high learning value
    outreach_workspace: str = ""      # Cross-ref to OutreachIndex workspace for relationship data

    def verdict_for(self, category: ObservationCategory) -> DossierVerdict | None:
        return next((v for v in self.verdicts if v.category == category), None)

class SynthesisPattern(BaseModel):
    pattern: str
    repos: list[str] = Field(default_factory=list)
    spectrum: SpectrumScore | None = None
    strategic: StrategicTag | None = None
    category: ObservationCategory | None = None
    action: str = ""

class FieldworkSynthesis(BaseModel):
    generated: str = ""
    patterns: list[SynthesisPattern] = Field(default_factory=list)
    cross_repo_verdicts: dict[str, str] = Field(default_factory=dict)

# --- Knowledge Output models ---

class KnowledgeOutputType(StrEnum):
    COMPARISON_STUDY = "comparison_study"       # Cross-repo analysis on one dimension
    TUTORIAL = "tutorial"                       # Step-by-step from contribution experience
    CURRICULUM_MODULE = "curriculum_module"      # Structured teaching unit with exercises
    ESSAY = "essay"                             # Analytical/argumentative from synthesis
    TOOL = "tool"                               # Automatable pattern → code
    PATTERN_CATALOG = "pattern_catalog"         # Named reusable patterns with formal properties
    COMMUNITY_SEED = "community_seed"           # Discussion topic / reading group material
    DISTRIBUTION_HOOK = "distribution_hook"     # Content that attracts inbound contributors
    CONTRIBUTION_PLAYBOOK = "contribution_playbook"  # Dossier scrubbed of strategic fields → "How to Contribute to X"

class KnowledgeOutputStatus(StrEnum):
    CANDIDATE = "candidate"     # Auto-detected or manually flagged
    DRAFTING = "drafting"       # Being produced
    PUBLISHED = "published"     # Live in target organ
    ARCHIVED = "archived"       # Superseded or retired

# Maps output types to their natural organ destination
OUTPUT_ORGAN_MAP: dict[KnowledgeOutputType, str] = {
    KnowledgeOutputType.COMPARISON_STUDY: "V",
    KnowledgeOutputType.TUTORIAL: "VI",
    KnowledgeOutputType.CURRICULUM_MODULE: "VI",
    KnowledgeOutputType.ESSAY: "V",
    KnowledgeOutputType.TOOL: "III",
    KnowledgeOutputType.PATTERN_CATALOG: "I",
    KnowledgeOutputType.COMMUNITY_SEED: "VI",
    KnowledgeOutputType.DISTRIBUTION_HOOK: "VII",
    KnowledgeOutputType.CONTRIBUTION_PLAYBOOK: "V",  # Also VII for distribution
}

class KnowledgeOutput(BaseModel):
    id: str
    title: str
    output_type: KnowledgeOutputType
    organ: str                                          # Target organ for production
    source_observations: list[str] = Field(default_factory=list)  # FieldObservation.id references
    source_dossiers: list[str] = Field(default_factory=list)      # Workspace IDs
    source_synthesis: list[str] = Field(default_factory=list)     # Pattern IDs from synthesis
    status: KnowledgeOutputStatus = KnowledgeOutputStatus.CANDIDATE
    artifact_path: str = ""                             # Path when produced
    refinement_notes: str = ""                          # What producing this taught us
    backflow_ref: str = ""                              # Backflow item if deposited

class KnowledgeOutputIndex(BaseModel):
    generated: str = ""
    outputs: list[KnowledgeOutput] = Field(default_factory=list)

    def candidates(self) -> list[KnowledgeOutput]:
        return [o for o in self.outputs if o.status == KnowledgeOutputStatus.CANDIDATE]

    def by_organ(self) -> dict[str, list[KnowledgeOutput]]:
        result: dict[str, list[KnowledgeOutput]] = {}
        for o in self.outputs:
            result.setdefault(o.organ, []).append(o)
        return result
```

## 8. Module API (`fieldwork.py`)

```python
# --- Observation capture ---
def record(workspace, category, signal, spectrum=0, strategic=None, source="repo_exploration", evidence="")
    """Append an observation to the fieldwork stream."""

def record_from_review(workspace, pr_number)
    """Auto-capture observations from a PR review response (tone, depth, response time).
    Dual-write: also appends an OutreachEvent to outreach.yaml with cross-reference
    to the generated FieldObservation.id. Same interaction, two perspectives, linked."""

# --- Dossier management ---
def compile_dossier(workspace) -> RepoDossier
    """Compile a dossier from observation stream + scraped metadata.

    Regeneration rules (provenance determines behavior):
    - SCRAPED fields: always overwritten from fresh API data
    - COMPILED fields (observations lists): rebuilt from current stream
    - SYNTHESIZED fields (verdicts): recomputed, but prior verdicts are
      preserved in a 'verdict_history' if they change (trajectory tracking)
    - FREEFORM fields (competitive_notes): never overwritten by regeneration"""

def scrape_metadata(workspace) -> RepoMetadata
    """Scrape automated metadata from GitHub API (branch protection, CI, labels, etc.)."""

# --- Strategic detection ---
def detect_shatterpoints(dossier) -> list[Shatterpoint]
    """Identify structural weaknesses and contribution opportunities.

    Detection logic (three methods, any can fire):
    1. METADATA GAPS: RepoMetadata boolean fields that are False constitute
       a missing capability. has_security_policy=False → missing_shield.
       has_contributing_md=False → friction_point. has_changelog=False → missing_shield.
    2. CROSS-REPO COMPARISON: If a dossier's metric falls below the median
       across all compiled dossiers (e.g., ci_avg_duration > 2x median),
       flag as a potential contribution opportunity.
    3. OBSERVATION-DRIVEN: Observations tagged with strategic values by the
       scorer/orchestrator are surfaced directly. An observation tagged
       'shatterpoint' or 'missing_shield' becomes a Shatterpoint entry."""

def generate_campaign_actions(shatterpoints) -> list[CampaignAction]
    """Convert shatterpoints into campaign queue entries."""

# --- Synthesis ---
def synthesize(dossiers) -> FieldworkSynthesis
    """Cross-repo pattern extraction from multiple dossiers.

    Quality filter — a pattern is surfaced only if it meets ALL of:
    1. BREADTH: spans 3+ repos (quantity threshold)
    2. VARIANCE: the repos span 2+ waves or 2+ domains (diversity threshold)
    3. ACTIONABILITY: at least one repo has spectrum != 0 or strategic != null
       (the pattern must suggest a response, not just state a fact)
    Patterns that pass quantity but fail quality are archived as 'noted'
    rather than surfaced as 'patterns'."""

# --- Integration ---
def absorb_to_backflow(observation) -> BackflowItem | None
    """If spectrum == ABSORB, generate a backflow item."""

# --- Knowledge output ---
def detect_outputs(synthesis) -> list[KnowledgeOutput]
    """Auto-detect knowledge output candidates from synthesis patterns.
    3+ repos in same category → comparison_study candidate.
    5+ observations in contributor_experience → tutorial candidate.
    Strong spectrum signal in cross-repo verdict → essay candidate.
    Repeated manual process → tool candidate."""

def produce_output(output, content) -> str
    """Register a produced artifact, record refinement notes, route to backflow."""

def refinement_audit(output) -> list[str]
    """Check source observations for gaps exposed by production.
    Returns list of questions the output couldn't answer from current data."""

# --- CLI ---
# python -m contrib_engine fieldwork record <workspace> <category> <signal> [--spectrum N] [--strategic TAG]
# python -m contrib_engine fieldwork dossier <workspace>
# python -m contrib_engine fieldwork dossier --all
# python -m contrib_engine fieldwork synthesize
# python -m contrib_engine fieldwork shatterpoints [workspace]
# python -m contrib_engine fieldwork outputs [--status candidate]
# python -m contrib_engine fieldwork outputs detect
# python -m contrib_engine fieldwork outputs audit <output-id>
```

## 9. Integration Points

### → Campaign System
When `detect_shatterpoints()` identifies a gap, it calls `generate_campaign_actions()` to inject new actions into the campaign queue. The fieldwork system becomes self-targeting.

### → Backflow Pipeline
When an observation scores `+2 (absorb)`, `absorb_to_backflow()` auto-generates a `BackflowItem` routed to the appropriate organ. The observation's category determines the backflow type:
- `tooling`, `ci_architecture`, `repo_layout` → code (ORGAN-III or IV)
- `governance`, `merge_protocol` → code (ORGAN-IV)
- `review_culture`, `communication_style` → narrative (ORGAN-V)
- `security_posture` → code (ORGAN-IV)

### → Outreach System
Observations about `communication_style` and `review_culture` feed relationship intelligence — updating `relationship_score` in `outreach.yaml` with evidence-based adjustments.

### → GitHub Project Board
Shatterpoints and missing shields can generate new issues in `a-organvm/a-organvm` and add them to the Plague Campaign project board as contribution opportunities.

### → Knowledge Output Pipeline (Layer 4)
Synthesis patterns auto-detect knowledge output candidates. Produced outputs route back through backflow to their target organs. The `refinement_audit()` function identifies gaps the production process exposed — these become new targeted observations, closing the refinement loop.

### → ORGAN-V (Logos) — Essays and Analysis
Comparison studies and essays route to ORGAN-V. The fieldwork system provides the data; Logos provides the rhetorical apparatus. Cross-repo verdicts are essay seeds. Publication attracts inbound.

### → ORGAN-VI (Koinonia) — Community and Education
Tutorials, curriculum modules, and community seeds route to ORGAN-VI. The contribution experience becomes teaching material. The professor's trick: producing the curriculum refines the fieldwork data because you can't teach what you haven't verified.

### → ORGAN-VII (Kerygma) — Distribution
Distribution hooks route to ORGAN-VII for syndication. The published analysis becomes the inbound funnel — "How 24 open-source projects handle contributor onboarding" posted to the right channels draws exactly the audience the contribution engine needs.

## 10. Capture Protocol

### Call sites — where `record()` is invoked

The system dies if observation capture depends on the contributing agent voluntarily stopping to write notes. Three call sites ensure consistent capture:

1. **Monitor cycle integration:** `monitor.py` already polls PR states. Extend the poll to call `record_from_review()` when a new review or comment is detected. Automated, no agent intervention needed.
2. **Agent instruction preamble:** Contributing agents receive a fieldwork instruction block in their prompt: "After completing each contribution action, record 1-3 fieldwork observations using `record()`. Focus on friction encountered, tooling observed, and process requirements." The observation is part of the contribution task, not separate from it.
3. **Phase transition hook:** When `campaign.py` transitions an action's phase, it triggers `compile_dossier()` which also runs `scrape_metadata()`. This is the orchestrator's assessment pass — re-scoring agent observations and assigning strategic tags.

### During contribution (inline)
The agent records observations naturally as it works. Examples:
- "Their CI requires all commits to be signed" → `merge_protocol`, spectrum: +1 (study)
- "No CONTRIBUTING.md — had to reverse-engineer process from merged PRs" → `contributor_experience`, strategic: friction_point
- "golangci-lint with 15 linters enabled, 2-minute CI" → `ci_architecture`, spectrum: +2 (absorb)

### On review response (autopsy)
When a maintainer responds to our PR:
- Measure response time (hours/days from submission)
- Assess review depth (line-level vs. architectural vs. rubber stamp)
- Note tone (welcoming, neutral, adversarial)
- Record specific feedback patterns (do they suggest alternatives? do they explain why?)

### On phase transition (synthesis)
At each campaign phase boundary (ENGAGE→CULTIVATE, CULTIVATE→HARVEST):
- Run `compile_dossier()` for the transitioning workspace
- Run `detect_shatterpoints()` to find new opportunities
- Run `synthesize()` if 3+ dossiers have new observations

### Automated scrape
Periodic metadata collection via GitHub API:
- Branch protection rules
- CI workflow files
- Label taxonomy
- Contributor count and activity
- Release cadence

## 11. File Layout

```
contrib_engine/
├── fieldwork.py                      # Core module — observation, dossier, synthesis, output detection
├── data/
│   ├── fieldwork.yaml                # Layer 1: Active observation stream (append-only, rotated at 500)
│   ├── fieldwork_synthesis.yaml      # Layer 3: Cross-repo patterns
│   ├── knowledge_outputs.yaml        # Layer 4: Knowledge output candidates and status
│   ├── dossiers/                     # Layer 2: Per-repo structured intelligence
│   │   ├── contrib--dapr-dapr.yaml
│   │   ├── contrib--pydantic-ai.yaml
│   │   ├── contrib--grafana-k6.yaml
│   │   └── ...
│   └── fieldwork_archive/            # Rotated observations (>90 days, already compiled)
│       ├── 2026-Q1.yaml
│       └── ...
```

## 12. Recursive Property

The fieldwork system exhibits the same recursive property as the absorption protocol, but deepened by the knowledge output layer. Three recursions operate simultaneously:

**Recursion 1 — Targeting:** Contributions generate observations → observations identify shatterpoints → shatterpoints become new contribution opportunities → new contributions generate more observations.

**Recursion 2 — Refinement:** Observations compile into dossiers → dossiers synthesize into patterns → patterns become knowledge outputs → producing outputs reveals gaps in the source data → gaps drive targeted new observations → the source data becomes more precise.

**Recursion 3 — Attraction:** Knowledge outputs get published → publications attract inbound contributors and opportunities → inbound generates new observations → observations produce richer outputs → richer outputs attract more inbound.

The professor's trick operates at every level. The micro (a single PR interaction) is the entry point. The macro (cross-repo institutional analysis) is the product. And the act of phasing between them — formalizing micro observations into macro patterns, then auditing macro claims against micro evidence — is the refinement mechanism. You cannot publish "How 24 projects handle merge protocols" without verifying each project's actual merge protocol. The publication forces the verification. The verification improves the data. The improved data improves the publication.

The contribution engine's thesis proves itself at each scale: the micro contribution teaches you what the macro analysis should say, and the macro analysis tells you where the next micro contribution should land.

---

*Spec version: 4.0 | 2026-03-30*
*v1: Core 3-layer architecture (stream, dossier, synthesis)*
*v2: Knowledge Output Pipeline (Layer 4), three axes, refinement loop, recursive attraction*
*v3 (Hardening R1): Stable observation IDs, stream retention/rotation, dual scoring protocol, temporal trajectory, dossier provenance markers, regeneration rules, shatterpoint detection logic (3 methods), absorption cross-referencing, contribution playbook output type*
*v4 (Hardening R2): Call site protocol (3 integration points), synthesis quality filter (breadth+variance+actionability), outreach dual-write cross-ref, confidence scoring on verdicts, compatibility score, list-based dossier verdicts*
*R3 findings (implementation scope): MVP phasing, test strategy, audit CLI subcommand — deferred to implementation plan*
