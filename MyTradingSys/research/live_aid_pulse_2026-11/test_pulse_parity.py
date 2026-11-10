"""Parity of the python port of pulse.js (pulse_port.py) with the live pulse.js and level_registry.js, run through node on fixtures.
Hand-computed unit tests come first (expected numbers worked out on paper from the rule text, not from either implementation); the
parity tests then compare python with node on a real kline fixture (no taker column) and seeded synthetic tapes (with taker volume).
Parity tests skip (never fail) without node."""
import json
import math
import random
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
LA = HERE.parent.parent / "tools" / "live_aid"
sys.path.insert(0, str(HERE))
import pulse_port as PP  # noqa: E402

T0 = 1_794_182_400_000   # 2026-11-09 00:00Z, a UTC day start


def _node(js_file, fn, *args):
    node = shutil.which("node")
    if not node:
        pytest.skip("node not installed")
    runner = "const P=require(process.argv[1]);let j='';process.stdin.on('data',d=>j+=d).on('end',()=>{j=JSON.parse(j);console.log(JSON.stringify(P[j.fn].apply(null,j.a)))})"
    out = subprocess.run([node, "-e", runner, str(LA / js_file)], input=json.dumps({"fn": fn, "a": list(args)}), capture_output=True,
                         text=True, encoding="utf-8", timeout=120)
    assert out.returncode == 0, out.stderr[-1500:]
    return json.loads(out.stdout)


def kl(t, c, delta, vol=20.0):
    return [t, c, c + 0.5, c - 0.5, c, vol, t + 59_999, 0, 0, (vol + delta) / 2]


