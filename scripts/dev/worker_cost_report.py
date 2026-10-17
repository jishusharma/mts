"""Aggregate worker cost from Claude Code transcripts (sessions, Agents, dispatcher ticks).

Prints ONLY aggregate numbers (no transcript text; the repo is public).
Usage: python scripts/dev/worker_cost_report.py [--days 5] [--json out.json]
Source of the numbers in MyTradingSys/system/WORKERS.md.
"""
import argparse
import datetime as dt
import glob
import json
import os
import statistics
import sys

ROOT = os.path.expanduser("~/.claude/projects/C--Users-E-ngineers-IdeaProjects-BinanceDataFeed")


def parse(path):
    """One transcript -> dict of counts. Assistant lines repeat per streamed block: dedupe on message id."""
    msgs = {}
    tools = 0
    ship = commit = False
    first_ts = last_ts = None
    compactions = []
    nturn = 0
    first_user = ""
    model_prompt = ""
    with open(path, encoding="utf8", errors="replace") as f:
        for line in f:
            try:
                o = json.loads(line)
            except ValueError:
                continue
            ts = o.get("timestamp")
            if ts:
                first_ts = first_ts or ts
                last_ts = ts
            if o.get("subtype") == "compact_boundary" or o.get("isCompactSummary"):
                compactions.append(nturn)
            m = o.get("message")
            if o.get("type") == "user" and not first_user and isinstance(m, dict):
                c = m.get("content")
                first_user = c if isinstance(c, str) else ""
            if o.get("type") != "assistant" or not isinstance(m, dict):
                continue
            mid = m.get("id") or o.get("uuid")
            u = m.get("usage") or {}
            if mid not in msgs:
                nturn += 1
            msgs[mid] = (m.get("model"), u)
            c = m.get("content")
            if isinstance(c, list):
                for b in c:
                    if isinstance(b, dict) and b.get("type") == "tool_use":
                        tools += 1
                        cmd = json.dumps(b.get("input", {}))
                        if "sync.py ship" in cmd or "sync.py\\\" ship" in cmd:
                            ship = True
                        if "git commit" in cmd or "git -C" in cmd and " commit" in cmd:
                            commit = True
    tot = dict(inp=0, out=0, cr=0, cw=0)
    peak = 0
    models = {}
    ctxs = []
    for mdl, u in msgs.values():
        ctxs.append((u.get("input_tokens", 0) or 0) + (u.get("cache_read_input_tokens", 0) or 0)
                    + (u.get("cache_creation_input_tokens", 0) or 0))
        i, ou = u.get("input_tokens", 0) or 0, u.get("output_tokens", 0) or 0
        cr, cw = u.get("cache_read_input_tokens", 0) or 0, u.get("cache_creation_input_tokens", 0) or 0
        tot["inp"] += i
        tot["out"] += ou
        tot["cr"] += cr
        tot["cw"] += cw
        peak = max(peak, i + cr + cw)
        models[mdl] = models.get(mdl, 0) + 1
    model = max(models, key=models.get) if models else None
    t0 = dt.datetime.fromisoformat(first_ts.replace("Z", "+00:00")) if first_ts else None
    t1 = dt.datetime.fromisoformat(last_ts.replace("Z", "+00:00")) if last_ts else None
    fu = first_user[:400]
    return dict(path=path, model=model, first_ctx=ctxs[0] if ctxs else 0, last_ctx=ctxs[-1] if ctxs else 0, turns=len(msgs), tools=tools, peak_ctx=peak,
                wall_min=(t1 - t0).total_seconds() / 60 if t0 and t1 else 0, start=t0,
                compactions=len(compactions), shipped=ship, committed=commit,
                kind_hint="dispatcher" if ("relay" in fu.lower() and "kick" in fu.lower()) else "",
                **tot)


def classify(p):
    if "/subagents/" in p["path"].replace("\\", "/"):
        return "agent"
    return p["kind_hint"] or "session"


