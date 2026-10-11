"""Top up the cached 1m klines (Dumps/backtest/raw/klines) to yesterday, for alert_rate_check.

Idempotent: the fetcher skips days already on disk. A failed download (archive lags ~1 day, no
internet) is not fatal; the check then runs on whatever candles exist and says so in its output.
Run daily before alert_rate_check (runtime_data/launch-alert-rate-check.vbs).
"""
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
FETCH = REPO / "MyTradingSys" / "backtest" / "fetch_binance_archive.py"
DAYS_BACK = 5


def main():
    today = date.today()
    start = (today - timedelta(days=DAYS_BACK)).isoformat()
    end = (today - timedelta(days=1)).isoformat()
    r = subprocess.run([sys.executable, str(FETCH), "--start", start, "--end", end, "--datasets", "klines"])
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
