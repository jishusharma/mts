counts: MATCH=8 DIFF=0 NOT_IN_DATA=0 (sum 8)

# Gemini Blind Read: scripts/dev/mts_signal.py Docstring vs Implementation and Tests

- Date: 2026-11-11
- Card: `gemini-blind-read-mts-signal-docstring-1111`
- Scope In:
  - `scripts/dev/mts_signal.py` (read)
  - `scripts/dev/test_mts_signal.py` (read)
  - `MyTradingSys/research/layer_lab/reports/2026-11-11_gemini-blind-read-mts-signal-docstring-1111.md` (new)
- Scope Out: no edit to the source files; no live-tree edit, no deploy, no `.secrets` or `.env` read; read-only audit

## Summary Table

| Clause # | Docstring Clause Requirement | Implementation Status | Implementation Code (`scripts/dev/mts_signal.py`) | Test Verification (`scripts/dev/test_mts_signal.py`) |
|---|---|---|---|---|
| 1 | `send`: `python scripts/dev/mts_signal.py send "<text>" [--to host\|all] [--kind note\|claim\|done\|ask\|broadcast]` | MATCH | SOURCED `scripts/dev/mts_signal.py:44` `python scripts/dev/mts_signal.py send "<text>" [--to host\|all] [--kind note\|claim\|done\|ask\|broadcast]`<br>SOURCED `scripts/dev/mts_signal.py:1389-1401` `ap = argparse.ArgumentParser(prog="mts_signal.py send")`, `ap.add_argument("text")`, `ap.add_argument("--to", default="all")`, `ap.add_argument("--kind", default="note", choices=["note", "claim", "done", "ask", "broadcast"])`; returns 0 if ok else 1; redirects kind="ask" to `main(["ask", a.text, "--to", a.to])` | SOURCED `scripts/dev/test_mts_signal.py:62-71` `test_send_then_other_machine_reads_not_own`<br>SOURCED `scripts/dev/test_mts_signal.py:72-78` `test_direct_to_host_only` testing `to` filtering<br>SOURCED `scripts/dev/test_mts_signal.py:80-84` testing `clean` length and secret redactions |
| 2 | `read`: `python scripts/dev/mts_signal.py read [--hours 24]` (newest last) | MATCH | SOURCED `scripts/dev/mts_signal.py:47` `python scripts/dev/mts_signal.py read [--hours 24]       newest last`<br>SOURCED `scripts/dev/mts_signal.py:1561-1575` parses `--hours` (default 24), loads rows from `h = ensure()`, filters `r.get("t", "") > since`, prints each line in chronological order (newest last), prints `"no signals in the last %g h"` if empty; returns 0 on success, 1 on no origin | SOURCED `scripts/dev/test_mts_signal.py:66-68` verifies loaded signal rows and ordering<br>SOURCED `scripts/dev/test_mts_signal.py:476-484` tests CLI `main(["read"])` and output formatting |
| 3 | `ack`: `python scripts/dev/mts_signal.py ack <id> told\|done [--note "..."]` | MATCH | SOURCED `scripts/dev/mts_signal.py:22-26` `python scripts/dev/mts_signal.py ack <id> told\|done [--note "..."]`<br>SOURCED `scripts/dev/mts_signal.py:1494-1526` `ap = argparse.ArgumentParser(prog="mts_signal.py ack")`, `ap.add_argument("id")`, `ap.add_argument("state", choices=["told", "done"])`, `ap.add_argument("--note", default="")`; validates open asks (`q-`) and high broadcasts (`b-`); enforces `--note` for `done` on ask (SOURCED line 1511) and for `told` on high broadcast with `--cmd` (SOURCED line 1520); returns 2 on validation failure, 0 if sent, 1 if push failed | SOURCED `scripts/dev/test_mts_signal.py:539-556` `test_ack_high_broadcast_told_then_done`<br>SOURCED `scripts/dev/test_mts_signal.py:575-587` `test_high_broadcast_with_cmd_refuses_told_without_note` verifying return code 2 and requirement for `--note` |
| 4 | `asks`: `python scripts/dev/mts_signal.py asks [--json]` | MATCH | SOURCED `scripts/dev/mts_signal.py:41` `asks [--json] and status_board.py list it as OVERDUE with age.`<br>SOURCED `scripts/dev/mts_signal.py:1418-1435` `if cmd == "asks":` calls `escalate(rows)` on overdue asks, loads rows, handles `--json` output (`json.dumps(res)`), or prints formatted list showing id, sender, recipient, state, age, deadline, escalation target, and text snippet; prints `"no open asks"` if empty; returns 0 on success, 1 on no origin | SOURCED `scripts/dev/test_mts_signal.py:734-750` `test_asks_listing_and_escalation`<br>SOURCED `scripts/dev/test_mts_signal.py:752-763` `test_asks_json_output` |
| 5 | `pending`: `python scripts/dev/mts_signal.py pending [--host <h>] [--json]` | MATCH | SOURCED `scripts/dev/mts_signal.py:27-28` `python scripts/dev/mts_signal.py pending [--host <h>] [--json]   HIGH broadcasts needing action on a host`<br>SOURCED `scripts/dev/mts_signal.py:1473-1493` `ap = argparse.ArgumentParser(prog="mts_signal.py pending")`, `ap.add_argument("--host", default="")`, `ap.add_argument("--json", action="store_true")`; loads active hosts or filters by `--host`; outputs JSON array or prints pending items with hours waiting; returns 0 on success, 1 on no origin | SOURCED `scripts/dev/test_mts_signal.py:558-573` `test_pending_lists_hosts_needing_action` asserting pending status and JSON serialization |
| 6 | `broadcast`: `python scripts/dev/mts_signal.py broadcast "<message>" [--to ...] [--prio normal\|high] [--cmd "..."]` | MATCH | SOURCED `scripts/dev/mts_signal.py:18` and `scripts/dev/mts_signal.py:45-46` `python scripts/dev/mts_signal.py broadcast "<text>" --prio high --cmd "<exact operator command>"`<br>SOURCED `scripts/dev/mts_signal.py:1436-1465` `ap = argparse.ArgumentParser(prog="mts_signal.py broadcast")`, args: `message`, `--to` (default "all"), `--prio` (choices `normal`, `high`), `--audience` (choices `all`, `top`), `--cmd` (default ""), `--wait` (float, default 0); generates `b-xxxxxx` id for HIGH broadcasts; returns 0 on success, 1 if push failed | SOURCED `scripts/dev/test_mts_signal.py:515-537` `test_high_broadcast_lifecycle_and_hooks`<br>SOURCED `scripts/dev/test_mts_signal.py:575-587` `test_high_broadcast_with_cmd_refuses_told_without_note` |
| 7 | `ask`: `python scripts/dev/mts_signal.py ask "<text>" --to <host\|A\|B\|C\|all> [--type ask\|resend\|task] [--wait M] [--due M]` | MATCH | SOURCED `scripts/dev/mts_signal.py:35-39` `python scripts/dev/mts_signal.py ask "<text>" --to <host\|A\|B\|C\|all> [--type ask\|resend\|task] [--wait M] [--due M]`<br>SOURCED `scripts/dev/mts_signal.py:1402-1417` `ap = argparse.ArgumentParser(prog="mts_signal.py ask")`, `ap.add_argument("text")`, `ap.add_argument("--to", default="all")`, `ap.add_argument("--type", default="ask", choices=sorted(ASK_TYPES))`, `ap.add_argument("--wait", type=int)`, `ap.add_argument("--due", type=int)`, `ap.add_argument("--wait-reply", type=float, default=0)`; generates `q-xxxxxx` id; returns 0 on success, 3 on duplicate re-ask inside wait period, 1 on failure | SOURCED `scripts/dev/test_mts_signal.py:680-705` `test_ask_and_ack_workflow`<br>SOURCED `scripts/dev/test_mts_signal.py:707-732` `test_ask_duplicate_refused_within_wait` |
| 8 | `acks`: `python scripts/dev/mts_signal.py acks [<id>]` | MATCH | SOURCED `scripts/dev/mts_signal.py:30-31` `python scripts/dev/mts_signal.py acks [<id>]   hosts seen in the last KEEP_DAYS vs none/told/done; no id = all open high broadcasts.`<br>SOURCED `scripts/dev/mts_signal.py:1527-1543` `if cmd == "acks":` extracts optional `<id>` from `argv[1]`, filters `high_open(rows)` for specified id or all open high broadcasts not in terminal states across targets; prints status per host and blocker notes; returns 0 on success, 1 on no origin | SOURCED `scripts/dev/test_mts_signal.py:539-556` `test_ack_high_broadcast_told_then_done`<br>SOURCED `scripts/dev/test_mts_signal.py:623-644` `test_acks_cli_output` |

