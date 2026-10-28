"""Qriptal scorer (card qriptal-score-binance, B162 step 1).

Input: the ELIGIBLE rows of CALL_LEDGER.csv (entry + stop + at least one target, all spoken by him).
Prices: Binance BTCUSDT 1m klines (F:/MTS/data/tom_raw/klines, archive to 2026-09-26), fee 0.05% per side (FORMULAS.md s17).
Rules: RULES.md (all numbers OURS). Data rule from the card: DEV data only, no holdout reads. A call is DEV only if its whole
24 h fill + 7 d open window ends before 2026-06-26 (ledger column window_split); the loader clamps every read to that date, so
a DEV call cannot read a holdout candle, and a holdout call is refused unless --allow-holdout is passed (off by default).

Usage (repo root):
    python MyTradingSys/research/qriptal_2026-10-10/score_calls.py run [--allow-holdout]   # rewrites SCORECARD.md
    python MyTradingSys/research/qriptal_2026-10-10/score_calls.py check                   # exit 1 if SCORECARD.md differs
"""
import csv
import io
import re
import sys
from datetime import datetime, timedelta, timezone
from math import comb
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
LEDGER = HERE / "CALL_LEDGER.csv"
SCORECARD = HERE / "SCORECARD.md"
KLINE_DIR = Path("F:/MTS/data/tom_raw/klines")

FEE_PER_SIDE = 0.0005                      # FORMULAS.md s17: 0.05% per side
MIN_MS = 60_000
FILL_WINDOW_MS = 24 * 3600 * 1000          # RULES.md: limit entry not filled within 24 h = NOT_FILLED
OPEN_WINDOW_MS = 7 * 24 * 3600 * 1000      # RULES.md: open after 7 days = closed at market
MAX_WINDOW = timedelta(days=8)             # 24 h + 7 d
HOLDOUT_START = datetime(2026, 6, 26, tzinfo=timezone.utc)   # BACKTEST_PROTOCOL s2: DEV 2025-09-01..2026-06-25

# What he says about himself (qriptal.com paste in items/B162_qriptal_signal_layer.md line 23; unit of the percentages unverified)
CLAIM = {"setups": 86, "wins": 49, "be": 13, "losses": 24, "win_rate": 0.671, "avg_win_pct": 3.99, "avg_loss_pct": 0.63}
# Power test: H0 p = his win rate, H1 p = coin flip, one-sided alpha 0.05 (OURS)
P0, P1, ALPHA = 0.671, 0.5, 0.05

COLUMNS = (("t1", "Primary: exit all at T1"), ("last", "Second: exit all at the last target"))


class HoldoutRefused(RuntimeError):
    pass


def _ms(dt):
    return int(dt.timestamp() * 1000)


