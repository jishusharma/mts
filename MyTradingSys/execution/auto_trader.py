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
import importlib.util
import json
import math
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
# Single source of the net_rr floor: MyTradingSys/system/net_rr_floor.json (MTS_REPO_ROOT is set by run_staged_tests.py).
sys.path.append(str(Path(os.environ.get("MTS_REPO_ROOT") or REPO) / "MyTradingSys" / "runtime"))
from net_rr_floor import NetRrFloorError, load_floor  # noqa: E402
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

TF_SECONDS = {"1m": 60, "3m": 180, "5m": 300, "15m": 900, "30m": 1800, "1h": 3600, "4h": 14400, "1d": 86400}

DEFAULT_CONFIG = {
    # Tom core: limit at the zone, stop/target from the alert. Whole size off at the target, or (R2) the
    # runner_leg_pct share on RUNNER_TARGET when the card carries one.
    # TF5 (EXEC_PROVENANCE_AUDIT H5 E1b, E2): max_hold_minutes is one flat time exit (no zone-TF scaling; None = no
    # time exit) and max_entry_seconds is the limit wait passed to executor --max-entry-seconds. Both NO-SOURCE testnet
    # defaults kept at the values the live path already used (120 = the old 15m fallback, 600 = executor default);
    # MEASURE (operator Ruling 3, pending).
    "tom": {"enabled": True, "size_usd": 200, "max_loss_usd": 25, "hours": 1.0, "max_hold_minutes": 120,
            "max_entry_seconds": 600, "max_age_seconds": 300,
            "verdicts": ["SETUP_FORMING", "SETUP_CONFIRMED"],   # net_rr floor is net_rr_floor.json, not a config key
            # R2: share of size on the runner leg (RUNNER_TARGET); the rest exits at TARGET and the stop moves to
            # breakeven when that first leg fills. NO-SOURCE testnet default (operator Ruling 2, 2026-10-03; BE
            # concept: Fabio P21 "I put my stop loss to break even"). 0 = off = single target, as before.
            "runner_leg_pct": 50},
    # Layers have no stop/target of their own: fixed bracket, market entry, small size. B118: stop_pct, targets, size,
    # hours, max_age_bars and max_hold_bars are NO-SOURCE (no trader quote); bracket_source labels every layer log row
    # SAMPLING (trades exist to sample layer behaviour, the values are not tuned or claimed).
    "layers": {"enabled": True, "size_usd": 100, "max_loss_usd": 10, "stop_pct": 1.0, "targets": "2",
               "bracket_source": "SAMPLING",
               "hours": 2.0, "max_age_bars": 1.2,
               "max_hold_bars": 8},   # time exit = 8 bars of the signal timeframe (minutes derived per alert tf)
    # (layer, event) -> side. "direction" means: up -> long, down -> short; "level" means the side comes from the level
    # crossed (CROSS_SIDE_BY_LEVEL), everything else unmapped. A "side" field on the alert wins.
    "layer_rules": {
        "rsi:support": "long",
        "rsi:rejection": "short",
        "rsi:cross": "level",
    },
    "disabled_layers": [],
    # source prefix -> named testnet account (credentials .secrets/testnet_<label>.secret.json).
    # Missing file -> shared default slot, exactly as before.
    "accounts": {"layer:fabio:": "fabio"},
    # Layer source prefixes that keep emitting alerts (data collection) but never place a trade, with the reason per
    # prefix. Tom ("tom") is never matched. Missing key = nothing blocked; a PRESENT but malformed key, or an unreadable /
    # missing config file, blocks ALL layer trades (fail closed) - see trade_block_reason / load_config.
    "trade_blocklist": [],
    "trade_blocklist_reasons": {},
    # Layer source prefix -> {"size_usd", "max_loss_usd"}; the longest matching prefix replaces the layers size and max
    # loss. Testnet calibration spread (operator 2026-10-07: "Use amounts ranging from 20 to 1000 $"). A malformed
    # entry rejects the signal (no order at a guessed size).
    "size_overrides": {},
    # Promotion pipeline default-deny (fable H1): a source with no promoted_setups.json entry trades only when it starts
    # with a prefix here ({prefix: {"reason", "review_by": "YYYY-MM-DD"}}). Empty = every unregistered source is rejected.
    "pre_pipeline_sources": {},
}
SECRETS_DIR = HERE / ".secrets"
# Promotion registry: repo-root based (MTS_REPO_ROOT is set by run_staged_tests, whose temp copies of this module have
# no sibling files), so a staged copy reads the real registry instead of failing closed.
_ROOT = Path(os.environ.get("MTS_REPO_ROOT") or REPO)
PROMOTED_SETUPS = _ROOT / "MyTradingSys" / "execution" / "promoted_setups.json"
REGISTRY_PY = _ROOT / "MyTradingSys" / "backtest" / "layers" / "promotion" / "registry.py"
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

