"""Trial T8 (angle e / red-team RT-1): count how many grid rows change between PRIOR_RULE = "last_closed" (primary) and
"cur_k_minus_1" (the first draft). Only grid points at an 8h/12h/1d/1w bucket close can differ (every 1d and 1w close is
an 8h close), so the VEC build is evaluated at every 8h close of DEV under both rules. Counts only.

  python prior_rule_count.py     -> prior_rule_count.md, appends row T8 to trials.csv
"""
import csv
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import context_asof as CA      # noqa: E402
import run_compare as RC       # noqa: E402

SCRATCH = os.environ.get("CF_SCRATCH", os.path.join(HERE, "_scratch"))
CACHE = os.path.join(SCRATCH, "dev1m.npz")
LEVEL_FIELDS = ("near_price", "near_src", "n_layers", "at_level", "level_age_h", "touch_count", "n_levels")
LADDER_FIELDS = ("ladder_rung", "ladder_stop_pct", "stop_d_pct", "stop_12_pct", "stop_8_pct", "ladder_cond")


def main():
    bars = CA.load_dev(cache=CACHE)
    fund = CA.load_funding()
    pts = list(range(479, CA.N_DEV, 480))
    rows = {}
    for rule in ("last_closed", "cur_k_minus_1"):
        CA.PRIOR_RULE = rule
        V = CA.VecTables(bars, fund)
        rows[rule] = {(t, s): RC.flat(V.context(t, s)) for t in pts for s in ("long", "short")}
    CA.PRIOR_RULE = "last_closed"
    diff_level = Counter()
    diff_ladder = Counter()
    at_level = {"last_closed": Counter(), "cur_k_minus_1": Counter()}
    for key in rows["last_closed"]:
        a, b = rows["last_closed"][key], rows["cur_k_minus_1"][key]
        s = key[1]
        if any(not RC.same(a[f], b[f]) for f in LEVEL_FIELDS):
            diff_level[s] += 1
        if any(not RC.same(a[f], b[f]) for f in LADDER_FIELDS):
            diff_ladder[s] += 1
        for rule in rows:
            at_level[rule][s] += int(rows[rule][key]["at_level"] is True)
    n = len(pts)
    L = ["# Trial T8: PRIOR_RULE last_closed (primary) vs cur_k_minus_1 (first draft), counts at every 8h close of DEV", "",
         f"{n} grid points x 2 sides. A row 'differs' when any of the listed fields differs between the two rules.", "",
         "| side | level fields differ | ladder fields differ | at_level (last_closed) | at_level (cur_k_minus_1) |", "|---|---|---|---|---|"]
    for s in ("long", "short"):
        L.append(f"| {s} | {diff_level[s]} of {n} | {diff_ladder[s]} of {n} | {at_level['last_closed'][s]} | {at_level['cur_k_minus_1'][s]} |")
    L += ["", "Level fields: " + ", ".join(LEVEL_FIELDS) + ". Ladder fields: " + ", ".join(LADDER_FIELDS) + ".",
          "Why the primary: the decision is taken at the close of bar t and filled at the open of bar t+1, which lies in the next bucket;",
          "the candle that completed at t is closed information at that moment, exactly like the Bollinger bands and ATR already use it.", ""]
    with open(os.path.join(HERE, "prior_rule_count.md"), "w", newline="\n", encoding="utf-8") as fh:
        fh.write("\n".join(L))
    tr = os.path.join(HERE, "trials.csv")
    with open(tr, newline="", encoding="utf-8") as fh:
        existing = list(csv.DictReader(fh))
    existing = [r for r in existing if r["trial_id"] != "T8"]
    existing.append(dict(trial_id="T8", factor="F1/F3 prior bucket", primary="last closed bucket (includes a candle completing at t)",
                         alternative="cur_k - 1 (skips a candle completing at t)",
                         reason="the fill at open[t+1] lies in the next bucket; a candle closed at t is closed information (same as BB/ATR)",
                         n_primary_long=at_level["last_closed"]["long"], n_primary_short=at_level["last_closed"]["short"],
                         n_alt_long=at_level["cur_k_minus_1"]["long"], n_alt_short=at_level["cur_k_minus_1"]["short"], outcome_read="no"))
    with open(tr, "w", newline="\n", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(existing[0].keys()))
        w.writeheader()
        w.writerows(existing)
    print("\n".join(L[4:8]))


if __name__ == "__main__":
    main()
