"""T07 step 2: rerun a study from today's code (HEAD of this worktree) inside a sandbox copy, never over a result file.
The sandbox is out/sandbox/<run>/ : a copy of the study folder(s) and the repo files they import, at the same relative depth,
so HERE-relative writes (RESULT.md, ledger.csv ...) land in the sandbox. Data is read from F:/MTS/data (read-only, DEV bars only:
every loader refuses a bar >= 2024-07-01).
Usage (worktree root): python .../t07_rerun.py <study_key> [<run_tag>]
"""
import hashlib
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
R = REPO / "MyTradingSys" / "research"
SANDBOX = Path("C:/Users/E-ngineers/AppData/Local/Temp/dsa_audit/T07/sandbox")

# key -> (study folder, script, args, extra repo dirs/files to copy)
STUDIES = {
    "gross_effect_screen": ("gross_effect_screen_2026-10-15", "screen.py", ["--full"], []),
    "opr_preopen_tops": ("opr_preopen_tops_2026-10-16", "study.py", ["--full"], ["chart_read_g5_2026-10-16", "gross_effect_screen_2026-10-15"]),
    "mal_bb_mid_engulf": ("mal_bb_mid_engulf_2026-10-16", "study.py", ["--full"], ["chart_read_g5_2026-10-16", "gross_effect_screen_2026-10-15"]),
    "opr_bb_mtf_center": ("opr_bb_mtf_center_2026-10-16", "study.py", ["--full"], ["chart_read_g5_2026-10-16", "gross_effect_screen_2026-10-15"]),
    "opr_weekly_low_round_sweep": ("opr_weekly_low_round_sweep_2026-10-16", "study.py", ["--full"], ["chart_read_g5_2026-10-16", "gross_effect_screen_2026-10-15"]),
    "wlow_bounce_bbrsi60": ("wlow_bounce_bbrsi60_2026-10-16", "study.py", ["--run"], []),
    "krown_malkan_g3": ("krown_malkan_g3_2026-10-16", "event_counts.py", ["--data", "F:/MTS/data/krown_daily", "--out", "{study}"], []),
    "mfe_exit": ("mfe_exit_2026-10-13", "mfe_exit_study.py", [], []),
    "published_strats": ("published_strats_2026-10-13", "run_pub.py", ["dev"], []),
    "orderflow_views": ("orderflow_views_2026-10-14", "study.py", ["bt"], []),
    "qriptal_scorecard": ("qriptal_2026-10-10", "score_calls.py", ["run"], []),
}
# sandbox-only source patches (file under the study folder, old, new): the study hard-codes a data root that is absent on JIS-NB
PATCH = {"mfe_exit": ("mfe_exit_study.py", "raw_fund/fundingRate", "raw/fundingRate")}
ENV = {"mfe_exit": {"MFE_DEV_ONLY": "1"}, "orderflow_views": {"OFV_DEV_ONLY": "1"}}
REPO_EXTRA = {
    "wlow_bounce_bbrsi60": ["MyTradingSys/backtest/layers/wlow_bounce", "MyTradingSys/backtest/layers/rsi/rsi_core.py"],
    "krown_malkan_g3": ["MyTradingSys/backtest/layers/rsi", "MyTradingSys/backtest/power_mde.py"],
}
IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache")


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def build(key, tag):
    box = SANDBOX / f"{key}__{tag}"
    if box.exists():
        shutil.rmtree(box)
    folder, script, args, extra = STUDIES[key]
    for d in [folder] + extra:
        shutil.copytree(R / d, box / "MyTradingSys" / "research" / d, ignore=IGNORE)
    for rel in REPO_EXTRA.get(key, []):
        src = REPO / rel
        dst = box / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(src, dst, ignore=IGNORE)
        else:
            shutil.copy2(src, dst)
        # package markers on the way down
        par = src.parent
        while par != REPO:
            ini = par / "__init__.py"
            if ini.is_file():
                (box / ini.relative_to(REPO)).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ini, box / ini.relative_to(REPO))
            par = par.parent
    return box


def run(key, tag="a"):
    box = build(key, tag)
    folder, script, args, _ = STUDIES[key]
    t0 = time.time()
    if key in PATCH:
        pf, old, new = PATCH[key]
        fp = box / "MyTradingSys" / "research" / folder / pf
        txt = fp.read_text(encoding="utf-8")
        assert old in txt
        fp.write_text(txt.replace(old, new), encoding="utf-8", newline=chr(10))
    study_dir = str(box / "MyTradingSys" / "research" / folder)
    env = dict(os.environ, **ENV.get(key, {}))
    p = subprocess.run([sys.executable, "-B", study_dir + "/" + script, *[a.replace("{study}", study_dir) for a in args]],
                       capture_output=True, text=True, encoding="utf-8", cwd=str(box), env=env)
    dt_s = time.time() - t0
    (box / "stdout.txt").write_text(p.stdout, encoding="utf-8", newline="\n")
    (box / "stderr.txt").write_text(p.stderr, encoding="utf-8", newline="\n")
    print(f"{key} [{tag}] rc={p.returncode} {dt_s:.0f}s box={box}")
    if p.returncode:
        print(p.stderr[-1500:])
    return box / "MyTradingSys" / "research" / folder


if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "a")