CARD_FIELD = re.compile(r"^(VERDICT|TIME|PRICE|SETUP|ZONE|ENTRY|STOP|TARGET|RUNNER_TARGET|R:R):\s*(.*)$", re.M)
ALERT_NO = re.compile(r"#(\d+)")


def _positive_float(raw):
    """Card field (RUNNER_TARGET, PRICE) -> positive finite float, or None (absent, 0 = none, or unparsable)."""
    try:
        v = float(raw)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) and v > 0 else None


def parse_tom_alert(alert: dict) -> dict:
    """Return {'alert_no','verdict','time','price','setup','side','entry','stop','target','runner_target','net_rr'}
    or {} if unusable. runner_target is None when the card carries no (valid) RUNNER_TARGET line; price (the
    engine's market read, card PRICE line, PS1 Build-Card) is None when absent or unparsable."""
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
    return {"alert_no": int(m.group(1)) if m else None, "verdict": fields.get("VERDICT", ""),
            "time": fields.get("TIME", ""), "price": _positive_float(fields.get("PRICE")),
            "setup": setup, "side": side, "entry": entry, "stop": stop,
            "target": target, "runner_target": _positive_float(fields.get("RUNNER_TARGET")),
            "net_rr": float(rr.group(1)) if rr else None}


def runner_split(p: dict, c: dict):
    """R2 leg split for a Tom alert -> (targets_arg, None) for 'near@pct,runner@pct', or (None, reason).
    Share of size sent to the runner leg = c['runner_leg_pct'] (NO-SOURCE testnet default 50, operator Ruling 2;
    0 disables). Fails closed to the single-target plan: no runner, runner not beyond TARGET, a leg that
    would floor below the 10 USD contract minimum, or legs that do not sum to the size (TF5 E3: the compiler floors
    each leg to 10 USD on its own, PC:266, so size 30 at 50/50 would leave 10 USD with no target)."""
    pct = c.get("runner_leg_pct") or 0
    if pct <= 0:
        return None, "runner_leg_pct off"
    runner = p.get("runner_target")
    if runner is None:
        return None, "no RUNNER_TARGET"
    beyond = runner > p["target"] if p["side"] == "long" else runner < p["target"]
    if not beyond:
        return None, f"runner {runner} not beyond target {p['target']}"
    size = c["size_usd"]
    near = int(size * (100 - pct) / 100 // 10) * 10       # each leg floored to 10 USD exactly as PC round_size does
    far = int(size * pct / 100 // 10) * 10
    if near < 10 or far < 10:
        return None, f"size {size} too small for a {100 - pct:g}/{pct:g} split"
    if near + far != size:
        return None, f"legs {near}+{far} do not sum to size {size}"
    tgt_pct = round(abs(p["target"] - p["entry"]) / p["entry"] * 100, 3)
    run_pct = round(abs(runner - p["entry"]) / p["entry"] * 100, 3)
    return f"{100 - pct:g}@{tgt_pct},{pct:g}@{run_pct}", None


def net_rr_floor_reject(net_rr: float):
    """None if net_rr clears the floor, else the reject reason. The file is re-read on every alert, so an edit
    applies without restarting the trader; unreadable -> reject (fail closed)."""
    try:
        floor = load_floor()
    except NetRrFloorError as e:
        return f"net_rr floor unreadable: {e}"
    return None if net_rr >= floor else f"net_rr {net_rr} < {floor}"


RT_TAKER_FEE_FRAC = 0.0010   # 2 x Deribit BTC-PERPETUAL taker 5 bp (backtest/fees.py, API-verified 2026-09-26): worst-case round trip


def fee_to_stop_reject(entry: float, stop: float, cut):
    """B146: None if the worst-case round-trip fee is at most `cut` of the stop distance (in R), else the reject reason.
    Off unless tom.max_fee_to_stop is set. Evidence: research/fast_track_2026-09-27/TOM_STOP_WIDTH_2026-10-09.md
    (stops under 0.10 % of price cost 3.8 to 7.6 R of fees per trade; cut 0.3 leaves under 0.3 R). Bad input -> reject."""
    try:
        cut = float(cut)
        dist = abs(float(entry) - float(stop))
        if not (cut > 0 and dist > 0 and float(entry) > 0):
            raise ValueError
    except (TypeError, ValueError):
        return f"fee_to_stop gate misconfigured or zero stop distance (cut {cut!r})"
    ratio = RT_TAKER_FEE_FRAC * float(entry) / dist
    return None if ratio <= cut else f"fee/stop {ratio:.2f} R > {cut:g} R (stop {dist / float(entry) * 100:.3f} % of price)"


def promotion_reject(source: str, cfg: dict, registry_path=None):
    """Reject reason when `source` may not trade under the promotion pipeline, else None. Default-deny, fail closed:
    the registry is re-read on every call (restart safe); unreadable/malformed registry or pre_pipeline_sources
    (including None, set by load_config for an unreadable config) rejects everything, Tom included."""
    try:
        spec = importlib.util.spec_from_file_location("_mts_promotion_registry", REGISTRY_PY)
        reg = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(reg)
        entries, err = reg.load_registry(registry_path or PROMOTED_SETUPS)
        d = reg.decision_for_source(source, None if err else entries, cfg.get("pre_pipeline_sources"))
    except Exception as e:                       # any failure of the gate itself is a rejection, never a pass
        return f"promotion registry error (fail closed): {e!r}"[:200]
    if d == "trade":
        return None
    if d == "shadow":
        return f"collection_only {source} (shadow)"
    if d == "unregistered":
        return "unregistered (promotion pipeline)"
    return "promotion registry error (fail closed): registry or pre_pipeline_sources unreadable/malformed"


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
    elif p["net_rr"] is not None and (rr_reject := net_rr_floor_reject(p["net_rr"])):
        reject = rr_reject
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
    cut = c.get("max_fee_to_stop")
    if not reject and cut is not None:
        reject = fee_to_stop_reject(p["entry"], p["stop"], cut)
    wait = c.get("max_entry_seconds")
    if not reject and not (isinstance(wait, int) and not isinstance(wait, bool) and wait > 0):
        reject = f"bad tom.max_entry_seconds {wait!r}"     # config error: no order rather than a guessed wait
    if not reject:
        reject = promotion_reject("tom", cfg)
    sig = {"source": "tom", "key": f"tom#{p['alert_no']}", "side": p["side"], "detail": p}
    if reject:
        sig["reject"] = reject
        return sig
    stop_pct = round(abs(p["entry"] - p["stop"]) / p["entry"] * 100, 3)
    tgt_pct = round(abs(p["target"] - p["entry"]) / p["entry"] * 100, 3)
    legs, why_single = runner_split(p, c)
    sig["log"] = {"runner_target": p["runner_target"]} if legs else {"runner_skipped": why_single}
    sig["plan_args"] = ["--side", p["side"], "--entry", "limit", "--price", f"{p['entry']}",
                        "--size", str(c["size_usd"]), "--stop", f"{stop_pct}", "--targets", legs or f"{tgt_pct}",
                        "--max-loss", str(c["max_loss_usd"]), "--hours", str(c["hours"])]
    if legs:                                   # R2: stop to breakeven when the first leg fills (position_manager)
        sig["plan_args"].append("--breakeven-after-first-target")
    if c.get("max_hold_minutes"):              # TF5 E2: one flat time exit; the zone name no longer scales it
        sig["plan_args"] += ["--max-hold-minutes", str(c["max_hold_minutes"])]
    sig["executor_args"] = ["--max-entry-seconds", str(c["max_entry_seconds"])]   # TF5 E1b
    sig["venue_price"] = True                  # TF5 E1a: cycle() moves --price onto Deribit before place()
    return sig


def deribit_mark(instrument: str = "BTC-PERPETUAL") -> float:
    """Deribit mark price (public/ticker, no credentials, testnet base by default). Raises on any failure."""
    if str(HERE) not in sys.path:
        sys.path.insert(0, str(HERE))
    import deribit_orders as do
    return do.get_ticker(instrument)["mark_price"]


def apply_venue_price(sig: dict, mark_fn=None):
    """TF5 E1a: the card's zone ENTRY is a Binance-derived price; Deribit trades at a basis to it. Move the limit to
    zone + (Deribit mark - card PRICE). Stop and target stay percentages of the entry, so they move with it.
    Returns None when --price was rewritten (and sig['log'] carries the numbers), else the reject reason.
    Fails closed: no usable card PRICE or an unreadable/invalid mark -> no order."""
    p = sig["detail"]
    if p.get("price") is None:
        return "no card PRICE: venue basis unknown"
    try:
        mark = float((mark_fn or deribit_mark)())
    except Exception as e:  # noqa: BLE001 - any ticker failure refuses the entry
        return f"deribit mark unreadable: {type(e).__name__}: {str(e)[:120]}"
    if not math.isfinite(mark) or mark <= 0:
        return f"deribit mark invalid: {mark!r}"
    basis = mark - p["price"]
    venue_entry = round(p["entry"] + basis, 1)
    a = sig["plan_args"]
    a[a.index("--price") + 1] = f"{venue_entry}"
    sig.setdefault("log", {}).update({"card_entry": p["entry"], "card_price": p["price"], "deribit_mark": mark,
                                      "basis": round(basis, 2), "venue_entry": venue_entry})
    return None


# ---------------------------------------------------------------- layer signals

# (RSI level, cross direction) -> side. MLK-R1 (backtest/layers/rsi/malkan_40_60.py): a bull regime cannot cross 40 downward,
# a bear regime cannot cross 60 upward, so those two crosses are the regime failing. Any other cross has no source: no side.
CROSS_SIDE_BY_LEVEL = {(40.0, "down"): "short", (60.0, "up"): "long"}


def layer_side(alert: dict, cfg: dict):
    """Side for a layer alert, or None if no rule maps it."""
    if alert.get("side") in ("long", "short"):
        return alert["side"]
    rule = cfg["layer_rules"].get(f"{alert.get('layer')}:{alert.get('event')}")
    if rule == "direction":
        return {"up": "long", "down": "short"}.get(alert.get("direction"))
    if rule == "level":
        lv = alert.get("level_value")
        return CROSS_SIDE_BY_LEVEL.get((float(lv), alert.get("direction"))) if isinstance(lv, (int, float)) else None
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


SIZE_CEILING_USD = 10000   # trade_plan_validator.MAX_NOTIONAL_CEILING


def size_override(source: str, cfg: dict):
    """(size_usd, max_loss_usd) from the longest size_overrides prefix matching source, or None. Raises ValueError on
    a malformed table or entry: size a positive 10 USD multiple (Deribit contract) up to the validator ceiling,
    max loss a positive number."""
    table = cfg.get("size_overrides") or {}
    if not isinstance(table, dict):
        raise ValueError("size_overrides is not an object")
    hits = [p for p in table if isinstance(p, str) and p and source.startswith(p)]
    if not hits:
        return None
    v = table[max(hits, key=len)]
    spec = importlib.util.spec_from_file_location("_mts_promotion_registry", REGISTRY_PY)
    reg = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(reg)
    try:
        return reg.size_entry(v, SIZE_CEILING_USD)       # one shared validator with promote.has_testnet_flag (L7)
    except ValueError as e:
        raise ValueError(f"{e} for {max(hits, key=len)}")


def layer_signal(alert: dict, cfg: dict, now: datetime) -> dict:
    c = cfg["layers"]
    layer, tf = alert.get("layer"), alert.get("tf")
    event = alert.get("event") or alert.get("kind") or alert.get("sub")
    # t_close is the bar's OPEN time in ms (Binance kline convention), not its close; the name is kept (operator 2026-10-08).
    key = f"{layer}:{alert.get('sub')}:{event}:{tf}:{alert.get('t_close')}"
    sig = {"source": f"layer:{layer}:{alert.get('sub')}:{tf}", "key": key, "detail": alert}
    sig["log"] = {"bracket_source": c.get("bracket_source", "SAMPLING")}
    side = layer_side(alert, cfg)
    sig["side"] = side
    if not c["enabled"] or layer in cfg["disabled_layers"]:
        sig["reject"] = "layer disabled"
    elif alert.get("collection_only") is True:
        # promotion pipeline: shadow setups (and any alert while the promoted_setups registry is unreadable) never trade;
        # checked before the side so side-less shadow events (fabio v3_grid) are not logged as unmapped
        sig["reject"] = f"collection_only {layer}:{event} (shadow)"
    elif side is None:
        sig["reject"] = f"unmapped {layer}:{event} (add a layer_rules entry)"
    elif (why := promotion_reject(sig["source"], cfg)):
        sig["reject"] = why                      # default-deny: unregistered and not grandfathered, or registry error
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
    size, max_loss = c["size_usd"], c["max_loss_usd"]
    if "reject" not in sig:
        try:
            size, max_loss = size_override(sig["source"], cfg) or (size, max_loss)
        except ValueError as e:
            sig["reject"] = f"bad size_overrides: {e}"
    if "reject" not in sig:
        sig["plan_args"] = ["--side", side, "--entry", "market", "--size", str(size),
                            "--stop", str(c["stop_pct"]), "--targets", c["targets"],
                            "--max-loss", str(max_loss), "--hours", str(c["hours"])]
        if c.get("max_hold_bars"):
            sig["plan_args"] += ["--max-hold-minutes", f"{c['max_hold_bars'] * bar / 60:g}"]
    return sig


# ---------------------------------------------------------------- trading

def brakes() -> list:
    return [p.name for p in (HALT, HALT_DAILY_LOSS) if p.exists()]


def account_secret_path(label: str) -> Path:
    return SECRETS_DIR / f"testnet_{label}.secret.json"


BLOCKLIST_INVALID = "trade_blocklist invalid or config unreadable: all layer trades blocked (fail closed)"


def trade_block_reason(source: str, cfg: dict):
    """Reason string when a LAYER source may not trade, else None. Tom (any source not starting 'layer:') is never
    blocked. Fail closed: a trade_blocklist that is present but not a list of non-empty strings, or reasons that are
    not a dict, blocks every layer source (never silently re-enables a layer that failed its backtest)."""
    if not str(source).startswith("layer:"):
        return None
    bl = cfg.get("trade_blocklist", [])
    reasons = cfg.get("trade_blocklist_reasons", {})
    if (not isinstance(bl, list) or not isinstance(reasons, dict)
            or not all(isinstance(p, str) and p for p in bl)):
        return BLOCKLIST_INVALID
    for prefix in bl:
        if source.startswith(prefix):
            r = reasons.get(prefix)
            return r if isinstance(r, str) and r else "blocklisted (no reason recorded)"
    return None


def load_config(path: Path) -> dict:
    """DEFAULT_CONFIG overlaid with the JSON file. A missing/unparseable/non-object file cannot be trusted to still
    carry the blocklist, so it sets trade_blocklist to None (-> trade_block_reason blocks all layer trades) and logs."""
    cfg = json.loads(json.dumps(DEFAULT_CONFIG))
    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError("config top level is not an object")
    except (OSError, ValueError) as e:
        log({"event": "config_unreadable", "path": str(path), "error": repr(e)[:200],
             "action": "all layer trades blocked (fail closed); Tom unaffected"})
        cfg["trade_blocklist"] = None
        cfg["pre_pipeline_sources"] = None       # promotion_reject: registry_error -> Tom and layers all rejected
        return cfg
    for k, v in raw.items():
        # accounts is an ordered prefix table (first match wins): the file replaces it, never overlays it, or a default
        # key keeps its early position and shadows the file's more specific prefixes (fabio fell to the main slot).
        cfg[k] = ({**cfg[k], **v} if isinstance(v, dict) and isinstance(cfg.get(k), dict) and k != "accounts" else v)
    return cfg


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


def account_secret_missing(source: str, cfg: dict):
    """Label of the named account this source is routed to when its secret file is missing, else None.
    A routed source must never fall back to the main slot (B148): that sent layer trades to MAIN at the override size."""
    for prefix, label in (cfg.get("accounts") or {}).items():
        if source.startswith(prefix):
            return None if account_secret_path(label).exists() else label
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
    rc, out = run([py, str(HERE / "executor.py"), str(plan_file), "--go", *sig.get("executor_args", [])],
                  account=account)
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
        base = {"source": sig["source"], "key": sig["key"], "side": sig.get("side"), **sig.get("log", {})}
        blocked = trade_block_reason(sig["source"], cfg)
        if blocked:
            # Alert already consumed (layer_offsets advance in read_new_layer_alerts, persisted each cycle): no retry.
            log({"event": "layer_trade_blocked", "source": sig["source"], "reason": blocked, "key": sig["key"],
                 "side": sig.get("side")})
        elif "reject" in sig:
            log({"event": "signal_rejected", **base, "reason": sig["reject"]})
        elif halted:
            log({"event": "skipped_halt", **base, "brakes": halted})
        elif AUTO_PAUSE.exists():
            log({"event": "skipped_auto_pause", **base})
        elif account_secret_missing(sig["source"], cfg):
            account_for(sig["source"], cfg)        # logs <label>_account_missing once
            log({"event": "signal_rejected", **base, "reason": "account_secret_missing",
                 "account": account_secret_missing(sig["source"], cfg)})
        else:
            acct = account_for(sig["source"], cfg)
            slot = extra.get(acct) if acct else active
            if slot:
                log({"event": "skipped_busy", **base, "busy_with": slot["plan_id"], "account": acct})
                continue
            if sig.get("venue_price"):           # read the mark only when the order is about to go out
                why = apply_venue_price(sig)
                if why:
                    log({"event": "signal_rejected", **base, "reason": why})
                    continue
                base.update(sig["log"])
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
    cfg = load_config(Path(a.config))
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
