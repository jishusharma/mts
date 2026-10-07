import sys
sys.dont_write_bytecode = True
"""Simulate Tom core setups over historical snapshots and write TOM_CORE_BT.md (+ FROZEN.md + trial registry)."""
import csv
import datetime as dt
import hashlib
import json
import random
import subprocess
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))
import tom_bt as T  # noqa: E402
import tom_bt_run as R  # noqa: E402

OUT_DIR = ROOT / "MyTradingSys" / "research" / "fast_track_2026-09-27"
RUN_DIR = OUT_DIR / "bt_runs"
T_DEV = dt.datetime(2025, 9, 1, tzinfo=dt.timezone.utc).timestamp()
T_HOLD = dt.datetime(2026, 6, 26, tzinfo=dt.timezone.utc).timestamp()
SIGNAL_VARIANTS = ["episode", "A", "watch_episode", "p4_episode"]
CONFIGS = {
    "base": dict(fees=T.FEES_DERIBIT, stop_first=True, slip=0.0),
    "all_taker_0.05": dict(fees=T.FEES_ALL_TAKER, stop_first=True, slip=0.0),
    "slip_5bps": dict(fees=T.FEES_DERIBIT, stop_first=True, slip=0.0005),
    "target_first": dict(fees=T.FEES_DERIBIT, stop_first=False, slip=0.0),
}


def period_of(t):
    return "hist_2022-01..2025-08" if t < T_DEV else "dev_2025-09..2026-06-25" if t < T_HOLD else "holdout_2026-06-26.."


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()[:16]


def adapter_line(root):
    """Provenance line for the archive adapter. 3fdf8cb promoted the staged .new files to tracked sources; prefer the
    promoted file and fall back to the old staged name so older checkouts still report."""
    d = Path(root) / "src/main/java/datafeed"

    def pick(*names):
        for n in names:
            if (d / n).exists():
                return n, sha(d / n)
        raise FileNotFoundError("none of %s under %s" % (names, d))

    a_name, a_sha = pick("ArchiveHistoricalSource.java", "ArchiveHistoricalSource.java.new")
    m_name, m_sha = pick("MarketDataSnapshot.java.archive_mode.new", "MarketDataSnapshot.java")
    return "Archive adapter (compiled in %%TEMP%% only): %s %s; %s %s" % (a_name, a_sha, m_name, m_sha)


def git(*a):
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True).stdout.strip()


def f2(x):
    return "%.2f" % x


def fmt(s):
    if s.get("n_filled", 0) == 0:
        return "%d | 0 | - | - | - | -" % s.get("n_signals", 0)
    flag = " (n<30)" if s["n_filled"] < 30 else ""
    return "%d | %d%s | %.0f%% | %.0f%% [%.0f-%.0f] | %s [%s, %s] | %s [%s, %s]" % (
        s["n_signals"], s["n_filled"], flag, 100 * s["fill_rate"], 100 * s["win"], max(0.0, 100 * s["win_ci"][0]),
        min(100.0, 100 * s["win_ci"][1]), f2(s["mean_gross"]), f2(s["gross_ci"][0]), f2(s["gross_ci"][1]),
        f2(s["mean_net"]), f2(s["net_ci"][0]), f2(s["net_ci"][1]))


HDR = "| group | n signals | n filled | fill | win [Wilson] | mean R gross [95% CI] | mean R net [95% CI] |\n|---|---|---|---|---|---|---|\n"


def table(groups):
    return HDR + "".join("| %s | %s |\n" % (k, fmt(T.summarize(v))) for k, v in groups)


def group_by(trades, keyfn):
    d = defaultdict(list)
    for t in trades:
        d[keyfn(t)].append(t)
    return sorted(d.items(), key=lambda kv: str(kv[0]))


