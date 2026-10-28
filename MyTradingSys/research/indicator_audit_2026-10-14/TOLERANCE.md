# Tolerance and seed (OURS), written 2026-10-20 BEFORE any reviewer reply

- Seed: 20261020 (OURS: the run date). Pool: public Binance USDT-M klines BTCUSDT/ETHUSDT x 5m/15m/1h, 1499 closed bars each, `klines_pool.json`.
- RSI, StochRSI K and D: absolute 0.01 points.
- Bollinger mid / upper / lower: relative 1e-6 (population sd, FORMULAS.md s22).
- A missing, non-numeric or non-finite reply value is a mismatch.
- Comparison is done in code (`scripts/dev/indicator_audit_compare.py`), never by asking a model.
