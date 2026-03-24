# Dissertation Plan — D-005: Biological Topology

## Working Title

**"A Murder of Agents: Biological Collective Intelligence as Architectural Pattern Language for Multi-Agent Systems"**

## Short Name

**The Venery Topology**

## Faculty

Primary: **formal-systems** (ORGAN-I)
Advisory: **creative-practice** (ORGAN-II), **applied-systems** (ORGAN-III)

## Thesis Statement

Named formations drawn from biological collective behavior (terms of venery) provide a superior architectural pattern language for multi-agent topology compared to graph-theoretic abstractions, because they encode not just connectivity but behavioral intent, phase transition dynamics, and emergent coordination properties. The topology IS the specification.

## Three-Paper Structure

### Paper I — The Substrate (Practitioner)
**"From Graph Theory to Ethology: Why Agent Topologies Should Be Named After Animals"**

The practitioner's argument: current multi-agent frameworks (LangGraph, CrewAI, AutoGen) treat topology as a graph-theoretic problem — nodes, edges, routing. This captures connectivity but not behavior. Biological collective nouns (a murder of crows, a murmuration of starlings) encode coordination dynamics that graph theory misses.

**Sections:**
1. Survey of topology in existing frameworks (LangGraph, CrewAI, AutoGen, SmolAgents, agentic-titan) — what each supports, what each misses
2. The graph-theoretic poverty: connectivity ≠ coordination. A fully-connected graph (swarm) and a star graph (hub-spoke) have different coordination properties that their adjacency matrices don't capture
3. Terms of venery as pattern language: the medieval hunting tradition meets software architecture. Each name carries behavioral expectations that function as a specification
4. Case study: m13v's evaluation of frameworks on issue #20 — a practitioner naturally reached for behavioral descriptions ("parallel execution failure handling"), not graph descriptions

**Evidence base:** agentic-titan issue #20 conversation (12+ comments), dbt-mcp and Temporal contribution experiences, framework comparative evaluation

### Paper II — The Dynamics (Theorist)
**"Continuous Topology Morphing in Multi-Agent Systems: Attractor Basins, Phase Transitions, and the Hegemonizing Swarm"**

The theorist's argument: named topologies are not discrete states but attractor basins in a continuous metric space parameterized by (order_parameter, task_correlation, territorialization). The system flows between basins driven by criticality dynamics. Phase transitions (topology changes) occur at the edge of chaos.

**Sections:**
1. The metric space: formal definition of the 3-dimensional topology space
   - order_parameter (0-1): from Landau theory of phase transitions
   - task_correlation (0-1): from fission-fusion dynamics in primates
   - territorialization (0-1): from Deleuze & Guattari's assemblage theory
2. Attractor basins: each named topology occupies a region in this space. Map all 12 topologies to their basins with hysteresis boundaries
3. Phase transitions: criticality detection (correlation length, susceptibility, relaxation time) as the signal for topology change. Connection to self-organized criticality
4. The Hegemonizing Swarm: fiction as design specification
   - Crichton's Prey: emergent predator-prey dynamics from simple rules
   - Matrix Deus Ex Machina: formation-as-interface (topology IS the API surface)
   - Lem's The Invincible: intelligence emergence threshold (minimum N for collective cognition)
   - Bear's Blood Music: the substrate IS the network (no infrastructure/computation separation)
5. Programmable matter / claytronics: continuous reconfiguration with energy cost model
6. Formal properties: prove that decay resolves contradictions (reader-side resolution pattern), that hysteresis prevents oscillation, that reinforcement acts as distributed voting

