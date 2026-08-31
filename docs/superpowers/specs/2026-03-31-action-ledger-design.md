# Action Ledger design: event-to-evidence execution contract

**Contract:** `organvm.execution/v1`  
**Status:** Draft implementation  
**Owners:** #146, #107  
**Control epic:** #192

## Decision

The Action Ledger remains ORGANVM's canonical append-only execution history.
GitHub events, Conductor dispatch receipts, model-provider state, UCC queue
events, and future product events enter through adapters. They do not become
independent systems of record.

Every consequential execution can be traced through this path:

`event -> scoped context -> policy -> approval -> work -> evidence -> verification`

Failure and rollback are first-class outcomes. An execution is a sequence of
immutable `Action` snapshots linked by `execution_id`; it is not a mutable chat
thread or vendor run.

## Components and ownership

| Component | Owns | Does not own |
| --- | --- | --- |
| Action Ledger | Ordered semantic actions, sequences, routes, execution snapshots | Raw provider payloads or secrets |
| `organvm.execution/v1` | Event, authority, gate, work, evidence, verification, failure/rollback | Full tool output blobs |
| Conductor dispatch ledger | Fleet dispatch, timecard, energy, scorecard domain records | A second cross-product execution history |
| Agent run directory | Prompt, tool output, patch, session log, large artifacts | Canonical lifecycle ordering |
| Product adapter | Domain-to-contract translation | Contract evolution or policy authority |

The agent-run layout and retention policy are already defined in
`docs/agent-run-logging.md`. The execution envelope stores the reviewable
summary and references the full run artifacts.

## Contract fields

`action_ledger.execution_schemas.ExecutionEnvelope` is embedded at
`Action.execution` and serializes with normal Action Ledger YAML persistence.

| Field | Purpose |
| --- | --- |
| `schema_version` | Compatibility boundary; fixed to `organvm.execution/v1` |
| `execution_id` | Stable identity across lifecycle snapshots |
| `idempotency_key` | Stage/attempt identity used with `execution_id` for replay dedupe |
| `stage` | Received, context-scoped, approval-pending, authorized, running, evidenced, verified, failed, rolled-back |
| `event` | Provider-neutral trigger reference; raw payload is excluded |
| `scope` | Retrieved and forbidden context references plus optional digest |
| `authority` | Principal, delegator, permissions, and policy reference |
| `policy` / `approval` | Machine decision and explicit human gate |
| `work` | Intended action, target, and mutation reference |
| `workflow` | Objective, plan, commands/results, dead ends, decisions, approvals |
| `evidence` | Durable artifact references and optional digests |
| `verification` | Checks, result, reviewer, review time |
| `rollback` / `failure` | Compensating action and structured failure |
| `provider_receipt_refs` | Links to source receipts without copying provider state |
| `dispute_refs` | Peer-review or dispute records |

## Invariants enforced in code

1. Authorized, running, evidenced, and verified stages require an `allow`
   policy decision.
2. If approval is required, active work cannot proceed until approval is
   `approved`.
3. `approval_pending` requires a pending, required gate.
4. `verified` requires passed verification and at least one evidence reference.
5. `failed` requires structured failure details.
6. `rolled_back` requires a completed rollback.
7. Redelivery is deduplicated by the pair
   `(execution_id, idempotency_key)`. The same key in another execution cannot
   collide, and a new stage in the same execution uses a new key.

### Concurrency boundary

The current YAML persistence layer is a single-writer store. Dedupe is atomic
inside one loaded `ActionIndex`, but it does not provide a cross-process lock or
database uniqueness constraint. Deployments MUST route ingestion through one
writer or an externally serialized queue. Multiple webhook workers writing the
same YAML files can race. A database-backed implementation should enforce a
unique index on `(execution_id, idempotency_key)` before enabling concurrent
writers.

## Redaction and evidence rules

The `scope.redacted` and `CommandResult.redacted` booleans are assertions made
by the adapter; they do not perform or prove sanitization.

Adapters MUST:

- omit raw comment, review, prompt, response, environment, and credential data;
- store a reference and digest when full output is needed for audit;
- scrub secrets before setting `redacted=true`;
- keep commands free of inline credentials and tokens;
- treat GitHub-authored text and retrieved pages as untrusted input;
- put large tool outputs in the run-artifact store governed by #107.

