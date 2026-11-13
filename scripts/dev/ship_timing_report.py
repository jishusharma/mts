#!/usr/bin/env python3
"""Read-only ship-time report for a UTC window (SHIP_ARCH_REVIEW_2026-11-12 method, re-run by SHIP_REMEASURE_2026-11-13).

  python scripts/dev/ship_timing_report.py --since 2026-11-12T18:43:39Z --until 2026-11-20T18:43:39Z [--no-gh]

Sources: runtime_data/gate_timing.jsonl in every tree under --trees-root (ship_wall rows = whole ship wall time; `ship` rows = gate_mode,
gate_reason, phases), ~/.mts/gate_timing.jsonl (per-machine ship rows), %TEMP%/mts_gate_slots/wait.log (slot wait), `gh run list`
(CI on trunk), `git log origin/fast-track` (admin/merge commits). Anything a source cannot give prints NOT MEASURED, never an estimate.
Trees that were retired lose their log, so ship counts are a floor; the report prints how many trees it read."""
import argparse, glob, json, os, statistics, subprocess, sys, tempfile
from datetime import datetime, timezone
from pathlib import Path

SLOW_S = 300


def parse_utc(s):
    d = datetime.fromisoformat(str(s).strip().replace("Z", "+00:00"))
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def _rows(path):
    try:
        with open(path, encoding="utf-8", errors="ignore") as fh:
            for ln in fh:
                try:
                    r = json.loads(ln)
                    if isinstance(r, dict):
                        yield r
                except ValueError:
                    continue
    except OSError:
        return


def _in(ts, since, until):
    try:
        return since <= parse_utc(ts) < until
    except (ValueError, TypeError):
        return False


def pct(vals, p):
    if not vals:
        return None
    v = sorted(vals)
    return v[min(len(v) - 1, int(round(p * (len(v) - 1))))]


def collect_ships(trees_root, home_log, since, until):
    """-> (ships, ntrees). One ship = ship_wall row joined to its `ship` row by sha (within 120 s). Deduped on (utc, sha)."""
    walls, infos, ntrees = {}, {}, 0
    for p in glob.glob(os.path.join(trees_root, "*", "runtime_data", "gate_timing.jsonl")):
        ntrees += 1
        for r in _rows(p):
            if not _in(r.get("utc", ""), since, until):
                continue
            key = (r.get("utc"), r.get("sha"))
            if r.get("step") == "ship_wall":
                walls[key] = r
            elif r.get("step") == "ship":
                infos[key] = r
    for r in _rows(home_log):       # per-machine log: ship rows only; temp-dir trees are test fixtures
        if "mts_run_" in str(r.get("tree", "")) or not _in(r.get("utc", ""), since, until):
            continue
        if r.get("step") == "ship":
            infos.setdefault((r.get("utc"), r.get("sha")), r)
    by_sha = {}
    for (u, sha), r in infos.items():
        by_sha.setdefault(sha, []).append((parse_utc(u), r))
    ships = []
    for (u, sha), w in walls.items():
        tw = parse_utc(u)
        cand = [(abs((t - tw).total_seconds()), r) for t, r in by_sha.get(sha, []) if abs((t - tw).total_seconds()) <= 120]
        info = min(cand, key=lambda c: c[0])[1] if cand else {}
        ships.append({"utc": u, "sha": sha, "wall_s": float(w.get("secs") or 0), "ok": bool(w.get("ok")),
                      "failed_steps": w.get("failed_steps") or [], "gate_mode": info.get("gate_mode") or None,
                      "gate_reason": info.get("gate_reason") or None,
                      "slot_wait_s": (info.get("phases") or {}).get("slot_wait_s") if info else None})
    return sorted(ships, key=lambda s: s["utc"]), ntrees


def ship_stats(ships):
    n = len(ships)
    out = {"ships": n}
    if not n:
        return out
    walls = [s["wall_s"] / 60 for s in ships]
    tot = sum(walls)
    slow = [s for s in ships if s["wall_s"] >= SLOW_S]
    fail = [s for s in ships if not s["ok"]]
    modes, reasons = {}, {}
    for s in ships:
        k = s["gate_mode"] or "NOT RECORDED"
        modes[k] = modes.get(k, 0) + 1
        if s["gate_reason"]:
            rk = s["gate_reason"].split(";")[0][:48]
            reasons[rk] = reasons.get(rk, 0) + 1
    sw = [s["slot_wait_s"] for s in ships if s["slot_wait_s"] is not None]
    out.update(passed=n - len(fail), failed=len(fail), total_min=round(tot, 1), median_min=round(statistics.median(walls), 2),
               p90_min=round(pct(walls, 0.9), 2), under2=sum(1 for s in ships if s["wall_s"] < 120),
               slow_n=len(slow), slow_min=round(sum(s["wall_s"] for s in slow) / 60, 1),
               slow_share=round(100 * sum(s["wall_s"] for s in slow) / 60 / tot, 1) if tot else 0,
               failed_min=round(sum(s["wall_s"] for s in fail) / 60, 1), modes=modes, reasons=reasons,
               slot_wait_rows=len(sw), slot_wait_min=round(sum(sw) / 60, 1) if sw else None)
    return out


