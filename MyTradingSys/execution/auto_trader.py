"""Auto-trader for Deribit TESTNET: turns live signals into plans and trades them with the existing tools.

Operator order 2026-09-29: "start trading now on test-net based on what we have functional, and on every build
launch fresh trades for newly built layers." This is an ORCHESTRATOR only. Every order goes through the same gated
path the operator uses by hand:
    new_plan.py --yes  ->  executor.py <plan> --go  ->  position_manager.py <plan_id>
so the HALT files, the R8 one-position preflight, the account cap and the fail-closed paths all still apply.
It never talks to the exchange itself and has no mainnet path (the executor is testnet-only).

Signal sources (read-only):
  - Tom core: runtime_data/last_alert.json (verdict SETUP_FORMING / SETUP_CONFIRMED, with ENTRY/STOP/TARGET).
  - Indicator layers: MyTradingSys/runtime/alerts/<tf>.jsonl written by the live alert runner. Any NEW layer that
    the runner emits is picked up automatically if its event maps to a side (config "layer_rules", or a "side"
    field on the alert). Unknown layer/event pairs are logged as "unmapped" so the supervisor can add a rule.
Priority when several signals are new: Tom first, then layers in arrival order. One trade at a time (the account
has one BTC-PERPETUAL position); signals that arrive while a trade is open are logged as skipped_busy, so every
layer still gets a signal count for later scoring.

Every decision is appended to MyTradingSys/execution/auto_trades.jsonl (source, signal, plan_id, outcome).
Usage (repo root):  python -m MyTradingSys.execution.auto_trader [--once] [--dry-run] [--poll-seconds 20]
Stop it with Ctrl+C or by creating execution/HALT (mts pause); it then trades nothing until the brake is removed.
To pause ONLY the auto-trader (e.g. while a testnet suite needs a flat account), create execution/AUTO_PAUSE.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
HALT = HERE / "HALT"
HALT_DAILY_LOSS = HERE / "HALT_DAILY_LOSS"
# Auto-trader-only pause: no new auto-trades, but no HALT (so manual trades and the testnet suites still run).
AUTO_PAUSE = HERE / "AUTO_PAUSE"
STATE_PATH = HERE / "auto_trader_state.json"
LOG_PATH = HERE / "auto_trades.jsonl"
MANAGER_LOG_DIR = HERE / "journal" / "auto_manager_logs"
OPERATOR_ALERTS = HERE / "OPERATOR_ALERTS.log"
MAX_RESPAWNS = 3   # position_manager respawns per plan when it exits while the exchange still shows a position
TOM_ALERT = REPO / "runtime_data" / "last_alert.json"
LAYER_ALERT_DIR = REPO / "MyTradingSys" / "runtime" / "alerts"

TF_SECONDS = {"1m": 60, "5m": 300, "15m": 900, "30m": 1800, "1h": 3600, "4h": 14400, "1d": 86400}

DEFAULT_CONFIG = {
    # Tom core: limit at the zone, stop/target from the alert, whole size off at the target.
    "tom": {"enabled": True, "size_usd": 200, "max_loss_usd": 25, "hours": 1.0, "max_hold_minutes": None, "max_hold_bars": 8, "max_age_seconds": 300,
            "verdicts": ["SETUP_FORMING", "SETUP_CONFIRMED"], "min_net_rr": 2.0},
    # Layers have no stop/target of their own: fixed bracket, market entry, small size.
    "layers": {"enabled": True, "size_usd": 100, "max_loss_usd": 10, "stop_pct": 1.0, "targets": "2",
               "hours": 2.0, "max_age_bars": 1.2,
               "max_hold_bars": 8},   # time exit = 8 bars of the signal timeframe (minutes derived per alert tf)
    # (layer, event) -> side. "direction" means: up -> long, down -> short. A "side" field on the alert wins.
    "layer_rules": {
        "rsi:support": "long",
        "rsi:rejection": "short",
        "rsi:cross": "direction",
    },
    "disabled_layers": [],
    # source prefix -> named testnet account (credentials .secrets/testnet_<label>.secret.json).
    # Missing file -> shared default slot, exactly as before.
    "accounts": {"layer:fabio:": "fabio"},
}
SECRETS_DIR = HERE / ".secrets"
_warned_missing = set()


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def log(event: dict, path: Path = None) -> None:
    event = {"ts": now_utc().strftime("%Y-%m-%dT%H:%M:%SZ"), **event}
    with open(path or LOG_PATH, "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(event) + "\n")
    print(json.dumps(event), flush=True)


def load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def save_json(path: Path, data) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8", newline="\n")
    tmp.replace(path)


# ---------------------------------------------------------------- Tom core signal

CARD_FIELD = re.compile(r"^(VERDICT|TIME|SETUP|ZONE|ENTRY|STOP|TARGET|R:R):\s*(.*)$", re.M)
ALERT_NO = re.compile(r"#(\d+)")


def parse_tom_alert(alert: dict) -> dict:
    """Return {'alert_no','verdict','time','setup','side','entry','stop','target','net_rr'} or {} if unusable."""
    card = alert.get("card_text") or ""
    fields = {k: v.strip() for k, v in CARD_FIELD.findall(card)}
    m = ALERT_NO.search(alert.get("title") or "")
    try:
        entry, stop, target = float(fields["ENTRY"]), float(fields["STOP"]), float(fields["TARGET"])
    except (KeyError, ValueError):
        return {}
    setup = fields.get("SETUP", "")
    side = "long" if setup.endswith("_long") else "short" if setup.endswith("_short") else None
    rr = re.search(r"net\s+([0-9.]+)", fields.get("R:R", ""))
    zm = re.match(r"(\d+[mhd])_", fields.get("ZONE", ""))
    return {"alert_no": int(m.group(1)) if m else None, "verdict": fields.get("VERDICT", ""),
            "zone_tf": zm.group(1) if zm and zm.group(1) in TF_SECONDS else None,
            "time": fields.get("TIME", ""), "setup": setup, "side": side, "entry": entry, "stop": stop,
            "target": target, "net_rr": float(rr.group(1)) if rr else None}


def tom_signal(alert: dict, state: dict, cfg: dict, now: datetime):
    """New, fresh, actionable Tom alert -> order signal; else None. Marks the alert as seen in state."""
    c = cfg["tom"]
    if not c["enabled"] or not alert:
        return None
    p = parse_tom_alert(alert)
    if not p or p["alert_no"] is None or p["alert_no"] <= state.get("tom_last_alert_no", -1):
        return None
    state["tom_last_alert_no"] = p["alert_no"]
    reject = None
    if p["verdict"] not in c["verdicts"]:
        reject = f"verdict {p['verdict']}"
    elif p["side"] is None:
        reject = f"unknown setup side {p['setup']!r}"
    elif p["net_rr"] is not None and p["net_rr"] < c["min_net_rr"]:
        reject = f"net_rr {p['net_rr']} < {c['min_net_rr']}"
    else:
        try:
            t = datetime.strptime(p["time"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            if (now - t).total_seconds() > c["max_age_seconds"]:
                reject = f"stale alert ({int((now - t).total_seconds())} s old)"
        except ValueError:
            reject = f"bad TIME {p['time']!r}"
    if not reject:
        wrong_side = (p["side"] == "long" and not (p["stop"] < p["entry"] < p["target"])) or \
                     (p["side"] == "short" and not (p["target"] < p["entry"] < p["stop"]))
        if wrong_side:
            reject = "entry/stop/target not ordered for the side"
    sig = {"source": "tom", "key": f"tom#{p['alert_no']}", "side": p["side"], "detail": p}
    if reject:
        sig["reject"] = reject
        return sig
    stop_pct = round(abs(p["entry"] - p["stop"]) / p["entry"] * 100, 3)
    tgt_pct = round(abs(p["target"] - p["entry"]) / p["entry"] * 100, 3)
    sig["plan_args"] = ["--side", p["side"], "--entry", "limit", "--price", f"{p['entry']}",
                        "--size", str(c["size_usd"]), "--stop", f"{stop_pct}", "--targets", f"{tgt_pct}",
                        "--max-loss", str(c["max_loss_usd"]), "--hours", str(c["hours"])]
    if c.get("max_hold_minutes"):
        sig["plan_args"] += ["--max-hold-minutes", str(c["max_hold_minutes"])]
    elif c.get("max_hold_bars"):   # time exit = N bars of the alert's zone timeframe (5m/15m/1h); 15m if unknown
        tf_s = TF_SECONDS[p.get("zone_tf") or "15m"]
        sig["plan_args"] += ["--max-hold-minutes", f"{c['max_hold_bars'] * tf_s / 60:g}"]
    return sig


# ---------------------------------------------------------------- layer signals

def layer_side(alert: dict, cfg: dict):
    """Side for a layer alert, or None if no rule maps it."""
    if alert.get("side") in ("long", "short"):
        return alert["side"]
    rule = cfg["layer_rules"].get(f"{alert.get('layer')}:{alert.get('event')}")
    if rule == "direction":
        return {"up": "long", "down": "short"}.get(alert.get("direction"))
    return rule if rule in ("long", "short") else None


def read_new_layer_alerts(state: dict, alert_dir: Path = None) -> list:
    """New JSONL lines since the stored byte offset of each file. First sight of a file = start at its end."""
    alert_dir = alert_dir or LAYER_ALERT_DIR
    offsets = state.setdefault("layer_offsets", {})
    out = []
    for f in sorted(alert_dir.glob("*.jsonl")):
        size = f.stat().st_size
        off = offsets.get(f.name)
        if off is None or off > size:        # new file or truncated/rotated: don't replay history
            offsets[f.name] = size
            continue
        with open(f, "rb") as fh:
            fh.seek(off)
            chunk = fh.read(size - off)
        complete = chunk.rsplit(b"\n", 1)[0] if b"\n" in chunk else b""
        offsets[f.name] = off + (len(complete) + 1 if complete else 0)
        for line in complete.decode("utf-8", errors="replace").splitlines():
            try:
                out.append(json.loads(line))
            except ValueError:
                continue
    return out


def layer_signal(alert: dict, cfg: dict, now: datetime) -> dict:
    c = cfg["layers"]
    layer, tf = alert.get("layer"), alert.get("tf")
    event = alert.get("event") or alert.get("kind") or alert.get("sub")
    key = f"{layer}:{alert.get('sub')}:{event}:{tf}:{alert.get('t_close')}"
    sig = {"source": f"layer:{layer}:{alert.get('sub')}:{tf}", "key": key, "detail": alert}
    side = layer_side(alert, cfg)
    sig["side"] = side
    if not c["enabled"] or layer in cfg["disabled_layers"]:
        sig["reject"] = "layer disabled"
    elif side is None:
        sig["reject"] = f"unmapped {layer}:{alert.get('event')} (add a layer_rules entry)"
    else:
        t_close = alert.get("t_close")
        bar = TF_SECONDS.get(tf)
        if not isinstance(t_close, (int, float)) or bar is None:
            sig["reject"] = "no t_close/tf"
        else:
            # t_close is the bar's open time in ms (Binance kline convention); the bar closes one tf later.
            # A lagged layer's event is first seen `t_confirm` (latest closed bar) after its own bar: age from that.
            t_seen = alert.get("t_confirm")
            if isinstance(t_seen, (int, float)) and t_seen > t_close:
                t_close = t_seen
            age = now.timestamp() - (t_close / 1000 + bar)
            if age > c["max_age_bars"] * bar:
                sig["reject"] = f"stale ({int(age)} s after bar close)"
    if "reject" not in sig:
        sig["plan_args"] = ["--side", side, "--entry", "market", "--size", str(c["size_usd"]),
                            "--stop", str(c["stop_pct"]), "--targets", c["targets"],
                            "--max-loss", str(c["max_loss_usd"]), "--hours", str(c["hours"])]
        if c.get("max_hold_bars"):
            sig["plan_args"] += ["--max-hold-minutes", f"{c['max_hold_bars'] * bar / 60:g}"]
    return sig


# ---------------------------------------------------------------- trading

def brakes() -> list:
    return [p.name for p in (HALT, HALT_DAILY_LOSS) if p.exists()]


def account_secret_path(label: str) -> Path:
    return SECRETS_DIR / f"testnet_{label}.secret.json"


def account_for(source: str, cfg: dict):
    """Named account for a signal source, or None (default shared slot). Existence check only, never reads the file."""
    for prefix, label in (cfg.get("accounts") or {}).items():
        if source.startswith(prefix):
            if account_secret_path(label).exists():
                return label
            if label not in _warned_missing:
                _warned_missing.add(label)
                log({"event": f"{label}_account_missing", "path": str(account_secret_path(label))})
            return None
    return None


def run(cmd: list, timeout: int = 900, account: str = None) -> tuple:
    env = {**os.environ, "MTS_ACCOUNT": account} if account else {k: v for k, v in os.environ.items() if k != "MTS_ACCOUNT"}
    r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace",
                       timeout=timeout, env=env)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def place(sig: dict, dry_run: bool, account: str = None) -> dict:
    """new_plan -> executor --go -> start position_manager. Returns an outcome dict (never raises)."""
    py = sys.executable
    rc, out = run([py, str(HERE / "new_plan.py"), *sig["plan_args"], "--yes"], timeout=60, account=account)
    m = re.search(r"SAVED (\S+)", out)
    if rc != 0 or not m:
        return {"outcome": "plan_refused", "output": out.strip()[-400:]}
    plan_id = m.group(1)
    plan_file = HERE / "plans" / f"{plan_id}.json"
    if dry_run:
        rc, out = run([py, str(HERE / "executor.py"), str(plan_file)], timeout=60, account=account)
        return {"outcome": "dry_run", "plan_id": plan_id, "rc": rc, "output": out.strip()[-300:]}
    rc, out = run([py, str(HERE / "executor.py"), str(plan_file), "--go"], account=account)
    if rc != 0:
        return {"outcome": "entry_failed", "plan_id": plan_id, "output": out.strip()[-400:]}
    if "no_fill" in out:                     # limit entry that never filled: nothing to manage
        return {"outcome": "no_fill", "plan_id": plan_id, "output": out.strip()[-300:]}
    proc = spawn_manager(plan_id, account)
    return {"outcome": "entered", "plan_id": plan_id, "manager_pid": proc.pid, "proc": proc,
            "output": out.strip()[-300:]}


def spawn_manager(plan_id: str, account: str = None):
    """Start position_manager for plan_id with the account's MTS_ACCOUNT. Returns the Popen."""
    MANAGER_LOG_DIR.mkdir(parents=True, exist_ok=True)
    mlog = open(MANAGER_LOG_DIR / f"{plan_id}.log", "a", encoding="utf-8")
    penv = {**os.environ, "MTS_ACCOUNT": account} if account else {k: v for k, v in os.environ.items() if k != "MTS_ACCOUNT"}
    return subprocess.Popen([sys.executable, str(HERE / "position_manager.py"), plan_id], cwd=REPO, stdout=mlog,
                            stderr=subprocess.STDOUT, env=penv)


