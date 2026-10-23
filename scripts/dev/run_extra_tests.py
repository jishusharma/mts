#!/usr/bin/env python
"""run_extra_tests.py - run the tracked test files that live outside the dirs the main gate collects (B150).

Each file runs in its own pytest process with the file's directory as cwd (the way each was written to run), so same-named
helper modules in different dirs cannot collide. Files run MTS_GATE_JOBS at a time (default min(4, cpu count); 1 = one after
the other), each with its own --basetemp, and print their line when they finish. Exit 1 if any file fails. The list is checked by
MyTradingSys/tests/test_gate_discovery_b150.py: a new tracked test file must be gated, listed here, or skipped with a reason.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
EXTRA = [
    "scripts/dev/test_prereq_guard.py",
    "scripts/dev/test_offer_guard.py",
    "scripts/dev/test_trunk_lag.py",
    "scripts/dev/test_ci_split.py",
    "scripts/dev/test_no_syntax_warnings.py",
    "scripts/dev/test_preship.py",
    "MyTradingSys/research/gap_g3_shadow_fills_2026-10-18/test_shadow_fills.py",
    "MyTradingSys/research/layer_lab/formula_spec_text/test_formula_spec.py",
    "MyTradingSys/research/wavetrend_2026-10-17/test_wt_parity_ref.py",
    "MyTradingSys/research/wavetrend_2026-10-17/test_count_events.py",
    "scripts/dev/test_trial_ledger.py",
    "scripts/dev/test_soak_six_slots.py",
    "scripts/dev/test_hook_bench.py",
    "scripts/dev/test_interview_feed.py",
    "scripts/dev/test_trace.py",
    "scripts/dev/test_lab_query.py",
    "scripts/dev/test_health_audit.py",
    "scripts/dev/test_mts_doctor.py",
    "scripts/dev/test_prereg_gate.py",
    "scripts/dev/test_eagle_gaps.py",
    "scripts/dev/test_research_kit_lint.py",
    "MyTradingSys/research/layer_lab/context_fix2_mde_rule/test_mde_rule.py",
    "MyTradingSys/research/layer_lab/candle_pattern_event_table/test_patterns.py",
    "MyTradingSys/research/layer_lab/context_fix1_stop_strata/test_stop_strata.py",
    "MyTradingSys/research/layer_lab/bigtrade_event_table/test_event_table.py",
    "MyTradingSys/backtest/bigtrade/test_relabel_fires_split.py",
    "MyTradingSys/research/layer_lab/funding_extreme_event_table/test_event_table.py",
    "MyTradingSys/research/layer_lab/dev_split_guard/test_event_table.py",
    "MyTradingSys/research/layer_lab/oi_delta_event_table/test_event_table.py",
    "MyTradingSys/research/layer_lab/volume_event_table/test_event_table.py",
    "MyTradingSys/research/layer_lab/forward_excursion/test_event_table.py",
    "MyTradingSys/research/layer_lab/session_levels_event_table/test_event_table.py",
    "MyTradingSys/research/layer_lab/bb_top_reversal_event_table/test_event_table.py",
    "MyTradingSys/research/layer_lab/malkan_rsi_event_table/test_event_table.py",
    "MyTradingSys/research/layer_lab/rsi_reclaim_event_table/test_event_table.py",
    "MyTradingSys/research/layer_lab/cc_msb_event_table/test_event_table.py",
    "MyTradingSys/research/layer_lab/fabio_escalation_event_table/test_event_table.py",
    "MyTradingSys/research/layer_lab/rsi_divergence_event_table/test_event_table.py",
    "MyTradingSys/research/layer_lab/session_momentum_event_table/test_event_table.py",
    "MyTradingSys/research/layer_lab/turn_of_candle_event_table/test_event_table.py",
    "MyTradingSys/research/layer_lab/fabio_lvn_touch_event_table/test_event_table.py",
    "scripts/dev/test_lab_flow.py",
    "MyTradingSys/research/qriptal_2026-10-10/test_ledger.py",
    "MyTradingSys/research/qriptal_2026-10-10/test_score_calls.py",
    "MyTradingSys/research/imbalance_qriptal_2026-10-16/test_imb.py",
    "MyTradingSys/research/imbalance_qriptal_2026-10-16/filter/test_filter_join.py",
    "MyTradingSys/research/chart_read_g5_2026-10-16/test_common.py",
    "MyTradingSys/research/opr_preopen_tops_2026-10-16/test_study.py",
    "MyTradingSys/research/krown_malkan_g3_2026-10-16/test_event_counts.py",
    "MyTradingSys/research/opr_bb_mtf_center_2026-10-16/test_study.py",
    "MyTradingSys/research/opr_weekly_low_round_sweep_2026-10-16/test_study.py",
    "MyTradingSys/research/mal_bb_mid_engulf_2026-10-16/test_study.py",
    "MyTradingSys/research/layer_lab/candle_close_2026-10-14/test_study.py",
    "MyTradingSys/research/layer_lab/candle_close_2026-10-14/test_pre_reg_spec.py",
    "MyTradingSys/research/gross_effect_screen_2026-10-15/test_screen.py",
    "MyTradingSys/research/context_factors_pit_2026-10-16/test_context_asof.py",
    "MyTradingSys/research/context_null_2026-10-16/test_context_null.py",
    "MyTradingSys/research/context_factors_2026-10-16/test_context_asof.py",
    "MyTradingSys/research/context_factors_2026-10-16/test_study.py",
    "MyTradingSys/research/context_factors_2026-10-16/test_dev_ext.py",
    "MyTradingSys/research/pit_levels_2026-10-16/test_pit_leakage.py",
    "MyTradingSys/research/level_ledger_2026-10-16/test_level_ledger.py",
    "MyTradingSys/research/level_ledger_2026-10-16/test_zone_standard.py",
    "scripts/dev/test_suplock.py",
    "MyTradingSys/research/mfe_exit_2026-10-13/test_mfe_exit_study.py",
    "MyTradingSys/research/malkan_extract_2026-10-15/tools/test_check_numbers.py",
    "MyTradingSys/research/g3_marks_2026-10-16/test_g3_pack.py",
    "scripts/dev/test_make_layer_map.py",
    "scripts/dev/test_make_layers_board.py",
    "scripts/dev/test_session_log.py",
    "scripts/dev/test_codex_pack.py",
    "scripts/dev/test_token_audit.py",
    "MyTradingSys/research/test_b141_htf_stage1.py",
    "MyTradingSys/research/test_b141_htf_stage2.py",
    "MyTradingSys/execution/tests/test_deribit_orders_phase3.py",
    "MyTradingSys/execution/tests/test_executor_reject_diag.py",
    "MyTradingSys/observation/tests/test_observation.py",
    "MyTradingSys/research/candle_patterns_2026-10-04/pilot/test_p1.py",
    "MyTradingSys/research/candle_patterns_2026-10-04/pilot/test_pilot.py",
    "MyTradingSys/research/fast_track_2026-09-27/backtest_xcheck/test_ref_ladder.py",
    "MyTradingSys/research/volume_2026-10-09/test_state.py",
    "MyTradingSys/research/volume_2026-10-09/test_volume.py",
    "MyTradingSys/research/tom_btc_2026-10-13/test_chart_lab.py",
    "MyTradingSys/research/levels_confluence_2026-10-14/test_levels.py",
    "MyTradingSys/research/levels_confluence_2026-10-14/test_event_table.py",
    "MyTradingSys/runtime/test_update_market_state.py",
    "scripts/dev/test_testnet_canary.py",
    "scripts/worker/test_audit_digest.py",
    "scripts/worker/test_audit_rotation.py",
    "scripts/worker/test_audit_t0_checks.py",
    "tests/test_worker_prefix_hash.py",
    "scripts/dev/test_fabio_prescreen.py",
    "MyTradingSys/research/fabio_transfer/test_ledger_audit.py",
    "scripts/dev/test_asr_to_canonical.py",
    "scripts/dev/test_fetch_captions_channel.py",
    "scripts/dev/test_sched_scripts.py",
    "scripts/dev/test_run_extra_tests.py",
    "scripts/dev/test_ci_deps_lint.py",
    "scripts/dev/test_ci_watch.py",
    "scripts/dev/test_c_drive_guard.py",
    "scripts/dev/test_host_health.py",
]
STUDY_ROOT = "MyTradingSys/research/"


def discovered(repo=None):
    """Tracked test_*.py under a study folder that EXTRA does not list and run_all_tests.py does not name: they run
    without a hand-kept entry (2026-10-17 audit: the two-list registration cost ~100 commits and several red gates in 72 h)."""
    repo = Path(repo or REPO)
    out = subprocess.run(["git", "ls-files", "--", STUDY_ROOT], cwd=repo, capture_output=True, text=True).stdout.splitlines()
    gate_py = repo / "scripts" / "dev" / "run_all_tests.py"
    gate = gate_py.read_text(encoding="utf-8") if gate_py.exists() else ""
    return sorted(p for p in out if p.endswith(".py") and Path(p).name.startswith("test_") and "archive" not in p.lower()
                  and p not in EXTRA and f'"{Path(p).stem}"' not in gate and f"{Path(p).stem}.py" not in gate)


def all_tests(repo=None):
    return EXTRA + discovered(repo)


def jobs():
    """Concurrent pytest processes: MTS_GATE_JOBS (the gate's knob), default min(4, cpu count)."""
    try:
        n = int(os.environ.get("MTS_GATE_JOBS", ""))
    except ValueError:
        n = min(4, os.cpu_count() or 1)
    return max(1, n)


def run_one(rel, basetemp):
    """(ok, one-line result) for one extra test file: its own pytest process, cwd and basetemp."""
    p = REPO / rel
    if not p.exists():
        return False, "missing"
    r = subprocess.run([sys.executable, "-m", "pytest", p.name, "-q", "-p", "no:cacheprovider", f"--basetemp={basetemp}"],
                       cwd=p.parent, capture_output=True, text=True, errors="replace")
    tail = (r.stdout.strip().splitlines() or ["(no output)"])[-1]
    if r.returncode != 0:
        tail += failure_detail(r.stdout, r.stderr)
    return r.returncode == 0, tail


def failure_detail(stdout, stderr, n=30):
    """Last `n` lines of a failed file's pytest output, indented under its FAIL line, so a CI log shows the cause (2026-10-16:
    five files failed on the runners with only '1 error in 0.6s' in the log and passed on every desktop)."""
    lines = (stdout or "").strip().splitlines()[-n:] + (stderr or "").strip().splitlines()[-10:]
    return "".join(chr(10) + "        | " + ln[:300] for ln in lines)


def run_files(rels, n_jobs, one=run_one, tmp=None):
    """Run every file `n_jobs` at a time and print one flushed line per file as it finishes. Returns the failures in list order."""
    # Own basetemp per file: pytest's default %TEMP%/pytest-of-<user>/pytest-current cleanup raises PermissionError
    # (exit 1 after all tests pass) when another account left that link behind (JIS-NB 2026-10-14); it is also what lets
    # the files run beside each other.
    tmp = Path(tmp or tempfile.mkdtemp(prefix="mts_xt_"))
    lock = threading.Lock()
    done = {}

    def work(item):
        i, rel = item
        ok, tail = one(rel, tmp / str(i))
        with lock:
            print(f"{'ok  ' if ok else 'FAIL'} {rel}: {tail}", flush=True)
        done[rel] = (ok, tail)

    with ThreadPoolExecutor(max_workers=max(1, n_jobs)) as pool:
        list(pool.map(work, enumerate(rels)))
    return [f"{rel}: missing" if done[rel][1] == "missing" else rel for rel in rels if not done[rel][0]]


def pick(argv, tests):
    """`--only A B ...` (the smoke gate's subset, GATE_SPEED D6): those of `tests`, in list order; a name not in `tests` is an error
    (a typo must not pass as 'nothing to run'). No --only: every test."""
    if "--only" not in argv:
        return list(tests)
    want = [a.replace("\\", "/") for a in argv[argv.index("--only") + 1:]]
    unknown = [w for w in want if w not in tests]
    if unknown:
        raise SystemExit(f"run_extra_tests: not an extra test: {', '.join(unknown)}")
    return [t for t in tests if t in want]


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    try:
        sys.stdout.reconfigure(line_buffering=True, errors="replace")
    except (AttributeError, ValueError):
        pass
    tests = pick(argv, all_tests())
    tmp = Path(tempfile.mkdtemp(prefix="mts_xt_"))
    bad = run_files(tests, jobs(), tmp=tmp)
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"extra tests ({len(tests)} files): " + ("FAIL " + ", ".join(bad) if bad else "PASS"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
