# D-005 Annotated Bibliography — "A Murder of Agents"

**Dissertation:** SGO-2026-D-005, The Venery Topology
**Compiled:** 2026-03-24
**Status:** Working bibliography — expand as research deepens

---

## I. PRIMARY SOURCES — Fiction

Works that originated or exemplify the swarm-topology concepts the dissertation formalizes.

### 1.1 Crichton, M. (2002). *Prey*. New York: HarperCollins.

A nano-particle swarm escapes containment and evolves predator-prey dynamics through Lamarckian evolution — each generation's members choose which traits to transmit. The swarm is self-sustaining, self-reproducing, learns from experience, and adapts strategy across generations. **Relevance:** Primary inspiration for Paper II's adversarial co-evolution model (#59). The swarm's topology emerges from environmental pressure, not selection — the key insight that named formations should be attractor basins, not manual selections. Crichton's three rules (separation, alignment, cohesion) directly reference Reynolds' Boids model but extend it with reproduction and predation. The novel's scientific rigor is contested (Kurzweil: "the science isn't real"), but the *architectural* pattern — emergent intelligence from simple rules + adversarial pressure — is implemented in `hive/fission_fusion.py` and `hive/criticality.py`.

### 1.2 Lem, S. (1964). *Niezwyciężony* [*The Invincible*]. Warsaw: Ministerstwo Obrony Narodowej. English trans. 1973, Ace Books.

Crystal-like micro-machines on the planet Regis III are individually mindless but collectively form electromagnetic intelligence capable of incapacitating any sentient threat. Written decades before artificial life research formalized these concepts. **Relevance:** First fictional treatment of intelligence emergence threshold (#61). Lem's "necroevolution" — evolution of non-living matter — prefigures our criticality model where `order_parameter` crossing a threshold produces collective cognition. The MIT Press Reader (2023) notes Lem "intuited that different environmental constraints might lead to radically different evolutionary results in automata compared to biological life forms." The swarm's power is specifically electromagnetic interference — a WARNING/FAILURE trace analogue in our pheromone field. Paper II cites this as precedent for the emergence threshold formalization.

### 1.3 Bear, G. (1985). *Blood Music*. New York: Arbor House.

Genetically modified intelligent cells reorganize their host's body from inside. The "swarm" is biological — the substrate IS the network. **Relevance:** The most radical topology concept: no separation between infrastructure and computation. In our architecture, the agents and the pheromone field are separate layers. Blood Music's noocytes collapse this distinction — the agents ARE the field. Paper II explores whether a topology where agents themselves constitute the communication medium (rather than depositing into a separate pheromone field) would exhibit different emergence properties.

### 1.4 *The Matrix Revolutions* (2003). Dir. Lana & Lilly Wachowski. Warner Bros.

The Deus Ex Machina — a face formed from thousands of insect-sized autonomous machines composing a volumetric display. **Relevance:** Primary source for the "formation-as-interface" concept (#62). The face is not decorative — it's the swarm's communication interface with Neo. The topology (face shape) IS the API surface. This directly inspires Paper I's argument that named formations should be externally observable and meaningful, not internal implementation details.

### 1.5 *Big Hero 6* (2014). Dir. Don Hall & Chris Williams. Walt Disney Animation Studios.

Microbots — millions of tiny magnetic actuators controlled by a neural headband, forming bridges, towers, and hands. **Relevance:** Demonstrates the STAR → MESH transition: centralized control (headband) produces distributed structure (linked formation). The controller dissolves into the controlled. Paper II uses this as the fiction analogue for the programmable matter reconfiguration cost model (#58).

### 1.6 *Stargate SG-1*, S06–S08 (2002–2005). "Human-Form Replicators." MGM Television.

Nanite-composed entities that appear human but can dissolve to dust or reshape limbs to weapons. **Relevance:** Mode switching — the same agent group serves different functions in different topology states. Passive form (stigmergic, blending in) vs. active form (mesh, reconfiguring for attack). Paper I uses this to argue that topology names should encode not just connectivity but *purpose* — "An Ambush" (tiger/territorialized) vs. "A Flamboyance" (flamingo/deterritorialized) name what the formation *does*, not just how it's shaped.

### 1.7 *Transformers: Age of Extinction* (2014). Dir. Michael Bay. Paramount.

KSI Drones (Galvatron) break into floating "Transformium" cubes that swarm through air and reassemble. **Relevance:** Zero-cost reconfiguration — no explicit "unbond" step. The cubes exist in a permanent state of potential reconfiguration. This challenges our current model where topology transitions have hysteresis costs. Paper II explores whether removing reconfiguration cost (making topology infinitely fluid) produces better or worse outcomes than our current hysteresis model.

---

## II. PRIMARY SOURCES — Scientific Literature

Peer-reviewed research directly cited in `agentic-titan/hive/` source code or forming the empirical foundation for the dissertation's claims.

### 2.1 Cavagna, A., Cimarelli, A., Giardina, I., Parisi, G., Santagati, R., Stefanini, F., & Viale, M. (2010). "Scale-free correlations in starling flocks." *Proceedings of the National Academy of Sciences*, 107(26), 11865–11870. [doi:10.1073/pnas.1005766107](https://www.pnas.org/doi/10.1073/pnas.1005766107)

Two-year field study of starling murmurations over a roosting site in Rome. **Finding:** Behavioral correlations are scale-free — the range of spatial correlation scales with the linear size of the flock, not with a fixed constant. Each bird's behavioral state affects and is affected by all other birds regardless of group size. **Relevance:** Foundational for `hive/neighborhood.py` which implements N=7 topological neighbors (from this research). Scale-free correlations mean information propagates through the entire group — the basis for our claim that stigmergic communication (pheromone field) can achieve global coordination through local interactions. Paper II formalizes the N=7 topological coupling as the connectivity primitive for the continuous topology space.

### 2.2 Rubenstein, M., Cornejo, A., & Nagpal, R. (2014). "Programmable self-assembly in a thousand-robot swarm." *Science*, 345(6198), 795–799. [doi:10.1126/science.1254295](https://www.science.org/doi/10.1126/science.1254295)

1,024 Kilobots (coin-sized robots with infrared communication and vibration locomotion) self-assemble into predetermined shapes using only local communication — no central leader, no global information. **Relevance:** Hardware proof that N-agent local-only interaction produces macro-shapes. Validates our stigmergic topology claim: if 1,024 robots with 3 simple rules can form a star or letter K, then our pheromone field (which carries richer type/intensity metadata) should produce even more complex formations. Paper II cites this as the empirical anchor for the emergence threshold (#61) and the programmable matter model (#58).

### 2.3 Aureli, F., Schaffner, C.M., Boesch, C., Bearder, S.K., Call, J., Chapman, C.A., ... & van Schaik, C.P. (2008). "Fission-fusion dynamics: New research frameworks." *Current Anthropology*, 49(4), 627–654.

Framework paper defining fission-fusion dynamics across three dimensions: spatial cohesion, subgroup size, and subgroup composition. Species range from low fission-fusion (stable groups, minimal splitting) to high (chimpanzees, dolphins — constant splitting and regrouping). **Relevance:** Direct theoretical basis for `hive/fission_fusion.py`. Our implementation maps Aureli's three dimensions to `crisis_level`, `task_correlation`, and `cluster_count`. Paper II formalizes the fission-fusion coordinate as one of three axes in the continuous topology space.

### 2.4 Reynolds, C.W. (1987). "Flocks, Herds, and Schools: A Distributed Behavioral Model." *Computer Graphics (SIGGRAPH '87 Conference Proceedings)*, 21(4), 25–34. [PDF](https://www.red3d.com/cwr/papers/1987/SIGGRAPH87.pdf)

The Boids model — three rules (separation, alignment, cohesion) producing realistic flocking from purely local interactions. **Relevance:** The ur-text of computational collective behavior. Every swarm topology in `hive/topology.py` descends from Reynolds' demonstration that complex group behavior emerges from simple local rules. Paper I surveys how each modern framework implements (or fails to implement) these rules. Crichton's Prey explicitly builds on Boids with the addition of predation and reproduction.

### 2.5 Bak, P., Tang, C., & Wiesenfeld, K. (1987). "Self-organized criticality: An explanation of the 1/f noise." *Physical Review Letters*, 59(4), 381–384.

The foundational paper on self-organized criticality (SOC). Systems drive themselves toward a critical state where scale-invariant avalanches occur. **Relevance:** Direct basis for `hive/criticality.py`. Our `CriticalityState` enum (SUBCRITICAL / CRITICAL / SUPERCRITICAL) maps to Bak's states. The critical point is where topology transitions naturally occur — the system is maximally sensitive. Paper II uses SOC as the theoretical framework for why topology changes happen at the edge of chaos, not at arbitrary thresholds.

### 2.6 Bak, P. (1996). *How Nature Works: The Science of Self-Organized Criticality*. New York: Copernicus/Springer.

Book-length treatment extending the 1987 paper. Applies SOC to earthquakes, evolution, economics, and neural networks. **Relevance:** Paper II's theoretical framework for phase transitions in agent systems. Bak's argument that complexity arises naturally at critical points (without parameter tuning) maps directly to our design principle: topology should emerge from metric-driven dynamics, not be selected by a human operator.

### 2.7 Bonabeau, E., Dorigo, M., & Theraulaz, G. (1999). *Swarm Intelligence: From Natural to Artificial Systems*. Santa Fe Institute Studies in the Sciences of Complexity. New York: Oxford University Press.

Definitive reference on stigmergy in artificial systems. Distinguishes quantitative stigmergy (pheromone concentration drives response) from qualitative stigmergy (different stimuli trigger different responses). **Relevance:** Our pheromone field implements both: intensity is quantitative stigmergy (higher intensity = stronger signal), `TraceType` enum is qualitative stigmergy (PATH vs WARNING trigger different agent behaviors). Paper I cites this as the bridge between biological stigmergy and our `hive/stigmergy.py` implementation.

### 2.8 Ward, M.P., & Raim, A. (2011). "The fly-and-social foraging hypothesis for diurnal migration: A re-evaluation of the evidence from American crows (*Corvus brachyrhynchos*)." *Behavioral Ecology and Sociobiology*.

Study of crow communal roosting as information centers. Follower crows that roosted overnight with leader crows were significantly more likely to visit food patches the next day. **Relevance:** Direct inspiration for `hive/information_center.py`. Our InformationCenter class aggregates and broadcasts patterns exactly as crow roosts aggregate and broadcast foraging information. Paper II formalizes the information center as the FUSION attractor basin's coordination mechanism.

### 2.9 Goldstein, S.C., & Mowry, T.C. (2004). "Claytronics: A Scalable Basis for Future Robots." *RoboSphere 2004*. [PDF](http://www.cs.cmu.edu/~seth/papers/goldstein-robosphere04.pdf)

Introduces claytronics and catoms — sub-millimeter computers that reconfigure relative to each other without moving parts. **Relevance:** The hardware vision behind our programmable matter model (#58). Paper II argues that agent topology reconfiguration should follow the catom model: each agent maintains local bonds (neighbor connections), macro-shape emerges from collective reconfiguration, and there's an energy cost for bonding/unbonding that the system minimizes.

---

## III. SECONDARY SOURCES — Peer-Reviewed Surveys & Frameworks

Works that survey, synthesize, or extend the primary literature. These provide the academic context for the dissertation's claims.

### 3.1 Guo, T., Chen, X., Wang, Y., Chang, R., Pei, S., Chawla, N.V., ... & Xu, J. (2024). "Large Language Model Based Multi-Agents: A Survey of Progress and Challenges." *IJCAI 2024*. [arXiv:2402.01680](https://arxiv.org/html/2412.17481v2)

Survey of LLM-based multi-agent systems covering architecture, communication mechanisms, and orchestration frameworks. Identifies four communication paradigms (memory, report, relay, debate) mapped to topologies (bus, star, ring, tree). **Relevance:** Paper I cites this as the state-of-the-art in LLM multi-agent topology. Our contribution: venery-named formations encode behavioral intent that these graph-theoretic topologies miss. The survey's MacNet evaluation of scalability across graph types provides the comparison baseline.

### 3.2 Multi-Agent Collaboration Mechanisms: A Survey of LLMs (2025). [arXiv:2501.06322](https://arxiv.org/html/2501.06322v1)

35-page survey covering collaborative frameworks including OpenAI Swarm, MetaGPT, AgentScope. **Relevance:** Paper I's framework comparison section uses this survey's taxonomy. Our topology engine extends beyond their "fixed topology" framing — we argue for dynamic, metric-driven topology that flows between named attractors.

### 3.3 Alexander, C., Ishikawa, S., & Silverstein, M. (1977). *A Pattern Language: Towns, Buildings, Construction*. New York: Oxford University Press.

253 architectural patterns organized as a language — each pattern describes a problem, context, and solution, and connects to related patterns. Directly inspired the Gang of Four software design patterns. **Relevance:** Paper I's theoretical frame: terms of venery function as a pattern language for agent topology. Each venery name (Murder, Parliament, Colony) describes a coordination problem, behavioral context, and formation solution — just as Alexander's patterns describe spatial problems and architectural solutions. The argument is that biological collective nouns ARE patterns in Alexander's sense.

### 3.4 Kauffman, S.A. (1993). *The Origins of Order: Self-Organization and Selection in Evolution*. New York: Oxford University Press.

Boolean networks at the edge of chaos exhibit optimal information processing. Systems that are too ordered (frozen) or too chaotic (random) process information poorly; those at criticality are maximally adaptive. **Relevance:** Paper II's theoretical basis for why topology transitions occur at the critical point. Our `criticality.py` implements Kauffman's insight: SUBCRITICAL = too rigid, SUPERCRITICAL = too chaotic, CRITICAL = maximally adaptive. The topology naturally shifts at criticality because that's where the system is most sensitive to perturbation.

### 3.5 Deleuze, G., & Guattari, F. (1980). *Mille Plateaux* [*A Thousand Plateaus*]. Paris: Éditions de Minuit. English trans. 1987, University of Minnesota Press.

Introduces the rhizome, assemblage theory, territorialization/deterritorialization, and the war machine / state machine distinction. **Relevance:** Direct theoretical basis for `hive/assembly.py`, `hive/machines.py`, and `hive/topology_extended.py`. Paper II frames our topology space using D&G's concepts: territorialization is the third coordinate axis; the war machine (nomadic, smooth space) maps to DETERRITORIALIZED/RHIZOMATIC topologies; the state machine (capture, striate) maps to HIERARCHY/ARBORESCENT. The tension between these poles IS the continuous morphing dynamics.

### 3.6 Berners, J. (attr.) (1486). *The Boke of Seynt Albans*. St Albans: Schoolmaster-Printer. [Gutenberg facsimile](https://www.gutenberg.org/files/71266/71266-h/71266-h.htm)

The "Company Terms" appendix — collective nouns for animals and professions. A "murder of crows," a "parliament of owls," a "shrewdness of apes." These terms were part of a gentleman's education, distinguishing the learned from the common. **Relevance:** Paper I's title and central metaphor. The argument: terms of venery were designed to encode behavioral observations about animal groups in memorable, communicable form. This is exactly what a pattern language for agent topology needs. The fact that these terms survived 540 years in common English while graph-theoretic terminology remains specialized suggests they encode something deeply recognizable about collective behavior.

### 3.7 Cavagna, A., & Giardina, I. (2022). "Marginal speed confinement resolves the conflict between correlation and control in collective behaviour." *Nature Communications*, 13, 2097. [doi:10.1038/s41467-022-29883-4](https://www.nature.com/articles/s41467-022-29883-4)

Follow-up to the 2010 murmuration paper. Resolves the paradox of how scale-free correlations (all birds affect all others) coexist with directional control (the flock moves coherently). The answer: marginal speed confinement — birds at the flock's edge are speed-constrained, creating a boundary layer that transmits turning information. **Relevance:** Paper II uses this to formalize the boundary between named attractor basins. Agents at the edge of a formation's basin (high uncertainty about which topology to occupy) transmit the transition signal to the interior. This is the continuous morphing mechanism.

### 3.8 Haken, H. (1983). *Synergetics: An Introduction. Nonequilibrium Phase Transitions and Self-Organization in Physics, Chemistry and Biology*. 3rd ed. Berlin: Springer.

Foundational work on how macroscopic patterns emerge from microscopic interactions near instability points. The order parameter concept (a few collective variables that describe the system's macroscopic state) comes from here. **Relevance:** Our `order_parameter` in `CriticalityMetrics` is directly from Haken. Paper II cites synergetics as the physics framework for understanding why agent groups self-organize into named topologies at phase transition points.

---

## IV. TERTIARY SOURCES — Framework Documentation & Technical Reports

### 4.1 LangGraph Documentation + PR #7237

Our restart-safety test contribution. Evidence of engagement with the framework's checkpoint architecture.

### 4.2 agentic-titan `hive/` module source code (18 files, ~8,000 lines)

The implementation being formalized. Source code IS evidence.

### 4.3 agentic-titan Issue #20 — full conversation with @m13v (12+ comments, 6 days)

Practitioner validation. A desktop agent builder independently reached for biological metaphors when evaluating topology. The Absorption Protocol case study.

### 4.4 dbt-labs/dbt-mcp architecture study (PR #669)

Cross-pollination evidence. 5 patterns absorbed into organvm-mcp-server design.

---

*Working bibliography — 25 entries across 4 categories. Expand as research deepens.*
*Next: add Vicsek et al. (1995) self-propelled particles, Couzin et al. (2005) leadership in mobile animal groups, Sumpter (2010) Collective Animal Behavior textbook.*