def exchange_flat(account: str = None, instrument: str = "BTC-PERPETUAL"):
    """Read-only exchange check for one account: True flat, False position open, None could not be read."""
    prev = os.environ.get("MTS_ACCOUNT")
    try:
        if str(HERE) not in sys.path:
            sys.path.insert(0, str(HERE))
        import deribit_orders as do
        if account:
            os.environ["MTS_ACCOUNT"] = account
        else:
            os.environ.pop("MTS_ACCOUNT", None)
        token = do.authenticate()
        return int(do.get_position(token, instrument).get("size") or 0) == 0
    except Exception:  # noqa: BLE001
        return None
    finally:
        if prev is None:
            os.environ.pop("MTS_ACCOUNT", None)
        else:
            os.environ["MTS_ACCOUNT"] = prev


def operator_alert(msg: str) -> None:
    with open(OPERATOR_ALERTS, "a", encoding="utf-8", newline="\n") as f:
        f.write(f"{now_utc().strftime('%Y-%m-%dT%H:%M:%SZ')} auto_trader {msg}\n")


def settle_slot(slot: dict, acct: str = None) -> bool:
    """True when the slot's trade is closed and the slot may be freed. A manager that exited non-zero frees the slot
    only if the exchange shows the account flat; otherwise it is respawned (max MAX_RESPAWNS) and the slot stays busy."""
    rc = slot["proc"].poll()
    if rc is None:
        return False
    if rc != 0:
        flat = exchange_flat(acct)
        if flat is None:
            slot["flat_check_fails"] = slot.get("flat_check_fails", 0) + 1
            if slot["flat_check_fails"] % 10 == 1:
                log({"event": "manager_exit_unverified", "plan_id": slot["plan_id"], "manager_rc": rc,
                     "account": acct, "note": "exchange position unreadable; slot kept busy"})
            return False
        if flat is False:
            n = slot.get("respawns", 0)
            if n >= MAX_RESPAWNS:
                if not slot.get("alerted"):
                    slot["alerted"] = True
                    log({"event": "manager_lost", "plan_id": slot["plan_id"], "manager_rc": rc, "account": acct,
                         "respawns": n, "action": "operator_alert_slot_busy"})
                    operator_alert(f"OPERATOR: position_manager for {slot['plan_id']} (account {acct or 'default'}) "
                                   f"keeps dying (rc={rc}) and the position is still OPEN; {MAX_RESPAWNS} respawns "
                                   f"used - manage/close it by hand")
                return False
            slot["respawns"] = n + 1
            log({"event": "manager_lost", "plan_id": slot["plan_id"], "manager_rc": rc, "account": acct,
                 "respawn": slot["respawns"], "action": "respawn"})
            try:
                slot["proc"] = spawn_manager(slot["plan_id"], acct)
            except Exception as e:  # noqa: BLE001 - the dead proc stays in the slot, next cycle retries
                log({"event": "respawn_error", "plan_id": slot["plan_id"], "error": repr(e)[:200]})
            return False
    log({"event": "trade_closed", "plan_id": slot["plan_id"], "source": slot["source"], "manager_rc": rc,
         **({"account": acct} if acct else {})})
    record_ledger(slot["plan_id"], slot["source"], acct, rc)
    return True


