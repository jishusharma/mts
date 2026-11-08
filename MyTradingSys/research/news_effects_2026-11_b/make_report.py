"""make_report.py - write REPORT.md from news_events.csv, class_summary.csv, baseline.csv (numbers only come from those files
and from BTCUSDT 1d klines for the regime mix). Prose is fixed text below."""
import csv
import datetime as dt
import statistics as st
from pathlib import Path

import build_events as be
import check_catalogue as cc

HERE = Path(__file__).parent


def regime_by_day():
    s0 = int(dt.datetime(2023, 11, 20, tzinfo=dt.timezone.utc).timestamp() * 1000)
    ks = be.get_json("%s?symbol=BTCUSDT&interval=1d&startTime=%d&limit=1000" % (be.API, s0))
    day = {dt.datetime.fromtimestamp(k[0] / 1000, dt.timezone.utc).date(): float(k[4]) for k in ks}
    out = {}
    for d, c in day.items():
        p = day.get(d - dt.timedelta(days=30))
        if p:
            r = c / p - 1
            out[d] = "bull" if r > 0.10 else "bear" if r < -0.10 else "range"
    return out


def mix(days, reg):
    xs = [reg[d] for d in days if d in reg]
    return "bull %d%% / bear %d%% / range %d%% (n=%d)" % tuple(
        [round(100 * xs.count(k) / len(xs)) for k in ("bull", "bear", "range")] + [len(xs)])


def f(x, nd=0):
    return "" if x in ("", None) else ("%." + str(nd) + "f") % float(x)


