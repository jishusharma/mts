import sys, hashlib
sys.dont_write_bytecode = True
from pathlib import Path
ROOT = Path(r"C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed")
BACKUP = ROOT / "backup_session"
BACKUP.mkdir(exist_ok=True)
def backup(rel):
    src = ROOT / rel
    (BACKUP / Path(rel).name).write_bytes(src.read_bytes())
def edit(rel, pairs):
    p = ROOT / rel
    backup(rel)
    before = p.read_bytes()
    hb = hashlib.sha256(before).hexdigest()[:8]
    text = before.decode("utf-8")
    for name, anchor, repl in pairs:
        c = text.count(anchor)
        print("  [%s] count=%d" % (name, c))
        if c != 1: raise SystemExit("ABORT %s: %s c=%d" % (rel, name, c))
        text = text.replace(anchor, repl)
    p.write_bytes(text.encode("utf-8"))
    after = p.read_bytes()
    ha = hashlib.sha256(after).hexdigest()[:8]
    na = sum(1 for c in text if ord(c) > 127)
    print("  => %s: %s -> %s, %d -> %d b, nonascii=%d" % (rel, hb, ha, len(before), len(after), na))
print("=== SURFACE_POLICY.md ===")
edit("MyTradingSys/system/SURFACE_POLICY.md", [
 ("cli_reach",
  "| CLI desktop (SUP) | full tree, queue, NUC gate, live processes, testnet, commits | live path, restarts, HALT, promote/merge, commits |",
  "| CLI desktop (SUP) | full tree, queue, live processes, testnet, commits | live path, restarts, HALT, promote/merge, commits |"),
 ("qwen_row",
  "| Qwen NUC | packed files only | implementation and extraction drafts |",
  "| AIBridge (F:\\AIBridge) | allowlisted loopback agent 127.0.0.1:7181, Chrome MV3 extension | PowerShell on desktop, on request from a web AI |"),
 ("handoff_line",
  "SUP: research/fast_track_2026-09-27/SUPERVISOR_INBOX.md. Qwen: queue incoming/. DSA worker: incoming_dsa/.",
  "SUP: research/fast_track_2026-09-27/SUPERVISOR_INBOX.md. AIBridge: F:\\AIBridge\\HANDOFF.md. DSA worker: incoming_dsa/."),
 ("budget_70",
  ">=70% weekly: Opus only for safety diffs; rest to T0, Qwen, DSA, other account.",
  ">=70% weekly: Opus only for safety diffs; rest to T0, DSA, other account."),
 ("budget_95",
  ">=95% or hit: suspend scheduled tasks and builders; live processes run; Qwen and DSA continue",
  ">=95% or hit: suspend scheduled tasks and builders; live processes run; AIBridge and DSA continue"),
 ("lanes",
  "Lanes: qwen-nuc = incoming/; dsaweb-nb = incoming_dsa/; ask-nb = poller. Directories are not renamed.",
  "Lanes: bridge-nb = F:\\AIBridge; dsaweb-nb = incoming_dsa/; ask-nb = poller. Directories are not renamed."),
])
print("=== CLAUDE.md ===")
edit("CLAUDE.md", [
 ("ladder",
  "- T0 script > T1 Qwen on the NUC (`scripts/worker/queue_tool.py pack|verify|status`) > T2 Haiku > T3 Sonnet > T4 Opus.",
  "- T0 script > T1 Haiku > T2 Sonnet > T3 Opus. (Qwen NUC lane decommissioned 2026-10-01; AIBridge on desktop is the run-command surface.)"),
 ("qwen_role",
  "- Qwen: implementations and transcript extractions only. Tests come from Haiku/Sonnet, derived from the spec.",
  "- Implementations go to Sonnet; tests derived from the spec, from Sonnet."),
])
print("=== claude_manager.py ===")
edit("scripts/manager/claude_manager.py", [
 ("remove_qwen_branch",
"""        open_record(p, sid, o["type"], tier, sub)
        if tier == "qwen":  # Qwen NUC lane is packed by the supervisor (queue_tool.py); manager only stages the brief
            p["handoff"].mkdir(parents=True, exist_ok=True)
            (p["handoff"] / (sid + ".md")).write_text(text, encoding="utf-8", newline="\\n")
            rc, tail = "staged", "staged for Qwen queue: Dumps/manager/handoff/%s.md" % sid
        else:
            run[sid] = {"model": tier, "pid": None}; _w(p["running"], run)
            def _on_start(pid, _sid=sid):
                _r = _rw(p["running"], {}); _r[_sid] = {"model": tier, "pid": pid}; _w(p["running"], _r)
            rc, tail = launch(tier, text, runner=runner, on_start=_on_start)
            _r = _rw(p["running"], {}); _r.pop(sid, None); _w(p["running"], _r)
""",
"""        open_record(p, sid, o["type"], tier, sub)
        run[sid] = {"model": tier, "pid": None}; _w(p["running"], run)
        def _on_start(pid, _sid=sid):
            _r = _rw(p["running"], {}); _r[_sid] = {"model": tier, "pid": pid}; _w(p["running"], _r)
        rc, tail = launch(tier, text, runner=runner, on_start=_on_start)
        _r = _rw(p["running"], {}); _r.pop(sid, None); _w(p["running"], _r)
"""),
])
print("=== BUGS.md ===")
edit("MyTradingSys/research/BUGS.md", [
 ("t049_row",
  "| T049 | 2026-09-25 | OPEN | MED | NUC worker v2: self-contained task packages, queue-only share, unattended start | Worker v1 replies 001-003 not grounded in repository files: invented file names (001), false missing-row claim for T048 (003). Per-item doc: MyTradingSys/items/T049_nuc_worker_v2.md. | - |",
  "| T049 | 2026-09-25 | CLOSED | MED | NUC worker v2: self-contained task packages, queue-only share, unattended start | Worker v1 replies 001-003 not grounded in repository files: invented file names (001), false missing-row claim for T048 (003). Per-item doc: MyTradingSys/items/T049_nuc_worker_v2.md. | 2026-10-01: Qwen decommissioned; NUC lane retired. AIBridge on desktop replaces the run-command surface. |"),
 ("b082_row",
  "| B082 | 2026-10-01 | OPEN | MED | Scheduled task MTS-QwenFeeder points at a script that does not exist anywhere | Task C:\\Users\\E-ngineers\\IdeaProjects\\BinanceDataFeed\\scripts\\worker\\qwen_feeder.cmd; file absent from disk, absent from origin/main, absent from origin/cloud/work, absent from all commit history. LastTaskResult=1 on last run 2026-09-29 23:51. Task State=Disabled. Either the .cmd needs writing or the task needs deleting. Per-item doc: MyTradingSys/items/B082_qwen_feeder_missing.md. | - |",
  "| B082 | 2026-10-01 | CLOSED | MED | Scheduled task MTS-QwenFeeder points at a script that does not exist anywhere | Task C:\\Users\\E-ngineers\\IdeaProjects\\BinanceDataFeed\\scripts\\worker\\qwen_feeder.cmd; file absent from disk, absent from origin/main, absent from origin/cloud/work, absent from all commit history. LastTaskResult=1 on last run 2026-09-29 23:51. Task State=Disabled. | 2026-10-01: task deleted; Qwen decommissioned. |"),
])
print("=== INDEX.md ===")
edit("MyTradingSys/items/INDEX.md", [
 ("t049_row",
  "T049 | OPEN    | T049_nuc_worker_v2.md | NUC worker v2 live, restart-proven; phase 5 first citation staged, pending four-step proof",
  "T049 | CLOSED  | T049_nuc_worker_v2.md | Qwen decommissioned 2026-10-01; NUC lane retired; AIBridge replaces run-command surface"),
 ("b082_row",
  "B082 | OPEN    | B082_qwen_feeder_missing.md | MTS-QwenFeeder scheduled task points at a script that does not exist",
  "B082 | CLOSED  | B082_qwen_feeder_missing.md | task deleted; Qwen decommissioned 2026-10-01"),
])
print("=== DSA_HANDOFF.md ===")
edit("Dumps/operator/context/DSA_HANDOFF.md", [
 ("tiers1", "- Routing tiers from tier_of(pct): ok / 70 / 85 / hold / qwen.",
           "- Routing tiers from tier_of(pct): ok / 70 / 85 / hold."),
 ("tiers2", "- Manager tiers: ok / 70 / 85 / hold / qwen.",
           "- Manager tiers: ok / 70 / 85 / hold."),
])
print("=== 03_FILE_INDEX.md ===")
edit("MyTradingSys/system/03_FILE_INDEX.md", [
 ("qt", "| scripts/worker/queue_tool.py | tool | NUC queue, desktop side: packs self-contained tasks with sized context, status, mechanical verify, deploy. T049. |",
        "| scripts/worker/queue_tool.py | tool | SUPERSEDED 2026-10-01: Qwen NUC decommissioned. Historical: NUC queue pack/verify/deploy. T049. |"),
 ("nw", "| scripts/worker/nuc-worker.ps1 | tool | NUC worker v2: Ollama HTTP with per-task context, outbox, heartbeat, requeue after crash, self-update. T049. |",
        "| scripts/worker/nuc-worker.ps1 | tool | SUPERSEDED 2026-10-01: Qwen NUC decommissioned. T049. |"),
 ("nl", "| scripts/worker/nuc-launcher.ps1 | tool | NUC supervisor: installs worker updates from the queue deploy folder, restarts the worker. T049. |",
        "| scripts/worker/nuc-launcher.ps1 | tool | SUPERSEDED 2026-10-01: Qwen NUC decommissioned. T049. |"),
 ("sd", "| scripts/worker/setup-desktop.ps1 | tool | One-time desktop setup: mtsworker account, queue-only share, retires whole-repository share and Everyone grant (ACL backup first). T049. |",
        "| scripts/worker/setup-desktop.ps1 | tool | SUPERSEDED 2026-10-01: Qwen NUC decommissioned. T049. |"),
 ("sn", "| scripts/worker/setup-nuc.ps1 | tool | One-time NUC setup: share credential, local install, scheduled task at sign-in, Ollama and power settings. T049. |",
        "| scripts/worker/setup-nuc.ps1 | tool | SUPERSEDED 2026-10-01: Qwen NUC decommissioned. T049. |"),
 ("td", "| MyTradingSys/items/T049_nuc_worker_v2.md | item | Per-item doc for T049. NUC worker v2 design, decisions, roadmap. |",
        "| MyTradingSys/items/T049_nuc_worker_v2.md | item | Closed 2026-10-01: Qwen NUC decommissioned. Historical design record. |"),
 ("nq", "| Dumps/workers/NUC-QUEUE/README.md | protocol | NUC queue protocol, version 2. Spec format, folders, flow, routing rule. T049. |",
        "| Dumps/workers/NUC-QUEUE/README.md | protocol | SUPERSEDED 2026-10-01: Qwen NUC decommissioned. T049. |"),
 ("dr", "| MyTradingSys/research/fast_track_2026-09-27/nuc_specs/2101-2113 (13 files) | spec | DSA-lane trade-reconstruction specs, one per Fabio/Tom video, template MISSING_PIECES 3.2. |",
        "| MyTradingSys/research/fast_track_2026-09-27/nuc_specs/2101-2113 (13 files) | spec | DSA-lane trade-reconstruction specs (runner-agnostic): one per Fabio/Tom video, template MISSING_PIECES 3.2. |"),
 ("fv", "| MyTradingSys/research/fast_track_2026-09-27/nuc_specs/2201-2203 (3 files) | spec | NUC Qwen specs: fabio_v3_signals.py, fabio_v3_exec.py, fabio_v3.py. |",
        "| MyTradingSys/research/fast_track_2026-09-27/nuc_specs/2201-2203 (3 files) | spec | Runner-agnostic task specs (Qwen decommissioned 2026-10-01): fabio_v3_signals.py, fabio_v3_exec.py, fabio_v3.py. Execute via AIBridge or DSA. |"),
])
print("DONE")