def record_ledger(plan_id: str, source: str, account, manager_rc) -> None:
    """Outcome ledger row for a closed trade (trade_ledger.py). Never raises: the ledger must not stop the trader."""
    try:
        if str(HERE) not in sys.path:
            sys.path.insert(0, str(HERE))
        import trade_ledger
        row = trade_ledger.record_closed(plan_id, source, account, manager_rc)
        log({"event": "ledger_row", "plan_id": plan_id, "net_pnl_usd": row and row.get("net_pnl_usd"),
             "exit_reason": row and row.get("exit_reason"),
             "account": account, "unresolved": row and row.get("unresolved")})
    except Exception as e:  # noqa: BLE001
        log({"event": "ledger_error", "plan_id": plan_id, "error": repr(e)[:200]})


# ---------------------------------------------------------------- restart recovery (adopt running managers)

ADOPTED_RC = -1   # exit code reported for an adopted manager once it is gone (real rc unknown -> exchange flat check)


class PidProc:
    """Popen-like handle for a manager we did not start: poll() is None while the pid lives, then ADOPTED_RC."""

    def __init__(self, pid: int, alive_fn=None):
        self.pid = pid
        self._alive = alive_fn or pid_alive

    def poll(self):
        return None if self._alive(self.pid) else ADOPTED_RC