## Detailed Clause Verification

### Clause 1: `send` command, flags, and exit codes
- **Docstring**: SOURCED `scripts/dev/mts_signal.py:44`:
  `python scripts/dev/mts_signal.py send "<text>" [--to host|all] [--kind note|claim|done|ask|broadcast]`
- **Code**:
  - Defined in `main()` at SOURCED `scripts/dev/mts_signal.py:1389-1401`.
  - Argument parser sets positional `text`, `--to` (default `"all"`), `--kind` (default `"note"`, choices `["note", "claim", "done", "ask", "broadcast"]`), `--sid` (suppressed).
  - Special branch at line 1397: `if a.kind == "ask": return main(["ask", a.text, "--to", a.to])`.
  - Sends record via `send(a.text, to=a.to, kind=a.kind, sid=a.sid)` (line 1399).
  - Exit code: `return 0 if ok else 1` (line 1401).
- **Test**:
  - `test_send_then_other_machine_reads_not_own` (SOURCED `scripts/dev/test_mts_signal.py:62-71`).
  - `test_direct_to_host_only` (SOURCED `scripts/dev/test_mts_signal.py:72-78`).
  - `test_clean_cuts_secretlike_and_length` (SOURCED `scripts/dev/test_mts_signal.py:80-84`).
- **Verdict**: MATCH.