def parse_utc(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


_NUM = re.compile(r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?")


def parse_price(text):
    """First number in the field: '82,200 (sweep of 82.2, not of 82.8)' -> 82200.0."""
    m = _NUM.search(text or "")
    if not m:
        raise ValueError(f"no price in {text!r}")
    return float(m.group(0).replace(",", ""))


def parse_targets(text):
    parts = [p for p in (text or "").split(";") if p.strip()]
    if not parts:
        raise ValueError(f"no targets in {text!r}")
    return [parse_price(p) for p in parts]


# ---------------------------------------------------------------- scoring one call

def _net(side, entry, exit_price, stop, fee):
    gross = side * (exit_price - entry)
    net = gross - fee * (entry + exit_price)
    risk = abs(entry - stop)
    return {"exit_price": exit_price, "net_pct": net / entry, "r_net": net / risk, "r_gross": gross / risk}


def _resolve(side, stop, target, cs, fill_i, end_ms):
    """Walk the candles from the fill candle. Stop is checked first inside every candle (RULES.md: stop and target in one
    1m candle = stop). The fill candle checks only the stop: the order of entry and target inside it is unknown.
    -> (exit, price, open_time_ms) or None when the data ends before the trade is resolved."""
    last = None
    for i in range(fill_i, len(cs)):
        t, o, h, l, cl = cs[i]
        if t >= end_ms:
            break
        last = (t, cl)
        if (l <= stop) if side > 0 else (h >= stop):
            return "STOP", stop, t
        if i > fill_i and ((h >= target) if side > 0 else (l <= target)):
            return "TARGET", target, t
    if last is None or last[0] < end_ms - 2 * MIN_MS:
        return None
    return "TIMEOUT", last[1], last[0]


def score_call(direction, entry, stop, targets, call_time, candles, fee=FEE_PER_SIDE):
    """Score one posted call on 1m candles [(open_time_ms, open, high, low, close)], ascending.
    The first candle that opens at or after the call time is the first one used (the candle he spoke in is skipped).
    Entry fills at the posted price in the first candle whose range contains it, within 24 h. -> dict, status in
    SCORED | NOT_FILLED | NO_DATA; SCORED carries columns 't1' and 'last' (exit TARGET | STOP | TIMEOUT, exit_price, net_pct, r_net)."""
    if direction not in ("long", "short"):
        raise ValueError(f"direction {direction!r}")
    side = 1 if direction == "long" else -1
    if side * (entry - stop) <= 0:
        raise ValueError("stop must sit on the losing side of the entry")
    if not targets or any(side * (t - entry) <= 0 for t in targets):
        raise ValueError("every target must sit on the winning side of the entry")
    call_ms = _ms(call_time)
    start_ms = -(-call_ms // MIN_MS) * MIN_MS
    fill_end = call_ms + FILL_WINDOW_MS
    cs = [x for x in candles if x[0] >= start_ms]
    fill_i, seen = None, None
    for i, (t, o, h, l, cl) in enumerate(cs):
        if t >= fill_end:
            break
        seen = t
        if l <= entry <= h:
            fill_i = i
            break
    if fill_i is None:
        return {"status": "NO_DATA" if seen is None or seen < fill_end - 2 * MIN_MS else "NOT_FILLED"}
    fill_ms = cs[fill_i][0]
    end_ms = fill_ms + OPEN_WINDOW_MS
    out = {"status": "SCORED", "fill_time_ms": fill_ms}
    for col, target in (("t1", targets[0]), ("last", targets[-1])):
        res = _resolve(side, stop, target, cs, fill_i, end_ms)
        if res is None:
            return {"status": "NO_DATA", "fill_time_ms": fill_ms}
        kind, price, t = res
        out[col] = {"exit": kind, "exit_time_ms": t, **_net(side, entry, price, stop, fee)}
    return out


# ---------------------------------------------------------------- data rule and loader

def guard_call_window(call_time, allow_holdout=False):
    """Card: dev data only. A call whose fill + open window (8 d) reaches 2026-06-26 would read holdout candles."""
    if call_time + MAX_WINDOW > HOLDOUT_START and not allow_holdout:
        raise HoldoutRefused(f"call at {call_time:%Y-%m-%dT%H:%M:%SZ} has a window that reaches the holdout (2026-06-26)")


def _read_file(path, start_ms, end_ms, into):
    with open(path, "r", encoding="utf-8", newline="") as f:
        for row in csv.reader(f):
            if not row or not row[0].isdigit():
                continue
            t = int(row[0])
            if t > 10 ** 14:
                t //= 1000
            if start_ms <= t < end_ms:
                into[t] = (t, float(row[1]), float(row[2]), float(row[3]), float(row[4]))


def load_candles(start_ms, end_ms, kline_dir, allow_holdout=False):
    """BTCUSDT 1m candles with start_ms <= open_time < end_ms, from the monthly and daily files in kline_dir.
    Without allow_holdout the window is clamped to end before 2026-06-26 and a window that starts there is refused."""
    holdout_ms = _ms(HOLDOUT_START)
    if not allow_holdout:
        if start_ms >= holdout_ms:
            raise HoldoutRefused("window starts inside the holdout")
        end_ms = min(end_ms, holdout_ms)
    kline_dir = Path(kline_dir)
    first = datetime.fromtimestamp(start_ms / 1000, tz=timezone.utc)
    last = datetime.fromtimestamp((end_ms - 1) / 1000, tz=timezone.utc)
    names, day = set(), first.replace(hour=0, minute=0, second=0, microsecond=0)
    while day <= last:
        names.add(f"BTCUSDT-1m-{day:%Y-%m}.csv")
        names.add(f"BTCUSDT-1m-{day:%Y-%m-%d}.csv")
        day += timedelta(days=1)
    got = {}
    for name in sorted(names):
        p = kline_dir / name
        if p.exists():
            _read_file(p, start_ms, end_ms, got)
    return [got[t] for t in sorted(got)]


# ---------------------------------------------------------------- power

def _cdf(n, k, p):
    return sum(comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(0, k + 1))


def power(n, p0=P0, p1=P1, alpha=ALPHA):
    """Exact binomial, one-sided: reject H0 (win rate = p0) when wins <= k, k the largest with P(X <= k | p0) <= alpha.
    Power = P(X <= k | p1); 0 when even zero wins is not rare enough under p0."""
    k = -1
    while k + 1 <= n and _cdf(n, k + 1, p0) <= alpha:
        k += 1
    return _cdf(n, k, p1) if k >= 0 else 0.0


def min_n_for_power(target=0.8, p0=P0, p1=P1, alpha=ALPHA, max_n=2000):
    for n in range(1, max_n + 1):
        if power(n, p0, p1, alpha) >= target:
            return n
    return None


# ---------------------------------------------------------------- the whole ledger

def read_committed_text(path):
    """A committed artefact as UTF-8 text with LF line ends. The renderers always write LF, but a Windows checkout with
    core.autocrlf=true (the Git for Windows default, so the windows-latest CI runner) stores the same file with CRLF.
    Only the line-end convention of the checkout is normalised; every other byte is still compared."""
    return Path(path).read_bytes().decode("utf-8").replace("\r\n", "\n")


def _summarize(results, col):
    xs = [r[col] for r in results if r["status"] == "SCORED"]
    wins = [x for x in xs if x["r_net"] > 0]
    losses = [x for x in xs if x["r_net"] < 0]
    mean = lambda v: sum(v) / len(v) if v else None
    return {"n": len(xs), "wins": len(wins), "losses": len(losses), "be": len(xs) - len(wins) - len(losses),
            "win_rate": len(wins) / (len(wins) + len(losses)) if wins or losses else None,
            "net_r_mean": mean([x["r_net"] for x in xs]), "net_r_sum": sum(x["r_net"] for x in xs) if xs else None,
            "mean_net_pct": mean([x["net_pct"] for x in xs]),
            "mean_win_pct": mean([x["net_pct"] for x in wins]), "mean_loss_pct": mean([x["net_pct"] for x in losses])}


def run(ledger_path, kline_dir, allow_holdout=False, loader=load_candles):
    rows = list(csv.DictReader(io.StringIO(Path(ledger_path).read_bytes().decode("utf-8"), newline="")))
    eligible = {"DEV": 0, "HOLDOUT": 0}
    rows_by_split = {}
    for r in rows:
        rows_by_split[r["window_split"]] = rows_by_split.get(r["window_split"], 0) + 1
        if r["eligible"] == "Y":
            eligible[r["window_split"]] = eligible.get(r["window_split"], 0) + 1
    results, unscored_holdout = [], []
    for r in rows:
        if r["eligible"] != "Y":
            continue
        base = {"call_id": r["call_id"], "video_id": r.get("video_id", ""), "published_utc": r["published_utc"],
                "window_split": r["window_split"], "direction": r["direction"]}
        if r["window_split"] == "NO_TIME":
            results.append({**base, "status": "NO_TIME"})
            continue
        if r["window_split"] != "DEV" and not allow_holdout:
            unscored_holdout.append({**base, "entry": r["entry"], "stop": r["stop"], "targets": r["targets"]})
            continue
        call_time = parse_utc(r["published_utc"])
        guard_call_window(call_time, allow_holdout)
        try:
            entry, stop, targets = parse_price(r["entry"]), parse_price(r["stop"]), parse_targets(r["targets"])
            candles = loader(_ms(call_time), _ms(call_time) + int(MAX_WINDOW.total_seconds() * 1000), kline_dir,
                             allow_holdout=allow_holdout)
            res = score_call(r["direction"], entry, stop, targets, call_time, candles)
        except ValueError as e:
            results.append({**base, "status": "UNPARSEABLE", "why": str(e)})
            continue
        results.append({**base, "entry": entry, "stop": stop, "targets": targets, **res})
    scored = [x for x in results if x["status"] == "SCORED"]
    status_counts = {}
    for x in results:
        status_counts[x["status"]] = status_counts.get(x["status"], 0) + 1
    return {"counts": {"ledger_rows": len(rows), "rows_by_split": rows_by_split, "eligible": eligible,
                       "scored": len(scored), "status": status_counts,
                       "plan_rows_no_stop_only": sum(1 for r in rows if r["reason"] == "no stop"),
                       "earliest_call": min((r["published_utc"] for r in rows if r["published_utc"]), default="")},
            "results": results, "unscored_holdout": unscored_holdout, "allow_holdout": allow_holdout,
            "summary": {col: _summarize(results, col) for col, _ in COLUMNS}}


# ---------------------------------------------------------------- SCORECARD.md

def claimed():
    c = CLAIM
    wl = c["wins"] / (c["wins"] + c["losses"])
    expect_pct = (c["wins"] * c["avg_win_pct"] - c["losses"] * c["avg_loss_pct"]) / c["setups"]
    return {"win_rate_excl_be": wl, "win_rate_incl_be": c["wins"] / c["setups"], "expect_pct": expect_pct,
            "expect_r": expect_pct / c["avg_loss_pct"], "fee_r": 2 * FEE_PER_SIDE * 100 / c["avg_loss_pct"]}


def _fmt(x, spec, none="n/a"):
    return none if x is None else format(x, spec)


def _pct(frac):
    return "n/a" if frac is None else f"{frac * 100:.2f}%"


def _r(x):
    return "n/a" if x is None else f"{x:+.2f}R"


def render_scorecard(out):
    cn, cl = out["counts"], claimed()
    elig, rbs = cn["eligible"], cn["rows_by_split"]
    n = cn["scored"]
    p_n = power(n)
    n80 = min_n_for_power(0.8)
    L = []
    L.append("# Qriptal scorecard (card qriptal-score-binance, B162 step 1)\n")
    if n == 0:
        L.append(f"Result: **scored n = 0.** No call is both ELIGIBLE and inside the DEV window, so there is no win rate and no net R to put against his "
                 f"{CLAIM['win_rate'] * 100:.1f}% / {CLAIM['avg_win_pct']}% / {CLAIM['avg_loss_pct']}%. Power at n = 0 is zero. "
                 f"Of {cn['ledger_rows']} candidate statements, {sum(elig.values())} are ELIGIBLE and {'both' if elig.get('HOLDOUT', 0) == 2 else 'all ' + str(elig.get('HOLDOUT', 0))} "
                 f"sit in the holdout window, which the card does not allow reading.\n")
    else:
        s = out["summary"]["t1"]
        L.append(f"Result: **scored n = {n}**, win rate {_fmt(s['win_rate'], '.1%')}, net R per call {_fmt(s['net_r_mean'], '+.2f')} (primary column), "
                 f"against his claim {CLAIM['win_rate'] * 100:.1f}% / {CLAIM['avg_win_pct']}% / {CLAIM['avg_loss_pct']}%. Power: {p_n:.0%}.\n")
    L.append("## Count per split (the data rule)\n")
    L.append("Card: dev data only, scope-out holdout reads. BACKTEST_PROTOCOL section 2: DEV 2025-09-01..2026-06-25, HOLDOUT 2026-06-26..2026-09-26. "
             f"A call is DEV only if its call time + 8 days (24 h fill window + 7 days open, RULES.md) ends by 2026-06-26T00:00Z "
             "(DECISION OURS, so no scored candle can be a holdout candle). The earliest Qriptal statement in the staged transcripts is dated {cn['earliest_call'][:10]}.\n")
    L.append("| Split | Ledger rows | ELIGIBLE | Scored |")
    L.append("|---|---|---|---|")
    for sp in ("DEV", "HOLDOUT"):
        sc = sum(1 for x in out["results"] if x["window_split"] == sp and x["status"] == "SCORED")
        L.append(f"| {sp} | {rbs.get(sp, 0)} | {elig.get(sp, 0)} | {sc} |")
    L.append(f"| Total | {cn['ledger_rows']} | {sum(elig.values())} | {n} |\n")
    if out["unscored_holdout"]:
        L.append("ELIGIBLE rows left unscored because they fall in the holdout window (not read):\n")
        L.append("| call_id | published (UTC) | direction | entry | stop | targets |")
        L.append("|---|---|---|---|---|---|")
        for x in out["unscored_holdout"]:
            L.append(f"| {x['call_id']} | {x['published_utc']} | {x['direction']} | {x['entry']} | {x['stop']} | {x['targets']} |")
        vids = len({x["video_id"] for x in out["unscored_holdout"]})
        L.append(f"\nThese {len(out['unscored_holdout'])} rows come from {vids} video(s); variants of one plan are one observation, not several. "
                 "The staged extract's own outcome check (stopped out about 14 h after the stream) is not reused: it reads holdout candles.\n")
    L.append("## Score against his claim\n")
    L.append("| | His claim (qriptal.com, 86 setups) | Scored here (DEV, 0.05% per side) |")
    L.append("|---|---|---|")
    s = out["summary"]["t1"]
    L.append(f"| Setups / calls | {CLAIM['setups']} (49 W / 13 BE / 24 L) | n = {n} |")
    L.append(f"| Win rate | {CLAIM['win_rate'] * 100:.1f}% (= 49 / (49 + 24), BE left out; with BE counted {cl['win_rate_incl_be'] * 100:.1f}%) | {_fmt(s['win_rate'], '.1%')} (wins / (wins + losses)) |")
    L.append(f"| Average winner | {CLAIM['avg_win_pct']}% | {_pct(s['mean_win_pct'])} |")
    L.append(f"| Average loser | {CLAIM['avg_loss_pct']}% | {_pct(s['mean_loss_pct'])} |")
    L.append(f"| Net R per call | about +{cl['expect_r']:.1f}R before fees if 1R = his average loser (expectancy {cl['expect_pct']:.2f}% per setup, BE as 0) | {_r(s['net_r_mean'])} (second column: {_r(out['summary']['last']['net_r_mean'])}) |")
    L.append("")
    L.append("His percentages are as he posts them; whether they are price moves or account percent is not stated. "
             f"Fees at 0.05% per side are 0.10% a round trip, about {cl['fee_r']:.2f}R if 1R is his 0.63% average loser.\n")
    L.append("## Power\n")
    L.append(f"Test: exact binomial, H0 true win rate = {P0:.1%} (his claim), H1 = {P1:.0%}, one-sided alpha {ALPHA}. "
             f"With n = {n} the power is {p_n:.0%}"
             + (", because no sample means no evidence either way." if n == 0 else ".") + "\n")
    L.append("| Scored calls n | Reject his claim if wins are | Power vs a coin flip |")
    L.append("|---|---|---|")
    for k in (0, 2, 3, 10, 30, 49, 56, 86):
        kk = -1
        while kk + 1 <= k and _cdf(k, kk + 1, P0) <= ALPHA:
            kk += 1
        L.append(f"| {k} | {'cannot reject' if kk < 0 else f'{kk} or fewer'} | {power(k):.1%} |")
    L.append(f"\nFirst n with 80% power: **{n80}** scored calls. To separate his claimed rate from a still-profitable 57% "
             f"(his own tally with BE counted) takes {min_n_for_power(0.8, P0, 0.57)} calls. Holdout rows that are variants of one plan count once, so scoring them "
             f"would give n = 1 and power {power(1):.0%}.\n")
    L.append("## Method (frozen before any score; every number OURS, none from a trader quote)\n")
    L.append("- Prices only from the ledger's ELIGIBLE rows: entry, stop and at least one target spoken with a number. A stop that was never priced is not invented; "
             f"the {cn['plan_rows_no_stop_only']} PLAN rows with an entry and a target but no stop stay unscored (NO-SOURCE, card scope-out).")
    L.append("- Call time = YouTube publish time (CALL_LEDGER.csv `published_utc`). The first candle used is the first one that opens at or after it.")
    L.append("- Entry fills at the posted price in the first 1m candle whose range contains it, within 24 h; else NOT_FILLED (counted, not scored). "
             "In the fill candle only the stop is checked (the order of entry and target inside one candle is unknown).")
    L.append("- Stop and target inside the same 1m candle = stop. Trade still open 7 days after the fill = closed at the close of the last candle before day 7. "
             "A series that ends before the trade resolves is NO_DATA (not scored).")
    L.append("- Primary column exits everything at T1; second column exits everything at the last target. Fee 0.05% of price per side: "
             "net = side x (exit - entry) - 0.0005 x (entry + exit); R = net / |entry - stop|; return = net / entry.")
    L.append("- Win = net R above 0, loss = net R below 0 (a stop-out is always a loss after fees); win rate = wins / (wins + losses), the same convention as his 67.1%.\n")
    L.append("## What would give a real score\n")
    L.append("1. His 86-setup list on qriptal.com / Discord with dates, entries, stops and targets (not staged; the operator paste only gives the totals).")
    L.append("2. His Sunday live streams (the weekly plans that carry priced stops; one is staged and holds the only 2 eligible calls) and the uploads still without transcripts, "
             "fetched by the daily retry (ids in LEDGER_NOTES.md).")
    L.append("3. A coordinator decision to read the holdout. Not taken here: it would add one plan at most, power stays about 0.\n")
    L.append("## Reproduce\n")
    L.append("```")
    L.append("python MyTradingSys/research/qriptal_2026-10-10/test_score_calls.py")
    L.append("python MyTradingSys/research/qriptal_2026-10-10/score_calls.py run      # rewrites this file")
    L.append("python MyTradingSys/research/qriptal_2026-10-10/score_calls.py check    # exit 1 if it differs")
    L.append("```")
    return "\n".join(L) + "\n"


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "check"
    allow = "--allow-holdout" in argv
    if cmd not in ("run", "check"):
        print(__doc__)
        return 2
    text = render_scorecard(run(LEDGER, KLINE_DIR, allow_holdout=allow))
    if cmd == "run":
        with open(SCORECARD, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        print(f"wrote {SCORECARD.name}")
        return 0
    same = SCORECARD.exists() and read_committed_text(SCORECARD) == text
    print("SCORECARD.md matches a rerun" if same else "SCORECARD.md DIFFERS from a rerun: run `run`")
    return 0 if same else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