def slot_wait(path, since, until):
    rows = [r for r in _rows(path) if _in(r.get("ts", ""), since, until)]
    if not rows:
        return {"rows": 0}
    by = {}
    for r in rows:
        d = by.setdefault(r.get("mode", "?"), {"n": 0, "wait_min": 0.0, "max_min": 0.0})
        w = float(r.get("wait_s") or 0) / 60
        d["n"] += 1
        d["wait_min"] = round(d["wait_min"] + w, 1)
        d["max_min"] = round(max(d["max_min"], w), 1)
    return {"rows": len(rows), "by_mode": by}


def ci_stats(since, until):
    cmd = ["gh", "run", "list", "--branch", "fast-track", "--limit", "1500", "--created", ">=" + since.strftime("%Y-%m-%d"),
           "--json", "databaseId,conclusion,createdAt,updatedAt,event,headSha"]
    try:
        runs = json.loads(subprocess.run(cmd, capture_output=True, text=True, timeout=120, check=True,
                             creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0)).stdout)
    except Exception as e:
        return {"error": "NOT MEASURED (" + type(e).__name__ + ")"}
    runs = [r for r in runs if r.get("conclusion") in ("success", "failure") and _in(r["createdAt"], since, until)]
    runs.sort(key=lambda r: r["createdAt"])
    red = [r for r in runs if r["conclusion"] == "failure"]
    durs = [(parse_utc(r["updatedAt"]) - parse_utc(r["createdAt"])).total_seconds() / 60 for r in runs]
    # red episode = first red run's start until the next green run's finish (how long trunk stayed red)
    eps, start = [], None
    for r in runs:
        if r["conclusion"] == "failure" and start is None:
            start = parse_utc(r["createdAt"])
        elif r["conclusion"] == "success" and start is not None:
            eps.append((parse_utc(r["updatedAt"]) - start).total_seconds() / 60)
            start = None
    return {"runs": len(runs), "green": len(runs) - len(red), "red": len(red),
            "median_ci_min": round(statistics.median(durs), 1) if durs else None,
            "red_episodes": len(eps) + (1 if start is not None else 0), "red_minutes": round(sum(eps), 1), "red_still_open": start is not None}


def git_stats(repo, since, until):
    cmd = ["git", "-C", str(repo), "log", "origin/fast-track", "--since=" + since.isoformat(), "--until=" + until.isoformat(),
           "--name-only", "--format=%x01%H%x09%P%x09%s"]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=120, check=True,
                             creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0)).stdout
    except Exception as e:
        return {"error": "NOT MEASURED (" + type(e).__name__ + ")"}
    total = merges = admin = 0
    for blk in out.split("\x01")[1:]:
        lines = blk.split("\n")
        parents, subj = (lines[0].split("\t") + ["", "", ""])[1:3]
        files = [x for x in lines[1:] if x.strip()]
        total += 1
        if len(parents.split()) > 1:
            merges += 1
        elif not files or subj.startswith(("route tag", "TASK:", "desk task")):
            admin += 1
    return {"commits": total, "merges": merges, "admin": admin,
            "admin_merge_share": round(100 * (merges + admin) / total, 1) if total else None}


def report(since, until, repo, trees_root, home_log, wait_log, use_gh=True):
    ships, ntrees = collect_ships(trees_root, home_log, since, until)
    return {"since": since.isoformat(), "until": until.isoformat(), "trees_read": ntrees, "ship": ship_stats(ships),
            "wait_log": slot_wait(wait_log, since, until), "ci": ci_stats(since, until) if use_gh else {"error": "NOT MEASURED (--no-gh)"},
            "git": git_stats(repo, since, until)}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--since", required=True)
    ap.add_argument("--until", default=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    ap.add_argument("--repo", default=str(Path(__file__).resolve().parents[2]))
    ap.add_argument("--trees-root", default=str(Path(__file__).resolve().parents[3]))
    ap.add_argument("--home-log", default=str(Path.home() / ".mts" / "gate_timing.jsonl"))
    ap.add_argument("--wait-log", default=os.path.join(tempfile.gettempdir(), "mts_gate_slots", "wait.log"))
    ap.add_argument("--no-gh", action="store_true")
    a = ap.parse_args(argv)
    print(json.dumps(report(parse_utc(a.since), parse_utc(a.until), a.repo, a.trees_root, a.home_log, a.wait_log, not a.no_gh), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