The GitHub adapter intentionally records PR URLs, head SHAs, event type, and
provider object IDs but not comment or review bodies.

## Conductor convergence (#146)

`dispatch_receipt_envelope()` maps existing Conductor data rather than copying
its implementation into this repository:

| Conductor artifact | Action Ledger mapping |
| --- | --- |
| Dispatch receipt outbound | Received execution action; objective, actor, context refs, permission |
| Dispatch receipt return | Verified or failed execution action; touched-file evidence and review |
| Timecard punch-in | Sequence start; scoped context, baseline, permission boundary |
| Timecard punch-out | Evidence, verification, attribution, rollback outcome |
| Energy ledger | Numeric Action parameters / automation axes |
| Scorecard | Cycle detection and agent-performance views over closed actions |
| `tool_execution_trace_v1` | Provider receipt reference and execution evidence, not a new ledger |

The adapter accepts a mapping instead of importing `conductor` at runtime. This
keeps the ledger deployable independently while retaining a versioned boundary.

## PR events awaken workers

Polling remains a reconciliation fallback, not the primary execution trigger.
The GitHub adapter routes these provider events:

| Event | Worker action |
| --- | --- |
| `pull_request_review.submitted` | `respond_to_review` |
| `issue_comment.created` on a PR | `triage_pr_comment` |
| `issue_comment.edited` on a PR | `triage_pr_comment` |
| `pull_request.synchronize` | `reverify_pr_commit` |
| `pull_request.ready_for_review` | `run_pr_readiness_checks` |
| `pull_request.reopened` | `run_pr_readiness_checks` |
| `pull_request.closed` | `record_pr_resolution` |

Plain issue comments and unsupported actions do not wake a PR worker. The
initial receipt grants read and proposal permissions only. A later action must
record an approval before pushing, merging, deploying, publishing, or changing
organization settings.

Provider event runners can invoke:

```bash
python -m action_ledger ingest-github-event \
  --event-name pull_request_review \
  --event-path "$GITHUB_EVENT_PATH" \
  --delivery-id "$GITHUB_DELIVERY_ID"
```

Use `--dry-run` to validate and print the envelope without persistence.

## UCC implementation slice

`ucc_collector_exception_envelope()` creates a fail-closed receipt for a
jurisdiction collector exception. It scopes the worker to one jurisdiction,
collector strategy, and redacted telemetry receipt. It permits diagnosis and a
patch proposal but leaves production activation pending owner approval.

`verify_ucc_jurisdiction_activation()` advances the same `execution_id` only
when it receives:

- named approver and approval reference;
- redacted commands/results;
- test and provenance evidence;
- explicit verification checks;
- rollback strategy.

The worked NY example is in
`examples/execution-contracts/ucc-ny-collector-activation.yaml` and is covered by
`tests/test_execution_contract.py`.

## Persistence, replay, and retention

- Each lifecycle transition appends an Action; prior actions are not rewritten.
- Provider redelivery returns the matching existing action.
- Intentional replay uses a new idempotency key and sets `event.replay_of`.
- The compact ledger retains execution metadata according to governance.
- Full run artifacts follow `docs/agent-run-logging.md`: full fidelity for 30
  days, compressed through day 90, then deletion unless a legal/security hold
  or durable evidence policy overrides it.
- Evidence referenced by a still-open approval, dispute, incident, or rollback
  MUST outlive the default run-artifact window.

## Rollout and rollback

Rollout:

1. Merge the schema, recording operation, adapters, tests, and this spec.
2. Route one non-mutating PR event through `--dry-run`.
3. Enable one serialized Action Ledger writer.
4. Attach the UCC collector-exception adapter to the existing audit/telemetry
   path.
5. Add product adapters without changing the canonical field meanings.

Rollback:

- Disable event ingestion and return to polling reconciliation.
- Existing actions remain readable because `Action.execution` is optional.
- Remove product adapter calls without deleting recorded evidence.
- Do not downgrade or mutate already persisted `organvm.execution/v1` actions.

## Acceptance evidence

- Replay/dedupe, cross-execution collision, approval, failure, verified-evidence,
  GitHub event routing, dispatch convergence, and UCC lifecycle tests pass.
- Existing Action Ledger and emission tests pass unchanged.
- This design resolves the formal-spec item in #146 while retaining #107 as the
  full artifact and retention standard.