class DeadProc:
    """Manager that was not running at restart; settle_slot then applies the exchange flat check / respawn rules."""
    pid = None

    def poll(self):
        return ADOPTED_RC


def pid_alive(pid: int) -> bool:
    if os.name == "nt":
        import ctypes
        k32 = ctypes.windll.kernel32
        h = k32.OpenProcess(0x1000, False, int(pid))    # PROCESS_QUERY_LIMITED_INFORMATION
        if not h:
            return False
        try:
            code = ctypes.c_ulong()
            return bool(k32.GetExitCodeProcess(h, ctypes.byref(code))) and code.value == 259   # STILL_ACTIVE
        finally:
            k32.CloseHandle(h)
    try:
        os.kill(int(pid), 0)
        return True
    except OSError:
        return False


def list_process_cmdlines() -> list:
    """[(pid, commandline)] of all processes (Win32_Process). [] when unavailable."""
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
                            "Get-CimInstance Win32_Process | Select-Object ProcessId,CommandLine | ConvertTo-Json -Compress"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60)
        rows = json.loads(r.stdout or "[]")
        rows = [rows] if isinstance(rows, dict) else rows
        return [(int(x["ProcessId"]), x.get("CommandLine") or "") for x in rows]
    except Exception:  # noqa: BLE001
        return []


