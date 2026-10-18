#!/usr/bin/env python3
"""Build EVIDENCE_REGISTER.json / EVIDENCE_REGISTER.md (roadmap P0-A).

Each citation is (path, needle): the needle must be an exact substring of one line of that file.
The builder resolves it to a line number and the file's sha256; verify_register.py re-checks both,
so a citation either resolves or the check fails. Run from anywhere:
    python build_register.py            # writes JSON + MD next to this file
    python verify_register.py           # exits 1 on any unresolved citation
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]          # repo root (MyTradingSys/research/<dir> -> three up)
REGISTER_VERSION = "1.0.0"
AS_OF = "2026-10-12"

L = "MyTradingSys/backtest/layers/"
RES = "MyTradingSys/research/"

# --- row schema -----------------------------------------------------------------------------
# id, system, identity (exact variant), source_role, code, fidelity, statistics (historical kept
# beside current), calibration, deployment, unknowns, missing_inputs, next_gate, cites{field: [(path, needle)]}
# fidelity enum: FAITHFUL | PARTIAL | MISMATCH | UNKNOWN | NA


def row(**k):
    return k


ROWS = [
    row(id="ER-01", system="RSI calculation (Wilder, period 14)",
        identity="rsi_core.rsi_core(closes, period=14); flat series -> 50 by documented convention",
        source_role="Standard indicator definition (FORMULAS.md); no trader-specific source needed",
        fidelity="FAITHFUL",
        statistics={"historical": "n/a (calculation, not a strategy)",
                    "current": "REPRODUCED: period-3 worked case 83.333333 then 66.666667 matches; 134 rsi tests pass on fast-track"},
        calibration="n/a", deployment="CODE: used by every RSI consumer; deployment SHA UNKNOWN (mirror stale)",
        unknowns=["Warm-up/missing-value parity with a charting platform on real series"],
        missing_inputs=["Platform export of RSI(14) for one real BTC 1h series (golden fixture)"],
        next_gate="Golden fixture from a real chart export matches to 1e-6 after warm-up",
        cites={"code": [(L + "rsi/rsi_core.py", "def rsi_core(closes: List[float], period: int = 14)")],
               "tests": [(RES + "non_core_layer_audit_2026-10-12/tests_rsi.txt", "")]}),
    row(id="ER-02", system="RSI level events (live: 40-support long, 0.5 tolerance)",
        identity="live_layers RSI_LEVEL=40.0, RSI_TOL=0.5 via rsi_events(); D3 study identity: 1h, 40-support, tol 0.5, 5-bar return",
        source_role="Level 40 = Malkan concept (CONCEPT-ONLY). Tolerance 0.5 = lowest value of the D3 grid 0.5..5.0 chosen by best in-sample return (NO-SOURCE R25). params/default.json tolerance 0 is rejected by the consumer (R04) and is not read by production code (only tests)",
        fidelity="MISMATCH",
        statistics={"historical": "D3 1h OOS n=89, gross +0.043%, PBO 0.030 (RECORDED); below 10 bp round trip",
                    "current": "No edge shown; tolerance is an in-sample boundary pick, so the 0.5 live value is unsourced"},
        calibration="Live RSI 5m/15m/1h closed rows exist in stale mirror (RSI 5m 48, 15m 13, 1h 4); not an experiment",
        deployment="CODE: registered 5m/15m/1h; running process/version UNKNOWN",
        unknowns=["Whether the live 0.5 tolerance was ever re-derived from a source",
                  "Which event types (support/rejection/failure/cross) the executed trades came from"],
        missing_inputs=["Event-level outcome rows with event type and side", "Deployed config SHA"],
        next_gate="One versioned event->side->exit identity used by both research and calibration; tolerance either sourced or labelled operator hypothesis",
        cites={"code": [(L + "alerts/live_layers.py", "RSI_TOL = 0.5"), (L + "alerts/live_layers.py", "RSI_LEVEL = 40.0"),
                        (L + "rsi/rsi_events.py", 'raise ValueError("tolerance must be > 0")'),
                        (L + "rsi/params/default.json", '"tolerance": 0,')],
               "provenance": [(RES + "LAYER_PROVENANCE_AUDIT.md", "| R04 |"), (RES + "LAYER_PROVENANCE_AUDIT.md", "| R25 |"),
                              (RES + "LAYER_PROVENANCE_AUDIT.md", "| R26 |")],
               "stats": [(L + "BACKTEST_L1_REPORT.md", "## D3 tolerance study")]}),
    row(id="ER-03", system="Malkan 40/60 single-timeframe (regime + candle at 40/60)",
        identity="malkan_regime(lo=40,hi=60,lookback=20) + malkan_setup_bull/bear(tolerance=2.0, candle required)",
        source_role="40/60 bull/bear ranges and candle confirmation: sourced concept (R12). Regime lookback 20 has no source window (R11 CONCEPT-ONLY). Event tolerance 2.0 (this layer) differs from live ER-02 tolerance 0.5",
        fidelity="PARTIAL",
        statistics={"historical": "Generic 1%/2% bracket: 1h n=43 net -0.092% PBO .760; 4h n=17; 1d n=5 (RECORDED)",
                    "current": "Rejects the tested proxy, not the complete Malkan entry; regime BULL can hold while current RSI is 45 (REPRODUCED), which matches a range-shift definition but is not a threshold gate"},
        calibration="No closed Malkan rows in stale mirror (unexplained: rare vs routing vs rejection)",
        deployment="CODE: malkan_bull/malkan_bear 1h registered; running version UNKNOWN",
        unknowns=["Complete daily entry/stop/target and HTF conditions", "Why the mirror has no closed Malkan rows"],
        missing_inputs=["Source ledger with frames (P0-B)", "Funnel logs: detector -> alert -> plan -> fill"],
        next_gate="Own-source rule ledger resolves target/confirmation/HTF gates or marks them UNKNOWN; only then a frozen strategy run",
        cites={"code": [(L + "rsi/malkan_40_60.py", "def malkan_regime(rsi: list"),
                        (L + "rsi/params/malkan_40_60_default.json", '"regime_lookback": 20,'),
                        (L + "rsi/params/malkan_40_60_default.json", '"event_tolerance": 2,')],
               "provenance": [(RES + "LAYER_PROVENANCE_AUDIT.md", "| R11 |"), (RES + "LAYER_PROVENANCE_AUDIT.md", "| R12 |")]}),
    row(id="ER-04", system="Malkan multi-timeframe composer",
        identity="malkan_mtf_bull/bear using state_asof on weekly/monthly regime strings",
        source_role="Higher-timeframe agreement is sourced as a concept; gates are regime strings not current weekly/monthly RSI thresholds",
        fidelity="PARTIAL",
        statistics={"historical": "No full-strategy MTF run receipt located on this machine",
                    "current": "UNKNOWN: absence locally does not prove global absence"},
        calibration="none", deployment="CODE only; not a registered live key",
        unknowns=["Whether a full MTF run exists on another machine"],
        missing_inputs=["Run manifest from data owner", "Explicit bar-open vs bar-close availability field"],
        next_gate="Causal HTF test: timestamps carry available_at; no query returns a bar closing after the signal",
        cites={"code": [(L + "rsi/malkan_mtf.py", "def state_asof(times: list, values: list, t: int):"),
                        (L + "rsi/malkan_mtf.py", "def malkan_mtf_bull(bars: list, rsi: list, daily_regime: list")]}),
    row(id="ER-05", system="RSI divergence (Malkan-window detector + operator variants)",
        identity="rsi_divergence(close, rsi, ts, min_bars=3, max_bars=10) from malkan_divergence_default.json; 19 TF x 2 columns x 2 sides + T088 extension",
        source_role="Close-to-close, 3-10 bars, confirmation: quoted (four extract quote gates pass). Pivot rule, triggers, targets C and partial exits are not sourced",
        fidelity="PARTIAL",
        statistics={"historical": "92 cells: 36 NO EDGE, 56 INSUFFICIENT-N, 0 edge candidates (RECORDED, regenerated exactly)",
                    "current": "Raw ten-bar forward-return event study less 0.10% fee; overlapping events; not a strategy. 1h operator bearish n=332 net +0.038% t=0.39 is not evidence"},
        calibration="none", deployment="Research only; no live key",
        unknowns=["Detection precision/recall against annotated source charts"],
        missing_inputs=["Per-event outcome rows", "Source frames for target C"],
        next_gate="Event rows exported; recall/false-positive measured on held-back source examples before any strategy exit is encoded",
        cites={"code": [(L + "rsi/rsi_divergence.py", "def rsi_divergence(close: list"),
                        (L + "rsi/params/malkan_divergence_default.json", '"min_bars_quote": "How many candles are needed? Three."')],
               "stats": [(RES + "rsi_divergence_mtf_2026-10-09/RESULT.md", "# T089 + T091 result"),
                         (RES + "t090_7h_2026-10-09/RESULT.md", "# T090 7h research")]}),
    row(id="ER-06", system="RSI reclaim / 2a / long-range operator ideas",
        identity="rsi_reclaim_events + rsi_retest; operator hypothesis 2a spec",
        source_role="Operator hypothesis, separate from Malkan rules (label must stay)",
        fidelity="UNKNOWN",
        statistics={"historical": "Higher-timeframe leads small-n and anchor-dependent (6h/7h: n 35-55, 3 of 18 cells t>2) RECORDED",
                    "current": "Unvalidated, underpowered; no promotion"},
        calibration="none", deployment="Research only",
        unknowns=["Frozen confluence definition (BB, CVD/OI, RSI-MA, speed trigger)"],
        missing_inputs=["Preregistered hypothesis; untouched period or symbols"],
        next_gate="Frozen spec + trial registry entry before any run; new combinations counted as new trials",
        cites={"code": [(L + "rsi/rsi_reclaim.py", "def rsi_reclaim_events(")],
               "spec": [(RES + "rsi_2a_2026-10-09/RSI_2A_SPEC.md", "")]}),
    row(id="ER-07", system="WaveTrend with Crosses [LazyBear]",
        identity="Designed only: n1=10, n2=21, wt2=SMA(wt1,4), const 0.015, levels +-60/+-53 (T061). No implementation",
        source_role="T3 practitioner indicator, [SCREENER] tag; no engine rule. T065 records the Pine source was opened and read on 2026-10-05 (not re-verified here)",
        fidelity="UNKNOWN",
        statistics={"historical": "none", "current": "No backtest, no output; not a failed layer"},
        calibration="none", deployment="Parked on Layer Board; not registered",
        unknowns=["Exact Pine version and licence terms", "EMA seeding (Pine: first source value, to confirm against saved source)",
                  "Zero-deviation (d=0) behaviour", "Which of layers/wavetrend/ vs layers/momentum/wavetrend.py owns it"],
        missing_inputs=["Saved Pine source snapshot", "Chart export for flat, trending, alternating and one real series"],
        next_gate="One module path; golden fixtures reproduce exported values; warm-up, d=0, equality and closed-bar tests pass; observation-only, no side inferred",
        cites={"spec": [(  "MyTradingSys/items/T061_wavetrend_lazybear.md", "wt2   = SMA(wt1, 4)"),
                        ("MyTradingSys/items/T061_wavetrend_lazybear.md", "Overbought Level 2 = 53")],
               "survey": [(RES + "T065_LAZYBEAR_SURVEY.md", "## 0. Evidence status")],
               "board": [("MyTradingSys/system/control_room.json", '"id": "wavetrend",')]}),
    row(id="ER-08", system="Other LazyBear indicators (Squeeze, Better Volume, VFI)",
        identity="Shortlisted designs in T065; none built",
        source_role="Pine sources read 2026-10-05 [PINE]; Squeeze author's updated source not opened",
        fidelity="UNKNOWN",
        statistics={"historical": "none (T3, no MTS backtest)", "current": "none"},
        calibration="none", deployment="none",
        unknowns=["Squeeze BB multiplier: displayed source vs corrected version", "VFI is not measured aggressor CVD"],
        missing_inputs=["Updated Squeeze source", "Chart parity exports"],
        next_gate="Source-version decision recorded per indicator before any code",
        cites={"survey": [(RES + "T065_LAZYBEAR_SURVEY.md", "Not verified: the Squeeze Momentum author's *updated* source")]}),
    row(id="ER-09", system="CryptoCred setups (SR flip, fib pullback, failed MSB)",
        identity="cc_setups.setup1/2 target_r=1.5, setup3 target_r=2.0; 0.1% stop buffer; live uses generic bracket",
        source_role="Structure/retest concepts sourced. 1.5 and 2 are the trader's MINIMUM R:R (counter-trend demands more), used in code as fixed take-profits: role swap (C15, C24). Buffer 0.1% NO-SOURCE",
        fidelity="MISMATCH",
        statistics={"historical": "Fill-bias corrections recorded; setups not S3-validated (RECORDED)",
                    "current": "Not evidence of edge in either direction under native geometry"},
        calibration="Stale mirror closed: SR flip 15m 19, 1h 2; fib 15m 7; failed MSB 15m 1 (event counts, not reconciled)",
        deployment="CODE: auto_trader.layer_signal builds market plan from configured stop_pct/targets, ignoring native entry/stop",
        unknowns=["Own-source instruction for fixed exits", "Whether live and backtest exits are the same experiment"],
        missing_inputs=["Canonical ledger", "Deployed config SHA"],
        next_gate="Role-level provenance corrected; live-vs-backtest contract written with distinct experiment ids",
        cites={"code": [(L + "cryptocred/cc_setups.py", "target_r: float = 1.5"),
                        ("MyTradingSys/execution/auto_trader.py", "def layer_signal(alert: dict, cfg: dict, now: datetime)")],
               "provenance": [(RES + "LAYER_PROVENANCE_AUDIT.md", "| C15 |"), (RES + "LAYER_PROVENANCE_AUDIT.md", "| C24 |")],
               "source": [("extracts/processed/cryptocred/extract_BHwoN7VPrBE.md", "greater minimum risk reward requirements")]}),
    row(id="ER-10", system="Positioning / funding-CVD fade",
        identity="funding_cvd_fade_events(lookback=90, n=20, hi=0.95 ...)",
        source_role="Concept only; lookback 20 is the project's own hypothesis (P05 NO-SOURCE)",
        fidelity="PARTIAL",
        statistics={"historical": "Full-funding rerun n=76 net -0.0453% (fails gate; RECORDED)",
                    "current": "Negative; reopen only with a materially different sourced hypothesis"},
        calibration="No closed rows in stale mirror", deployment="CODE: positioning|funding_cvd_fade|1h registered; defaults differ from research variant",
        unknowns=["Raw CVD/funding coverage for the research window"], missing_inputs=["Data manifest"],
        next_gate="Variant identity frozen (research == live defaults or explicitly separate)",
        cites={"code": [(L + "positioning/funding_cvd_fade.py", "def funding_cvd_fade_events(")],
               "provenance": [(RES + "LAYER_PROVENANCE_AUDIT.md", "| P05 |")],
               "stats": [(RES + "fast_track_2026-09-27/T055_BT_RERUN_FULLFUNDING_2026-10-07.md", "# T055 C1/C2 RERUN, full funding")]}),
    row(id="ER-11", system="Session momentum",
        identity="session_momentum_events(); research NY-open 60 min vs live UTC 30 min default",
        source_role="Session concept; window lengths unsourced",
        fidelity="MISMATCH",
        statistics={"historical": "n=299 net +0.0177% Sharpe .0084, 1 of 2 OOS years positive (RECORDED, fails gate)",
                    "current": "Tiny, inconsistent; variant differs from live"},
        calibration="5 closed session rows in stale mirror", deployment="CODE: session|session_momentum|15m registered",
        unknowns=["Intended sourced/adapted session contract"], missing_inputs=["Per-year and per-session risk-adjusted table"],
        next_gate="Test exactly the intended contract; report per-year; do not retrofit research variant to live",
        cites={"code": [(L + "session/session_momentum.py", "def session_momentum_events(")],
               "stats": [(RES + "fast_track_2026-09-27/T055_BT_RERUN_FULLFUNDING_2026-10-07.md", "## Result")]}),
    row(id="ER-12", system="Turn of candle",
        identity="turn_of_candle_events(lead_minutes=1); live adapter enters at minute 14 using minute-0 imbalance",
        source_role="Operational timing sample; explicitly tagged calibration",
        fidelity="MISMATCH",
        statistics={"historical": "49,823 OOS events, ~0 gross, net -0.1201% (RECORDED); imbalance variants fail",
                    "current": "High frequency is not edge; research enters at opening-window close, live at minute 14"},
        calibration="548 closed rows in stale mirror: calibration ledger, not validation", deployment="CODE: turn_of_candle|1m registered",
        unknowns=["Exact timing parity between research entry and live entry"], missing_inputs=["Entry timestamps per event"],
        next_gate="Timing reconciled; calibration results kept separate from strategy evidence",
        cites={"code": [(L + "turn_of_candle/turn_of_candle.py", "def turn_of_candle_events(")],
               "stats": [(RES + "fast_track_2026-09-27/T055_BT_c3.md", "# T055 backtest - C3")]}),
    row(id="ER-13", system="Session levels / failed first break",
        identity="session_levels.py: ASIA_END 480, US_OPEN 840, FAIL_WINDOW 60 min (placeholders)",
        source_role="Clocks, failure window and targets are placeholders",
        fidelity="PARTIAL",
        statistics={"historical": "Cells with sufficient n negative (RECORDED)", "current": "No parameter search to rescue"},
        calibration="none", deployment="Research only",
        unknowns=["Justified session boundaries"], missing_inputs=["Event rows; like-for-like null"],
        next_gate="Event rows + justified boundaries + matched null",
        cites={"code": [(L + "session_levels/session_levels.py", "FAIL_WINDOW_MIN = 60")],
               "stats": [(RES + "t087_session_levels_2026-10-09/RESULT.md", "# T087 failed first break")]}),
    row(id="ER-14", system="Tick / extreme flags",
        identity="tick_flagger tiers from build_tiers (1m klines 2022-01.., aggTrades 90d window)",
        source_role="Ranking/tier tables; no trader source",
        fidelity="UNKNOWN",
        statistics={"historical": "Flag rate 0.11/day on aggTrades window (RECORDED)", "current": "Rare flags do not prove predictiveness"},
        calibration="none", deployment="Not in default registry",
        unknowns=["Why kline vs aggTrades delta differs (max 68.25 BTC over 126,720 bars). missing_in_klines=2880 is exactly 2x1440, i.e. two whole days absent, which explains the missing count but not the delta gap; distribution of differences not recorded"],
        missing_inputs=["Raw 1m klines for the compared window (Dumps/backtest/raw_1m_2022 absent on this machine)", "Per-bar difference list"],
        next_gate="Mismatch mechanism identified; builder wording corrected or data fixed; no threshold promotion before",
        cites={"code": [(L + "tick/build_tiers.py", "identical to the aggTrades 1m delta"),
                        (L + "tick/tiers_meta.json", '"max_abs_delta_diff_btc"'),
                        (L + "tick/tick_flagger.py", "def make_flag(")]}),
    row(id="ER-15", system="Timeframe resampling infrastructure",
        identity="tf_resample.resample/bucket_start/bucket_end with registry.json anchors",
        source_role="Infrastructure",
        fidelity="PARTIAL",
        statistics={"historical": "n/a", "current": "REPRODUCED: gapped bucket returned with gap_count=20,n_bars=40; the divergence driver does not read gap_count, so the info exists but is not enforced"},
        calibration="n/a", deployment="CODE",
        unknowns=["Impact of gapped closed buckets on divergence results"],
        missing_inputs=["Per-event gap_count in export"],
        next_gate="Consumer filters or reports gap_count>0; variable-duration buckets not described as uniform 7h",
        cites={"code": [(L + "timeframe/tf_resample.py", "gap_count = max(0, n_expected - n_bars)"),
                        (L + "timeframe/tf_realdata_gate.py", 'if bucket["gap_count"] != 0:')]}),
    row(id="ER-16", system="Consensus / RSI observation hook",
        identity="consensus_after_poll(): one row per firing poll; RSI value from latest RSI event",
        source_role="Observation only; not voting",
        fidelity="PARTIAL",
        statistics={"historical": "n/a", "current": "52 tests pass; README says nothing calls it, which is stale"},
        calibration="n/a", deployment="CODE: hook wired in live runner; running state UNKNOWN",
        unknowns=["Write-failure accounting"], missing_inputs=["Freshness tag spec"],
        next_gate="as-of/age fields so stale RSI cannot look current; README corrected",
        cites={"code": [(L + "consensus/hook.py", "def consensus_after_poll(")],
               "doc": [(L + "consensus/README.md", "## Status: nothing calls it yet")]}),
    row(id="ER-17", system="MA / candle / volume research",
        identity="P1 candle patterns (DEV), V3 RSI-volume validation",
        source_role="Screening research; stage labels must be preserved",
        fidelity="NA",
        statistics={"historical": "V3 candidate n=50 net -2 bp CI [-68,+64] INSUFFICIENT-N vs min 100; candle results DEV triage",
                    "current": "No validated standalone entry system"},
        calibration="none", deployment="none",
        unknowns=["Whether frozen candidates survive on unseen data"], missing_inputs=["Reserved data"],
        next_gate="Frozen candidates only; event rows; multiplicity control",
        cites={"stats": [(RES + "volume_2026-10-09/V3_VALIDATION_RESULTS.md", "# V3 VALIDATION RESULTS"),
                         (RES + "candle_patterns_2026-10-04/P1_RESULTS.md", "# P1 RESULTS")]}),
    row(id="ER-18", system="Kurisko candidate",
        identity="Four-stochastic vs four-RSI source conflict; not encoded",
        source_role="Source unresolved", fidelity="UNKNOWN",
        statistics={"historical": "none", "current": "none"},
        calibration="none", deployment="none",
        unknowns=["Oscillator definition, third setting, trigger, market translation"],
        missing_inputs=["Primary chart/source confirmation"],
        next_gate="Source confirmation before any parameter set",
        cites={"history": [(RES + "rsi_kurisko_2026-10-09/RSI_HISTORY.md", "# RSI line of work")]}),
    row(id="ER-19", system="Probability / options / analyst-caller feeds (inventory only)",
        identity="prob_table.py, cbp_adapter.py exist; not deeply audited",
        source_role="n/a", fidelity="UNKNOWN",
        statistics={"historical": "not audited", "current": "UNKNOWN, not passed"},
        calibration="not audited", deployment="not audited",
        unknowns=["Calibration, feed integrity, execution readiness"], missing_inputs=["Dedicated audit"],
        next_gate="Separate calibration and feed-integrity audit",
        cites={"code": [("MyTradingSys/backtest/prob_table.py", "")]}),
]

# Cross-cutting findings that change how rows should be read (added by the 2026-10-12 review).
REVIEW_NOTES = [
    "ER-02: the audit's 'tolerance 0 invalid' finding was already provenance-logged as R04/Q3; the open question (what does the live runner pass?) is answered: live_layers passes 0.5 and default.json is read only by tests. New: 0.5 is the boundary value of an in-sample grid, so it is itself NO-SOURCE.",
    "ER-03: a live tolerance of 0.5 (ER-02) and 2.0 (ER-03 params, labelled source MalkanView) coexist for the same 40 level; the two are different experiments and must not share a label.",
    "ER-15: the audit asked for a 'duration field'; gap_count and n_bars already exist per bucket. The defect is consumer-side (not read), not schema-side.",
    "ER-14: 2880 missing bars is exactly two days; narrows the mechanism question but does not settle the 68.25 BTC maximum.",
    "ER-05: independent recount from summary.json/summary_T088.json at horizon 10 gives 92 cells, 36 with n>=300 (35 net negative, one +0.038% t=0.39), 56 insufficient. All 36 powered cells are on 1m-2h; gross spans -18 to +14 bp against a 10 bp fee, so the result is a fee-and-power statement about low timeframes, not a measurement of divergence information on 4h/1d where n is too small.",
    "Roadmap P0-A deliverable is the register; roadmap wording caveat stands: a fixed bracket is not a proven lower bound on source management.",
]


def resolve(path, needle):
    p = ROOT / path
    if not p.is_file():
        return {"path": path, "needle": needle, "ok": False, "why": "file missing"}
    data = p.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    if not needle:
        return {"path": path, "needle": "", "line": 1, "sha256": sha, "ok": True}
    for i, ln in enumerate(data.decode("utf-8", "replace").splitlines(), 1):
        if needle in ln:
            return {"path": path, "needle": needle, "line": i, "sha256": sha, "ok": True}
    return {"path": path, "needle": needle, "ok": False, "why": "needle not found"}


def main():
    out_rows, bad = [], 0
    for r in ROWS:
        r = dict(r)
        cites = {k: [resolve(p, n) for p, n in v] for k, v in r.pop("cites").items()}
        bad += sum(1 for v in cites.values() for c in v if not c["ok"])
        r["citations"] = cites
        out_rows.append(r)
    reg = {"register_version": REGISTER_VERSION, "as_of": AS_OF,
           "scope": "non-core layers; Tom and Fabio excluded (owned by parallel sessions)",
           "supersedes": "REPORT.md layer table (GPT, 2026-10-12) - historical verdicts preserved in 'statistics.historical'",
           "unknown_policy": "missing proof is UNKNOWN; no row asserts deployment from repo wiring alone",
           "mirror_stale": "mirror@2026-10-11T20:09:30Z",
           "review_notes": REVIEW_NOTES, "rows": out_rows}
    (HERE / "EVIDENCE_REGISTER.json").write_text(json.dumps(reg, indent=1) + "\n", encoding="utf-8", newline="\n")
    md = ["# Evidence register v%s (as of %s)\n" % (REGISTER_VERSION, AS_OF),
          "Machine-readable twin: `EVIDENCE_REGISTER.json`; check with `verify_register.py`. "
          "Fidelity: FAITHFUL | PARTIAL | MISMATCH | UNKNOWN | NA. Historical verdicts are kept beside the current assessment.\n",
          "| ID | System | Fidelity | Historical verdict | Current assessment | Calibration | Deployment | Next acceptance gate |",
          "|---|---|---|---|---|---|---|---|"]
    for r in out_rows:
        md.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (
            r["id"], r["system"], r["fidelity"], r["statistics"]["historical"], r["statistics"]["current"],
            r["calibration"], r["deployment"], r["next_gate"]))
    md.append("\n## Unknowns and missing inputs\n")
    for r in out_rows:
        md.append("**%s %s**" % (r["id"], r["system"]))
        md.extend("- UNKNOWN: " + u for u in r["unknowns"])
        md.extend("- NEEDS: " + m for m in r["missing_inputs"])
        md.append("")
    md.append("## Review notes (2026-10-12)\n")
    md.extend("- " + n for n in REVIEW_NOTES)
    md.append("\n## Citations\n")
    for r in out_rows:
        md.append("**%s**" % r["id"])
        for k, v in r["citations"].items():
            for c in v:
                md.append("- %s: `%s:%s` %s" % (k, c["path"], c.get("line", "?"),
                                                 ("`" + c["needle"][:70] + "`") if c["needle"] else ""))
        md.append("")
    (HERE / "EVIDENCE_REGISTER.md").write_text("\n".join(md) + "\n", encoding="utf-8", newline="\n")
    print("rows=%d unresolved_citations=%d" % (len(out_rows), bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
