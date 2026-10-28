# SOUND — Review gate R1: trusted stamp writer and reviewer authority

**Verdict: SOUND (Specification and Trust-Boundary Audit)**

This bounded Layer Lab report addresses findings R1, R6, and follow-up 1 from `MyTradingSys/research/lab_guy/findings/2026-10-19_review_harden_pair.md`. It provides the required analysis, threat boundary mapping, option comparison, and implementation contract for reviewer-attribution trust at the C2 review gate. Per the card scope, no code or test edits are made; implementation and deployment remain unapproved.

---

## 1. Existing State and Trace

| Component | Code Reference | What It Actually Validates | What It Cannot Validate (Human/Authority Gap) |
|---|---|---|---|
| **Stamp Grammar** | `scripts/dev/tasks.py:560-561` | Validates regex match against two patterns: `STAMP_PLAN_RE` (`^REVIEWED:\s*(\d{4}-\d{2}-\d{2})\s+(ACCEPT\|T0-ONLY)`) and `REVIEWED_RE` (`^REVIEWED:\s+(?!\d{4}-\d{2}-\d{2})(\S+)\s+(\d{4}-\d{2}-\d{2})`). | Does not validate that the stamp was authored by a designated reviewer or that the date is contemporaneous. |
| **Producer Checks** | `scripts/dev/tasks.py:581-583` | Casefolded string matching against literal card fields: `producer`, `producer_model`, `vendor`, `model`, `worker`, `refined_by`, plus a fixed placeholder blacklist (`x`, `self`, `producer`, `reviewer`, `pending`, `unknown`). | Any unlisted string (e.g. `bob`, `codex_run.py`, `Sonnet`, `operator`) passes trivially. If a producer edits the note directly via text editor, Git, or `apply-op --note`, the card accepts the forgery. |
| **Hard Review Gate** | `scripts/dev/tasks.py:638-648` (`review_gate`) | Checks whether `stamp_kind(card) == "real"` for cards with `weight` in `("CRUCIAL", "CRITICAL")` or `class` in `("C2", "C3")`. | Confirms only the syntactic presence of a "real" stamp string. Does not bind the review to a signed cryptographic key or server-side authorization event. |
| **Close Receipt** | `scripts/dev/tasks.py:646-647` | Requires `result` string to be non-empty when finishing (`finishing=True`). | Does not validate content integrity, external attestation, or reviewer identity. |
| **Provenance Values** | `scripts/dev/tasks.py:581` | Compares self-declared metadata fields stored in the same mutable JSON card file. | Mutable within the same repository commit; a committer or worker can alter both the card fields and the stamp simultaneously. |

**Key Finding:** Today's stamp mechanism is a syntactic convention, not an authentication boundary. It ensures machine checks don't accidentally treat `T0-ONLY` as a full review, but it provides zero cryptographic or operational defense against intentional or accidental self-stamping by an actor with repository write access.

---

## 2. Threat Boundary and Trust Model Comparison

Any defensible trust model must protect against the primary threat: **a session or agent modifying a task card to grant itself review clearance on a C2/C3 foundational card without an authorized independent review.**

### Model A: Externally Held Signing Key Over a Canonical Review Payload
- **Trust Root:** Asymmetric cryptographic keypair (e.g., Ed25519 or SSH/GPG signing key). The private key is held strictly outside the repository worktrees (e.g., in a dedicated secure keystore or local agent keychain accessible only to the designated Lab_Guy / Reviewer process).
- **Key / Identity Lifecycle:**
  - Public keys are registered in a pinned, root-of-trust configuration file (e.g., `system/REVIEW_KEYS.json`) mapping Key ID -> Reviewer Role/Identity.
  - Revocation is handled by removing or blacklisting the Key ID in the root configuration.
- **Canonical Payload Structure:**
  ```json
  {
    "card_id": "lab-review-gate-stamp-writer",
    "scope_sha": "<git commit sha being reviewed>",
    "verdict": "ACCEPT",
    "timestamp_utc": "2026-10-18T22:00:00Z",
    "reviewer_id": "lab_guy_sonnet_01",
    "nonce": "<random-uuid>"
  }
  ```
- **Replay Protection:** The signed payload must bind directly to the specific `scope_sha` (commit hash of the files under review) and the `card_id`. A signature created for commit $A$ cannot be reused for commit $B$.
- **Threat Boundary (Checkout / Repo-Writer):**
  - An untrusted producer modifying `.json` task cards in its worktree cannot forge a signature without access to the external private key.
  - Tampering with the task card or re-pointing it to unreviewed code invalidates the signature against `scope_sha`.