def manager_pids(plan_id: str, procs: list) -> list:
    """Pids of python processes running `position_manager.py <plan_id>` (exact plan id token)."""
    pat = re.compile(r'position_manager\.py"?\s+"?' + re.escape(plan_id) + r'"?(\s|$)')
    return sorted(pid for pid, cl in procs
                  if pat.search(cl) and "python" in cl.split("position_manager.py")[0].lower())


def open_plans_from_log(path: Path = None) -> list:
    """trade_attempt outcome=entered without a later trade_closed for the same plan_id. Oldest first."""
    entered, closed = {}, set()
    try:
        lines = (path or LOG_PATH).read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    for line in lines:
        try:
            e = json.loads(line)
        except ValueError:
            continue
        pid = e.get("plan_id")
        if e.get("event") == "trade_attempt" and e.get("outcome") == "entered" and pid:
            entered[pid] = e
            closed.discard(pid)
        elif e.get("event") == "trade_closed" and pid:
            closed.add(pid)
    return [e for pid, e in entered.items() if pid not in closed]


def recover_slots(log_path: Path = None, procs=None, alive_fn=None) -> tuple:
    """Rebuild (active, extra) slots at start from the log + live processes. Account comes from the logged attempt.
    Manager alive -> adopt. Manager dead -> slot with DeadProc: the first cycle's settle_slot does the exchange check
    (open -> respawn per MAX_RESPAWNS, flat -> trade_closed + ledger row). An older open plan of an account that has a
    newer one is closed as superseded (one position per account)."""
    plans = open_plans_from_log(log_path)
    procs = list_process_cmdlines() if procs is None else procs
    active, extra = {}, {}
    for e in reversed(plans):                                  # newest first
        pid, acct = e["plan_id"], e.get("account") or None
        taken = (active if not acct else extra.get(acct))
        pids = manager_pids(pid, procs)
        if taken:
            if pids:
                log({"event": "adopt_skipped", "plan_id": pid, "account": acct, "manager_pids": pids,
                     "note": f"slot already held by {taken['plan_id']}; alert operator"})
                operator_alert(f"OPERATOR: two live managers for account {acct or 'default'}: {pid} and "
                               f"{taken['plan_id']} - check by hand")
            else:
                log({"event": "trade_closed", "plan_id": pid, "source": e.get("source"), "manager_rc": ADOPTED_RC,
                     "note": "superseded_at_restart", **({"account": acct} if acct else {})})
                record_ledger(pid, e.get("source"), acct, ADOPTED_RC)
            continue
        slot = {"proc": PidProc(pids[0], alive_fn) if pids else DeadProc(), "plan_id": pid, "source": e.get("source")}
        log({"event": "adopted", "plan_id": pid, "source": e.get("source"), "account": acct,
             "manager_pid": pids[0] if pids else None, "manager": "alive" if pids else "dead_checking_exchange"})
        if acct:
            extra[acct] = slot
        else:
            active = slot
    return active, extra


