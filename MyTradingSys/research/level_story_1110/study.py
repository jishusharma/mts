"""Level-story history study (DESCRIPTIVE, no holdout, no trade claim). Runs the live levelstory.js via walk.js with ex = {}.
Usage: python study.py [bars_cache.json]"""
import json
import statistics
import subprocess
import sys
import time
import urllib.request
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
LS = HERE.parent.parent / "tools" / "live_aid" / "levelstory.js"
CACHE = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "bars.json"
DAYS, FEE = 180, 10.0
M15 = 900_000
DAYMS = 86_400_000


def fetch():
    now = int(time.time() * 1000)
    start = now // DAYMS * DAYMS - (DAYS + 2) * DAYMS
    rows, t = [], start
    while t < now:
        u = f"https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=15m&startTime={t}&limit=1000"
        with urllib.request.urlopen(u, timeout=30) as r:
            b = json.load(r)
        if not b:
            break
        rows += b
        t = b[-1][0] + M15
    rows = [r for r in rows if r[6] < now]
    seen, out = set(), []
    for r in rows:
        if r[0] not in seen:
            seen.add(r[0])
            out.append(r)
    return out


if CACHE.exists():
    bars = json.loads(CACHE.read_text())
else:
    bars = fetch()
    CACHE.write_text(json.dumps(bars))
