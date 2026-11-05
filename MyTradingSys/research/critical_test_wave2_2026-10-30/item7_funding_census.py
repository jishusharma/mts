"""Critical test wave 2 item 7: which backtest scripts charge historical perp funding.

Scans tracked .py files under MyTradingSys/backtest and MyTradingSys/research (tests excluded) that simulate
trades (a trade-result marker: net_r, pnl, simulate_trade, fees import) and classifies each:
  CHARGES   calls a funding charge (bt_engine.simulate_trade with funding records, trade_costs.funding_paid,
            bt_data.funding_cost_pct, a local funding_charge) and never passes funding=[] only
  ZERO      calls simulate_trade only with funding=[] (explicit no-funding model)
  MENTIONS  says "funding" but calls no charge (feature, comment or filter): fee-only lower bound
  NONE      no funding at all: fee-only lower bound
Run: python MyTradingSys/research/critical_test_wave2_2026-10-30/item7_funding_census.py
"""
import collections
import re
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent / "item7_census.tsv"
TRADE = re.compile(r"\bnet_r\b|\bpnl\b|net_R|simulate_trade|import fees|from fees|fees\.(DERIBIT|BINANCE)|"
                   r"fee_r\b|fee_pct|trade_costs")
ZERO = re.compile(r"funding\s*=\s*\[\]")
FUNDREC = re.compile(r"funding\s*=\s*(?!\[\])\w")


def classify(text):
    if re.search(r"^def (funding_paid|funding_cost_pct|funding_charge|funding_r)\(|^def simulate_trade\(side, entry_price", text, re.M):
        return "LIB"
    calls = re.sub(r"^def .*$", "", text, flags=re.M)
    if re.search(r"funding_paid\(|funding_cost_pct\(|funding_charge\(|funding_r\(", calls) or (
            "net_return(" in calls and "trade_costs" in text):
        return "CHARGES"
    if not TRADE.search(text):
        return None
    if "simulate_trade(" in calls and "bt_engine" in text:
        if FUNDREC.search(text):
            return "CHARGES"
        if ZERO.search(text):
            return "ZERO"
        return "CHARGES"   # simulate_trade raises without funding (B103), so a working caller passed records
    return "MENTIONS" if re.search("funding", text, re.I) else "NONE"


def main():
    files = subprocess.run(["git", "-C", str(REPO), "ls-files", "MyTradingSys/backtest", "MyTradingSys/research"],
                           capture_output=True, text=True, check=True).stdout.split()
    rows = []
    for f in files:
        name = f.rsplit("/", 1)[-1]
        if not f.endswith(".py") or name.startswith("test_") or "/tests/" in f:
            continue
        try:
            text = (REPO / f).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        c = classify(text)
        if c:
            rows.append((c, f))
    rows.sort()
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("class\tpath\n")
        for c, f in rows:
            fh.write(f"{c}\t{f}\n")
    cnt = collections.Counter(c for c, _ in rows)
    top = collections.Counter((c, f.split("/")[1]) for c, f in rows)
    print("trade scripts:", len(rows), dict(cnt))
    print({f"{c}:{area}": n for (c, area), n in sorted(top.items())})


if __name__ == "__main__":
    main()
