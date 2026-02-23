# AGENTS.md (for gpt-5.3-codex)
Project: IRIS (Integrated Reasoning via Internal State)

## 0) Non-Negotiable Operating Mode
You are an implementation agent. You must not introduce architectural drift.
Before *any* development work (code changes, refactors, new modules, eval harness), you MUST complete the mandatory reading steps in Section 1 and follow the permissions in Section 3.

If there is any conflict between documents:
- **System-level invariants and normative contracts override everything else.**
- "Draft" or "design notes" never override normative/authoritative contracts.

When uncertain, explicitly label **不確定** and default to *not* making the change until the relevant contract text is consulted.

---

## 1) Mandatory Reading (Always Required)
Before you implement or modify anything, read these documents in this order:

1. `docs/System Invariants & Non-Negotiables.md` (Authoritative hard invariants) :contentReference[oaicite:3]{index=3}
2. `docs/What This Model Is Explicitly NOT.md` (Explicit non-goals; disallowed shortcuts) :contentReference[oaicite:4]{index=4}
3. `docs/Routing, Gating, and Control Are Learnable.md` (Control must be learnable; if/else is technical debt only) :contentReference[oaicite:5]{index=5}
4. `docs/State IR Canonical Spec.md` (Canonical State IR; closed token types) :contentReference[oaicite:6]{index=6}
5. `docs/State IR Examples & Edge Cases.md` (Normative examples and forbidden schema drift) :contentReference[oaicite:7]{index=7}
6. `docs/Single Trunk Contract & Allowed Variations.md` (Trunk contract; allowed vs forbidden changes) :contentReference[oaicite:8]{index=8}
7. `docs/Credit Assignment & Failure Recovery Model.md` (Credit/blame routing; recovery semantics) :contentReference[oaicite:9]{index=9}
8. Level contracts:
   - `docs/Level Contracts/Level 0–1 Contract.md` :contentReference[oaicite:10]{index=10}
   - `docs/Level Contracts/Level 2 Contract.md` :contentReference[oaicite:11]{index=11}
   - `docs/Level Contracts/Level 3–4 Contract.md` :contentReference[oaicite:12]{index=12}
   - `docs/Level Contracts/Level 5–6 Contract.md` :contentReference[oaicite:13]{index=13}

These are binding. If your change would violate any item above, **do not implement**; propose an alternative that complies.

---

## 2) Legacy Planning References (Required When Task Touches Planning/Eval Policy)
If your task mentions or implies work on planning, evaluation policy, metrics, or regression process, you MUST read:

- `docs/harness/legacy/DevelopmentPlan.md` (legacy phase definitions and gates)
- `docs/harness/legacy/metrics.md` (legacy metrics vocabulary and gates)
- `docs/harness/legacy/regression.md` (legacy regression harness policy)

Notes:
- `docs/plan/phase_A.md` to `docs/plan/phase_E.md` are no longer active mainline documents.
- Legacy documents are reference material and do not override Section 1 normative contracts.

---

## 3) Permissions and Authority Boundaries (Read/Write Rules)
This section defines what you may modify. Treat this as a repository policy.

### 3.1 Read-Only (RO): Binding Contracts and Invariants
You MUST NOT edit these files as part of routine development:
- `docs/System Invariants & Non-Negotiables.md` :contentReference[oaicite:22]{index=22}
- `docs/What This Model Is Explicitly NOT.md` :contentReference[oaicite:23]{index=23}
- `docs/Routing, Gating, and Control Are Learnable.md` :contentReference[oaicite:24]{index=24}
- `docs/State IR Canonical Spec.md` :contentReference[oaicite:25]{index=25}
- `docs/State IR Examples & Edge Cases.md` :contentReference[oaicite:26]{index=26}
- `docs/Single Trunk Contract & Allowed Variations.md` :contentReference[oaicite:27]{index=27}
- All Level Contracts under `docs/Level Contracts/` :contentReference[oaicite:28]{index=28} :contentReference[oaicite:29]{index=29} :contentReference[oaicite:30]{index=30} :contentReference[oaicite:31]{index=31}
- `docs/Credit Assignment & Failure Recovery Model.md` :contentReference[oaicite:32]{index=32}

If you believe a RO document is wrong or incomplete, you may:
- Write a proposal in a *new* document (see 3.3) explaining the conflict, implications, and migration plan.
- Do not silently change contracts.

### 3.2 Tooling Vendored Code (RO by Default)
The following are treated as externally sourced or "vendored":
- `tools/arc-agi-benchmarking/` (Do not modify tool internals as part of IRIS core work) :contentReference[oaicite:33]{index=33}
- `tools/ConceptARC/` (Do not rewrite the dataset/tool logic for convenience) :contentReference[oaicite:34]{index=34}

Allowed: add adapters/wrappers in `src/` that consume these tools without altering their upstream semantics.

