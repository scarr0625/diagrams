# Phase 1 Backlog — Epics, Stories & Acceptance Criteria

**AI-Assisted GCP Onboarding · POC (Milestone 1) — for Project Manager story creation**

12 epics · three 2-week sprints (weeks 1–6) · POC scope only — MVP / Live is a later phase

> ## How to use this backlog
>
> Story title = the summary line; acceptance criteria = the `-` bullets under it (put them as a checklist in the Jira description).
>
> Tags: **S1/S2/S3 = sprint.** Size: **S = 1–2 pts, M = 3–5, L = 8.** Spikes are time-boxed, not pointed.
>
> Dependencies: set Jira “is blocked by” links per the **blocked by** notes.
>
> IDs (E#-S#) are for reference/linking only — replace with Jira keys on import.

## Sprint plan & demo checkpoints

| Sprint | Weeks | Goal | Demo checkpoint |
|---|---:|---|---|
| **Sprint 1** | 1–2 | Foundations & discovery — build everything that doesn't touch the client environment | Local agent produces a valid construct from a sample request; CI green |
| **Sprint 2** | 3–4 | Vertical slice on real infra — construct → dispatch → one real GCP project, with approval gate | One real project provisioned end-to-end (vertical slice) |
| **Sprint 3** | 5–6 | Thicken & confirm — RAG, guardrails, confirmation loop, logging; pilot | Full POC: chatbot → grounded construct → project → confirmation + audit |

> ## Definition of Done (applies to every story)
>
> - [ ] Code reviewed and merged; unit tests where applicable.
> - [ ] Construct passes schema + policy validation (where relevant).
> - [ ] Proposer boundary holds — the agent has no GCP write access.
> - [ ] Golden intake→construct test updated where relevant.
> - [ ] No secrets in code or logs; least-privilege identities.
> - [ ] Demoable, and documented in the repo README / runbook.

# Epics & Stories

## Epic 1 · Discovery & Design Baseline (Sprint 1)

*Remove the design-blocking unknowns and lock the target design before building.*

### E1-S1 `S1` · `M` Run the project-factory discovery session (Jul 2) and document findings.

- Session held with factory owners; notes captured
- Current manual flow diagrammed; artifact inventory started

### E1-S2 `S1` · `M` Spike: confirm the construct schema / input contract.

- Exact fields (required/optional) + allowed values documented
- A real example construct file obtained; decision recorded

### E1-S3 `S1` · `S` Spike: confirm one-file-per-project vs. aggregate file.

- Model confirmed; impact on PR/dispatch strategy noted

### E1-S4 `S1` · `M` Spike: confirm the `workflow_dispatch` contract (workflow file, inputs, ref, gate).

- Workflow YAML reviewed; declared inputs listed
- Whether apply is gated (environment/approval) documented

### E1-S5 `S1` · `M` Submit & track access requests (repo, GCP read + scoped admin, GitHub App, Vertex, Secret Manager).

- Requests submitted with owners + ETAs
- Blockers escalated; status tracked to granted

### E1-S6 `S1` · `M` Produce target architecture + sequence doc; obtain client sign-off.

- Architecture + 7-step sequence documented
- Reviewed with client; sign-off recorded

### E1-S7 `S1` · `S` Confirm environment model & pilot scope (org/folder hierarchy, dev/test/prod, pilot team).

- Hierarchy + pilot team/project selected and agreed

## Epic 2 · Project Setup & Ways of Working (Sprint 1)

*Stand up the delivery scaffolding so the team can build cleanly from day one.*

### E2-S1 `S1` · `S` Create the agent repo — branch protection, CODEOWNERS, PR template.

- Repo created; main protected; required reviewers set

### E2-S2 `S1` · `M` Set up CI for the agent repo (lint, unit tests, format) on PRs.

- CI runs on every PR; lint + tests gate merges

### E2-S3 `S1` · `S` Define coding standards, project structure, dependency management (pin ADK version).

- Structure + standards documented; ADK version pinned

### E2-S4 `S1` · `S` Configure the board, sprint cadence, DoR/DoD, and ceremonies.

- Board configured; DoR/DoD agreed; cadence set

### E2-S5 `S1` · `S` Provision non-prod sandbox GCP project(s) for POC development.

- Sandbox project(s) available with billing + basic IAM
- **Blocked by:** E1-S5

## Epic 3 · Construct Schema & Validation (Sprint 1 → 2)

*Define the contract the factory consumes and the enforcement that guarantees correctness.*

### E3-S1 `S1` · `M` Define the JSON Schema for the project construct.

- Covers all required fields with enums/patterns
- Validates the real example file

### E3-S2 `S1` · `M` Build the validation script (schema + semantic/policy checks) with clear failure output.

- Passes a good construct; fails a bad one with specific messages
- Non-zero exit blocks CI

### E3-S3 `S1` · `M` Assemble the deterministic allow-list catalog (APIs, folders, billing, labels), shared with CI.

- Catalog in version control; agent + CI read the same source

### E3-S4 `S1` · `M` Create golden intake→construct examples as a regression set.

- ≥5 representative pairs; runnable as a test

### E3-S5 `S2` · `M` Reconcile our schema with the client's actual factory contract.

- Schema updated to match the real contract
- A real construct file validates cleanly
- **Blocked by:** E1-S2

### E3-S6 `S2` · `S` Add policy-as-code checks (OPA/conftest) for business rules beyond shape.

- Residency, naming, and mandatory-label policies enforced

## Epic 4 · ADK Agent Core (Sprint 1 → 2)

*The reasoning agent that maps intake into a valid construct.*

### E4-S1 `S1` · `M` Scaffold the ADK agent (`agent.py`) — model, instruction/persona, tools registry.

- Agent boots; `adk web` / `adk run` works locally

### E4-S2 `S1` · `M` Implement `build_project_construct` (assemble + self-validate against the schema).

- Returns valid/errors; an invalid construct never proceeds

### E4-S3 `S1` · `M` Implement the deterministic `lookup_catalog` tool.

- Returns approved values; agent selects only from these

### E4-S4 `S1` · `M` Author the instruction/persona (constraints, ordered procedure, refusal/scope).

- Encodes never-invent, ask-don't-guess, stay-in-scope, prod-flag

### E4-S5 `S1` · `M` Run locally end-to-end on `InMemorySessionService` with a hardcoded request.

- Sample request → valid construct produced locally

### E4-S6 `S2` · `M` Add the bounded self-correction loop on validation failure.

- Only invalid output the agent retries with errors; retries capped

### E4-S7 `S2` · `M` Implement multi-turn intake gathering (ask one question for a missing field).

- Missing required field → one targeted question; resumes on answer

### E4-S8 `S2` · `S` Model selection & prompt tuning against the golden set.

- Mapping accuracy measured on the golden set; model choice recorded

## Epic 5 · Knowledge & RAG Layer (Sprint 1 bridge → 3)

*Ground the mapping in internal standards, with citations — enrichment after the vertical slice.*

### E5-S1 `S1` · `S` Bridge: embed a concise internal-standards summary in the prompt for Sprints 1–2.

- Correct mapping possible pre-RAG from the prompt summary + catalog

### E5-S2 `S2` · `S` Inventory & stage internal standards docs for ingestion (from discovery).

- Standards docs collected into a governed bucket
- **Blocked by:** E1 access to standards

### E5-S3 `S3` · `M` Stand up the Vertex AI RAG corpus; ingest the standards docs.

- Corpus created; docs imported; retrieval returns relevant chunks

### E5-S4 `S3` · `M` Wire the `VertexAiRagRetrieval` tool into the agent.

- Agent retrieves the governing standards during mapping

### E5-S5 `S3` · `M` Capture source citation per field decision into the audit trail.

- Each construct records which standard informed key fields

### E5-S6 `S3` · `S` Verify the soft/hard split — allow-lists stay deterministic, out of the corpus.

- Confirmed no allow-list values are served from RAG

## Epic 6 · Pipeline Integration — the handoff (Sprint 2)

*Tap into the client's existing pipeline via `workflow_dispatch`.*

### E6-S1 `S2` · `M` Build the pipeline adapter (`submit_construct`) — payload + reference strategies.

- Given a valid construct, dispatches via both strategies (configurable)

### E6-S2 `S2` · `M` Implement the `workflow_dispatch` trigger against the client's real workflow.

- A dispatch triggers a real run against the correct ref with declared inputs
- **Blocked by:** E1-S4 + access

### E6-S3 `S2` · `M` Configure the scoped GitHub App / token via Secret Manager.

- Least-privilege App; token from Secret Manager, not code

### E6-S4 `S2` · `S` Confirm/wire the materialize-construct step with the client (payload → file).

- Workflow reads the input and writes `projects/{key}.json` (client-confirmed)
- **Blocked by:** E1-S4

### E6-S5 `S2` · `S` Resolve the run URL (poll `actions/runs`) to report back to the requester.

- After dispatch, the adapter resolves and returns the run link

### E6-S6 `S2` · `S` Handle idempotency — the “dispatched” flag prevents double-provisioning.

- A retried session won't dispatch twice

## Epic 7 · Provisioning & Environment (Sprint 2)

*The agent runs on real infra and provisions one project through the factory.*

### E7-S1 `S2` · `M` Stand up Workload Identity Federation — pool, provider, scoped apply identity.

- CI authenticates to GCP via OIDC; no long-lived keys
- **Blocked by:** access

### E7-S2 `S2` · `M` Dockerize the agent and deploy to Cloud Run.

- Container builds; service deploys; reachable (private / IAM)

### E7-S3 `S2` · `M` Wire the DB-backed session (Cloud SQL Postgres) with an env-driven selector.

- Sessions persist across instances/restarts; in-memory for local

### E7-S4 `S2` · `S` Configure the Cloud Run service account (Vertex AI User) + Cloud SQL client.

- Least-privilege SA; agent reaches Vertex + Cloud SQL

### E7-S5 `S2` · `L` Provision one real pilot project end-to-end through the factory. **(VERTICAL-SLICE MILESTONE)**

- Request → construct → dispatch → approval → project created

### E7-S6 `S2` · `S` Verify the human approval gate (GitHub Environment) between plan and apply.

- Apply pauses for a reviewer; approval recorded

### E7-S7 `S2` · `S` Confirm Terraform state backend & apply scoping for the pilot.

- State in GCS with locking; targeted/segmented apply
- **Blocked by:** E1-S2

## Epic 8 · Guardrails & Human-in-the-Loop (Sprint 2)

*Make the agent safe by construction — enforcement beyond the prompt.*

### E8-S1 `S2` · `M` ADK callbacks (`before_model`/`before_tool`/`after_tool`) to inspect & block.

- A tool call with an unapproved value is blocked; injection attempts inert

### E8-S2 `S2` · `S` Enforce proposer boundary — the agent identity has no GCP write.

- Agent SA/token cannot mutate GCP; test attempts fail

### E8-S3 `S2` · `S` Prod-environment guardrail (explicit `project_id`, no random; force review).

- Prod requests require an explicit id + human approval

### E8-S4 `S2` · `S` Approval routing / segregation of duties (approver ≠ requester).

- SoD enforced via environment reviewers / CODEOWNERS

### E8-S5 `S2` · `S` Scope guardrail — the agent can act only on the factory repo.

- GitHub App scoped to one repo; no other repo actions possible

## Epic 9 · Confirmation, Observability & Governance (Sprint 3)

*Close the loop back to the requester and make every run auditable.*

### E9-S1 `S3` · `M` Post-apply verification (project ACTIVE, APIs enabled) before reporting success.

- Success reported only when the project is confirmed ready

### E9-S2 `S3` · `M` Build the confirmation card (project id, network/CIDRs, console links) back to the requester.

- Requester receives a clear card with network details, links, correlation id

### E9-S3 `S3` · `M` Structured logging + correlation IDs threaded end-to-end.

- Correlation id spans intake → dispatch → provisioning → confirmation

### E9-S4 `S3` · `M` SIEM integration + audit retention.

- Logs shipped to SIEM; retention configured

### E9-S5 `S3` · `M` Complete the audit trail — requester, intake, citations, approval, outcome.

- Each onboarding has a full, queryable record

### E9-S6 `S3` · `S` Cost/budget labels + budget alert on provisioned projects.

- Budget + chargeback labels set at creation from the construct

## Epic 10 · Security & Compliance (cross-cutting, S1 → S3)

*Security designed in, not bolted on. (Note: certification & pen-testing are out of scope.)*

### E10-S1 `S1` · `S` Threat-model the agent + pipeline; document trust boundaries.

- Threat model doc; mitigations mapped to stories

### E10-S2 `S1` · `S` Secrets management standard (Secret Manager; none in code/logs).

- Policy documented; secret scanning enforced in CI

### E10-S3 `S2` · `S` IAM least-privilege review (agent SA, apply SA, GitHub App).

- Each identity scoped to minimum; reviewed and recorded

### E10-S4 `S2` · `S` PII handling in session state & logs (what's stored, redaction).

- Sensitive intake handled per policy; logs scrubbed

### E10-S5 `S3` · `S` IaC + dependency security scanning in CI (tfsec/trivy, deps).

- Scans run; high/critical findings block

### E10-S6 `S1` · `S` Confirm compliance requirements & map to controls (from discovery).

- Applicable regimes documented; out-of-scope items flagged

## Epic 11 · Testing, QA & Evaluation (cross-cutting, S1 → S3)

*Prove it works and keep it working as prompts, models, and code change.*

### E11-S1 `S1` · `M` Unit tests for core tools (`build_construct`, validation, adapter).

- Core tools unit-tested; CI enforces

### E11-S2 `S1` · `M` Golden intake→construct eval harness (regression on prompt/model changes).

- Eval runs in CI; regressions flagged

### E11-S3 `S2` · `M` Integration test — dispatch against a test/sandbox workflow (no prod).

- Adapter → dispatch verified without touching prod

### E11-S4 `S2` · `S` Negative tests — invalid constructs, injection, missing fields, unapproved values.

- Each is rejected/handled as designed

### E11-S5 `S3` · `M` End-to-end test — request → provisioned sandbox project → confirmation.

- Full thread passes in a sandbox

### E11-S6 `S2` · `S` Concurrency sanity — multiple simultaneous onboardings.

- Concurrent sessions isolated; no cross-talk; dispatch idempotent

## Epic 12 · Pilot, Demo, Docs & Handoff (Sprint 3)

*Land the POC: prove it with real users, show it, and document it.*

### E12-S1 `S3` · `M` Run the scoped pilot with a real team/request.

- Pilot request processed end-to-end; outcome captured

### E12-S2 `S3` · `S` Capture structured feedback (surveys/SME debrief) and prioritize fixes.

- Feedback collected; a prioritized fix list produced

### E12-S3 `S3` · `M` POC demo prep & delivery.

- Demo script; live demo of the full loop

### E12-S4 `S3` · `M` Documentation — architecture, runbook, README, setup (WIF/Cloud SQL), operations.

- A new engineer can set up & run from the docs

### E12-S5 `S3` · `S` POC readiness write-up — what's proven, deferred to MVP, known limitations.

- Readiness doc delivered; MVP recommendations listed

### E12-S6 `S3` · `S` Handoff plan & knowledge transfer to the owning team.

- KT session held; ownership + operations documented

# Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Access (repo / GCP / GitHub App) delayed | Sprint 1 is dependency-free by design; submit & escalate access early (E1-S5); reforecast S2/S3 if it slips. |
| Client factory schema differs from our assumptions | Schema reconciliation story (E3-S5); keep the schema config-driven so it adapts to their contract. |
| `workflow_dispatch` runs straight to apply (no gate) | Add a GitHub Environment approval gate (E7-S6 / E8-S4) before go-live. |
| Payload-mode drift (next apply destroys the project) | Commit the file back or use reference mode; scope apply with `-target` (E6 / E7). |
| Model mapping accuracy insufficient | Golden intake→construct eval (E11-S2); constrained generation; escalate model (E4-S8). |
| RAG returns stale / wrong values | Enforce the soft/hard split — allow-lists stay deterministic (E5-S5); validation is the backstop. |
| GCP quota / rate limits on project creation | Identify & request increases early (discovery); serialize with concurrency handling. |
| Scope creep (Terraform scaffold vs JSON; MVP items) | Assumptions & exclusions doc; change control; confirm the construct-vs-scaffold question at discovery. |

> ## Assumptions & open questions to confirm
>
> Phase 1 is 6 weeks (three 2-week sprints); adjust distribution if longer. POC scope only.
>
> Access (repo, GCP, GitHub App, Vertex, Secret Manager) granted by end of Sprint 1.
>
> Client provides: factory repo, workflow YAML, real construct examples, standards docs, approved catalogs.
>
> Open: file-per-project vs aggregate; `workflow_dispatch` inputs & gate; the real construct schema; model choice; the confirmation channel; and whether the agent emits only JSON or also Terraform (“scaffold”) — resolve at discovery.
