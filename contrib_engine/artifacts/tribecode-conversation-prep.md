# Conversation Prep: Alex Morris (tribecode.ai)

## Know Your Counterpart
- **Alex Morris**, robotics engineering (Queen's), co-founded Koii Network (DePIN, 90K+ nodes)
- TRIBE: 2-10 person startup, SF, building AI dev orchestration
- MUSE = leader+workers via git worktrees + tmux. CIRCUIT = autonomous issue-queue workers with watchdog
- They use SQLite full-text search for memory. You use Redis + ChromaDB + pheromone fields
- They have 2 patterns. You have 9 topologies with runtime switching
- They build bottom-up from dev tooling. You build top-down from orchestration theory

## The "Context IS Coordination" Argument (Your Hook)

Most systems treat context (a store) and coordination (a protocol) as separate. In stigmergy, they're identical:

1. **Depositing context IS signaling intent** — `deposit(EXPLORATION, "auth-module")` simultaneously stores context and tells others someone's there
2. **Sensing context IS making a coordination decision** — `follow_strongest()` is reading AND deciding
3. **Context decay IS memory management** — 10% decay/cycle means old coordination fades without explicit cleanup
4. **Diffusion IS coordination propagation** — 5% intensity to neighbors, local context becomes distant coordination
5. **Topology changes ARE context scope changes** — fission = local context, fusion = global context

**Killer question for Alex:** "If an agent stores something in shared context, does that act alone change what other agents do? Or does it require a separate coordination step?"

## Three Questions to Ask (Reveal Their Architecture)

1. "When two agents disagree about shared context, whose version wins?" — reveals consistency model
2. "Does context scope change based on what's happening, or is it fixed?" — reveals static vs dynamic
3. "If you doubled agents, what breaks first — the store or the query patterns?" — reveals scaling model

## 30-Second Explanations (Conversational)

**Stigmergy:** "Agents write traces into a shared environment that fades over time. Other agents sense the environment and adjust behavior. Nobody needs to know who wrote what. Like a whiteboard that auto-erases."

**k=7 Neighborhood:** "Each agent interacts with exactly 7 neighbors regardless of total count. From starling murmuration research. O(N) connections instead of O(N^2). Information still reaches everyone in ~3 hops."

**Fission-Fusion:** "The swarm switches between sparse and dense modes based on task correlation. Below 0.3: scatter into independent clusters. Above 0.7: merge into one group. Based on crow roost dynamics."

**Criticality:** "Monitors whether the system is too rigid, too chaotic, or at the edge of chaos. Four indicators from statistical physics. Detects phase transitions and recommends topology changes."

## Three Things NOT to Claim

1. **Don't claim the criticality model detects emergence.** The order parameter conflates structural and functional connectivity. Known gap, issue #66.
2. **Don't claim the pheromone field handles conflicting context.** Contradicting traces coexist unresolved. Conflict detection is designed but not built.
3. **Don't claim production-scale validation.** 1357 tests cover the machinery. Not run at N=64. Frame as: "architecturally designed and unit-tested, not validated at scale."

## Landmines to Avoid

- Don't confuse tribecode.ai with Tribe AI (different company)
- Don't dismiss their telemetry product as "just analytics" — it's their shipping product and revenue base
- Don't challenge their Eliza OS co-founder claim without verification
- Don't oversell ORGANVM as a product — it's a system, not a company
- Don't mention job interest

## Conversation Strategy

1. Lead with stigmergy (sensing, not querying) — this is the distinctive claim
2. Feel for whether they're doing conventional RAG-for-agents or something structural
3. Cite m13v and voidborne-d threads as external validation (not just your own ideas)
4. If asked about scale: be honest. Unit-tested, not production-validated.
5. Let him discover your GitHub. The PR brought him to you. The repos are the iceberg.
