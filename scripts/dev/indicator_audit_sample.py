"""Seeded sample + blind packets for the indicator-values audit (card indicator-values-multi-model-audit).

  python scripts/dev/indicator_audit_sample.py fetch  --pool <pool.json>            # public Binance fapi klines, closed bars only
  python scripts/dev/indicator_audit_sample.py draw   --pool <pool.json> --seed N --out <dir>

A packet = 500 consecutive closes ending at the sampled bar + the FORMULAS.md definition text + the question.
It never holds our value or any engine code (this module does not import the engine). Market data only: public repo.
Formulas: MyTradingSys/backtest/layers/FORMULAS.md s1 (RSI), s22 (Bollinger), s23 (StochRSI).
"""
import argparse
import hashlib
import json
import pathlib
import random
import re
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
FORMULAS = ROOT / "MyTradingSys" / "backtest" / "layers" / "FORMULAS.md"
FAPI = "https://fapi.binance.com/fapi/v1/klines"

WINDOW = 500                      # OURS: card says >= 500 closes (Wilder seed truncation costs < 1e-9 at 500 bars)
PER_INDICATOR = 7                 # OURS: 7 x 3 = 21 values ("about 20", >= 6 each)
SYMBOLS = ("BTCUSDT", "ETHUSDT")  # OURS
TFS = ("5m", "15m", "1h")         # OURS: three timeframes (card needs >= 2)
POOL_BARS = 1500
INDICATORS = ("RSI", "BB", "STOCHRSI")
ANSWER_KEYS = {"RSI": ["RSI"], "BB": ["BB_mid", "BB_up", "BB_low"], "STOCHRSI": ["StochRSI_K", "StochRSI_D"]}
QUESTION = {
    "RSI": "Compute RSI with period 14 at the LAST close of the list (the definition below).",
    "BB": "Compute Bollinger Bands with n=20 and mult=2 at the LAST close of the list: BB_mid, BB_up, BB_low.",
    "STOCHRSI": "Compute Stochastic RSI with rsi_len=14, stoch_len=14, k_len=3, d_len=3 at the LAST close of the "
                "list: StochRSI_K and StochRSI_D, both in 0..100.",
}


def window_sha256(closes):
    return hashlib.sha256(json.dumps(closes, separators=(",", ":")).encode()).hexdigest()


def _section(text, num):
    m = re.search(rf"^## {num}\. .*?$(.*?)(?=^## \d+\. |^## Verification note)", text, re.S | re.M)
    if not m:
        raise SystemExit(f"FORMULAS.md section {num} not found")
    return m.group(1).strip()


def _scrub(s):
    """Remove the clauses that name repo files/code so a packet carries the definition only; keep the layout."""
    s = re.sub(r"; CoinGlass shows the same pair, verified chart by chart with `chart_verify\.py --seen`", "", s)
    s = re.sub(r"Checked 2026-10-17 against `[^`]*\.py` lines [0-9-]+: it divides by n \(population\), so the two agree\. ", "", s)
    if ".py" in s or "chart_verify" in s:
        raise SystemExit("definition text still names a repo file; update _scrub")
    return s


def definition_text(indicator, formulas_path=FORMULAS):
    text = pathlib.Path(formulas_path).read_text(encoding="utf-8")
    s1 = _section(text, 1)
    rsi_def = s1[s1.index("**Chosen definition"):s1.index("**Canonical source")].strip()
    rsi_ex = s1[s1.index("**Worked example (period=3)"):].strip()
    rsi = _scrub(rsi_def + "\n\n" + rsi_ex)
    if indicator == "RSI":
        return rsi
    if indicator == "BB":
        return _scrub(_section(text, 22))
    if indicator == "STOCHRSI":
        return "Section 1 (RSI) definition:\n" + rsi + "\n\nSection 23 (Stochastic RSI):\n" + _scrub(_section(text, 23))
    raise ValueError(indicator)


def draw(pool, seed):
    """pool: {"SYM|tf": {symbol, tf, open_times, closes}} -> list of packets, deterministic in seed."""
    rnd = random.Random(seed)
    keys = [f"{s}|{t}" for s in SYMBOLS for t in TFS]
    packets = []
    for ind in INDICATORS:
        order = keys[:]
        rnd.shuffle(order)
        for i in range(PER_INDICATOR):
            key = order[i % len(order)]
            row = pool[key]
            n = len(row["closes"])
            end = rnd.randrange(WINDOW - 1, n)          # index of the last close in the window
            closes = row["closes"][end - WINDOW + 1:end + 1]
            pid = f"{ind.lower()}-{i + 1:02d}-{row['symbol'].lower()}-{row['tf']}"
            packets.append({
                "id": pid, "indicator": ind, "symbol": row["symbol"], "tf": row["tf"],
                "last_close_open_time_ms": row["open_times"][end], "n_closes": len(closes),
                "closes": closes, "sha256": window_sha256(closes),
                "definition": definition_text(ind), "question": QUESTION[ind],
                "answer_keys": ANSWER_KEYS[ind],
                "reply_format": "JSON object with exactly the answer_keys as keys and plain numbers as values, "
                                "e.g. {\"%s\": 0.0}" % ANSWER_KEYS[ind][0],
            })
    return packets


def fetch_pool(path):
    """Public klines only. The still-forming last bar is dropped so every close is final."""
    pool = {}
    for sym in SYMBOLS:
        for tf in TFS:
            with urllib.request.urlopen(f"{FAPI}?symbol={sym}&interval={tf}&limit={POOL_BARS}", timeout=30) as f:
                rows = json.load(f)[:-1]
            pool[f"{sym}|{tf}"] = {"symbol": sym, "tf": tf, "open_times": [int(r[0]) for r in rows],
                                   "closes": [float(r[4]) for r in rows]}
    pathlib.Path(path).write_text(json.dumps(pool, separators=(",", ":")), encoding="utf-8", newline="\n")
    return pool


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("fetch")
    p.add_argument("--pool", required=True)
    p = sub.add_parser("draw")
    p.add_argument("--pool", required=True)
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    if a.cmd == "fetch":
        pool = fetch_pool(a.pool)
        print({k: len(v["closes"]) for k, v in pool.items()})
        return 0
    pool = json.loads(pathlib.Path(a.pool).read_text(encoding="utf-8"))
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    pk = draw(pool, a.seed)
    for p in pk:
        (out / f"{p['id']}.json").write_text(json.dumps(p, separators=(",", ":")), encoding="utf-8", newline="\n")
    manifest = [{k: p[k] for k in ("id", "indicator", "symbol", "tf", "last_close_open_time_ms", "n_closes", "sha256")}
                for p in pk]
    (out / "manifest.json").write_text(json.dumps({"seed": a.seed, "packets": manifest}, indent=1) + "\n",
                                       encoding="utf-8", newline="\n")
    print(f"seed={a.seed} packets={len(pk)} -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
