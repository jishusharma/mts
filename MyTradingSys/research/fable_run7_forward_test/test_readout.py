"""Offline tests for readout.py (card krown-s8-forward-weekly-readout) with a planted auto_trades.jsonl + ledger.
Run: python -m pytest MyTradingSys/research/fable_run7_forward_test/test_readout.py -q
Expected numbers are written by hand from FORWARD_PREREG s3 (12 R, 12 losers, n >= 30 and mean + 1.28 SE < 0)."""
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import readout as ro  # noqa: E402

WEEK = datetime(2026, 11, 9, tzinfo=timezone.utc)          # a Monday
SRC = "layer:krown:s8_break:4h"


def ms(dt):
    return int(dt.timestamp() * 1000)


def bar(i):
    """Bar-open ms of the i-th 4h bar of the week (bar 0 opens Monday 00:00)."""
    return ms(WEEK) + i * ro.BAR_MS


def key(t):
    return f"krown:s8_break:S8:4h:{t}"


def ledger(i, r, account="krown_s8", side="long", t=None, risk=100.0, stop=None, exits=None):
    t = bar(i) if t is None else t
    row = {"source": SRC, "account": account, "plan_id": f"p{i}", "alert_key": key(t), "side": side,
           "entry": {"price": 100000.0, "amount": 100, "ts": (WEEK + timedelta(hours=4 * i + 4)).strftime(
               "%Y-%m-%dT%H:%M:%SZ")},
           "risk_usd": risk, "net_pnl_usd": r * risk}
    if stop is not None:
        row["stop"] = stop
    if exits:
        row["exits"] = exits
    return row


def attempt(i, account="krown_s8", t=None, side="long"):
    t = bar(i) if t is None else t
    return {"event": "trade_attempt", "source": SRC, "key": key(t), "side": side, "plan_id": f"p{i}",
            "outcome": "entered", "account": account}


def skip(ev, t, side="long"):
    return {"event": ev, "source": SRC, "key": key(t), "side": side, "account": "krown_s8"}


def run(rs, replay=None, auto=None, extra_ledger=()):
    rows = [ledger(i, r) for i, r in enumerate(rs)]
    return ro.analyse(auto or [], rows + list(extra_ledger), WEEK,
                      replay if replay is not None else [{"t": bar(i), "side": "long", "stop": None} for i in range(len(rs))])


def test_fail_a_at_exactly_12_r_not_11_9():
    # peak starts at 0; a winner between losers keeps the loser streak short, so only FAIL-A can fire
    below = run([-4.0, -4.0, 1.0, -4.9])        # cum -4, -8, -7, -11.9 -> drawdown 11.9
    assert abs(below["dd_r"] - 11.9) < 1e-9 and below["fail"] is None
    at = run([-4.0, -4.0, 1.0, -5.0])           # cum ... -12.0 -> drawdown 12.0
    assert abs(at["dd_r"] - 12.0) < 1e-9 and at["fail"] == "FAIL-A"
    peaked = run([3.0, -5.0, 1.0, -5.0, 1.0, -4.9])   # cum 3,-2,-1,-6,-5,-9.9: peak 3, drawdown 12.9
    assert peaked["fail"] == "FAIL-A"


def test_fail_b_at_12_losers_not_11():
    assert run([0.5] + [-0.1] * 11 + [0.5])["fail"] is None             # 11 small losers then a winner
    res = run([0.5] + [-0.1] * 12)
    assert res["fail"] == "FAIL-B" and res["streak"] == 12


def test_fail_c_at_n30_with_negative_upper_bound():
    neg = [-0.5, 0.2] * 15                      # n 30: mean -0.15, sd ~0.35, SE 0.064, upper -0.07 < 0; no DD/streak hit
    res = run(neg)
    assert res["n"] == 30 and res["fail"] == "FAIL-C" and res["upper90"] < 0
    assert run(neg[:29])["fail"] is None        # n = 29: rule not armed
    pos = [-0.1, 0.2] * 15                      # n 30, mean 0.05: upper bound > 0
    assert run(pos)["fail"] is None


