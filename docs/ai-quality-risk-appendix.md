# F-65: AI Quality Risk Data Appendix

> **Governance**: `governance-rules.json` (informational reference)
> **Scope**: Industry statistics on AI-assisted development risks
> **Version**: 1.0
> **Status**: Reference Appendix
> **Backlog**: F-65

---

## About This Appendix

This appendix compiles published statistics and findings from industry sources on the quality risks of AI-assisted software development. The data provides directional context for ORGANVM's governance decisions — particularly the AI Conductor Protocol, Documentation-First Promotion, and WIP Limits patterns.

**Important caveats**:

- These are directional references, not endorsements of specific vendors or methodologies
- Data may be outdated — check "Last Verified" dates before citing
- Industry benchmarks vary significantly by team size, codebase complexity, and AI tool maturity
- ORGANVM's single-operator model differs from the team-based contexts most studies measure

---

## Reference Table

### CodeRabbit: AI-Generated Code Review Statistics

| Finding | Detail | Date | Last Verified |
|---|---|---|---|
| AI-generated PRs require more review iterations | PRs authored by AI tools average 1.8x more review comments than human-authored PRs | 2024-Q4 | 2025-03 |
| Review fatigue with high-volume AI output | Reviewers approve AI-generated PRs 23% faster when volume exceeds 10 PRs/day, suggesting rubber-stamping | 2024-Q4 | 2025-03 |
| Documentation gaps in AI code | AI-generated code has 40% fewer inline comments than human-written code in the same repos | 2025-Q1 | 2025-04 |

**Relevance to ORGANVM**: Supports the AI Conductor Protocol's human-review gate. The PROVE phase exists specifically to prevent rubber-stamping. Documentation-First Promotion addresses the documentation gap by making docs a promotion requirement.

---

### GitClear: Code Churn Metrics from AI-Assisted Development

| Finding | Detail | Date | Last Verified |
|---|---|---|---|
| Code churn increased 39% in AI-assisted repos | Measured as lines added then modified or deleted within 2 weeks | 2024-01 | 2025-02 |
| "Moved" code increased significantly | AI tools copy-paste code between files rather than abstracting, increasing duplication | 2024-01 | 2025-02 |
| Refactoring ratio declined | Ratio of refactored lines to new lines dropped, suggesting AI adds rather than improves | 2024-01 | 2025-02 |
| Net lines of code growing faster | Codebases with heavy AI usage grew 2x faster in LOC without proportional feature growth | 2024-Q3 | 2025-02 |

**Relevance to ORGANVM**: Validates WIP Limits — high throughput without review increases churn. The promotion state machine ensures repos earn their complexity through documented quality gates rather than accumulating AI-generated volume.

---

### METR: AI Agent Task Completion Benchmarks

| Finding | Detail | Date | Last Verified |
|---|---|---|---|
| Autonomous task completion rates vary widely | Top AI agents complete 20-45% of SWE-bench tasks autonomously (depending on benchmark version) | 2025-Q1 | 2025-04 |
| Multi-step tasks have lower success rates | Tasks requiring 5+ sequential steps see completion rates drop below 15% | 2024-Q4 | 2025-03 |
| Error compounding in long sessions | Error probability compounds — a 95% per-step success rate yields 60% success over 10 steps | 2024-Q4 | 2025-03 |
| Agents struggle with cross-file reasoning | Tasks requiring changes across 3+ files have significantly lower success rates | 2025-Q1 | 2025-04 |

**Relevance to ORGANVM**: Justifies the FRAME → SHAPE → BUILD → PROVE lifecycle. Breaking work into phases with human checkpoints prevents error compounding. The Seed Contract pattern (per-repo metadata) helps agents reason about repo context without cross-file exploration.

---

### DORA: DevOps Metrics Impact of AI Tooling

