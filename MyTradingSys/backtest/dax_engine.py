"""Run the Java engine's archive mode on a non-BTC symbol (DAX probe, research/tom_transfer_2026-10-11/PROBE_PLAN.md).

Compiles src/main + the harness SnapAt/TomSnapshotGen into a temp copy (never src/ or target/), runs from an empty cwd
with -Dmts.symbol=<SYMBOL>. Jars as in shot.py (engine_jars). JDK 17 first on PATH (C:/tools/jdk-17.0.18/bin).
  python MyTradingSys/backtest/dax_engine.py snap --raw F:/MTS/data/dax_archive --at 2026-05-12T08:05:00Z [...] --out snaps.jsonl
  python MyTradingSys/backtest/dax_engine.py fade --raw F:/MTS/data/dax_archive --dates dates.txt --out fires.jsonl [--shards 8]
                                                  (card tom-v2-recall-fire-rate: every window minute of those Berlin dates, fade call only)
  python MyTradingSys/backtest/dax_engine.py gen  --raw F:/MTS/data/dax_archive --out F:/MTS/data/dax_snapshots
                                                  --start 2025-01-06T00:00:00Z --end 2026-10-10T00:00:00Z [--step 15]
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "dev"))
import shot  # noqa: E402  (engine_jars)

HARNESS = REPO / "MyTradingSys" / "research" / "core_readiness_2026-09-27" / "harness" / "java"


def build(tmp):
    src, out = tmp / "src", tmp / "out"
    src.mkdir(); out.mkdir()
    for f in sorted((REPO / "src" / "main" / "java" / "datafeed").glob("*.java")) + [HARNESS / "SnapAt.java", HARNESS / "TomSnapshotGen.java", HARNESS / "FadeReplay.java"]:
        shutil.copy2(f, src / f.name)
    cp = os.pathsep.join(shot.engine_jars())
    r = subprocess.run(["javac", "-nowarn", "-encoding", "UTF-8", "-d", str(out), "-cp", cp, *sorted(str(f) for f in src.glob("*.java"))],
                       capture_output=True, text=True)
    if r.returncode:
        raise SystemExit("javac failed: " + (r.stderr or r.stdout)[-1500:])
    return str(out) + os.pathsep + cp


def java_cmd(cp, symbol, main, args, spike_fade=False):
    """Command line; -Dmts.spikeFade=true only when asked (card tom-encode-spike-fade, default off)."""
    flags = [f"-Dmts.symbol={symbol}"] + (["-Dmts.spikeFade=true"] if spike_fade else [])
    return ["java", "-Xmx3g", *flags, "-cp", cp, main, *args]


def java(cp, symbol, main, args, tmp, spike_fade=False):
    cwd = tmp / "cwd"
    cwd.mkdir(exist_ok=True)
    r = subprocess.run(java_cmd(cp, symbol, main, args, spike_fade), cwd=str(cwd), text=True)
    if r.returncode:
        raise SystemExit(f"{main} failed rc={r.returncode}")


def main(argv=None):
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("snap"); s.add_argument("--raw", required=True); s.add_argument("--at", nargs="+", required=True)
    s.add_argument("--out", required=True); s.add_argument("--symbol", default="GER40")
    g = sp.add_parser("gen"); g.add_argument("--raw", required=True); g.add_argument("--out", required=True)
    g.add_argument("--start", required=True); g.add_argument("--end", required=True); g.add_argument("--step", default="15")
    g.add_argument("--symbol", default="GER40"); g.add_argument("--shards", type=int, default=1)
    f = sp.add_parser("fade"); f.add_argument("--raw", required=True); f.add_argument("--dates", required=True)
    f.add_argument("--out", required=True); f.add_argument("--symbol", default="GER40"); f.add_argument("--shards", type=int, default=4)
    for q in (s, g):
        q.add_argument("--spike-fade", action="store_true", help="emit family A fade_short candidates (-Dmts.spikeFade=true)")
    x = ap.parse_args(argv)
    tmp = Path(tempfile.mkdtemp(prefix="mts_dax_"))
    try:
        cp = build(tmp)
        if x.cmd == "snap":
            inst = tmp / "instants.txt"
            inst.write_text("\n".join(x.at) + "\n", encoding="utf-8", newline="\n")
            java(cp, x.symbol, "datafeed.SnapAt", [x.raw, str(inst), str(Path(x.out).resolve())], tmp, x.spike_fade)
        elif x.cmd == "fade":
            procs = []
            for k in range(x.shards):
                part = Path(str(x.out) + f".part{k}")
                cmd = java_cmd(cp, x.symbol, "datafeed.FadeReplay", [x.raw, str(Path(x.dates).resolve()), str(part.resolve()), str(k), str(x.shards)], True)
                (tmp / f"cwd{k}").mkdir()
                procs.append((part, subprocess.Popen(cmd, cwd=str(tmp / f"cwd{k}"), text=True)))
            bad = [str(p) for p, pr in procs if pr.wait()]
            if bad:
                raise SystemExit("FadeReplay failed: " + ", ".join(bad))
            with open(x.out, "w", encoding="utf-8", newline="\n") as o:
                for part, _ in procs:
                    o.write(part.read_text(encoding="utf-8"))
                    part.unlink()
        else:
            for k in range(x.shards):  # sequential shards keep memory bounded; months are dealt round-robin
                java(cp, x.symbol, "datafeed.TomSnapshotGen", [x.raw, x.out, x.start, x.end, x.step, str(k), str(x.shards)], tmp, x.spike_fade)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
