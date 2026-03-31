# Conversation Filters: Humanities & ELI5

---

## HUMANITIES FILTER

### Stigmergy (Pheromone Field)

The architectural precedent isn't computer science — it's ecology. E.O. Wilson's 1959 observation: termites build cathedrals without architects. No termite holds the blueprint. Each one deposits a chemical trace, and the next termite's behavior is altered by what it senses. The cathedral emerges from the accumulation of traces, not from a plan.

Our system does this literally. Agents deposit typed traces (resource, warning, path, failure) into a shared field. Other agents sense the field and adjust. The coordination is *immanent* in the environment, not *transcendent* in a controller. Deleuze would call it a plane of immanence — no privileged vantage point, only local sensing producing global order.

The decay mechanism is forgetting as a feature. Nietzsche's active forgetting — the system must forget in order to act. A failure trace at full intensity paralyzes. At 10% decay per cycle, the field gradually permits retry. The forgetting IS the permission to try again.

### Fission-Fusion (Dynamic Topology)

The model is crow roost dynamics — Marzluff and Heinrich's research on corvid information centers. Crows disperse at dawn to forage independently (fission). At dusk they reconvene at the roost (fusion). The roost isn't just shelter — it's an information exchange. Unsuccessful foragers follow successful ones the next morning. The social structure oscillates between individual exploration and collective knowledge sharing.

The threshold is task correlation. When agents work on unrelated problems, dispersal is optimal — don't waste bandwidth on irrelevant updates. When a crisis emerges (high correlation), the swarm contracts into a single deliberative body. Parliament vs. scouts. The organism breathes.

### Topological Neighborhood (k=7)

Cavagna et al. studied starling murmurations — thousands of birds moving as one. The surprise: each bird doesn't track every other bird. Each interacts with exactly 6-7 neighbors based on *topological* distance (relationship rank), not *metric* distance (physical proximity). This is why murmurations maintain coherence even when the flock stretches and compresses.

The insight is Dunbar's number at the interaction layer. Not "how many can you know" but "how many can you *attend to* per decision cycle." Seven. The rest is handled by propagation — your neighbors' neighbors carry the signal further. Three hops covers the flock.

### Context IS Coordination

The Western metaphysical tradition separates knowledge from action — *theoria* from *praxis*. You learn, then you decide, then you act. Three steps. Most software architectures replicate this: query the database (know), run the decision logic (decide), execute the action (act).

Stigmergy collapses the trichotomy. The act of sensing IS the decision. The act of depositing IS the communication. There is no gap between knowing and coordinating because the environment that carries knowledge IS the medium of coordination. Merleau-Ponty's embodied cognition: the agent doesn't represent the world and then act on the representation. The agent is *in* the world, and its perception is already action.

### Criticality (Phase Transitions)

Per Bak's self-organized criticality — the sandpile model. Add grains one at a time. Most fall and settle. Occasionally, an avalanche. The system naturally evolves toward the critical point between order and chaos. Too much order: the pile is frozen, nothing moves. Too much chaos: everything collapses at once.

The monitoring system detects where the swarm sits on this spectrum. Subcritical (too ordered): agents are stuck in routines, not exploring. Supercritical (too chaotic): agents are thrashing, no coherent output. The edge of chaos is where computation happens — Langton's lambda, Kauffman's adjacent possible. The system steers toward criticality, not away from it.

### Perceptual Gating (The Frontier)

The newest architectural proposal: topology doesn't control who talks to whom. It controls what each agent can *perceive*. The pheromone field is always there, always full. Topology is a mask over perception.

This is Umwelt theory — von Uexküll's concept that each organism inhabits its own perceptual world. A tick perceives only butyric acid, warmth, and hair. A starling perceives flock-mates within 7 topological ranks. The same physical environment, radically different experienced worlds. Topology as Umwelt.

---

## ELI5 FILTER

### Stigmergy

Imagine ants finding food. The first ant wanders randomly. When it finds food, it leaves a scent trail on the way back. The next ant smells the trail and follows it. More ants follow, the trail gets stronger. If the food runs out, no new scent is added, and the old trail fades away. Nobody's in charge. The trail IS the plan.

Our agents do this with a digital scent trail. They leave notes like "found something useful here" or "this path is a dead end." Other agents smell the notes and adjust. The notes fade over time so old information doesn't stick around forever.

### Fission-Fusion

Think of a school of fish. When there's no danger, they spread out to find food on their own. When a shark appears, they instantly clump together into a tight ball. Nobody gives the order — they just sense the danger and contract.

Our agents do the same thing. Working on separate tasks? Spread out, don't bother each other. Big problem that needs everyone? Merge into one group and focus together. The system watches how related the work is and decides: spread or merge.

### k=7 Neighborhood

You have 100 coworkers but you really only talk to about 7 of them regularly. Those 7 each talk to their own 7. So if you learn something important, you tell your 7, they tell their 7, and within a couple of rounds everyone knows — without you having to email all 100 people.

### Context IS Coordination

Imagine a busy kitchen with one whiteboard. A cook writes "out of tomatoes." Every other cook who glances at the whiteboard changes their plan — no tomato dishes. Nobody had to call a meeting. Nobody had to send a message. Just writing on the whiteboard changed everyone's behavior.

Most computer systems separate the whiteboard (where you store information) from the walkie-talkie (how you tell people what to do). We made them the same thing. Write on the board = tell everyone. Simpler, fewer things that can break.

### Criticality

Imagine a classroom. If everyone sits silently doing nothing — too orderly, nothing's happening. If everyone screams at once — too chaotic, nothing useful comes out. The sweet spot is somewhere in between: enough energy that ideas flow, enough structure that people can build on each other.

Our system watches for that sweet spot. Too quiet? Shake things up. Too loud? Add some structure. Always steering toward the productive middle.

### Perceptual Gating

Imagine the same library, but different people can only see certain shelves. A new employee sees the shelf right next to them. A manager sees the whole floor. The CEO sees every branch. Same library, different views based on your role.

Our agents have different views of the shared information based on their topology — some see their neighbors' notes, some see everything. Same environment, different windows into it.