def pct(xs, q):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(q * len(xs)))] if xs else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=float, default=5)
    ap.add_argument("--json")
    a = ap.parse_args()
    cut = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=a.days)
    files = glob.glob(ROOT + "/*.jsonl") + glob.glob(ROOT + "/*/subagents/*.jsonl")
    rows = []
    for fp in files:
        if dt.datetime.fromtimestamp(os.path.getmtime(fp), dt.timezone.utc) < cut:
            continue
        p = parse(fp)
        if p["turns"] == 0:
            continue
        p["worker"] = classify(p)
        rows.append(p)
    print(f"transcripts in last {a.days} days with assistant turns: {len(rows)}")
    groups = {}
    for p in rows:
        fam = (p["model"] or "?").replace("claude-", "").split("[")[0]
        groups.setdefault((p["worker"], fam), []).append(p)
    # input-price-equivalent units: input 1, cache-write 1.25, cache-read 0.1, output 5 (model price ratio NOT applied)
    for p in rows:
        p["eq"] = p["inp"] + 1.25 * p["cw"] + 0.1 * p["cr"] + 5 * p["out"]
    hdr = "worker,model,n,shipped,eq_per_ship_k,med_eq_k,med_turns,p90_turns,med_tools,med_total_tok,p90_total_tok,med_peak_ctx,med_out,compacted,med_wall_min"
    print(hdr)
    for (w, m), ps in sorted(groups.items()):
        tt = [x["inp"] + x["out"] + x["cr"] + x["cw"] for x in ps]
        print(",".join(str(v) for v in [
            w, m, len(ps), sum(x["shipped"] for x in ps),
            int(sum(x["eq"] for x in ps) / max(1, sum(x["shipped"] for x in ps)) / 1000),
            int(statistics.median(x["eq"] for x in ps) / 1000),
            int(statistics.median(x["turns"] for x in ps)), pct([x["turns"] for x in ps], .9),
            int(statistics.median(x["tools"] for x in ps)),
            int(statistics.median(tt)), pct(tt, .9),
            int(statistics.median(x["peak_ctx"] for x in ps)),
            int(statistics.median(x["out"] for x in ps)),
            sum(1 for x in ps if x["compactions"]), int(statistics.median(x["wall_min"] for x in ps))]))
    # floor: first-turn context of agents (cold start) approximated by min peak among small agents
    ag = [x for x in rows if x["worker"] == "agent"]
    if ag:
        print("agent cold-start proxy: min peak_ctx", min(x["peak_ctx"] for x in ag),
              "median peak_ctx", int(statistics.median(x["peak_ctx"] for x in ag)))
    # per-turn economics for shipped Sonnet work: context growth and turn buckets
    for w in ("agent", "session"):
        sh = [x for x in rows if x["worker"] == w and "sonnet" in (x["model"] or "") and x["turns"] >= 5]
        if sh:
            grow = [(x["last_ctx"] - x["first_ctx"]) / (x["turns"] - 1) for x in sh]
            print(f"{w} sonnet (>=5 turns, n={len(sh)}): median first_ctx {int(statistics.median(x['first_ctx'] for x in sh))}, "
                  f"median growth/turn {int(statistics.median(grow))}, turns<=15 {sum(x['turns']<=15 for x in sh)}, "
                  f"16-40 {sum(15<x['turns']<=40 for x in sh)}, >40 {sum(x['turns']>40 for x in sh)}")
    comp = [x for x in rows if x["compactions"]]
    print("sessions with compaction:", len(comp), "turns-per-compaction median:",
          int(statistics.median(x["turns"] / x["compactions"] for x in comp)) if comp else 0)
    if a.json:
        for p in rows:
            p["start"] = p["start"].isoformat() if p["start"] else None
            p["path"] = os.path.basename(p["path"])
        with open(a.json, "w", newline="\n") as f:
            json.dump(rows, f)


if __name__ == "__main__":
    sys.exit(main())