- **Operational Dependencies:** Requires a signing utility or agent tool capable of signing payloads, and Python verification logic (`cryptography` or standard SSH/GPG verification) in `tasks.py`.

### Model B: Protected CI Identity Backed by a Server-Side Review Event
- **Trust Root:** Remote repository platform permissions (e.g. GitHub Actions / GitLab CI trusted environment, or protected branch rule + PR approval / webhook event).
- **Key / Identity Lifecycle:**
  - Identity is established via the CI runner's authenticated OIDC token or platform bot credentials (`GITHUB_TOKEN` / App private key).
  - Reviewer authorization is configured in repository platform settings / branch protection rules.
- **Canonical Payload / Event:**
  - A dedicated review workflow triggered by an approved review event or comment from an authorized account.
  - The workflow appends an immutable attestation artifact or commits a verified merge/review receipt directly to the target branch.
- **Replay Protection:** CI checks commit parentage, PR number, and HEAD SHA. The review event is strictly tied to a specific commit SHA evaluated by the remote workflow.
- **Threat Boundary (Checkout / Repo-Writer):**
  - Local sessions and worktrees cannot simulate a server-side CI event; local commits attempting to claim review status without a corresponding CI-signed receipt are rejected during `sync.py ship` or at the CI gate.
- **Operational Dependencies:** Requires network connectivity to the remote git remote / CI server, branch protection enforcement, and asynchronous coordination (cards cannot be stamped purely offline).

---

## 3. Comparison Matrix

| Evaluation Dimension | Model A: External Signing Key | Model B: Protected CI Identity |
|---|---|---|
| **Independence of Trust Root** | **High** (private key kept in secure agent store outside repo checkout) | **High** (remote server / CI platform identity) |
| **Offline / Local Multi-Session Operation** | **Full Support** (NUC / laptop can verify signatures locally without network reach) | **Poor / Blocked** (requires network reach to origin and server-side workflow execution) |
| **Resistance to Local Worktree Forgery** | **Absolute** (cryptographic signature cannot be synthesized by local script) | **Absolute at Gate** (local commits blocked upstream, but local gates fail unless cached) |
| **Replay & Scope Binding** | Binds explicitly to `(card_id, scope_sha, verdict)` | Binds to remote PR / commit SHA |
| **Implementation Complexity** | Medium (standalone standard Python script / ed25519 verification) | High (requires remote webhooks, branch protection, CI actions) |
| **Operational Feasibility in MTS** | **Directly matches current multi-tree local protocol (`PARALLEL.md`)** | Diverges from current decentralized peer sync via `sync.py` |

---

## 4. Recommendation and Missing Decision

### Recommendation
**Model A (Externally Held Signing Key over Canonical Review Payload)** is the only trust model that aligns with MTS's existing architecture (`PARALLEL.md`, offline / local peer worktrees across JIS-NB, JIS-NUC, and laptop).

### Missing Operator Decision
Before implementation can proceed, the operator must explicitly choose:
1. **Keystore Location and Keyholder Allocation:** Where the private keys reside (e.g., local agent secret storage for designated review agents vs. operator-controlled YubiKey/SSH key).
2. **Reviewer Roster Authority:** The authoritative source for approved reviewer keys (e.g. `MyTradingSys/system/REVIEW_ROSTER.json` checked into Git, or an operator-signed root key).
3. **Dual-Key vs Single-Key for C2/C3:** Whether C2 cards require two distinct signatures (e.g., non-Claude model + Claude verification) as outlined in `roles/lab_guy.md`.

*Until these operational decisions are recorded by the operator, code changes in `tasks.py` remain unapproved.*

---

## 5. Follow-Up Implementation Contract

When the operator approves Model A and defines the keystore:
1. **Signature Specification:**
   - Detached signature in hex or base64 placed in task card field `review_signature`.
   - Payload canonicalization: deterministic JSON string of `{"card_id": id, "scope_sha": sha, "reviewer": reviewer_id, "timestamp": iso_utc, "verdict": "ACCEPT"}`.
2. **Verification in `tasks.py:review_gate`:**
   - Parse `review_signature` on C2/C3 and CRUCIAL/CRITICAL cards.
   - Lookup public key for `reviewer` in approved roster.
   - Verify signature against current `scope_sha` (or git rev-parse of card scope).
   - Reject any card where signature is missing, invalid, or mismatched to the current commit state.
3. **Deprecation of Free-Text Stamp:**
   - Deprecate free-text `REVIEWED: ...` in `note` as a bypass mechanism for C2/C3 cards.