**Evidence base:** hive/fission_fusion.py, hive/criticality.py, hive/stigmergy.py, hive/assembly.py, hive/neighborhood.py, hive/topology.py; Cavagna et al. murmuration research; Goldstein & Mowry claytronics; Rubenstein et al. Kilobots; reader-side resolution pattern (backflow item #9)

### Paper III — The Protocol (System)
**"The Absorption Protocol: How External Questions Generate Internal Theory in Self-Describing Systems"**

The system's argument: a contribution engine that sends code outward and absorbs theory inward creates a self-describing system — one whose architecture documents itself through the process of being questioned about itself. The Absorption Protocol formalizes this: external questions → detect expansion triggers → auto-formalize → deposit theory → the theory improves the system → the improved system generates better answers → deeper questions. A strange loop.

**Sections:**
1. The bidirectional contribution engine: outbound contributions as knowledge extraction
2. The Absorption Protocol: 8 expansion heuristics, 6 reduction filters, trigger taxonomy (assumption divergence, unnamed pattern, independent convergence)
3. Reader-side resolution as a case study: Matt asked "how do you handle conflicting traces?" → the question exposed an unnamed pattern → the pattern was formalized → the formalization became ORGAN-I theory → the theory informed the next answer → Matt asked deeper → the system expanded
4. The self-describing loop: code generates conversation generates theory generates code
5. Independent convergence as structural proof: when two systems evolve the same pattern independently (our pheromone field, Matt's TTL file locks), the pattern is a structural attractor worth formalizing
6. Constitutional directives: the contribution engine's doctrines (System Simply Knows, Full Context Ingestion, Never Make Human Look Stupid, Never Defer to Human) as governance rules that bind the system's interactions with the outside world

**Evidence base:** contrib_engine/absorption.py, agentic-titan issue #20 full conversation, reader-side-resolution-pattern.md, all 13 backflow items, the Absorption Protocol documentation

## Research Programme Integration

| Paper | RP Connection | Cross-references |
|-------|-------------|-----------------|
| I | RP-03 (Organ Topology) — hybrid topology principle | SYN-02 SS4.2, IRF-RES-011 |
| II | RP-06 (Type-Theoretic Characterization) — formal properties | IRF-RES-066, IRF-RES-067 |
| III | SYN-02 (Autonomous Governance) — self-describing systems | SYN-03 SS5.1-5.3, IRF-RES-012 |

## Evidence Already Collected

- 12+ comment conversation with m13v (practitioner validation)
- 12 PRs across 11 repos (contribution engine in operation)
- 13 backflow deposits (bidirectional flow proven)
- 4 auto-formalized theory notes (Absorption Protocol in operation)
- 7 issues (#57-63) as research programme
- Fiction catalog: 9 works mapped to topology types
- Venery mapping: 12 topologies + 5 additional concepts
- 5 dbt-mcp patterns absorbed (cross-pollination from contribution)

## Writing Timeline

| Phase | What | When |
|-------|------|------|
| Commission | Register in inquiry-log.yaml as SGO-2026-D-005 | Now |
| Paper I outline | Section headings + evidence mapping | Session +1 |
| Paper II formal work | Metric space definition, attractor basin mapping, proofs | Session +2-3 |
| Paper III | Absorption Protocol case study, strange loop argument | Session +3-4 |
| Integration | Cross-references, bibliography, constitutional directives | Session +5 |
| TRP review | Submit for Technical Review Panel clearance | After integration |

## Bibliography (Preliminary)

### Primary (directly cited in system code/docs)
- Cavagna, A. et al. (2010). "Scale-free correlations in starling flocks." PNAS 107(26)
- Deleuze, G. & Guattari, F. (1987). A Thousand Plateaus
- Crichton, M. (2002). Prey
- Lem, S. (1964). The Invincible
- Bear, G. (1985). Blood Music
- Rubenstein, M. et al. (2014). "Programmable self-assembly in a thousand-robot swarm." Science 345(6198)
- Goldstein, S.C. & Mowry, T.C. (2004). "Claytronics: An Instance of Programmable Matter." Wild and Crazy Ideas Session, SOSP

### Secondary (framework evaluations, pattern language theory)
- Berners, J. (1486). The Book of Saint Albans
- Alexander, C. (1977). A Pattern Language
- Bonabeau, E. et al. (1999). Swarm Intelligence: From Natural to Artificial Systems
- Kauffman, S. (1993). The Origins of Order: Self-Organization and Selection in Evolution
- Bak, P. (1996). How Nature Works: The Science of Self-Organized Criticality

### Tertiary (framework documentation)
- LangGraph documentation + PR #7237
- CrewAI, AutoGen, SmolAgents documentation
- agentic-titan hive module source code
