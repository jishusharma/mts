"""Context-only forward logger around build_auction_trade_plan (2 setups: failed_auction_reclaim, va_acceptance_continuation).

No gate, no order, no exchange write, no process start. It appends one JSONL row per event and simulates the
maker-limit trade on supplied bars only (a decision at bar t uses bars <= t; fills/management use bars after t, passed in
by the caller as they close). Net R uses FEES_DERIBIT from MyTradingSys/backtest/fees.py (no own fee literal).

Labels: SOURCED = taken from a cited source; OURS = our choice, to be tested.
  RANGE_LO/RANGE_HI 75,400-80,900   SOURCED  MyTradingSys/research/mts_bible/BIBLE.md:28
  KILL_N = 30 gate-pass fades, net R <= 0 stops the run   SOURCED  REVIEW_FABLE.md d (null -0.087 R)
  entry = maker limit at the level  SOURCED TOM-005
  WAIT_BARS = 3, MIN_TARGET_R = 2.5, BE at +1R, half off at POC, MAX_HOLD_BARS = 48, session blocks, stop buffer 5 bps  OURS
  Fades counted by the kill rule = filled gate-pass failed_auction_reclaim rows  OURS (DECISION)
  Conservative bar order  OURS: stop checked before target; no management on the fill bar; BE applies from next bar.
Output path is gitignored runtime data (runtime/ next to this file); never commit it.
"""
import importlib.util
import json
import sys
from itertools import islice
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))
from MyTradingSys.backtest.fees import FEES_DERIBIT  # noqa: E402

_ac_path = _REPO / "MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py"
_spec = importlib.util.spec_from_file_location("auction_context_fwd", _ac_path)
_ac = importlib.util.module_from_spec(_spec)
sys.modules["auction_context_fwd"] = _ac
_spec.loader.exec_module(_ac)

RANGE_LO = 75400.0
RANGE_HI = 80900.0
KILL_N = 30
WAIT_BARS = 3
MIN_TARGET_R = 2.5
MAX_HOLD_BARS = 48
FEE_RT_BPS = (FEES_DERIBIT["entry"] + FEES_DERIBIT["stop"]) * 10000.0  # maker entry + taker stop, worst case
DEFAULT_PATH = Path(__file__).resolve().parent / "runtime" / "events.jsonl"


def session_block(ts_ms):
    h = (int(ts_ms) // 3600000) % 24
    return "asia" if h < 7 else "london" if h < 12 else "ny" if h < 21 else "late"


def simulate_trade(plan, bars_after, half_price=None, target_price=None, wait_bars=WAIT_BARS,
                   max_hold=MAX_HOLD_BARS, fees=FEES_DERIBIT):
    d = 1 if plan["direction"] == "long" else -1
    entry, stop = float(plan["entry"]), float(plan["structural_stop"])
    risk = abs(entry - stop)
    fill_i = None
    for i, b in enumerate(bars_after[:wait_bars]):
        if (d == 1 and b["l"] <= entry) or (d == -1 and b["h"] >= entry):
            fill_i = i
            break
    if fill_i is None:
        return {"filled": False, "exit_reason": "no_fill", "net_r": 0.0}
    gross, fee, rem, be, half_done = 0.0, fees["entry"] * entry / risk, 1.0, False, False
    reason = "open"
    managed = list(islice(bars_after, fill_i + 1, fill_i + 1 + max_hold))  # bars after the fill bar, supplied as they close

    def reached(b, p):
        return b["h"] >= p if d == 1 else b["l"] <= p

    for b in managed:
        if (d == 1 and b["l"] <= stop) or (d == -1 and b["h"] >= stop):
            gross += rem * d * (stop - entry) / risk
            fee += rem * fees["stop"] * stop / risk
            reason, rem = ("be_stop" if be else "stop"), 0.0
            break
        if half_price and not half_done and reached(b, half_price):
            gross += 0.5 * d * (half_price - entry) / risk
            fee += 0.5 * fees["target"] * half_price / risk
            rem, half_done = 0.5, True
        if target_price and reached(b, target_price):
            gross += rem * d * (target_price - entry) / risk
            fee += rem * fees["target"] * target_price / risk
            reason, rem = "target", 0.0
            break
        if not be and reached(b, entry + d * risk):
            stop, be = entry, True
    if rem > 0.0:
        if len(managed) < max_hold:
            return {"filled": True, "exit_reason": "open", "net_r": None}
        c = managed[-1]["c"]
        gross += rem * d * (c - entry) / risk
        fee += rem * fees["timeout"] * c / risk
        reason = "timeout"
    return {"filled": True, "exit_reason": reason, "net_r": gross - fee}


def build_event_row(context, interaction, entry_price, targets, bars_after, ts_ms, level_family,
                    delta=None, stop_buffer_bps=5.0):
    plan = _ac.build_auction_trade_plan(context, interaction, entry_price, targets, stop_buffer_bps=stop_buffer_bps,
                                        fee_rt_bps=FEE_RT_BPS, min_net_rr=MIN_TARGET_R)
    row = {
        "ts_ms": int(ts_ms), "session": session_block(ts_ms), "level_family": level_family,
        "setup_type": plan.get("setup_type"), "action": plan["action"], "gate_pass": plan["action"] == "TAKE_TRADE",
        "htf_bias": plan.get("htf_bias", context.get("htf_bias")),
        "with_htf": (plan.get("sizing_tier") == "full_with_htf") if plan["action"] == "TAKE_TRADE" else False,
        "delta": delta if delta is not None else interaction.get("delta"),
        "fee_r": plan.get("fee_r"), "filled": False, "exit_reason": "no_trade", "net_r": 0.0,
    }
    if row["gate_pass"]:
        tgt = plan["primary_target"]["price"]
        half = next((p for n, p in targets if n == "POC" and (p - entry_price) * (1 if plan["direction"] == "long" else -1) > 0
                     and (tgt - p) * (1 if plan["direction"] == "long" else -1) > 0), None)
        row.update(simulate_trade(plan, bars_after, half_price=half, target_price=tgt))
        row["entry"], row["stop"], row["target"] = plan["entry"], plan["structural_stop"], tgt
    return row


def append_row(path, row):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")


def kill_check(rows):
    fades = [r for r in rows if r.get("gate_pass") and r.get("filled") and r.get("setup_type") == "failed_auction_reclaim"
             and r.get("net_r") is not None]
    net = sum(r["net_r"] for r in fades)
    return {"gate_pass_fades": len(fades), "net_r": net, "killed": len(fades) >= KILL_N and net <= 0.0}


def range_ended(daily_closes):
    return any(c < RANGE_LO or c > RANGE_HI for c in daily_closes)


def main(argv):
    p = Path(argv[1]) if len(argv) > 1 else DEFAULT_PATH
    rows = [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()] if p.exists() else []
    k = kill_check(rows)
    print(f"gate-pass fades {k['gate_pass_fades']}/{KILL_N}  net R {k['net_r']:.3f}  killed={k['killed']}")
    return 1 if k["killed"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
