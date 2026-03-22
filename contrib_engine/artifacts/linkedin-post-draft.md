# LinkedIn Post — The Plague Campaign (v3)

## Images (carousel order)
1. `linkedin-01-network.png` — Contribution network topology
2. `linkedin-02-phases.png` — Campaign phase architecture
3. `linkedin-03-symbiote.png` — Cross-organ symbiote pattern

---

## Post Text

**I built a contribution engine. Then I had to answer why.**

AdenHQ's contributor guidelines open with a line that stopped me: "Aden Hive is built by practitioners for practitioners."¹ Not by companies for users, not by committees for compliance — by people who build the thing for people who build with it. That framing forced a question I couldn't sidestep: if I'm going to contribute to someone else's codebase, what exactly do I bring that their own team doesn't already have?

So I audited my own system — 118 repositories, 8 organizational units, 23,000+ tests — and mapped where my patterns collide with their open problems. The result wasn't a PR. It was an engine that makes PRs the byproduct of a deeper process.

Seven targets emerged, each solving a different problem in the AI agent ecosystem. Hive orchestrates autonomous agent swarms for teams building without manual workflow wiring.¹ LangGraph provides the stateful orchestration layer trusted by Klarna, Replit, and Elastic.² Temporal powers durable workflows at enterprise scale.³ Anthropic's Skills repository defines how Claude extends its own capabilities through community-contributed patterns.⁴ These aren't random repos — they're the infrastructure layer I already think in, which means the domain overlap is structural, not cosmetic.

But domain overlap alone produces drive-by patches that die in review queues. Lakhani and von Hippel's research on open-source participation revealed something more specific: the exchange between contributor and community is inherently bidirectional — the contributor transforms the project, but the project also transforms the contributor's understanding of their own patterns.⁵ That bidirectionality is usually accidental. I wanted to engineer it. Therefore each contribution workspace includes a backflow pipeline — a formal routing system that captures what I learn and deposits it into typed categories: theory formalization, generative artifacts, reusable code patterns, public narrative, community capital, distribution content. One PR, seven returns. Each return sharpens the capability map that identifies the next target, which means the system compounds rather than depletes.

Von Krogh, Spaeth, and Lakhani showed that what separates sustained contribution from abandoned PRs is joining specialization — the process of finding where your existing expertise maps onto a project's specific needs.⁶ But their research describes this as emergent. The contribution engine makes it mechanical: a scanner reads signal sources, scores targets by domain overlap and relationship strength, and a campaign sequencer prescribes actions in priority order. Not "find an issue and hope" — infrastructure that treats contribution as a systems problem.

Seven PRs open. 111 tests passing. The campaign is live, but the system matters more than the output. Open-source contribution at scale isn't a volume game. It's a knowledge-routing problem — and the literature on structural social capital suggests that solving it deliberately, rather than letting it emerge accidentally, is what converts peripheral participation into standing.⁷

What would change about how you contribute if you treated every PR as both an outbound delivery and an inbound learning channel?

---

## Notes

1. AdenHQ/Hive, CONTRIBUTING.md, §Philosophy; README.md. github.com/adenhq/hive
2. LangChain, LangGraph README. github.com/langchain-ai/langgraph
3. Temporal Technologies, Python SDK README. github.com/temporalio/sdk-python
4. Anthropic, Agent Skills README. github.com/anthropics/skills
5. Lakhani, K. R. & von Hippel, E. (2003). "How Open Source Software Works: 'Free' User-to-User Assistance." *Research Policy*, 32(6), 923–943.
6. von Krogh, G., Spaeth, S., & Lakhani, K. R. (2003). "Community, Joining, and Specialization in Open Source Software Innovation." *Research Policy*, 32(7), 1217–1241.
7. Singh, P. V. & Monge, P. (2011). "Network Effects: The Influence of Structural Social Capital on Open Source Project Success." *J. of Computer-Mediated Communication*, 16(4).

## Narratological Algorithms Applied

- **South Park BUT/THEREFORE**: "domain overlap alone produces drive-by patches BUT... THEREFORE each workspace includes a backflow pipeline"; "their research describes this as emergent BUT the engine makes it mechanical"
- **Larry David collision geometry**: 7 apparently independent repos converge through the bridge element (ORGANVM capability map). The collision point is the thesis: one system's patterns mechanically unlock another's open problems.
- **Waller-Bridge triple-layer**: Every paragraph carries ethos (118 repos, 23K tests), logos (Lakhani's bidirectionality, von Krogh's joining specialization), and pathos ("what exactly do I bring that their own team doesn't already have?") simultaneously.
- **Kubrick non-submersible units**: Paragraphs 1 (the question), 2 (the audit), 3 (the targets + backflow), 4 (the engine), 5 (the thesis) each stand alone.
- **Aristotle recognition**: Readers who know Research Policy see the theory operationalized. Practitioners see the method. Everyone reads a story about someone who asked a hard question and built something to answer it.

## Tagging
- @ Vincent Jiang (AdenHQ) — ONLY after joining their Discord first
- Mention by name without @: Anthropic, LangChain, Temporal
