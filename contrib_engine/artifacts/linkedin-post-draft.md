# LinkedIn Post — The Plague Campaign

## Images (carousel order)
1. `linkedin-01-network.png` — Contribution network topology
2. `linkedin-02-phases.png` — Campaign phase architecture
3. `linkedin-03-symbiote.png` — Cross-organ symbiote pattern

## Post Text

---

**I built a contribution engine. Then I pointed it at 7 open-source repos.**

AdenHQ's Hive framework runs on a principle stated in their contributor guidelines: "Aden Hive is built by practitioners for practitioners."¹ That single line captures why I built what I built — not a framework for contributing, but a system for making contribution systematic.

The targets span the AI agent and data infrastructure ecosystems. Hive orchestrates autonomous agent swarms. Anthropic's Skills repository provides the standard for extending Claude's capabilities across 100K+ stars' worth of community attention.² LangGraph handles long-running stateful agent orchestration for companies like Klarna, Replit, and Elastic.³ Temporal's Python SDK powers durable workflow execution at enterprise scale.⁴ And dbt's MCP server bridges AI agents to data transformation pipelines.⁵ Seven repos, 138K combined stars.

Each target gets a full contribution workspace: a capability map matching my system's patterns to their open problems, a campaign sequencer that prioritizes by relationship strength, an outreach tracker modeling the engagement lifecycle, and a backflow pipeline routing what I learn back into my own system.

The methodology has roots deeper than personal preference. In their foundational study of open-source participation, Lakhani and von Hippel examined how knowledge moves through contributor communities and found that the exchange is inherently bidirectional — contributors teach the community while the community transforms the contributor.⁶ Von Krogh, Spaeth, and Lakhani extended this, showing that what separates sustained high-impact contribution from drive-by patches is joining specialization — the process by which a newcomer finds where their existing expertise maps onto a project's open problems.⁷ That's exactly what the capability map automates: matching patterns I've built across 118 repos to the specific issues each target cares about.

The engineering is a 5-phase campaign:

UNBLOCK → ENGAGE → CULTIVATE → HARVEST → INJECT

Unblocking clears technical barriers — CLAs, CI failures, issue claiming. Engaging joins the community before submitting code, because relationship context before cold PRs is the difference between a merged contribution and an ignored one. Cultivating responds to review feedback within 24 hours. Harvesting extracts patterns and formalizes theory from the fusion of two codebases. Injecting routes knowledge back: theory formalization, generative artifacts, public narrative, community capital, distribution content.

One contribution, seven returns. Singh and Monge's research on open-source network effects demonstrates why this compounds: structural social capital — the trust and standing built through visible, sustained participation — increases a contributor's influence on subsequent projects.⁸ Each merged PR doesn't just ship code; it builds the reputation infrastructure that makes the next target more likely to engage.

7 PRs open. 111 tests passing. The campaign is live.

What systems have you built to make open-source contribution sustainable and symbiotic rather than episodic?

---

## Notes

1. AdenHQ/Hive, CONTRIBUTING.md, §Philosophy. github.com/adenhq/hive
2. Anthropic, Agent Skills README. "Skills teach Claude how to complete specific tasks in a repeatable way, whether that's creating documents with your company's brand guidelines, analyzing data using your organization's specific workflows, or automating personal tasks." github.com/anthropics/skills
3. LangChain, LangGraph README. github.com/langchain-ai/langgraph
4. Temporal Technologies, Python SDK README. github.com/temporalio/sdk-python
5. dbt Labs, dbt-mcp README. github.com/dbt-labs/dbt-mcp
6. Lakhani, K. R. & von Hippel, E. (2003). "How Open Source Software Works: 'Free' User-to-User Assistance." *Research Policy*, 32(6), 923–943.
7. von Krogh, G., Spaeth, S., & Lakhani, K. R. (2003). "Community, Joining, and Specialization in Open Source Software Innovation: A Case Study." *Research Policy*, 32(7), 1217–1241.
8. Singh, P. V. & Monge, P. (2011). "Network Effects: The Influence of Structural Social Capital on Open Source Project Success." *J. of Computer-Mediated Communication*, 16(4).

## Tagging
- @ Vincent Jiang (AdenHQ) — ONLY after joining their Discord first
- Mention by name without @: Anthropic, LangChain, Temporal, dbt Labs