last_t = bars[-1][6]
eval_from = (last_t // M15) * M15 - DAYS * DAYMS
mid = eval_from + (DAYS // 2) * DAYMS
res = subprocess.run(["node", str(HERE / "walk.js"), str(LS), str(CACHE), str(eval_from)], capture_output=True, text=True, encoding="utf-8")
if res.returncode:
    sys.exit(res.stderr[-2000:])
recs = json.loads(res.stdout)
C = [float(r[4]) for r in bars]


def fwd(i, h, sgn):
    return None if i + h >= len(C) else sgn * (C[i + h] / C[i] - 1) * 1e4


def void_hit(i, rec):
    v = rec["voidAt"]
    if v is None or i + 8 >= len(C):
        return None
    for j in range(i + 1, i + 9):
        if (rec["res"] and C[j] > v) or ((not rec["res"]) and C[j] < v):
            return 1
    return 0


def bucket(x):
    return "<3" if x < 3 else "3" if x == 3 else "4" if x == 4 else ">=5"


def stats(evs):
    o = {"n": len(evs)}
    for h in (4, 8):
        v = [e[f"r{h}"] for e in evs if e[f"r{h}"] is not None]
        if v:
            p = sum(1 for x in v if x > 0) / len(v)
            o[f"share{h}"] = round(p, 3)
            o[f"mean{h}"] = round(statistics.mean(v), 2)
            o[f"median{h}"] = round(statistics.median(v), 2)
            o[f"net{h}"] = round(statistics.mean(v) - FEE, 2)
            o[f"n{h}"] = len(v)
    vs = [e["void"] for e in evs if e.get("void") is not None]
    if vs:
        o["void8"] = round(sum(vs) / len(vs), 3)
    return o


last = {}
sig, base = [], []
for r in recs:
    i = r["i"]
    key = r["lv"]
    if not r["near"]:
        last.pop(key, None)
        continue
    away = -1 if r["res"] else 1          # resistance -> down, support -> up
    half = 1 if bars[i][0] >= mid else 0
    base.append({"half": half, "res": r["res"], "ra4": fwd(i, 4, away), "ra8": fwd(i, 8, away), "up4": fwd(i, 4, 1), "up8": fwd(i, 8, 1)})
    prev = last.get(key)
    cur = (r["state"], r["idea"])
    last[key] = cur
    if prev == cur:
        continue
    through = r["state"] in ("ACCEPTED", "BREAKING")
    sgn = -away if through else away
    if r["idea"]:
        sgn = 1 if r["idea"] == "LONG" else -1
    sig.append({"i": i, "half": half, "state": r["state"], "idea": r["idea"], "turn": r["turn"], "thru": r["thru"],
                "r4": fwd(i, 4, sgn), "r8": fwd(i, 8, sgn), "void": void_hit(i, r) if r["idea"] else None,
                "state_changed": prev is None or prev[0] != cur[0], "idea_changed": prev is None or prev[1] != cur[1]})


def split(evs):
    return {"all": stats(evs), "h1_first90": stats([e for e in evs if e["half"] == 0]), "h2_last90": stats([e for e in evs if e["half"] == 1])}


out = {"label": "DESCRIPTIVE, OURS thresholds as coded, no holdout, no trade claim; ex={} (no WaveTrend/OI evidence, no forming bar)",
       "bars": len(bars), "window_days": DAYS,
       "first_bar_utc": time.strftime("%Y-%m-%d %H:%M", time.gmtime(bars[0][0] / 1000)),
       "last_bar_utc": time.strftime("%Y-%m-%d %H:%M", time.gmtime(bars[-1][0] / 1000)),
       "level_bar_pairs_near": len(base), "signals": len(sig), "fee_bp": FEE}
bl = {}
for nm, flt in (("near_resistance_bars_dir_down", True), ("near_support_bars_dir_up", False)):
    for half, lab in ((None, "all"), (0, "h1_first90"), (1, "h2_last90")):
        s = [b for b in base if b["res"] == flt and (half is None or b["half"] == half)]
        bl.setdefault(nm, {})[lab] = stats([{"r4": b["ra4"], "r8": b["ra8"]} for b in s])
for half, lab in ((None, "all"), (0, "h1_first90"), (1, "h2_last90")):
    s = [b for b in base if half is None or b["half"] == half]
    bl.setdefault("all_near_bars_raw_up", {})[lab] = stats([{"r4": b["up4"], "r8": b["up8"]} for b in s])
out["baseline"] = bl
out["by_state_change"] = {s: split([e for e in sig if e["state"] == s and e["state_changed"]]) for s in sorted({e["state"] for e in sig})}
out["state_by_turn_bucket"] = {f"{s} turn {b}": split([e for e in sig if e["state"] == s and e["state_changed"] and bucket(e["turn"]) == b])
                               for s in ("REJECTED", "FAILED BREAK") for b in ("<3", "3", "4", ">=5")}
ib = {}
for idea in ("SHORT", "LONG"):
    for b in ("3", "4", ">=5"):
        ib[f"{idea} turn {b}"] = split([e for e in sig if e["idea"] == idea and e["idea_changed"] and bucket(e["turn"]) == b])
    ib[f"{idea} any"] = split([e for e in sig if e["idea"] == idea and e["idea_changed"]])
ib["ANY idea"] = split([e for e in sig if e["idea"] and e["idea_changed"]])
out["ideas"] = ib
tb = {}
for b in ("<3", "3", "4", ">=5"):
    tb[f"turn {b} (REJECTED+FAILED BREAK)"] = split([e for e in sig if e["state"] in ("REJECTED", "FAILED BREAK") and e["state_changed"] and bucket(e["turn"]) == b])
    tb[f"thru {b} (any state)"] = split([e for e in sig if e["state_changed"] and bucket(e["thru"]) == b])
out["turn_thru_buckets"] = tb
out["state_counts_all_barlevel"] = dict(Counter(r["state"] for r in recs if r["near"]))
(HERE / "results.json").write_text(json.dumps(out, indent=1), encoding="utf-8", newline="\n")


def row(name, s):
    if s["n"] == 0:
        return f"| {name} | 0 | | | | | | | |"
    g = lambda k: s.get(k, "")
    return f"| {name} | {s['n']} | {g('share4')} | {g('mean4')} / {g('median4')} | {g('net4')} | {g('share8')} | {g('mean8')} / {g('median8')} | {g('net8')} | {g('void8')} |"


H = "| group | n | share+ 4b | mean/med bp 4b | net of 10bp 4b | share+ 8b | mean/med bp 8b | net 8b | void<8b |\n|---|---|---|---|---|---|---|---|---|"


def table(d):
    return H + "\n" + "\n".join(row(f"{k} [{lab}]", v[lab]) for k, v in d.items() for lab in ("all", "h1_first90", "h2_last90"))


verdict = (Path(HERE / "verdict.txt").read_text().strip() if (HERE / "verdict.txt").exists() else "VERDICT PENDING")
md = f"""# Level story on history (DESCRIPTIVE)

**{verdict}**

Descriptive only. Thresholds are OURS and coded as in levelstory.js (one pass, no tuning). No holdout, no trade claim. BTCUSDT spot 15m, {out['first_bar_utc']} to {out['last_bar_utc']} UTC ({DAYS} days evaluated), ex = {{}} (no WaveTrend, OI, or forming bar, so those evidence lines and TESTING never fire). Levels: prior UTC day high/low/close, today's Asia (00-08Z) high/low after 08Z. Near = close within 0.3% of the level. A signal counts only when the state or idea for that level changes (leaving the 0.3% band resets). Share+ = share of moves in the signal direction (away from the level for REJECTED/FAILED BREAK/APPROACHING, the idea direction when an idea exists, through for ACCEPTED/BREAKING), close to close after 4 and 8 bars. Events overlap in time (several levels, same hours), so n overstates independent samples; the standard error of a share is about 0.5/sqrt(n). Net = mean bp minus 10 bp round-trip fee. void<8b = share where a 15m close went beyond voidAt before 8 bars. Halves: first 90 days vs last 90 days.

Bars near a level (level x bar pairs): {out['level_bar_pairs_near']}. Signals counted: {out['signals']}. State frequency over all level-bar pairs: {out['state_counts_all_barlevel']}.

## Baseline: all bars near a level
{table(out['baseline'])}

## By state (state-change events)
{table(out['by_state_change'])}

## REJECTED and FAILED BREAK by turn bucket
{table(out['state_by_turn_bucket'])}

## Turn / thru buckets across states
{table(out['turn_thru_buckets'])}

## Ideas (idea-change events) by turn bucket
{table(out['ideas'])}
"""
(HERE / "RESULT.md").write_text(md, encoding="utf-8", newline="\n")
print(json.dumps({k: out[k] for k in ("bars", "level_bar_pairs_near", "signals", "state_counts_all_barlevel")}))
