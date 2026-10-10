package datafeed;

/**
 * Single shared home for execution-math constants (net R:R). B070 (operator ruling (a), 2026-10-03): net R:R uses the
 * exchange fee model from MyTradingSys/backtest/fees.py (FORMULAS.md section 17), not the flat 25% haircut that had no
 * trader source. Python twin: MyTradingSys/runtime/mts_math.py calculate_net_rr.
 */
public final class ExecutionMathConstants {

    private ExecutionMathConstants() {
    }

    /**
     * B070: taker fee per side as a fraction of price. Mirrors MyTradingSys/backtest/fees.py DERIBIT_TAKER (= BINANCE_TAKER,
     * 0.0005). fees.py is the source; MyTradingSys/tests/test_b070_fee_parity.py fails if this number drifts from it.
     */
    public static final double TAKER_FEE_PER_SIDE = 0.0005;

    /**
     * Tom-verdict fee per market: FDAX (symbol GER40) taker fee per side as a fraction of price, ~0.1 point per round turn.
     * Mirrors MyTradingSys/backtest/fees.py FDAX_FEE_PER_SIDE; test_b070_fee_parity.py fails if this drifts.
     */
    public static final double FDAX_FEE_PER_SIDE = 0.000005;

    /** Fee per side for the instrument. GER40 -> FDAX; BTCUSDT, null and every unknown symbol -> TAKER_FEE_PER_SIDE (unchanged live value). */
    public static double feePerSide(String symbol) {
        return "GER40".equals(symbol) ? FDAX_FEE_PER_SIDE : TAKER_FEE_PER_SIDE;
    }

    /** Per-instrument netRR; same formula as the 3-arg overload with the instrument's fee. */
    public static double netRR(String symbol, double entry, double target, double stop) {
        double risk = Math.abs(entry - stop);
        if (risk == 0) {
            return 0.0;
        }
        double cost = 2.0 * feePerSide(symbol) * entry;
        return (Math.abs(target - entry) - cost) / (risk + cost);
    }

    /**
     * B070 fee model (FORMULAS.md section 17): both legs taker, cost = 2 * taker * entry in price units.
     * netRR = (|target - entry| - cost) / (|entry - stop| + cost). Zero risk -> 0.0. Replaces the flat gross * 0.75.
     */
    public static double netRR(double entry, double target, double stop) {
        return netRR(null, entry, target, stop);
    }
}
