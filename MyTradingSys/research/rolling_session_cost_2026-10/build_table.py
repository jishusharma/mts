"""Builds the tables of REPORT.md from committed files only (no transcripts, no live data).

  python MyTradingSys/research/rolling_session_cost_2026-10/build_table.py [--write]

Every row cites (file, needle). The script finds the needle in the file and prints file:line; a needle that is
not found stops the run with exit 1, so no source can be a guess. Missing cells are the string NOT_IN_DATA.
context_gap_runs.jsonl is read for the fleet-level aggregate row.
"""
import json
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MTS = os.path.abspath(os.path.join(HERE, "..", ".."))
ND = "NOT_IN_DATA"
D = "research/mts_doctor/"
S = "system/"


def where(rel, needle):
    p = os.path.join(MTS, rel)
    with open(p, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            if needle in line:
                return "%s:%d" % (rel, i)
    print("NEEDLE NOT FOUND: %s in %s" % (needle, rel))
    sys.exit(1)


# (name, role/login, run length, ctx start, ctx end or peak, budget spent, compactions, [(file, needle)...])
SESSIONS = [
    ("Rotation-test stand-in coordinator (local_1d839155)", "Sonnet coordinator, login C, JIS-NB",
     "2 task turns + 5 rebuild model calls", "69K", "75K before clear; 72K after rebuild", ND,
     "0 compactions, 1 clear_session",
     [(D + "ROTATION_TEST_2026-10-24.md", "context 69K at start, 72K at the end"),
      (D + "ROTATION_TEST_2026-10-24.md", "Context before the clear | 75K")]),
    ("Pilot 1b coordinator", "Sonnet coordinator, login C, JIS-NB", "4 h (14:28Z-18:30Z)",
     "109K after 10 min", ND, "5 h window stayed under 80% (PASS, no figure)", ND,
     [(D + "PILOT1B_NOTES.md", "started 14:28Z, stop 18:30Z"),
      (D + "compaction_long_runs_2026-10-24.md", "The pilot coordinator was at 109K after 10 minutes"),
      (D + "REPORT_pilots_2026-10-25.md", "| 5 Cost | 5 h < 80% | PASS | PASS")]),
    ("Pilot 2 coordinator (6 workers)", "Sonnet coordinator, login C, JIS-NB", "about 2 h (18:48Z-20:50Z, ended early)",
     ND, "232K and 250K (two hand /compact, to 93K and 97K; which pilot is not stated)",
     "5 h window 13% -> 42%; week 34% -> 38% (whole fleet)", "2 manual /compact",
     [(D + "REPORT_pilots_2026-10-25.md", "5 h 13% -> 42%; week 34% -> 38%"),
      (D + "REPORT_pilots_2026-10-25.md", "operator /compact works (232K -> 93K, 250K -> 97K)")]),
    ("Pilot 3 supervisor (pilot3_sup, Haiku workers)", "Sonnet supervisor, login C", "14 min (05:46Z-06:00Z)",
     ND, "127K at end", "5 h 3% -> 7%; week 44% -> 44%", "0",
     [(S + "handoff_history/PILOT3_RESULTS.md", "Supervisor context 127k at end"),
      (S + "handoff_history/PILOT3_RESULTS.md", "5h window: 3% start, 7% end")]),
    ("Rolling chain links 1-5 (local_37a9ec3e), 2026-10-27", "Coordinator chain, DESKTOP-F7IU69N",
     "5 links in one 5 h window; wall time " + ND, ND, "about 12% (of the window; absolute tokens " + ND + ")",
     "5 h window 94% (about 1h06m left); week 40%", ND,
     [(S + "NEXT_SESSION.md", "5h usage window was at 94% with ~1h6m left"),
      (S + "SUPER_SESSION.md", "context only ~12%")]),
    ("Rolling chain links 6-9, login A, 2026-10-27/28", "Coordinator chain, DESKTOP-F7IU69N / JIS-LAPTOP login A",
     "4 links; closed by operator, stopped before the 5 h window ran out", ND, ND, ND, ND,
     [(S + "NEXT_SESSION.md", "stopped BEFORE the 5h window ran out this time")]),
    ("Supervisor C, Krown session (528eee96), 2026-10-22", "Supervisor, login C, JIS-NB", "93 min (22:06Z-23:39Z)",
     ND, ND, ND, ND,
     [(D + "AUDIT_SUPER_C_2026-10-23.md", "2026-10-22 22:06Z to 23:39Z"),
      (D + "AUDIT_SUPER_C_2026-10-23.md", "The turn meter cut the session 4 s later")]),
]

# (issue, source file, needle)
ISSUES = [
    ("Compactions that lost money: 39 of 70 (56%) before the 10-15 audit; 3 of 20 (15%) after, once they ran at about 268K",
     "research/_archive/loose_2026-10/COMPACTION_REPORT_2026-10-16.md", "| Losing money | 39 of 70 (56%) | 3 of 20 (15%) |"),
    ("10-15 audit: 68 compactions, 39 lost work because state lived only in the context",
     S + "SUPER_SESSION.md", "10-15 audit: 68 compactions, 39 lost work"),
    ("Mid-session cache misses: 126 in 7 days over 134 sessions, about 14% of cost (a long idle wait rebuilds the whole history at 2x)",
     D + "context_cost_2026-10-24.md", "Mid-session cache misses alone are about 14% of cost"),
    ("Context bloat: 10 of 134 sessions ran over 200 turns and used 39% of all context; the first-turn base (about 75K) is 57% of re-read context",
     D + "context_cost_2026-10-24.md", "Sessions over 200 turns | 10 of 134, but 39% of all context"),
    ("Auto-compact percent override does not work on current versions (GitHub #63186 closed, #82761 compactions at 370K-828K); the old 25/12 setting may never have worked",
     D + "compaction_long_runs_2026-10-24.md", "#82761 (open; compactions fired anywhere from 370K to 828K)"),
    ("A stale main-checkout settings.json forced about 250K compaction on every model",
     S + "WORKERS.md", "a stale one forced ~250k for every model"),
    ("Opus: 43 of 46 compactions were manual; Fable session c11be9cb took 84 operator prompts and 13 compactions",
     "research/context_policy_review/REVIEW_OPUS.md", "Fable session c11be9cb took 84 operator prompts (13 compactions)"),
    ("clear_session refused 3 times while a wake, ship or Remote Control was live; rotation in pilot 2 needed the operator",
     D + "REPORT_pilots_2026-10-25.md", "`clear_session` is refused while any wake, ship or Remote Control is live (3 refusals)"),
    ("Early end by a hook: the turn meter cut Supervisor C 4 s after it tried to spawn the Krown Builder (turn_meter removed 2026-10-24, 43d3bfc8f)",
     D + "AUDIT_SUPER_C_2026-10-23.md", "The turn meter cut the session 4 s later"),
    ("Chain stopped by the 5 h plan window, not by context (context about 12% when the window was at 94%)",
     S + "SUPER_SESSION.md", "context was never the constraint"),
    ("Two hand-over triggers overlap: transit at 150K context or a 3 h wave (supervisor.py) versus D5 rotation at about 200K and D6 24 h runs",
     "research/lead/2026-10-28_rolling-super-sessions-per-station.md", "Overlap between hand-over rules"),
    ("Agents report no per-worker context, so Pilot 3 context was NOT MEASURED; only subagent token sums exist",
     S + "handoff_history/PILOT3_RESULTS.md", "NOT MEASURED (Agents have no get_usage context)"),
    ("The ship tail, not the work, sets a link's length: worker Agent link p50 5 / p90 34 / max 181 min over 255 links",
     "research/lead/2026-10-28_rolling-chain-link-latency-levers.md", "worker Agent link | 255 | 5 / 34 / 181"),
]


def fleet():
    p = os.path.join(MTS, "research", "mts_doctor", "context_gap_runs.jsonl")
    with open(p, encoding="utf-8") as f:
        row = json.loads(f.readline())
    ps = row["per_session"]
    bases = [s["base"] for s in ps]
    rew = [s["rewrites"] for s in ps]
    return (len(ps), statistics.median(bases), min(bases), max(bases), sum(rew), sum(1 for r in rew if r > 0),
            where("research/mts_doctor/context_gap_runs.jsonl", '"base_median"'))


def build():
    out = ["## Table 1: past rolling and long coordinator sessions (NOT_IN_DATA = no committed number)", "",
           "| Session | Role / login | Run length | Context at start | Context at end or peak | Budget spent | Compactions | Source |",
           "|---|---|---|---|---|---|---|---|"]
    for name, role, length, cs, ce, bud, comp, srcs in SESSIONS:
        src = "; ".join(where(f, n) for f, n in srcs)
        out.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (name, role, length, cs, ce, bud, comp, src))
    n, med, lo, hi, rsum, rn, src = fleet()
    out += ["", "## Table 2: fleet aggregate from context_gap_runs.jsonl (one run; main-thread sessions with 5+ turns)", "",
            "| Sessions | First-turn context median (min-max) | Full cache rewrites (sum) | Sessions with a rewrite | Source |",
            "|---|---|---|---|---|",
            "| %d | %d (%d-%d) | %d | %d | %s |" % (n, med, lo, hi, rsum, rn, src), "",
            "## Table 3: past issues", "", "| # | Issue | Source |", "|---|---|---|"]
    for i, (txt, f, needle) in enumerate(ISSUES, 1):
        out.append("| %d | %s | %s |" % (i, txt, where(f, needle)))
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    tables = build()
    if "--write" in sys.argv:
        with open(os.path.join(HERE, "tables.md"), "w", encoding="utf-8", newline="\n") as f:
            f.write(tables)
    print(tables)