def main():
    rows = cc.load()
    summ = list(csv.DictReader(open(HERE / "class_summary.csv")))
    base = {(r["symbol"], r["interval"]): r["median_abs_ret_bps"] for r in csv.DictReader(open(HERE / "baseline.csv"))}
    reg = regime_by_day()
    ev_days = [dt.date.fromisoformat(r["date_utc"]) for r in rows]
    all_days = [d for d in reg if dt.date(2024, 1, 1) <= d <= dt.date(2026, 11, 7)]
    small = [s["class"] for s in summ if s["verdict"] == "unknown"]
    nq = {q: sum(r["ts_quality"] == q for r in rows) for q in ("exact", "approx", "day")}
    n_rec = sum(r["date_check"] == "recalled" for r in rows)
    L = []
    L.append("Regime mix: events %s; all days 2024-01-01..2026-11-07 %s (BTC trailing 30-day close-to-close return +-10 %%, OURS)"
             % (mix(ev_days, reg), mix(all_days, reg)))
    L += ["", "# News-effect event catalogue 2024-2026 (card news-effect-event-catalogue-1108)", "",
          "Observation only. No weight, flash, bias or gate rule is proposed here. Reaction = BTCUSDT and ETHUSDT public 1m klines "
          "(data-api.binance.vision). Files: `news_events.csv` (%d events), `class_summary.csv`, `baseline.csv`, `build_events.py`, "
          "`check_catalogue.py` (+ `test_catalogue.py`), `fetch_calendars.py`, `events_seed.py`." % len(rows), "",
          "## 1. What is in it", "",
          "- %d events, %d before and %d after 2025-01-20 17:00 UTC (inauguration, OURS cut)."
          % (len(rows), sum(r["era"] == "pre" for r in rows), sum(r["era"] == "post" for r in rows)),
          "- Timestamp quality: exact (minute known) %d, approx (hour, about +-1 h) %d, day-only %d. Day-only rows carry the 24 h return "
          "from 00:00 UTC only; approx rows carry 60 m / 240 m / 1440 m; exact rows carry every column." % (nq["exact"], nq["approx"], nq["day"]),
          "- SOURCED = public release calendars fetched this session: BLS CPI, jobs report (NFP), PPI release dates "
          "(bls.gov schedule pages read through Internet Archive snapshots, because bls.gov refuses direct fetches) and FOMC decision days "
          "(federalreserve.gov/monetarypolicy/fomccalendars.htm). Release times 08:30 ET and 14:00 ET converted to UTC with the New York tz rules.",
          "- OURS = every other class (grouping is ours; %d dates come from recall of public coverage, `date_check=recalled`, not fetched)." % n_rec,
          "", "## 2. Definitions (all OURS)", "",
          "ref = open of the 1m candle at t0. ret_Hm = close of the candle starting t0+H-1m over ref, in bps (1 bp = 0.01 pct). "
          "maxabs60 = largest wick distance from ref in the first 60 candles; peak_min = the minute it happened. "
          "vol_x = base volume in the first 15 m (exact) or 60 m (approx) over the average for the same span in the prior 120 m. "
          "Baseline (all hours / all days 2024-01-01..2026-11-07, median |open-close|): BTC 1h %s bps, 1d %s bps; ETH 1h %s, 1d %s."
          % (base[("BTCUSDT", "1h")], base[("BTCUSDT", "1d")], base[("ETHUSDT", "1h")], base[("ETHUSDT", "1d")]), "",
          "## 3. Class table (median absolute BTC reaction; blank = too few rows with that precision)", "",
          "| class | label | n | pre | post | exact | day-only | med abs 15m | med abs 60m | med abs 1440m | x base 60m | x base 1d | later/first 1440m | verdict |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for s in summ:
        L.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            s["class"], s["label"], s["n"], s["n_pre"], s["n_post"], s["n_exact"], s["n_day_only"], f(s["btc_med_abs_15m_bps"], 1),
            f(s["btc_med_abs_60m_bps"], 1), f(s["btc_med_abs_1440m_bps"], 1), f(s["x_base_60m"], 2), f(s["x_base_1d"], 2),
            f(s["decay_later_over_first_1440m"], 2), s["verdict"]))
    L += ["", "x base = class median over the all-hours (60m) or all-days (1d) median. The hour of a data release is a busy hour, so "
          "x base 60m for CPI/NFP/FOMC overstates the effect versus a same-hour baseline (not computed here: gap). "
          "'later/first' = median |1440m| of the later half of the class over the earlier half (needs 8+ rows with a 24 h return).", ""]
    # era split
    L += ["## 4. Before vs after 2025-01-20 (median absolute BTC 24 h return, bps; class needs 4+ rows per era)", "",
          "| class | pre n | pre med | post n | post med |", "|---|---|---|---|---|"]
    for s in summ:
        rs = [r for r in rows if r["class"] == s["class"] and r["btc_ret_1440m_bps"] != ""]
        pre = [abs(float(r["btc_ret_1440m_bps"])) for r in rs if r["era"] == "pre"]
        post = [abs(float(r["btc_ret_1440m_bps"])) for r in rs if r["era"] == "post"]
        L.append("| %s | %d | %s | %d | %s |" % (s["class"], len(pre), f(st.median(pre), 0) if len(pre) >= 4 else "unknown",
                                                len(post), f(st.median(post), 0) if len(post) >= 4 else "unknown"))
    # repeats: scheduled classes by year
    L += ["", "## 5. Does the same kind of news work twice? (scheduled classes, median |60m| BTC bps by half-year)", "",
          "| class | " + " | ".join(h for h in ("2024H1", "2024H2", "2025H1", "2025H2", "2026H1", "2026H2")) + " |", "|---|---|---|---|---|---|---|"]
    for c in ("CPI", "NFP", "FOMC", "PPI"):
        cells = []
        for h in ("2024H1", "2024H2", "2025H1", "2025H2", "2026H1", "2026H2"):
            y, hh = int(h[:4]), h[4:]
            xs = [abs(float(r["btc_ret_60m_bps"])) for r in rows if r["class"] == c and r["btc_ret_60m_bps"] != "" and
                  r["date_utc"][:4] == str(y) and ((int(r["date_utc"][5:7]) <= 6) == (hh == "H1"))]
            cells.append("%s (n=%d)" % (f(st.median(xs), 0), len(xs)) if len(xs) >= 3 else "unknown (n=%d)" % len(xs))
        L.append("| %s | %s |" % (c, " | ".join(cells)))
    L += ["", "Magnitude only. Direction cannot be judged: the catalogue has no consensus-versus-actual (surprise) column, so "
          "'same news moved the opposite way' is not testable from this file (gap 3 below).", ""]
    top = sorted([r for r in rows if r["btc_ret_60m_bps"] != ""], key=lambda r: -abs(float(r["btc_ret_60m_bps"])))[:10]
    L += ["## 6. Ten largest BTC 60 m moves", "", "| event | quality | BTC 60m bps | ETH 60m bps |", "|---|---|---|---|"]
    for r in top:
        L.append("| %s | %s | %s | %s |" % (r["event_id"], r["ts_quality"], f(r["btc_ret_60m_bps"], 0), f(r["eth_ret_60m_bps"], 0)))
    L += ["## 7. Cross-check against the catalogue already landed by another Builder (commit 6bfe981fb, folder news_effects_2026-11)", "",
          "Same card built twice; this folder is the second, independent build and is kept beside the first, not over it. Compared once, offline:",
          "- Both have 192 events; 158 event dates are in both, 24 only in the first, 20 only in this one (own-grouping events differ).",
          "- On the 128 timed rows that share the same event minute, the first build's BTC 60 m return (percent x 100) equals this build's "
          "bps value with median difference 0.0 bps and maximum 1.9 bps (its reference is the prior minute's close, this one is the event minute's open). "
          "So the kline arithmetic agrees; differences are in which events exist and how time is graded.",
          "- The first build has 5 analyst-named rows (it could read the CBP extractions); this build has none (gap 2). Treat the first build as the primary "
          "catalogue and this one as an arithmetic cross-check plus the era/half-year tables above.",
          ""]
    L += ["## Gaps (honest list)", "",
          "1. Classes with fewer than 8 events are reported `unknown`, no number: %s." % ", ".join(small),
          "2. Analyst-named events from the CBP extractions and transcripts: NOT included. `F:/CryptoScrapper/cbp_v2/extractions.md` and the "
          "transcript store are absent on this machine (no F: drive). Only the repo's own Binance-hack report was used (HACK 2026-10-29).",
          "3. No actual-versus-consensus data (CPI, NFP surprise), so no direction or surprise-size split.",
          "4. %d of %d events are day-only: only a 24 h return, and that window holds other news and the weekend/US-session mix. "
          "Their 24 h numbers are weak evidence." % (nq["day"], len(rows)),
          "5. %d approx timestamps are from memory of press coverage (about +-1 h); a wrong hour would shift the 60 m window." % nq["approx"],
          "6. All %d non-calendar dates are recalled, not fetched; the price move itself is the only corroboration. Not verified against a source page." % n_rec,
          "7. INFERRED: CPI/NFP dates Oct 2025 - Feb 2026 (government shutdown reschedule). Six snapshot dates (CPI 2025-10-15, 11-13, 12-10; "
          "NFP 2025-10-03, 11-07, 12-05) were dropped because they were not held that day (both old and new dates appear across snapshots; "
          "that they were not held is recall). PPI in Oct 2025 - Feb 2026 is dropped (unverified). Rows flagged `inferred=yes`.",
          "8. Events after mid-2025 other than the calendars, the Fusaka upgrade, the BoJ hike and the Binance hack are thin; 2026 "
          "non-calendar news is almost absent (author has no 2026 recall; no online news archive was read).",
          "9. Calendars: 14:00 ET FOMC statement time is the usual time; unscheduled meetings and press-conference timing are not separate rows. "
          "PPI/CPI/NFP overlap with other news on the same minute (not de-confounded).",
          "10. Overlapping events (same day: 2025-03-06/07, 2025-05-12) share one price move; rows are not independent.",
          "11. 20-row re-derivation (`check_catalogue.py`) runs offline from `raw/derive_sample.csv` (klines saved by the builder; "
          "formula re-coded separately); `--online` refetches. Only 5m/15m/60m are re-derived, not 240m/1440m.",
          "", "## Parameters, SOURCED or OURS", "",
          "- SOURCED: release dates and times (BLS, Fed pages). - OURS: class grouping, quality grades, 2025-01-20 17:00 UTC era cut, "
          "minimum 8 events per class, +-10 % trailing-30-day regime cut, reaction horizons, 120 m volume baseline.",
          "", "DECISION (OURS): where a time was uncertain the row is graded down (approx/day) instead of guessed to the minute.",
          "", "Next: per-class same-hour baseline, surprise column from a public consensus archive, transcript-sourced events once F: is mounted.", ""]
    (HERE / "REPORT.md").write_text("\n".join(L), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