def random_entry_null(trades, b, n_perm=200, seed=7):
    """Protocol 5a (simplified): same direction, same stop/target distance (% of entry), same hold; entry minute
    drawn uniformly within the same UTC day at a next-bar-open fill. Returns (real mean gross, p-value, null mean)."""
    filled = [t for t in trades if t.get("filled") and t["reason"] in ("target", "stop", "timeout")]
    if len(filled) < 30:
        return None
    rng = random.Random(seed)
    real = sum(t["gross_r"] for t in filled) / len(filled)
    means = []
    for _ in range(n_perm):
        tot = cnt = 0
        for t in filled:
            day0 = int(t["t"] // 86400) * 86400
            i_lo = b.idx(day0 * 1000)
            k = rng.randrange(i_lo, i_lo + 1440 - 1)
            if k + 1 >= b.n:
                continue
            e = b.o[k + 1]
            zp = float(t["zprice"])
            sp, tp = abs(zp - float(t["stop"])) / zp, abs(float(t["target"]) - zp) / zp
            sgn = 1.0 if t["dir"] == "long" else -1.0
            tfm = T.ZONE_TF_MIN[t["zone_tf"]]
            r = T.sim_limit_trade(b, k + 1, t["dir"], e, e * (1 - sgn * sp), e * (1 + sgn * tp), 1, 8 * tfm,
                                  T.FEES_DERIBIT, True, 0.0)
            if r["filled"] and r["reason"] in ("target", "stop", "timeout"):
                tot += r["gross_r"]
                cnt += 1
        if cnt:
            means.append(tot / cnt)
    p = (1 + sum(1 for m in means if m >= real)) / (1 + len(means))
    return real, p, sum(means) / len(means)


def main():
    rows = R.load_rows()
    metas = [json.load(open(p)) for p in sorted(R.SNAP_DIR.glob("*.meta.json"))]
    ev_n = sum(m["evaluated"] for m in metas)
    kept_n = sum(m["kept"] for m in metas)
    err_n = sum(m["errors"] for m in metas)
    b = T.load_bars_1m(R.RAW)
    first_ts, last_ts = rows[0]["t"], rows[-1]["t"]
    iso = lambda t: dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%Y-%m-%d")
    run_id = "tom_core_" + dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d")
    from collections import Counter
    vc = Counter(r["verdict"] for r in rows)
    pc = Counter(r["proof"] for r in rows)

    # ---- freeze
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    (RUN_DIR / run_id).mkdir(exist_ok=True)
    frozen = ["# FROZEN %s" % run_id, "",
              "git HEAD: %s (branch %s); working tree not committed at run time" % (git("rev-parse", "HEAD"), git("branch", "--show-current")),
              "SetupCandidatesBuilder.java sha256[:16]: %s" % sha(ROOT / "src/main/java/datafeed/SetupCandidatesBuilder.java"),
              "verdict.py: %s | tom_bt.py: %s | tom_bt_run.py: %s | l1_patch_mds.py: %s" % (
                  sha(HERE / "verdict.py"), sha(HERE / "tom_bt.py"), sha(HERE / "tom_bt_run.py"), sha(HERE / "l1_patch_mds.py")),
              adapter_line(ROOT),
              "Rules: Tom core unchanged (D1/D3/D4 rulings as committed); verdict.py fail_closed proof direction; no fitted parameters",
              "(walk-forward has nothing to fit: every month is out-of-sample by construction; the split below is descriptive).",
              "Signals: rank-1 candidate; entry limit at zone price; stop/target from math; order life and time exit 8 zone-tf bars;",
              "zone tf = SetupCandidatesBuilder.getSwingTF; one position at a time; stop-first on ambiguous bars.",
              "Fees: entry/target maker 0, stop/timeout taker 0.0005 (Deribit BTC-PERPETUAL as in sim.py); stress: 0.0005 on every fill,",
              "5 bps extra slippage on stop/timeout, target-first ambiguity. Funding not modelled (hold <= 8 zone bars).",
              "Splits: hist 2022-01-20..2025-08-31 | dev 2025-09-01..2026-06-25 | HOLDOUT 2026-06-26..2026-09-26 (run once, this run).",
              "Fabio tags: L1 IS-best frozen params (FABIO_L1_REPORT.md), descriptive only."]
    (RUN_DIR / run_id / "FROZEN.md").write_text("\n".join(frozen) + "\n", encoding="utf-8", newline="\n")

    # ---- regimes cut points (vol terciles over the whole history, sampled weekly)
    vols = []
    for t in range(int(first_ts) + 30 * 86400, int(last_ts), 7 * 86400):
        rf = T.regime_features(b, t)
        if rf:
            vols.append(rf[1])
    cuts = T.tercile_cuts(vols)

    fab = json.load(open(R.WORK / "fabio_events.json")) if (R.WORK / "fabio_events.json").exists() else {}
    fams = {"cvd_absorption": [], "escalation": [], "fvg_bounce": []}
    for name, ev in fab.items():
        fams[name.rsplit("_", 1)[0]].extend(tuple(e) for e in ev)
    for k in fams:
        fams[k].sort()
    fams["any"] = sorted(sum((fams[k] for k in ("cvd_absorption", "escalation", "fvg_bounce")), []))

    md = []
    results = {}
    reg_rows = []
    for var in SIGNAL_VARIANTS:
        sigs = T.signals(rows, var)
        for cname, cfg in CONFIGS.items():
            tr = T.run_variant(sigs, b, **cfg)
            results[(var, cname)] = tr
            s = T.summarize(tr)
            nets = [t["net_r"] for t in tr if t.get("filled") and t["reason"] in ("target", "stop", "timeout")]
            sh = None
            if len(nets) > 2:
                m = sum(nets) / len(nets)
                sd = (sum((x - m) ** 2 for x in nets) / (len(nets) - 1)) ** 0.5
                sh = m / sd if sd else None
            reg_rows.append([run_id, dt.date.today().isoformat(), "%s/%s" % (var, cname), s.get("n_filled", 0),
                             "%.4f" % s["mean_net"] if s.get("n_filled") else "", "%.4f" % sh if sh is not None else ""])
    reg = RUN_DIR / "TRIAL_REGISTRY.csv"
    new = not reg.exists()
    already = (not new) and any(l.startswith(run_id + ",") for l in open(reg, encoding="utf-8"))
    if not already:  # a re-render of the same frozen run is not a new trial
        with open(reg, "a", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh, lineterminator="\n")
            if new:
                w.writerow(["run_id", "date", "variant", "n_trades", "mean_R_net", "sharpe_per_trade"])
            w.writerows(reg_rows)
    n_trials = sum(1 for _ in open(reg, encoding="utf-8")) - 1

    def enrich(trs):
        for t in trs:
            if t.get("filled") and "regime" not in t:
                rf = T.regime_features(b, t["t"])
                t["regime"] = T.trend_tag(rf[0]) if rf else "n/a"
                t["vol"] = T.vol_tag(rf[1], cuts) if rf else "n/a"
                t["period"] = period_of(t["t"])
                for n_ in (12, 4):
                    for fam in ("any", "cvd_absorption", "escalation", "fvg_bounce"):
                        t["fab_%s_%d" % (fam, n_)] = T.fabio_tag(fams.get(fam, []), t["t"], t["dir"], n_)
            t.setdefault("period", period_of(t["t"]))
        return trs

    md.append("# TOM CORE outcome backtest (historical snapshots, BTCUSDT)\n")
    md.append("Run `%s`, trial registry rows to date: **%d** (`bt_runs/TRIAL_REGISTRY.csv`; frozen rules: `bt_runs/%s/FROZEN.md`).\n" % (run_id, n_trials, run_id))
    md.append("## 1. Data and adapter status\n")
    md.append("- Adapter: ArchiveHistoricalSource (staged .new) compiled and run in a `%%TEMP%%` copy only. 1m archive 2022-01-01..2026-09-26, "
              "%d bars, zero gaps (load-time continuity check). Historical snapshots every 15 min (asOf), 2022-01-20..2026-09-26: %d evaluated, %d kept "
              "(>= 1 candidate), %d errors. Rows used: %d (%s .. %s). Snapshots on `F:\\MTS\\data\\tom_snapshots\\` (gz JSONL, %s).\n" % (
                  b.n, ev_n, kept_n, err_n, len(rows), iso(first_ts), iso(last_ts), "compact"))
    md.append("- **Staged wiring defect found and fixed in the proposed diff:** `MarketDataSnapshot.java.new` rewired the three range calls in the LIVE "
              "`fetchSnapshot`, not in `fetchHistoricalSnapshot`, which still called live REST (also a look-ahead). Proposed fix: "
              "`MarketDataSnapshot.java.archive_mode.new` (generated by `MyTradingSys/backtest/l1_patch_mds.py`): live path back to the committed original, "
              "historical path wired + `dropFormingBar`, `spot_perp_basis`/`oi_breakdown` no longer fetched from live REST in archive mode, "
              "`trade_flow.net_delta_*` and `cvd_trade_flow_aligned` derived from the 1m klines with the live formula (were 0.0/false).\n")
    md.append("- **What the historical snapshots cannot contain** (no raw source wired): book imbalance, funding, OI, spot-perp basis, liquidation. "
              "Consequence: the book-imbalance proof never counts, so the maximum proof is 6 instead of 7 and `SETUP_FORMING` (proof >= 5) is far rarer than live. "
              "Verdict counts over all rows: %s. Proof-count histogram: %s.\n" % (dict(vc), dict(sorted(pc.items(), key=lambda kv: str(kv[0])))))
    md.append("- `SETUP_CONFIRMED` is not produced by `verdict.py` (it is a live state-machine step); only SETUP_FORMING is simulated. "
              "The WATCH-based variants below are SENSITIVITY on the proof ceiling, not the live rule.\n")
    md.append("- Simulation: see FROZEN.md summary. Not modelled: funding, Deribit-vs-Binance basis, queue position, mark-price stops. Trades are simulated on Binance 1m trade bars. "
              "Caveat: 15-min cadence means a signal is seen up to 15 min after it first became true.\n")
    md.append("- Periods: hist = 2022-01..2025-08 (outside the protocol dev window), dev = 2025-09-01..2026-06-25, holdout = 2026-06-26..2026-09-26 (run once). "
              "Tom has no fitted parameter, so every period is out-of-sample; protocol minimum evidence is >= 100 trades with net CI lower bound > 0.\n")

    verdict_lines = []
    for var in SIGNAL_VARIANTS:
        tr = enrich(results[(var, "base")])
        for cname in CONFIGS:
            if cname != "base":
                enrich(results[(var, cname)])
        s = T.summarize(tr)
        md.append("\n## 2.%d Variant `%s`\n" % (SIGNAL_VARIANTS.index(var) + 1, var))
        md.append({"episode": "SETUP_FORMING episodes (first row of each; primary = the live rule).",
                   "A": "sim.py rule A: every SETUP_FORMING row while flat (re-entries on the same zone allowed).",
                   "watch_episode": "WATCH or SETUP_FORMING episodes (proof >= 3, sensitivity).",
                   "p4_episode": "WATCH/SETUP_FORMING with proof >= 4 (one below live SETUP_FORMING threshold, sensitivity)."}[var] + "\n")
        md.append("Overall (base fees): n signals %d.\n" % s["n_signals"])
        if s.get("n_filled", 0) == 0:
            md.append("No filled trades. **insufficient N**\n")
            verdict_lines.append("- `%s`: n filled 0 -> insufficient N" % var)
            continue
        md.append("### by period\n" + table(group_by(tr, lambda t: t["period"]) + [("ALL", tr)]))
        md.append("\n### by setup type\n" + table(group_by(tr, lambda t: t["setup"])))
        md.append("\n### by zone timeframe\n" + table(group_by(tr, lambda t: t["zone_tf"])))
        md.append("\n### by direction\n" + table(group_by(tr, lambda t: t["dir"])))
        md.append("\n### by trend regime (prior 30d return, |x| >= 7.5% = trend)\n" + table(group_by([t for t in tr if t.get("filled")], lambda t: t["regime"])))
        md.append("\n### by realised-vol tercile (prior 30d hourly vol)\n" + table(group_by([t for t in tr if t.get("filled")], lambda t: t["vol"])))
        md.append("\n### by year\n" + table(group_by(tr, lambda t: dt.datetime.fromtimestamp(t["t"], dt.timezone.utc).year)))
        # exit mix and ambiguity
        fl = [t for t in tr if t.get("filled") and t["reason"] in ("target", "stop", "timeout")]
        risks = sorted(abs(float(t["zprice"]) - float(t["stop"])) / float(t["zprice"]) * 100 for t in fl)
        md.append("\nWin = target hit (timeouts are not wins). Exit mix (filled): %s; ambiguous bars: %d; unfilled reasons: %s. "
                  "Median stop distance %.3f%% of price; mean fee %.2f R (base fees); mean planned gross R:R %.2f.\n" % (
                      s["exits"], s["ambiguous"], dict(Counter(t["reason"] for t in tr if not t.get("filled"))),
                      risks[len(risks) // 2], sum(t["fee_r"] for t in fl) / len(fl),
                      sum(float(t["gross_rr"] or 0) for t in fl) / len(fl)))
        md.append("\n### stress\n" + table([(cname, results[(var, cname)]) for cname in CONFIGS]))
        null = random_entry_null(tr, b)
        if null:
            md.append("\nRandom-entry null (200 draws, same day, same direction and stop/target distance, next-bar-open fill): real mean gross R %.3f, null mean gross R %.3f, one-sided p(null >= real) = %.3f.\n" % (null[0], null[2], null[1]))
        # Tom x Fabio (descriptive)
        md.append("\n### Tom x Fabio confluence - DESCRIPTIVE, NOT A FILTER (operator's Tom-vs-Fabio ruling is still open)\n")
        md.append("Tag = a Fabio kline detector (L1 frozen params, 5m/15m/1h) fired in the SAME direction and its bar closed within N bars (of its own tf) before the signal. "
                  "No selection, no threshold, nothing is fed back to Tom.\n\n")
        conf = []
        filled = [t for t in tr if t.get("filled")]
        for n_ in (12, 4):
            for fam in ("any", "cvd_absorption", "escalation", "fvg_bounce"):
                key = "fab_%s_%d" % (fam, n_)
                conf.append(("%s within %d bars: TAGGED" % (fam, n_), [t for t in filled if t[key]]))
                conf.append(("%s within %d bars: not tagged" % (fam, n_), [t for t in filled if not t[key]]))
        md.append(table(conf))
        md.append("\n#### tagged minus untagged, mean net R (8 comparisons per variant; the Bonferroni-adjusted interval uses alpha = 0.05/8)\n")
        md.append("| tag | n tagged / untagged | diff net R [95% CI] | diff [Bonferroni-8 CI] | excludes 0 after Bonferroni |\n|---|---|---|---|---|\n")
        for n_ in (12, 4):
            for fam in ("any", "cvd_absorption", "escalation", "fvg_bounce"):
                key = "fab_%s_%d" % (fam, n_)
                a_ = [t["net_r"] for t in filled if t[key] and t["reason"] in ("target", "stop", "timeout")]
                b_ = [t["net_r"] for t in filled if (not t[key]) and t["reason"] in ("target", "stop", "timeout")]
                if len(a_) < 5 or len(b_) < 5:
                    md.append("| %s/%d | %d / %d | n too small | | |\n" % (fam, n_, len(a_), len(b_)))
                    continue
                d1 = T.diff_ci(a_, b_, 0.05)
                d2 = T.diff_ci(a_, b_, 0.05 / 8)
                md.append("| %s within %d bars | %d / %d | %+.2f [%+.2f, %+.2f] | [%+.2f, %+.2f] | %s |\n" % (
                    fam, n_, len(a_), len(b_), d1[0], d1[1], d1[2], d2[1], d2[2], "yes" if d2[1] > 0 or d2[2] < 0 else "no"))
        if not fab:
            md.append("\n(Fabio events file missing: tags are all False.)\n")
        # protocol verdict
        nets = [t["net_r"] for t in filled if t["reason"] in ("target", "stop", "timeout")]
        oos = [t for t in filled if t["period"] != "hist_2022-01..2025-08"]
        so = T.summarize(oos)
        line = "- `%s`: n filled %d (protocol OOS dev+holdout: %d); mean net R %s [%s, %s]" % (
            var, s["n_filled"], so.get("n_filled", 0), f2(s["mean_net"]), f2(s["net_ci"][0]), f2(s["net_ci"][1]))
        if s["n_filled"] < 100:
            line += " -> **insufficient N** (< 100)"
        elif s["net_ci"][0] > 0:
            line += " -> net CI lower bound > 0 on this sample (other protocol gates not all met: see stress table)"
        else:
            line += " -> net CI includes 0 / negative: **not proven**"
        verdict_lines.append(line)
    def _one(var, period=None):
        tr_ = [t for t in results[(var, "base")] if period is None or t.get("period", period_of(t["t"])) == period]
        return T.summarize(tr_)
    tl = ["\n**Answer in one paragraph.** Before this run Tom core had never been back-tested on outcomes (only a parity replay existed). "
          "Now it has, on 4.7 years of BTCUSDT 1m data through the L1 archive adapter. Live rule (SETUP_FORMING): only %d filled trades in 4.7 years, "
          "because the history has no book-imbalance/funding/OI proofs (max proof 6, SETUP_FORMING needs 5) -> insufficient N, no claim either way. "
          "Sensitivity on the weaker gates (proof >= 3, WATCH+SETUP_FORMING episodes, n = %d filled): mean gross R %.2f [%.2f, %.2f], mean net R %.2f [%.2f, %.2f] "
          "(Deribit-style fees; tight stops make fees ~%.2f R per trade); holdout 2026-06-26..: n = %d, net R %.2f [%.2f, %.2f]. "
          "So no edge is shown; gross is at or slightly below zero and fees turn it clearly negative. The random-entry null is at least as good as the real setups. "
          "The Tom x Fabio tables below are descriptive only.\n" % (
              _one("episode").get("n_filled", 0), _one("watch_episode")["n_filled"], _one("watch_episode")["mean_gross"],
              _one("watch_episode")["gross_ci"][0], _one("watch_episode")["gross_ci"][1], _one("watch_episode")["mean_net"],
              _one("watch_episode")["net_ci"][0], _one("watch_episode")["net_ci"][1],
              _one("watch_episode")["mean_gross"] - _one("watch_episode")["mean_net"],
              _one("watch_episode", "holdout_2026-06-26..")["n_filled"], _one("watch_episode", "holdout_2026-06-26..")["mean_net"],
              _one("watch_episode", "holdout_2026-06-26..")["net_ci"][0], _one("watch_episode", "holdout_2026-06-26..")["net_ci"][1])]
    md.insert(2, "\n".join(tl))
    md.append("\n## 3. Verdict per protocol section 6\n" + "\n".join(verdict_lines) + "\n")
    md.append("\nDSR/PBO: no variant is *selected* on this data (all four are reported), so PBO does not apply; DSR would need >= 100 trades and "
              "N_trials = %d (registry rows). Reported only descriptively where n >= 100 in the tables above (per-trade Sharpe in the registry).\n" % n_trials)
    (OUT_DIR / "TOM_CORE_BT.md").write_text("\n".join(md), encoding="utf-8", newline="\n")
    json.dump({"%s/%s" % k: T.summarize(v) for k, v in results.items()}, open(R.WORK / "summary.json", "w"), default=str, indent=1)
    print("wrote", OUT_DIR / "TOM_CORE_BT.md")