def norm(x):
    """python value -> what JSON.stringify of the JS value gives (NaN -> None), recursively."""
    if isinstance(x, float) and (math.isnan(x) or math.isinf(x)):
        return None
    if isinstance(x, dict):
        return {k: norm(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [norm(v) for v in x]
    return x


def same(a, b, path="", tol=1e-9):
    if isinstance(a, dict):
        assert isinstance(b, dict) and set(a) == set(b), (path, sorted(a), sorted(b) if isinstance(b, dict) else b)
        for k in a:
            same(a[k], b[k], path + "." + k, tol)
    elif isinstance(a, list):
        assert isinstance(b, list) and len(a) == len(b), (path, len(a), len(b) if isinstance(b, list) else b)
        for i, (x, y) in enumerate(zip(a, b)):
            same(x, y, f"{path}[{i}]", tol)
    elif isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
        assert abs(a - b) <= tol * max(1.0, abs(a), abs(b)), (path, a, b)
    else:
        assert a == b, (path, a, b)


# ---------- hand-computed, python only ----------
def test_fold_sums_volume_and_taker_buy_by_hand():
    # four 1m bars, volume 20, taker buy 10..13 (delta = 2*buy - 20 = 0, 2, 4, 6); 2m buckets from the UTC day start
    rows = [kl(T0 + i * 60_000, 100 + i, 2 * i) for i in range(4)]
    f = PP.foldK(rows, 120_000)
    assert [r[0] for r in f] == [T0, T0 + 120_000]
    assert [r[5] for r in f] == [40, 40] and [r[9] for r in f] == [21, 25]    # 10+11, 12+13
    assert (f[0][1], f[0][4], f[0][2], f[0][3]) == (100, 101, 101.5, 99.5)


def test_divergence_by_hand():
    # w=3. bullish: price halves [5,4,6] / [3,5,4] (lower low 3 < 4); indicator [1,0,2] / [1,1,0.5] (low 0.5 > 0)
    assert PP.divergence([5, 4, 6, 3, 5, 4], [1, 0, 2, 1, 1, 0.5], 3) == 1
    # bearish: price higher high (9 > 8) with indicator lower high (3 < 4)
    assert PP.divergence([8, 7, 6, 9, 7, 6], [4, 3, 2, 3, 2, 1], 3) == -1
    # lower low in price but the indicator low is not higher (2 vs 2), and no higher high -> none
    assert PP.divergence([8, 7, 6, 7, 6, 5], [4, 3, 2, 4, 3, 2], 3) == 0
    assert PP.divergence([1, 2, 3], [1, 2, 3], 3) is None                       # fewer than 2w points


def test_bearish_cvd_read_by_hand():
    # 60 x 1m: bars 0-29 flat 100 delta 0; 30-44 climb to 110 delta +10 (cum 150); 45-58 drift down 0.5/bar delta -5; bar 59 = 111, delta -5.
    # Last 15 vs the 15 before: price max 111 > 110, cum delta max 145 < 150 -> bearish CVD divergence -1; CVD of last 10 bars = -50.
    rows = []
    for i in range(60):
        if i < 30:
            c, d = 100.0, 0.0
        elif i < 45:
            c, d = 100 + (i - 29) * 10 / 15, 10.0
        elif i < 59:
            c, d = 110 - (i - 44) * 0.5, -5.0
        else:
            c, d = 111.0, -5.0
        rows.append(kl(T0 + i * 60_000, c, d))
    r = PP.read(rows, 60_000)
    assert r["div"]["cvd"] == -1 and r["cvd"] == -50 and r["v"]["cvd"] == -1
    assert PP.read(rows[:39], 60_000) is None                                   # under the 40-bar floor


LAD = {"at": None, "above": [{"price": 75000, "name": "Today high"}], "below": [{"price": 73750, "name": "Today low"}]}
G_DOWN = {"hi": -0.3, "rows": [{"tf": "5m", "r": {"div": {"rsi": 0, "wt": None, "cvd": -1}}}, {"tf": "1h", "r": {"div": {"rsi": -1, "wt": 0, "cvd": 0}}}]}


def test_setup_rules_by_hand():
    s = PP.setup(G_DOWN, LAD, 74950, "WAIT")                    # 0.0667 % under 75000 -> inside 0.15 %
    assert s["side"] == "SHORT" and s["level"] == 75000 and s["divs"] == ["5m CVD"]   # the 1h divergence is not a low timeframe
    assert PP.setup(G_DOWN, LAD, 74800, "WAIT") is None         # 0.267 % away
    assert PP.setup(dict(G_DOWN, hi=0.3), LAD, 74950, "WAIT") is None   # big picture up, home not short
    assert PP.setup(dict(G_DOWN, hi=0.3), LAD, 74950, "SHORT")["side"] == "SHORT"
    g = {"hi": 0.4, "rows": [{"tf": "7m", "r": {"div": {"rsi": 1, "wt": 1, "cvd": 0}}}]}
    s = PP.setup(g, LAD, 73800, "WAIT")                         # 0.068 % over 73750
    assert s["side"] == "LONG" and s["divs"] == ["7m RSI", "7m WaveTrend"]


def test_merge_ladder_by_hand():
    # 100.00 and 100.10 (0.10 % above) merge; 100.20 is 0.20 % above the zone's low -> its own zone; merged price = round1((100+100.1)/2) = 100.1
    z = PP.merge([{"price": 100.0, "label": "High"}, {"price": 100.10, "label": "Low"}, {"price": 100.20, "label": "Open"}])
    assert [(x["lo"], x["hi"], x["label"], x["n"]) for x in z] == [(100.0, 100.1, "Cluster", 2), (100.2, 100.2, "Open", 1)]
    assert z[0]["price"] == 100.1
    lad = PP.ladder(z, 100.05)
    assert lad["at"]["lo"] == 100.0 and lad["above"][0]["lo"] == 100.2 and lad["below"] == []


# ---------- parity python vs node ----------
def synth(n, seed, start=T0):
    rnd = random.Random(seed)
    p, rows = 70000.0, []
    for i in range(n):
        o = p
        p = max(1000.0, p * (1 + rnd.gauss(0, 0.0008) + 0.00003 * math.sin(i / 200)))
        hi, lo = max(o, p) * (1 + abs(rnd.gauss(0, 0.0003))), min(o, p) * (1 - abs(rnd.gauss(0, 0.0003)))
        v = 50 + 30 * rnd.random()
        buy = v * (0.5 + 0.25 * math.tanh((p - o) / o * 800) + 0.1 * (rnd.random() - 0.5))
        t = start + i * 60_000
        rows.append([t, o, hi, lo, p, v, t + 59_999, 0, 0, buy])
    return rows


def real_fixture():
    return json.load(open(LA / "fixture_klines.json"))["klines"]


def tfk_native(rows1m):
    return {"1m": rows1m, "3m": PP.foldK(rows1m, 180_000), "5m": PP.foldK(rows1m, 300_000), "15m": PP.foldK(rows1m, 900_000),
            "30m": PP.foldK(rows1m, 1_800_000), "1h": PP.foldK(rows1m, 3_600_000), "2h": PP.foldK(rows1m, 7_200_000),
            "4h": PP.foldK(rows1m, 14_400_000)}


def test_parity_fold_and_read_every_grid_frame():
    rows = synth(1500, 7)
    for ms in (60_000, 120_000, 180_000, 300_000, 420_000, 600_000, 900_000, 3_600_000, 14_400_000):
        same(norm(PP.foldK(rows, ms)), _node("pulse.js", "foldK", rows, ms), f"fold{ms}")
    for ms in (60_000, 120_000, 300_000, 420_000, 600_000, 900_000):
        k = PP.foldK(rows, ms)
        same(norm(PP.read(k, ms)), _node("pulse.js", "read", k, ms), f"read{ms}")


def test_parity_grid_on_synthetic_tape_with_taker_volume():
    tfk = tfk_native(synth(2600, 11))
    py, js = norm(PP.grid(tfk)), _node("pulse.js", "grid", tfk)
    same(py, js, "grid")
    assert py["n"] >= 8     # most frames carry a read, so the comparison is not vacuous


def test_parity_grid_on_real_fixture_without_taker_column():
    rows = real_fixture()
    assert len(rows[0]) == 6                         # the repo fixture has no taker column: CVD must come out null in both
    tfk = {"1m": rows}
    py, js = norm(PP.grid(tfk)), _node("pulse.js", "grid", tfk)
    same(py, js, "grid")
    assert py["rows"][0]["r"]["div"]["cvd"] is None and py["rows"][0]["r"]["cvd"] is None


def test_parity_setup_over_random_ladders():
    rnd = random.Random(3)
    hits = 0
    for seed in range(6):
        tfk = tfk_native(synth(2600, 100 + seed))
        g = PP.grid(tfk)
        px = tfk["1m"][-1][4]
        for _ in range(6):
            def zone(dx):
                return {"price": px * (1 + dx), "name": "L%d" % int(dx * 1e5)}
            lad = {"at": zone(rnd.uniform(-0.001, 0.001)) if rnd.random() < 0.3 else None,
                   "above": [zone(rnd.uniform(0.0, 0.004))], "below": [zone(-rnd.uniform(0.0, 0.004))]}
            for home in ("WAIT", "LONG", "SHORT"):
                a, b = norm(PP.setup(g, lad, px, home)), _node("pulse.js", "setup", norm(g), lad, px, home)
                same(a, b, "setup")
                hits += a is not None
    assert hits > 0         # at least one fixture must produce a setup or the check proves nothing


def test_parity_merge_and_ladder_with_level_registry():
    rnd = random.Random(5)
    keys = ("lo", "hi", "price", "label", "n")
    for _ in range(10):
        items = [{"price": 70000 * (1 + rnd.uniform(-0.01, 0.01)), "src": "playbook", "label": rnd.choice(["High", "Low", "Open"]), "badge": "x"}
                 for _ in range(rnd.randint(2, 14))]
        z_py = PP.merge(items)
        z_js = _node("level_registry.js", "merge", items)
        same([{k: z[k] for k in keys} for z in z_py], [{k: z[k] for k in keys} for z in z_js], "merge")
        px = 70000 * (1 + rnd.uniform(-0.01, 0.01))
        l_py, l_js = PP.ladder(z_py, px), _node("level_registry.js", "ladder", z_js, px)

        def key(z):
            return None if z is None else (z["lo"], z["hi"])
        assert key(l_py["at"]) == key(l_js["at"])
        assert [key(z) for z in l_py["above"]] == [key(z) for z in l_js["above"]]
        assert [key(z) for z in l_py["below"]] == [key(z) for z in l_js["below"]]