### Clause 2: `read` command, flags, and exit codes
- **Docstring**: SOURCED `scripts/dev/mts_signal.py:47`:
  `python scripts/dev/mts_signal.py read [--hours 24]       newest last`
- **Code**:
  - Defined in `main()` at SOURCED `scripts/dev/mts_signal.py:1561-1575`.
  - Optional flag `--hours` (default `24`).
  - Ensures repository clone exists (`h = ensure()`), exits with `1` if `h is None` (lines 1565-1568).
  - Filters rows where timestamp `t > since` (line 1570).
  - Iterates over rows in append order, printing `line(r)` (chronological, newest last).
  - If no rows match, prints `"no signals in the last %g h" % hours` (line 1574).
  - Exit code: `return 0` on success.
- **Test**:
  - Read verification in `SignalTest` (SOURCED `scripts/dev/test_mts_signal.py:66-70`).
  - CLI read test in `test_read_cli` (SOURCED `scripts/dev/test_mts_signal.py:476-484`).
- **Verdict**: MATCH.

### Clause 3: `ack` command, flags, and exit codes
- **Docstring**: SOURCED `scripts/dev/mts_signal.py:22-26`:
  `python scripts/dev/mts_signal.py ack <id> told|done [--note "..."]`
- **Code**:
  - Defined in `main()` at SOURCED `scripts/dev/mts_signal.py:1494-1526`.
  - Arguments: `id`, `state` (choices `["told", "done"]`), `--note` (default `""`).
  - Supports both ask IDs (`q-`) and broadcast IDs (`b-`):
    - For `q-`: checks `a.id in asks_open(rows)`, exits `2` if unknown or already answered (lines 1506-1509). Requires `--note` if `state == "done"`, exits `2` if missing (lines 1510-1512).
    - For `b-`: checks `a.id in high_open(rows)`, exits `2` if unknown or expired (lines 1516-1519). If `state == "told"` and broadcast has `cmd`, requires non-empty `--note`, exits `2` if missing (lines 1520-1523).
  - Dispatches `send(...)` with extra metadata (`id`, `state`, `host`, `login`, `note`).
  - Exit code: `return 0 if ok else 1`.
- **Test**:
  - `test_ack_high_broadcast_told_then_done` (SOURCED `scripts/dev/test_mts_signal.py:539-556`).
  - `test_high_broadcast_with_cmd_refuses_told_without_note` (SOURCED `scripts/dev/test_mts_signal.py:575-587`).
- **Verdict**: MATCH.

### Clause 4: `asks` command, flags, and exit codes
- **Docstring**: SOURCED `scripts/dev/mts_signal.py:40-41`:
  `Past the deadline unanswered: the first hook or asks run that sees it escalates ONCE (kind esc)...; asks [--json] and status_board.py list it as OVERDUE with age.`
- **Code**:
  - Defined in `main()` at SOURCED `scripts/dev/mts_signal.py:1418-1435`.
  - Checks origin; exits `1` if absent.
  - Automatically runs `escalate(rows)` on loaded signals, printing any newly escalated asks (lines 1424-1425).
  - Calls `ask_rows(load(h))`.
  - If `--json` is in `argv`, prints `json.dumps(res)` and returns `0` (lines 1427-1429).
  - Otherwise prints formatted summary for each open ask (id, from, to, state, overdue status, age, deadline, escalation, text snippet).
  - If no open asks, prints `"no open asks"` (line 1434).
  - Exit code: `return 0`.
- **Test**:
  - `test_asks_listing_and_escalation` (SOURCED `scripts/dev/test_mts_signal.py:734-750`).
  - `test_asks_json_output` (SOURCED `scripts/dev/test_mts_signal.py:752-763`).
- **Verdict**: MATCH.

### Clause 5: `pending` command, flags, and exit codes
- **Docstring**: SOURCED `scripts/dev/mts_signal.py:27-28`:
  `python scripts/dev/mts_signal.py pending [--host <h>] [--json]   HIGH broadcasts needing action on a host (state none, or told expired) with hours waiting`