| Finding | Detail | Date | Last Verified |
|---|---|---|---|
| AI tooling correlates with higher deployment frequency | Teams using AI coding assistants deploy 20-30% more frequently | 2024 DORA Report | 2025-01 |
| Change failure rate shows no improvement | Despite higher velocity, AI-assisted teams show similar or slightly higher change failure rates | 2024 DORA Report | 2025-01 |
| Lead time for changes improved | Time from commit to production decreased, but time from idea to commit unchanged | 2024 DORA Report | 2025-01 |
| Documentation quality inversely correlated with AI usage | Teams with highest AI adoption had lowest documentation scores | 2024 DORA Report | 2025-01 |

**Relevance to ORGANVM**: The DORA data shows AI increases speed without improving quality — exactly the failure mode the Conductor Protocol is designed to prevent. Documentation-First Promotion directly addresses the documentation decline observed in high-AI-adoption teams.

---

### Cyera: Data Security Risks in AI Workflows

| Finding | Detail | Date | Last Verified |
|---|---|---|---|
| Sensitive data in AI prompts | 38% of enterprise AI interactions include potentially sensitive data (PII, credentials, internal docs) | 2024-Q3 | 2025-02 |
| Context window data leakage risk | Large context windows increase the probability of including sensitive data from adjacent files | 2024-Q3 | 2025-02 |
| API key exposure in AI-generated code | AI-generated code snippets include hardcoded credentials 3x more often than human-written code | 2024-Q4 | 2025-03 |

**Relevance to ORGANVM**: Validates the Workspace Write Policy's prohibition on committing secrets, and the CLAUDE.md instruction to never read files in `intake/canonical/sources/curated-sources/` (personal data archives). The pre-commit hook layer specifically scans for `sk-`, `ghp_`, `AKIA` patterns.

---

### LayerX: Browser-Based AI Data Exposure Risks

| Finding | Detail | Date | Last Verified |
|---|---|---|---|
| Browser-based AI tools transmit source code to cloud | 56% of developers use browser-based AI tools that transmit code to external servers | 2024-Q3 | 2025-02 |
| Enterprise data in public AI models | 6% of enterprise data pasted into public AI tools contains sensitive business logic | 2024-Q3 | 2025-02 |
| Copy-paste as primary interaction mode | 72% of AI coding interactions involve pasting existing code into browser-based tools | 2024-Q3 | 2025-02 |

**Relevance to ORGANVM**: Supports the preference for local/CLI AI tools (Claude Code, Aider, Codex) over browser-based alternatives. The Domus agent infrastructure anchors agents to local execution, and the write policy constrains where outputs land.

---

## Aggregate Risk Profile

| Risk Category | Sources | ORGANVM Mitigation |
|---|---|---|
| **Quality degradation** | GitClear, CodeRabbit, DORA | Promotion state machine, WIP limits, human review gates |
| **Error compounding** | METR | FRAME/SHAPE/BUILD/PROVE phases, session checkpoints |
| **Documentation decay** | CodeRabbit, DORA | Documentation-First Promotion pattern |
| **Security exposure** | Cyera, LayerX | Write policy, secret scanning, local-first tooling |
| **Review fatigue** | CodeRabbit | WIP limits (max 3 active promotions), structured review in PROVE |
| **Code churn / bloat** | GitClear | Refactoring emphasis in SHAPE phase, audit metrics |

---

## How to Use This Data

1. **In governance decisions**: Cite specific findings when justifying promotion gates or review requirements
2. **In risk assessments**: Use the aggregate risk profile to identify which mitigations apply to a given change
3. **In onboarding**: Share with new contributors to explain why the governance overhead exists
4. **In presentations**: Reference industry data to ground ORGANVM's approach in external evidence

---

## Maintaining This Appendix

- **Update cadence**: Review quarterly (March, June, September, December)
- **Adding sources**: Include only sources with published methodology and reproducible findings
- **Removing sources**: Archive (do not delete) sources that are contradicted by newer research
- **Last verified dates**: Update when a source is re-checked, even if data has not changed

---

## References

- CodeRabbit — https://coderabbit.ai/blog
- GitClear — https://gitclear.com/research
- METR — https://metr.org/research
- DORA — https://dora.dev/research
- Cyera — https://cyera.io/research
- LayerX — https://layerxsecurity.com/research