def test_other_account_fill_is_contaminated_and_excluded():
    other = ledger(50, -9.0, account="main", t=bar(50))
    res = run([1.0, 1.0], extra_ledger=[other])
    assert res["n"] == 2 and res["mean"] == 1.0
    assert [c["plan_id"] for c in res["contaminated"]] == ["p50"]
    md = ro.to_markdown(res)
    assert "CONTAMINATED: plan p50 account main" in md


def test_non_replay_entry_is_parity_fail_but_stays_in_a_to_c():
    replay = [{"t": bar(0), "side": "long", "stop": None}]
    rows = [ledger(0, 1.0), ledger(1, -1.0)]    # trade 1 has no replay event
    auto = [attempt(0), attempt(1), skip("skipped_busy", bar(0))]
    res = ro.analyse(auto, rows, WEEK, replay)
    assert res["parity"] == "fail" and res["non_replay"] == ["p1"]
    assert res["n"] == 2 and abs(res["mean"]) < 1e-12 and res["trades"][1]["non_replay"] is True


def test_replay_event_with_skip_row_is_not_a_miss_without_any_row_is():
    replay = [{"t": bar(0), "side": "long", "stop": None}, {"t": bar(3), "side": "short", "stop": None}]
    for ev in ("skipped_busy", "skipped_floor"):
        res = ro.analyse([skip(ev, bar(0)), skip(ev, bar(3), "short")], [], WEEK, replay)
        assert res["parity"] == "ok" and res["missed"] == []
    res = ro.analyse([skip("skipped_busy", bar(0))], [], WEEK, replay)
    assert res["parity"] == "fail" and res["missed"] == [{"t": bar(3), "side": "short"}]


def test_counts_week_scope_and_unknown_parity():
    auto = [skip("skipped_busy", bar(1)), skip("skipped_floor", bar(2)),
            skip("skipped_busy", bar(-10))]    # last week: not counted
    res = ro.analyse(auto, [], WEEK, None)
    assert (res["skipped_busy"], res["skipped_floor"], res["parity"]) == (1, 1, "unknown")
    assert res["n"] == 0 and res["fail"] is None


def test_same_bar_both_and_unrecorded_and_csv_replaces_week(tmp_path):
    ex = [{"label": "p0:stop"}, {"label": "p0:t1"}]
    rows = [ledger(0, 1.0, exits=ex)]
    res = ro.analyse([attempt(0), attempt(9)], rows, WEEK, [{"t": bar(0), "side": "long", "stop": None},
                                                            {"t": bar(9), "side": "long", "stop": None}])
    assert res["same_bar_both"] == 1 and res["entered_unrecorded"] == ["p9"]
    log = tmp_path / "FORWARD_LOG.csv"
    ro.write_log_row(log, res)
    ro.write_log_row(log, res)
    lines = log.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2 and lines[1].startswith("2026-11-09,")


def test_main_writes_readout_and_exit_code(tmp_path):
    auto, led, rep = tmp_path / "a.jsonl", tmp_path / "l.jsonl", tmp_path / "r.json"
    auto.write_text("", encoding="utf-8")
    led.write_text("\n".join(json.dumps(ledger(i, -0.1 if i else 0.5)) for i in range(13)) + "\n", encoding="utf-8")
    rep.write_text(json.dumps([{"t": bar(i), "side": "long", "stop": None} for i in range(13)]), encoding="utf-8")
    rc = ro.main(["--week", "2026-11-09", "--auto-log", str(auto), "--ledger", str(led), "--replay-json", str(rep),
                  "--outdir", str(tmp_path)])
    assert rc == 2                              # FAIL-B at 12 losers; the missing attempts also fail parity
    md = (tmp_path / "READOUT_2026-11-09.md").read_text(encoding="utf-8")
    assert "FAIL-B" in md and "n 13 trades" in md


def test_missing_decision_log_is_parity_unknown_not_fail(tmp_path):
    rep = tmp_path / "r.json"
    rep.write_text(json.dumps([{"t": bar(1), "side": "long", "stop": None}]), encoding="utf-8")
    rc = ro.main(["--week", "2026-11-09", "--auto-log", str(tmp_path / "none.jsonl"),
                  "--ledger", str(tmp_path / "none2.jsonl"), "--replay-json", str(rep), "--outdir", str(tmp_path)])
    assert rc == 0 and "parity unknown" in (tmp_path / "READOUT_2026-11-09.md").read_text(encoding="utf-8")