def cycle(state: dict, cfg: dict, dry_run: bool, active: dict, now: datetime = None, extra: dict = None) -> dict:
    """One poll. Returns the (possibly new) default-slot trade dict. `active` = {'proc','plan_id','source'} or {}.
    `extra` = {account_label: trade dict}, mutated in place (named-account slots)."""
    now = now or now_utc()
    extra = extra if extra is not None else {}
    for lab in list(extra):
        if settle_slot(extra[lab], lab):
            del extra[lab]
    if active and settle_slot(active, None):
        active = {}
    signals = []
    s = tom_signal(load_json(TOM_ALERT, {}), state, cfg, now)
    if s:
        signals.append(s)
    signals += [layer_signal(a, cfg, now) for a in read_new_layer_alerts(state)]
    halted = brakes()
    for sig in signals:
        base = {"source": sig["source"], "key": sig["key"], "side": sig.get("side")}
        if "reject" in sig:
            log({"event": "signal_rejected", **base, "reason": sig["reject"]})
        elif halted:
            log({"event": "skipped_halt", **base, "brakes": halted})
        elif AUTO_PAUSE.exists():
            log({"event": "skipped_auto_pause", **base})
        else:
            acct = account_for(sig["source"], cfg)
            slot = extra.get(acct) if acct else active
            if slot:
                log({"event": "skipped_busy", **base, "busy_with": slot["plan_id"], "account": acct})
                continue
            res = place(sig, dry_run, acct) if acct else place(sig, dry_run)
            proc = res.pop("proc", None)
            log({"event": "trade_attempt", **base, **res, "account": acct})
            if proc is not None:
                new = {"proc": proc, "plan_id": res["plan_id"], "source": sig["source"]}
                if acct:
                    extra[acct] = new
                else:
                    active = new
    return active


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="build plans and dry-run the executor; place nothing")
    ap.add_argument("--poll-seconds", type=int, default=20)
    ap.add_argument("--config", default=str(HERE / "auto_trader_config.json"))
    a = ap.parse_args(argv)
    cfg = json.loads(json.dumps(DEFAULT_CONFIG))
    for k, v in load_json(Path(a.config), {}).items():
        cfg[k] = {**cfg[k], **v} if isinstance(v, dict) and isinstance(cfg.get(k), dict) else v
    state = load_json(STATE_PATH, {})
    if "tom_last_alert_no" not in state:     # first start: never trade an alert that predates the trader
        p = parse_tom_alert(load_json(TOM_ALERT, {}))
        state["tom_last_alert_no"] = p.get("alert_no") or -1
    log({"event": "start", "dry_run": a.dry_run, "brakes": brakes(), "tom_last_alert_no": state["tom_last_alert_no"]})
    active, extra = recover_slots()
    try:
        while True:
            active = cycle(state, cfg, a.dry_run, active, extra=extra)
            save_json(STATE_PATH, state)
            if a.once:
                return 0
            time.sleep(a.poll_seconds)
    except KeyboardInterrupt:
        log({"event": "stop", "active": active.get("plan_id")})
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
