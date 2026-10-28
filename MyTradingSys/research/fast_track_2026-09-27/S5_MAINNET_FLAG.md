# S5 — Mainnet Flag Design (design only, no code) — 2026-09-28

Status today (evidenced, `deribit_orders.py` v3 as staged): `BASE = "https://test.deribit.com/api/v2"` is
hardcoded ("testnet only - deliberately not parameterised") and `_load_secret()` raises
`RuntimeError('REFUSED: secret file env must be "test"')` unless the secret file's `"env"` key is exactly
`"test"`. There is no mainnet code path today (per FT-2 guard audit, `research/fast_track_2026-09-27/FT2_GUARD_GAPS.md`,
guard G-f: "safe by omission" - the explicit-flag mechanism itself has not been built). This document designs
the smallest change that adds one, without weakening anything that exists.

## Goals / non-goals

- Goal: make mainnet reachable only through a path that requires *several independent, deliberate* operator
  actions, each of which is individually testable offline (no real network call needed to prove a refusal).
- Goal: keep testnet the zero-friction default - no flag, no confirmation, behaves exactly as today.
- Non-goal: this document does not touch `executor.py`, `position_manager.py`, or any other file. It proposes
  a diff to `deribit_orders.py` only, plus one new CLI entry point. No file in this design doc's diff sketch
  is applied by this task - S5 is design-only.

## The four independent gates (all four must pass, in this order)

1. **Explicit flag.** `deribit_orders` gains `select_environment(mainnet: bool = False)` (or the CLI/env
   equivalent below) - `BASE` becomes a value chosen at call time, never a module-level constant read at
   import. Default (`mainnet=False`) is always testnet, so every existing caller that never asks for mainnet
   keeps working unchanged.
2. **Secret env match.** The secret file loaded must declare `"env": "mainnet"` to be used against the
   mainnet base URL. A `"test"` secret can never authenticate against mainnet, and a `"mainnet"` secret can
   never authenticate against testnet - `_load_secret()` is given the target environment and refuses on any
   mismatch, in both directions. This is the same mechanism that already exists (today only checks `== "test"`
   because only testnet exists); it is widened to a two-way check, not replaced.
3. **Separate subaccount key.** The mainnet secret file lives at a different path
   (`.secrets/mainnet.secret.json`, never `.secrets/testnet.secret.json` with fields swapped) and its
   `client_id`/`client_secret` must belong to a Deribit **subaccount created for MTS only** - never the
   operator's main account. This is an operator-side setup requirement (documented, not enforced by code,
   since the code cannot know which subaccount a key belongs to) but `authenticate()`'s existing
   withdraw-scope refusal (`"wallet:read_write" in scope`) stays unchanged and applies to this key too - it is
   the one machine-checkable property of "least-privilege key" available.
4. **Interactive, typed confirmation.** The mainnet CLI entry point refuses to proceed unless the operator
   types an exact, non-guessable confirmation string back at a prompt (see below) - never a bare `y/N`, never
   accepted via a flag (a flag could end up in a saved shell history or a script run unattended).

Each gate is independent: flipping only the flag without a mainnet secret file fails gate 2; having a mainnet
secret file but not passing the flag never reaches gate 2 at all (gate 1 already returned testnet); typing the
wrong confirmation string fails gate 4 after gates 1-3 already passed. No single mistake is enough to reach a
live order.

## Refusal matrix

