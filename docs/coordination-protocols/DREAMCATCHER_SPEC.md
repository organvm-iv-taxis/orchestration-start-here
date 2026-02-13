# Dreamcatcher: Autonomous Creation Architecture ("Project Aeterna")

**Version:** 1.0
**Status:** DRAFT
**Objective:** Enable "Asynchronous Sovereignty" by decoupling decision-making from execution, allowing the metasystem to continuous develop itself using available AI resources.

---

## 1. The Core Philosophy
To allow the human operator to rest while work continues, the system must transition from **Tool** (passive) to **Machine** (active).
- **The Genome (`seed.yaml`)** is the unchanging will of the creator.
- **The Machine (Dreamcatcher)** is the tireless executor of that will.

## 2. System Architecture: The Infinity Loop

The system operates on a continuous **Token-Arbitrage Cycle**, leveraging specific strengths of different models to overcome individual context or logic limits.

### 2.1 The Power Grid (Resource Allocation)
The `ModelRouter` assigns work based on cognitive profile:

| Role | Model Archetype | Triggers | Responsibility |
| :--- | :--- | :--- | :--- |
| **The Architect** | Claude 3.5 Sonnet / Opus | `New Feature`, `Refactor`, `Plan` | Reads `seed.yaml`, interprets intent, writes `SPEC.md`. High context, high reasoning. |
| **The Builder** | GPT-4o / Codex | `Implement`, `Test`, `Fix` | Reads `SPEC.md`, writes code files. High speed, syntax fluency. |
| **The Critic** | Gemini 1.5 Pro | `Review`, `Audit` | Reads Diff + Spec. Large context window for cross-file consistency checks. |

### 2.2 The Control Plane (Node.js)
Located in `omni-dromenon-machina/core-engine/src/dreamcatcher`.

1.  **`NightWatchman`**: An event loop that runs when the system is idle.
    - *Scans:* Git diffs, `TODO` comments, failing tests, `.orchestrator/inbox`.
    - *Dispatches:* Creates a `Task` if idle capacity exists.
2.  **`CircuitBreaker`**: The safety mechanism.
    - *Budget:* Max tokens/dollars per hour.
    - *Scope:* Docker container isolation.
    - *Git:* Only commits to `auto/*` branches.

## 3. The Workflow Protocol

1.  **Dream State (Idle):**
    - Watchman detects `seed.yaml` change or open `ai-task` issue.
2.  **Lucid Dreaming (Planning):**
    - Watchman routes to **Architect**.
    - Architect produces `TASK_PLAN.md` with file paths and atomic steps.
3.  **Manifestation (Execution):**
    - Watchman routes step 1 to **Builder**.
    - Builder writes code.
4.  **Reality Check (Verification):**
    - System runs `npm test`.
    - If fail -> Route log to **Builder** (Fix).
    - If pass -> Route diff to **Critic** (Review).
5.  **Memory Consolidation (Commit):**
    - If Critic approves, Watchman commits to `nightly-build`.

## 4. Implementation Details

### 4.1 Directory Structure
```
core-engine/src/dreamcatcher/
├── router.ts       # Model selection logic
├── watchman.ts     # Event loop & polling
├── circuit.ts      # Safety limits
└── bridge.ts       # Interfaces to LLM Providers (OpenAI/Anthropic/Gemini)
```

### 4.2 Configuration (`seed.yaml` Addendum)
```yaml
dreamcatcher:
  enabled: true
  schedule: "0 0 * * *" # Run at midnight or continuous
  budget:
    max_loops: 50
    max_files_touched: 10
  providers:
    architect: "claude-3-5-sonnet"
    builder: "gpt-4o"
```

## 5. Security Mandates
1.  **No Main Branch Pushes:** Agents are strictly forbidden from pushing to `main`.
2.  **Secret Blindness:** Agents cannot read `.env` files or files matching `credentials*`.
3.  **Sandboxed Runtime:** Code execution happens in ephemeral Docker containers (OrchestratorTester).

---
**Next Steps:**
1. Implement `router.ts` and `circuit.ts`.
2. Wire `watchman.ts` into the main server loop.
3. Sleep.
