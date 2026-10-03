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
     * B070 fee model (FORMULAS.md section 17): both legs taker, cost = 2 * taker * entry in price units.
     * netRR = (|target - entry| - cost) / (|entry - stop| + cost). Zero risk -> 0.0. Replaces the flat gross * 0.75.
     */
    public static double netRR(double entry, double target, double stop) {
        double risk = Math.abs(entry - stop);
        if (risk == 0) {
            return 0.0;
        }
        double cost = 2.0 * TAKER_FEE_PER_SIDE * entry;
        return (Math.abs(target - entry) - cost) / (risk + cost);
    }
}