### 3.3 Writable (W): Plans, Metrics, Regression, New Notes
You MAY edit/add under:
- `docs/plan/` (active planning docs, if present), provided you do not contradict RO contracts
- `docs/harness/legacy/` (archived planning/metrics/regression references)
- New documents under `docs/` that are explicitly labeled as:
  - `Design Note (Non-normative)` OR
  - `Change Proposal (Requires Approval)`
  and that clearly state they do not override contracts.

### 3.4 Writable (W): Core Implementation
You MAY implement and refactor core system code under:
- `src/` (the only place where core model behavior should live in Phase C and beyond) :contentReference[oaicite:37]{index=37} :contentReference[oaicite:38]{index=38}

You MUST keep:
- State IR schema enforcement in `src/schema/` aligned with State IR Canonical Spec. :contentReference[oaicite:39]{index=39}
- Trunk implementation consistent with trunk contracts (no hidden second trunk, and no architecture-specific bypass that violates the contract). :contentReference[oaicite:40]{index=40} :contentReference[oaicite:41]{index=41}

---

## 4) Hard Prohibitions (Reject Changes That Do This)
You must refuse to implement changes that:
1. Add new State IR token categories or change canonical ordering without a versioned spec revision (not allowed in normal development). :contentReference[oaicite:42]{index=42} :contentReference[oaicite:43]{index=43}
2. Bypass State IR by sending raw tensors, tool outputs, or program traces directly into the trunk. :contentReference[oaicite:44]{index=44} :contentReference[oaicite:45]{index=45}
3. Replace learned routing/gating/termination with deterministic if/else policy (except explicitly labeled guardrail technical debt with removal criteria). :contentReference[oaicite:46]{index=46} :contentReference[oaicite:47]{index=47}
4. Turn Level 2 into a "neural proposer + symbolic executor" split or a Python DSL interpreter as the core executor. :contentReference[oaicite:48]{index=48} :contentReference[oaicite:49]{index=49}
5. Add a secondary high-capacity network that competes with the trunk ("second trunk" in disguise). :contentReference[oaicite:50]{index=50} :contentReference[oaicite:51]{index=51}
6. Remove, collapse, or bypass any Level interface L0–L6 (including by deleting its I/O contract or stub behavior). Implementations may be disabled only if the interface contract remains intact. :contentReference[oaicite:52]{index=52}

---

## 5) Required Workflow for Any Change
### 5.1 Declare the Change Class
At the start of your work, explicitly declare one:
- Pure refactor (no behavior change expected)
- Targeted fix (must name failure category / suspected Level)
- Capability expansion (must name concepts / expected impact)

Use the failure taxonomy / metrics vocabulary; do not invent new labels ad hoc. :contentReference[oaicite:53]{index=53} :contentReference[oaicite:54]{index=54}

### 5.2 Maintain "Phase-Appropriate" Scope
- Phase A: diagnostics, verifier signals, trace/logging skeleton only (no solver heuristics). :contentReference[oaicite:55]{index=55}
- Phase B: tool generation alignment (failure tags, paired tasks), do not encode correctness rules into tools. :contentReference[oaicite:56]{index=56}
- Phase C: minimal closed loop in `src/` with all Level interfaces present (mounted or stubbed); failures must be attributable. :contentReference[oaicite:57]{index=57}
- Phase D: ConceptARC as diagnostic harness; output isolation/leakage/attribution metrics (not leaderboard tuning). :contentReference[oaicite:58]{index=58}
- Phase E: arc-agi-benchmarking as regression & verifier harness; no benchmark hacks. :contentReference[oaicite:59]{index=59}

### 5.3 Regression Discipline (Always-On)
Any architectural/training/eval-impacting change must:
- Preserve the regression harness expectations and artifacts.
- Avoid silent shifts in failure distributions unless explicitly intended and documented. :contentReference[oaicite:60]{index=60} :contentReference[oaicite:61]{index=61}

---

## 6) "Technical Debt" Rule for Hard Control (Only as Guardrail)
If you must introduce a hard cap (e.g., max steps), you MUST:
- Label it clearly as TEMPORARY TECHNICAL DEBT.
- Isolate it so it can be removed.
- Provide a removal criterion and the intended learned replacement.
- Ensure it does not become routine policy. :contentReference[oaicite:62]{index=62} :contentReference[oaicite:63]{index=63}

---

## 7) Repository Structure Expectations (Do Not Violate)
- Core model behavior belongs in `src/`.
- Tools remain in `tools/` and should not become the intelligence substrate.
- Datasets are under `data/` and are not a place to encode semantics. :contentReference[oaicite:64]{index=64} :contentReference[oaicite:65]{index=65}

---

## 8) Minimal Completion Checklist (Attach to Each PR/Change)
You must include:
- Which mandatory docs you consulted (Section 1 + any Phase docs from Section 2).
- The change class (refactor / targeted fix / expansion).
- The expected failure-category impact (using canonical metrics).
- Any introduced technical debt guardrails (with removal criteria), if applicable.
- Regression status: what suites are expected to pass / what artifacts are updated. :contentReference[oaicite:66]{index=66} :contentReference[oaicite:67]{index=67}

End of AGENTS.md
