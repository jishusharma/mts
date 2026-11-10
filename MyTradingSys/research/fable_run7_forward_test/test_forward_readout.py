"""Tests for forward_readout.py: one fixture log per state (fixtures are generated into tmp_path from the
R series below, in the trade_ledger.jsonl row format). Fixtures only; no live files."""
from __future__ import annotations

import json
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import forward_readout as fr  # noqa: E402

KROWN = "layer:krown:s8_break:4h"
MALKAN = "layer:rsi:malkan_level_short:4h"
T06 = "layer:rsi:rsi_ma_cross:4h"


def rows(source, account, rs, start_day=1, per_day=1, risk=10.0):
    """Ledger rows (trade_ledger.build_row shape) with net_pnl_usd = r * risk_usd, one per UTC day."""
    out = []
    for i, r in enumerate(rs):
        d = date(2026, 12, 1) + timedelta(days=start_day - 1 + i // per_day)
        out.append({"source": source, "account": account, "plan_id": f"{source[-8:]}-{i}",
                    "entry": {"price": 100.0, "amount": 100, "ts": d.isoformat() + "T00:00:00Z"},
                    "net_pnl_usd": round(r * risk, 6), "risk_usd": risk, "exit_reason": "target"})
    return out


def write(tmp_path, rs_rows, name="ledger.jsonl"):
    p = tmp_path / name
    p.write_text("\n".join(json.dumps(r) for r in rs_rows) + "\n", encoding="utf-8")
    return p


def state_of(tmp_path, slot_rows, slot_key="krown_s8", asof="2027-01-20"):
    res = fr.readout(write(tmp_path, slot_rows), asof=asof)
    return {r["slot"]: r for r in res["slots"]}[slot_key]


def test_running_few_trades(tmp_path):
    r = state_of(tmp_path, rows(KROWN, "krown_s8", [1.9, -1, -1, 1.9, -1]))
    assert r["state"] == "RUNNING" and r["n"] == 5


def test_fail_a_exactly_12r_not_11_9(tmp_path):
    # drawdown from peak 0: eleven -1 R then -0.9 R = 11.9 -> still running; -1 R last = 12.0 -> FAIL-A
    # (a +0.5 breaks the losing streak so FAIL-B cannot fire first)
    base = [-1.0] * 6 + [0.5] + [-1.0] * 5
    r = state_of(tmp_path, rows(KROWN, "krown_s8", base + [-1.4]))
    # (E- already KILLs this series: the point here is only that FAIL-A needs the full 12.0 R)
    assert r["dd_r"] < 12 and r["state"] != "FAIL-A"
    r = state_of(tmp_path, rows(KROWN, "krown_s8", base + [-1.5]))
    assert r["state"] == "FAIL-A"


def test_fail_b_streak_12(tmp_path):
    # wins of +0.5 keep drawdown under 12 R is impossible with 12 -0.3: use small losers
    pre = [1.0, 1.0]
    r = state_of(tmp_path, rows(KROWN, "krown_s8", pre + [-0.3] * 11))
    assert r["streak"] == 11 and r["state"] == "RUNNING"
    r = state_of(tmp_path, rows(KROWN, "krown_s8", pre + [-0.3] * 12))
    assert r["streak"] == 12 and r["state"] == "FAIL-B"


def test_fail_c_n30_upper_bound_negative(tmp_path):
    # alternate 0 / -0.5: mean -0.25, tiny SE, never 12 streak, DD < 12 -> FAIL-C at n=30 and not at 29
    rs = [0.0 if i % 2 == 0 else -0.5 for i in range(30)]
    # kill (E-) must not fire first: keep e-kill below 10 by checking state is FAIL-C explicitly
    r30 = state_of(tmp_path, rows(KROWN, "krown_s8", rs))
    assert r30["state"] == "FAIL-C"
    r29 = state_of(tmp_path, rows(KROWN, "krown_s8", rs[:29]))
    assert r29["state"] != "FAIL-C"


def test_promote(tmp_path):
    rs = ([1.9, -1.0, 1.9, 1.9, -1.0, 1.9] * 8)[:48]      # mean ~ +0.9 R
    r = state_of(tmp_path, rows(MALKAN, "paper", rs), "malkan_level_short")
    assert r["state"] == "PROMOTE" and r["e_plus"] >= 80 and r["n"] >= 30


def test_kill_by_e_minus_not_krown_rule(tmp_path):
    # paper slot: no A/B/C rules; steady loser -> KILL once E- >= 10 (n >= 10)
    rs = [-1.0, 0.2] * 10
    r = state_of(tmp_path, rows(T06, "paper", rs), "t06_rsi_ma")
    assert r["state"] == "KILL" and r["e_minus"] >= 10


def test_retire_at_150_undecided(tmp_path):
    # mean ~ +0.1: neither promoted nor killed; 150 clusters
    rs = [1.1, -1.0, -0.9, 1.0, 0.2] * 30
    r = state_of(tmp_path, rows(T06, "paper", rs), "t06_rsi_ma", asof="2027-06-01")
    assert r["state"] == "RETIRE"


def test_retire_after_12_months(tmp_path):
    rs = rows(T06, "paper", [1.0, -1.0, 1.0])
    r = state_of(tmp_path, rs, "t06_rsi_ma", asof="2027-12-20")
    assert r["state"] == "RETIRE"


def test_other_account_krown_is_contaminated_and_excluded(tmp_path):
    rs = rows(KROWN, "krown_s8", [1.0, -1.0]) + rows(KROWN, None, [-1.0] * 20)
    res = fr.readout(write(tmp_path, rs), asof="2027-01-20")
    k = {r["slot"]: r for r in res["slots"]}["krown_s8"]
    assert k["n"] == 2 and res["contaminated"] == 20


def test_unresolved_rows_counted_not_scored(tmp_path):
    rs = rows(KROWN, "krown_s8", [1.0]) + [{"source": KROWN, "account": "krown_s8", "plan_id": "x",
                                           "net_pnl_usd": None, "unresolved": "exchange read failed"}]
    res = fr.readout(write(tmp_path, rs), asof="2027-01-20")
    assert res["unresolved"] == 1 and {r["slot"]: r for r in res["slots"]}["krown_s8"]["n"] == 1


def test_matches_sim_sequential_math(tmp_path):
    import numpy as np
    sim = fr.load_sim()
    rs = [1.9, -1.0, 0.5, -1.0, 1.9, -1.0, -1.0, 1.9, 1.9, -1.0]
    r = state_of(tmp_path, rows(KROWN, "krown_s8", rs))
    assert abs(r["e_plus"] - float(sim.e_promote(np.array(rs))[0, -1])) < 1e-9
    assert abs(r["e_minus"] - float(sim.e_kill(np.array(rs))[0, -1])) < 1e-9


def test_markdown_table_has_every_slot_and_columns(tmp_path):
    p = write(tmp_path, rows(KROWN, "krown_s8", [1.0, -1.0]))
    md = fr.to_markdown(fr.readout(p, asof="2027-01-20"))
    head = "| slot | n | mean R | SE | DD R | streak | E+ | E- | state |"
    assert head in md
    for s in ("krown_s8", "malkan_level_short", "t06_rsi_ma"):
        assert s in md


def test_same_day_trades_pool_into_one_observation(tmp_path):
    # two trades same UTC day (BTC+ETH pair) = one e-process observation, but n counts trades
    rs = rows(T06, "paper", [1.0, -1.0, 1.0, 1.0], per_day=2)
    r = state_of(tmp_path, rs, "t06_rsi_ma")
    assert r["n"] == 4 and r["n_obs"] == 2