| Flag (`--mainnet`) | Secret file `env` | Confirmation typed | Result |
|---|---|---|---|
| absent | any | any | testnet (today's behavior, unchanged) |
| present | `.secrets/mainnet.secret.json` missing | any | `RuntimeError: MISSING: .secrets/mainnet.secret.json` (existing `_load_secret` missing-file message, same shape as today's testnet one) |
| present | `"test"` (wrong file loaded, or testnet secret copied) | any | `RuntimeError: REFUSED: secret file env must be "mainnet"` (mirror of today's message, other direction) |
| present | `"mainnet"` but key scope includes `wallet:read_write` | any | `RuntimeError: REFUSED: key can withdraw...` (existing `authenticate()` check, unchanged, now exercised on the mainnet path too) |
| present | `"mainnet"`, scope OK | anything other than the exact confirmation string | refuse before calling `authenticate()` at all - no network call is made, no token requested |
| present | `"mainnet"`, scope OK | exact confirmation string | proceeds to `authenticate()` against mainnet `BASE` |

The confirmation string is not a secret; it exists purely to make an accidental Enter-key-mash or a copy-pasted
command line insufficient. Proposed literal: `I understand this places a real order with real money on
BTC-PERPETUAL mainnet`, entered at an interactive `input()` prompt (never read from argv/env, so it can't be
baked into a saved command). No config file or environment variable can supply it.

## FT-2 guards that must be active before mainnet orders

Per `research/fast_track_2026-09-27/FT2_GUARD_GAPS.md`, mainnet must not be reachable until these are wired
and their own offline tests pass (this task does not implement or verify them - it records the dependency):

- **G-c daily loss guard** (`daily_loss_guard.py` + `daily_loss_monitor.py`, this session's S2 task) running
  and its `HALT_DAILY_LOSS` file check wired into whatever preflight gate ends up guarding order placement.
- **G-e kill switch** (`kill_switch.py`, staged) reachable - an operator must be able to flatten mainnet in
  one command before the first mainnet order is ever placed, not built afterward.
- **G-b account notional cap** (`risk_guard.py`, staged) wired into preflight, so a mainnet plan cannot alone
  or in combination with other live plans exceed `MAX_ACCOUNT_NOTIONAL_USD`.
- **G-d unprotected-position bound** hardened (explicit `max_unprotected_seconds`, per the audit) - mainnet
  fills are real money the moment they land; the implicit poll-count bound that exists today should be made
  explicit first.

Recommendation: gate the mainnet flag itself (gate 1 above) behind a repo-level checklist file (e.g.
`execution/MAINNET_READINESS_CHECKLIST.md`, operator-maintained, not code-enforced) rather than trying to
machine-verify "are the guards wired" from `deribit_orders.py` - that verification would require the module to
know about `executor.py`'s preflight contents, which crosses the "standalone module" boundary this fast-track
has otherwise kept clean.

## Proposed diff sketch for `deribit_orders.py`

Sketch only - not applied by this task. Shape, not final code:

```python
# --- before (current, staged v3) ---
BASE = "https://test.deribit.com/api/v2"  # testnet only - deliberately not parameterised
SECRET = ROOT / "MyTradingSys" / "execution" / ".secrets" / "testnet.secret.json"

def _load_secret() -> dict:
    if not SECRET.exists():
        raise RuntimeError(f"MISSING: {SECRET} - operator must create it first (see execution/README.md)")
    cfg = json.loads(SECRET.read_text(encoding="utf-8"))
    if cfg.get("env") != "test":
        raise RuntimeError('REFUSED: secret file env must be "test"')
    return cfg

def authenticate() -> str:
    cfg = _load_secret()
    ...

# --- after (sketch) ---
ENVIRONMENTS = {
    "test":    {"base": "https://test.deribit.com/api/v2",
                "secret": ROOT / "MyTradingSys" / "execution" / ".secrets" / "testnet.secret.json"},
    "mainnet": {"base": "https://www.deribit.com/api/v2",
                "secret": ROOT / "MyTradingSys" / "execution" / ".secrets" / "mainnet.secret.json"},
}
DEFAULT_ENV = "test"  # every call site that doesn't opt in stays on testnet, unchanged

def _load_secret(env: str = DEFAULT_ENV) -> dict:
    spec = ENVIRONMENTS[env]
    if not spec["secret"].exists():
        raise RuntimeError(f"MISSING: {spec['secret']} - operator must create it first (see execution/README.md)")
    cfg = json.loads(spec["secret"].read_text(encoding="utf-8"))
    if cfg.get("env") != env:
        raise RuntimeError(f'REFUSED: secret file env must be "{env}"')
    return cfg

def authenticate(env: str = DEFAULT_ENV) -> str:
    cfg = _load_secret(env)
    auth = _call("public/auth", {...}, retry=False, base=ENVIRONMENTS[env]["base"])
    if "wallet:read_write" in auth.get("scope", ""):
        raise RuntimeError("REFUSED: key can withdraw (wallet:read_write). Recreate it with wallet none/read.")
    return auth["access_token"]
```

Every function currently closing over module-level `BASE` (`_post`, `_call`, and transitively every public
function) needs `base`/`env` threaded through, or a slimmer alternative: keep `BASE`/`SECRET` as module-level
*variables* (not constants) and add one function `use_mainnet(confirmed: bool)` that reassigns them after
gates 1-4 all pass, called once at process start by the new mainnet CLI entry point, never by library code
importing `deribit_orders` for testnet use. The threaded-parameter version above is more testable (no shared
mutable module state) and is the recommended shape; the reassignment version is smaller but reintroduces
hidden global state this repo's v2/v3 review history (see the file's own docstring) has been actively removing
elsewhere. **Recommend the threaded-parameter version.**

New file (not part of this diff sketch, separate small script):
`MyTradingSys/execution/mainnet_confirm.py` - the interactive CLI entry point implementing gate 4 (`input()`
prompt, exact-string compare, then calls `deribit_orders.authenticate(env="mainnet")` only after all four
gates pass). Kept as its own file so it can be a **SONNET** task with a tiny, obviously-correct diff, separate
from any changes to `deribit_orders.py` itself.

## Tests that prove each refusal offline (design only - not written by this task)

All can run with `run_staged_tests.py`, no network, using the existing fake-secret-file pattern already used
elsewhere in this repo's tests (write a temp `.secrets/mainnet.secret.json` with controlled contents):

1. `env=DEFAULT_ENV` (no mainnet requested) -> `_load_secret()`/`authenticate()` use the testnet path exactly
   as before (regression test: today's behavior must not change).
2. Mainnet requested, `.secrets/mainnet.secret.json` absent -> `RuntimeError` naming that path, `authenticate`
   never reaches `_call`/network.
3. Mainnet requested, secret file present with `"env": "test"` -> `RuntimeError: REFUSED: secret file env
   must be "mainnet"`.
4. Mainnet requested, secret file present with `"env": "mainnet"` and `scope` containing
   `"wallet:read_write"` (fake `_call`/`authenticate` response) -> existing withdraw-scope `RuntimeError`,
   unchanged message.
5. Mainnet confirm script: wrong confirmation string typed (simulate `input()` via monkeypatch) -> refuses
   before calling `authenticate` at all - assert the fake `authenticate` was never invoked (call-count == 0).
6. Mainnet confirm script: exact confirmation string typed, valid mainnet secret + non-withdraw scope (fully
   faked, no real network) -> `authenticate` invoked exactly once with `env="mainnet"`.
7. Sanity: assert `ENVIRONMENTS["test"]["base"] != ENVIRONMENTS["mainnet"]["base"]` and that no test in this
   suite ever asserts against `"https://www.deribit.com"` reachability (it must never actually be hit in
   offline tests).
