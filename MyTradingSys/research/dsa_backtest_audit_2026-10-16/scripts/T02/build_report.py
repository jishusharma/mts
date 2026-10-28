"""Builds ../../T02_lookahead_time.md from out/trunc_log_*.txt (one line per layer). Run from the worktree root:
python MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T02/build_report.py"""
import glob
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
LINE = re.compile(r"^(\S+)\s+n=(\d+) cuts=(\d+) events=(\d+) late=(\d+) repaint=(\d+) nan_diff=(\d+) x10_diff=(\d+) "
                  r"lag=(\d+)/(\d+) err\(tr/nan/x10\)=(\d+)/(\d+)/(\d+)")
rows = []
for f in sorted(glob.glob(os.path.join(HERE, "out", "trunc_log_*.txt"))):
    for l in open(f, encoding="utf-8"):
        m = LINE.match(l)
        if m:
            rows.append([m.group(1)] + [int(x) for x in m.groups()[1:]])


def verdict(r):
    key, n, cuts, ev, late, rep, nan, x10, lag, decl, e1, e2, e3 = r
    if ev == 0:
        return "NOT DECISIVE (0 events on synthetic bars)"
    if rep:
        return "FAIL (repaint)"
    if late:
        return "PASS-LAG" if lag <= decl else "FAIL-LAG"
    if nan or x10:
        return "FAIL (poison)"
    return "PASS"


tab = ["| Layer key (layer / sub / tf) | synth bars | cuts | events (full run) | late | repaint | NaN diff | x10 diff | errors tr/nan/x10 | Verdict |",
       "|---|---|---|---|---|---|---|---|---|---|"]
cnt = {}
for r in rows:
    v = verdict(r)
    cnt[v.split(" ")[0]] = cnt.get(v.split(" ")[0], 0) + 1
    tab.append("| %s | %d | %d | %d | %d | %d | %d | %d | %d/%d/%d | %s |" % (r[0].replace("|", " / "), r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[10], r[11], r[12], v))
summary = ", ".join("%s %d" % (k, v) for k, v in sorted(cnt.items()))
tpl = open(os.path.join(HERE, "report_template.md"), encoding="utf-8").read()
out = tpl.replace("{{TRUNC_TABLE}}", "\n".join(tab)).replace("{{TRUNC_SUMMARY}}", summary).replace("{{N_LAYERS}}", str(len(rows)))
dest = os.path.abspath(os.path.join(HERE, "..", "..", "T02_lookahead_time.md"))
with open(dest, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(out)
print("wrote", dest, len(rows), summary)
