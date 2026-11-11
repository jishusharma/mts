Counts: MATCH: 6, DIFF: 0, NOT_IN_DATA: 0

# Gemini Blind Read of `scripts/dev/stop_guard.py` vs Module Docstring Contract

- **Card ID**: `gemini-blind-read-stop-guard-1111`
- **Auditor**: Gemini 3.8 Flash (Low)
- **Date**: 2026-11-11
- **Target**: `scripts/dev/stop_guard.py:1-9`

## Summary Table

| ID | Docstring Promise | Docstring Quote (`scripts/dev/stop_guard.py`) | Implementation Quote (`scripts/dev/stop_guard.py`) | Status | Notes |
|---|---|---|---|---|---|
| P1 | Block when tree holds real work | "when the session tries to stop and `sync.py where` logic says its tree holds real work, block ONCE with the instruction to commit and `sync.py ship`." (`scripts/dev/stop_guard.py:4-5`) | `scripts/dev/stop_guard.py:89-126,238,243-244` | MATCH | `reason()` evaluates work vs noise and returns reason string; `hook()` formats decision `"block"` (or `"continue"` for Antigravity) with message to commit and ship. |
| P2 | Block only once per state | "block ONCE with the instruction to commit and `sync.py ship`." (`scripts/dev/stop_guard.py:4-5`) | `scripts/dev/stop_guard.py:200-220,241` | MATCH | `seen_before(sid, why)` caches the state per session in `mts-stop-guard.json` (keeping last 50 sessions). If seen before, `hook()` allows stop by returning `""`. |
| P3 | Second stop allowed | "A second stop in the same turn (stop_hook_active) is always allowed: a stuck gate must not trap a session in a loop." (`scripts/dev/stop_guard.py:5-6`) | `scripts/dev/stop_guard.py:229-230` | MATCH | `hook()` checks `if data.get("stop_hook_active"): return ""` which bypasses all checks and allows the stop immediately. |
| P4 | Never raises | "Never raises." (`scripts/dev/stop_guard.py:6`) | `scripts/dev/stop_guard.py:225,245-246` | MATCH | The entire body of `hook()` is enclosed in `try: ... except Exception: return ""`, ensuring no unhandled exception is ever raised. |
| P5 | Ignores .mts_live, trunk checkouts, and regenerable noise | "Ignores the live tree (.mts_live), trunk checkouts and regenerable noise." (`scripts/dev/stop_guard.py:6`) | `scripts/dev/stop_guard.py:96-97,108-110,122-126` | MATCH | `(top / ".mts_live").exists()` returns None; branch in `("fast-track", "master", "main")` returns None; `sync.not_work(top, rows)` and `sync.is_noise(l)` filter out noise rows. |
| P6 | MTS_STOP_GUARD=off disables | "Env: MTS_STOP_GUARD=off disables." (`scripts/dev/stop_guard.py:7`) | `scripts/dev/stop_guard.py:226-227` | MATCH | `if os.environ.get("MTS_STOP_GUARD", "").lower() == "off": return ""` immediately allows the stop. |

## Detailed Line-by-Line Code Verification

### Promise 1 & 2: Block once when tree holds real work
- **Docstring**: "when the session tries to stop and `sync.py where` logic says its tree holds real work, block ONCE with the instruction to commit and `sync.py ship`." (`scripts/dev/stop_guard.py:4-5`)
- **Code**:
  - `seen_before(session_id, why)` at `scripts/dev/stop_guard.py:200-220` records `d[session_id] = why` in `mts-stop-guard.json`.
  - `hook()` at `scripts/dev/stop_guard.py:241-244`:
    ```python
    if not why or (not sup and seen_before(sid, why)):
        return ""
    decision = "continue" if is_agy else "block"
    return json.dumps({"decision": decision, "reason": message(why)})
    ```
  - `message(why)` at `scripts/dev/stop_guard.py:195-197`:
    ```python
    return (f"STOP GUARD: this worktree still holds work ({why}). Commit it (body ends `Result: ...`) and run "
            f"`python scripts/dev/sync.py ship`; if the files are scratch, delete them or add them to .gitignore. "
            f"Then end the session.")
    ```
- **Finding**: **MATCH**

### Promise 3: Second stop in the same turn (stop_hook_active) is always allowed
- **Docstring**: "A second stop in the same turn (stop_hook_active) is always allowed: a stuck gate must not trap a session in a loop." (`scripts/dev/stop_guard.py:5-6`)
- **Code**:
  - In `hook(stdin_text)` at `scripts/dev/stop_guard.py:229-230`:
    ```python
    if data.get("stop_hook_active"):
        return ""
    ```
- **Finding**: **MATCH**

### Promise 4: Never raises
- **Docstring**: "Never raises." (`scripts/dev/stop_guard.py:6`)
- **Code**:
  - In `hook(stdin_text)` at `scripts/dev/stop_guard.py:225-246`:
    ```python
    def hook(stdin_text):
        """-> JSON string for Claude Code or Antigravity, or '' to allow the stop."""
        try:
            ...
        except Exception:
            return ""
    ```
- **Finding**: **MATCH**

### Promise 5: Ignores the live tree (.mts_live), trunk checkouts and regenerable noise
- **Docstring**: "Ignores the live tree (.mts_live), trunk checkouts and regenerable noise." (`scripts/dev/stop_guard.py:6`)
- **Code**:
  - Live tree check at `scripts/dev/stop_guard.py:96-97`:
    ```python
    if (top / ".mts_live").exists():
        return None
    ```
  - Trunk checkouts check at `scripts/dev/stop_guard.py:108-110`:
    ```python
    branch = branch.strip()
    if branch in ("fast-track", "master", "main") or branch.startswith("gemini-q/"):
        return None
    ```
  - Regenerable noise check at `scripts/dev/stop_guard.py:122-125`:
    ```python
    skip = sync.not_work(top, rows)     # B6 CRLF/LF-only rewrites, B3 files of a nested (another session's) worktree
    t = dict(path=str(top), name=top.name, branch=branch, ahead=int(ahead.strip() or 0),
             work=[l for l in rows if not sync.is_noise(l) and l not in skip],
             noise=[l for l in rows if sync.is_noise(l) or l in skip], fix="")
    ```
- **Finding**: **MATCH**

### Promise 6: Env MTS_STOP_GUARD=off disables
- **Docstring**: "Env: MTS_STOP_GUARD=off disables." (`scripts/dev/stop_guard.py:7`)
- **Code**:
  - In `hook(stdin_text)` at `scripts/dev/stop_guard.py:226-227`:
    ```python
    if os.environ.get("MTS_STOP_GUARD", "").lower() == "off":
        return ""
    ```
- **Finding**: **MATCH**

## Counts Verification (SOURCED)
- Evaluated promises: 6
- MATCH: 6 (`scripts/dev/stop_guard.py:4-7` vs `scripts/dev/stop_guard.py:96-97,108-110,122-126,195-197,200-220,226-230,241-246`)
- DIFF: 0
- NOT_IN_DATA: 0
