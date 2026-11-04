import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import liq_mirror as M

def ev(sym, side, price, t, qty=1.0):
    return {"symbol": sym, "side": side, "price": price, "qty": qty, "eventTime": t, "tradeTime": t}

def write(p, rows):
    with open(p, "w", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")

def test_mirror_is_idempotent_and_counts_flushes(tmp_path):
    src, dst = tmp_path / "src", tmp_path / "dst"
    src.mkdir()
    m = 60_000
    # 3 events: SELL flush at 100 (two events), then price rebounds +1% within the hold window
    rows = [ev("BTCUSDT", "SELL", 100.0, 0), ev("BTCUSDT", "SELL", 99.5, m), ev("BTCUSDT", "BUY", 100.6, 10 * m)]
    write(src / "BTCUSDT.jsonl", rows)
    r1 = M.mirror(str(src), str(dst))
    r2 = M.mirror(str(src), str(dst))
    assert r1["BTCUSDT"] == 3 and r2["BTCUSDT"] == 0  # second run copies nothing new
    assert len(open(dst / "BTCUSDT.jsonl").read().splitlines()) == 3
    # appended line is picked up once
    with open(src / "BTCUSDT.jsonl", "a", newline="\n") as f:
        f.write(json.dumps(ev("BTCUSDT", "BUY", 101.0, 11 * m)) + "\n")
    assert M.mirror(str(src), str(dst))["BTCUSDT"] == 1
    res = M.base_rate(M.load(str(dst)), min_events=2, gap_ms=5 * m, hold_ms=30 * m, move_pct=0.5)
    assert res["n"] == 1 and res["reversed"] == 1 and res["rate"] == 1.0
    assert res["sources"] == ["BTCUSDT.jsonl 1970-01-01..1970-01-01"]