- **Code**:
  - Defined in `main()` at SOURCED `scripts/dev/mts_signal.py:1473-1493`.
  - Arguments: `--host` (default `""`), `--json` (action `store_true`).
  - Checks origin; exits `1` if absent.
  - Determines target host list: `[hosts.key(a.host)]` if provided, else all active hosts plus current host (line 1484).
  - Evaluates `pending(rows, t)` for each host.
  - If `--json`, outputs serialized JSON (line 1487).
  - Otherwise prints line per pending broadcast: id, host, state, waiting hours, blocker note.
  - If none pending, prints `"nothing pending"` (line 1492).
  - Exit code: `return 0`.
- **Test**:
  - `test_pending_lists_hosts_needing_action` (SOURCED `scripts/dev/test_mts_signal.py:558-573`).
- **Verdict**: MATCH.

### Clause 6: `broadcast` command, flags, and exit codes
- **Docstring**: SOURCED `scripts/dev/mts_signal.py:18, 45-46`:
  `python scripts/dev/mts_signal.py broadcast "<text>" --prio high --cmd "<exact operator command>"`
  `python scripts/dev/mts_signal.py broadcast "<message>"   a signal every other session shows on its NEXT turn`
- **Code**:
  - Defined in `main()` at SOURCED `scripts/dev/mts_signal.py:1436-1465`.
  - Arguments: `message`, `--to` (default `"all"`), `--prio` (default `"normal"`, choices `["normal", "high"]`), `--audience` (default `"all"`, choices `["all", "top"]`), `--cmd` (default `""`), `--wait` (float, default 0).
  - If `--prio high`, constructs unique id `b-<sha1[:6]>` and populates `extra={"id": bid, "prio": "high", "cmd": clean(a.cmd, CMD_MAX)}` (lines 1448-1452).
  - Sends broadcast via `send(a.message, to=a.to, kind="broadcast", extra=extra)`.
  - Exit code: `return 0 if ok else 1` (line 1465).
- **Test**:
  - `test_high_broadcast_lifecycle_and_hooks` (SOURCED `scripts/dev/test_mts_signal.py:515-537`).
  - `test_broadcast_audience_top` (SOURCED `scripts/dev/test_mts_signal.py:646-670`).
- **Verdict**: MATCH.

### Clause 7: `ask` command, flags, and exit codes
- **Docstring**: SOURCED `scripts/dev/mts_signal.py:35-39`:
  `python scripts/dev/mts_signal.py ask "<text>" --to <host|A|B|C|all> [--type ask|resend|task] [--wait M] [--due M]`
- **Code**:
  - Defined in `main()` at SOURCED `scripts/dev/mts_signal.py:1402-1417`.
  - Arguments: `text`, `--to` (default `"all"`), `--type` (default `"ask"`, choices `ASK_TYPES`), `--wait` (int), `--due` (int), `--wait-reply` (float, default 0).
  - Calls `new_ask(a.text, to=a.to, typ=a.type, wait=a.wait, due=a.due)`.
  - Prevents re-asks within wait window.
  - Exit codes: returns `0` on successful send; `3` if re-ask was refused because another active ask exists; `1` on push failure or invalid target.
- **Test**:
  - `test_ask_and_ack_workflow` (SOURCED `scripts/dev/test_mts_signal.py:680-705`).
  - `test_ask_duplicate_refused_within_wait` (SOURCED `scripts/dev/test_mts_signal.py:707-732`).
- **Verdict**: MATCH.

### Clause 8: `acks` command, flags, and exit codes
- **Docstring**: SOURCED `scripts/dev/mts_signal.py:30-31`:
  `python scripts/dev/mts_signal.py acks [<id>]   hosts seen in the last KEEP_DAYS vs none/told/done; no id = all open high broadcasts.`
- **Code**:
  - Defined in `main()` at SOURCED `scripts/dev/mts_signal.py:1527-1543`.
  - Checks origin; exits `1` if absent.
  - Extracts optional broadcast id from `argv[1]`.
  - If `want` id specified, checks only that broadcast in `high_open(rows)`; otherwise gathers all open high broadcasts where any target is not terminal.
  - Lists each broadcast and reports ack state (`none`, `told`, `expired`, `done`) along with blocker note for all active target hosts.
  - Prints `"no such broadcast"` (if specific ID was passed) or `"no open HIGH broadcasts"` if empty (line 1542).
  - Exit code: `return 0`.
- **Test**:
  - `test_ack_high_broadcast_told_then_done` (SOURCED `scripts/dev/test_mts_signal.py:539-556`).
  - `test_acks_cli_output` (SOURCED `scripts/dev/test_mts_signal.py:623-644`).
- **Verdict**: MATCH.
