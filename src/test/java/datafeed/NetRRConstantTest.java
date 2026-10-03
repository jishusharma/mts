package datafeed;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

/**
 * B070: net R:R is the exchange fee model (MyTradingSys/backtest/fees.py, FORMULAS.md section 17), not gross * 0.75.
 *   cost   = 2 * taker * entry, taker = 0.0005
 *   net_rr = (|target - entry| - cost) / (|entry - stop| + cost)
 * Hand-computed cases, entry 100 -> cost = 0.1:
 *   long  100 -> 104, stop 98   : (4 - 0.1) / (2 + 0.1) = 3.9 / 2.1
 *   short 100 -> 96,  stop 102  : same
 *   100 -> 100.3, stop 99.9     : (0.3 - 0.1) / (0.1 + 0.1) = 1.0 (gross 3.0)
 *   stop == entry               : 0.0
 */
public class NetRRConstantTest {

    private static final double EPS = 1e-9;

    @Test
    void takerFeeMatchesFeesPy() {
        assertEquals(0.0005, ExecutionMathConstants.TAKER_FEE_PER_SIDE, EPS);
    }

    @Test
    void netRRLong() {
        assertEquals(3.9 / 2.1, ExecutionMathConstants.netRR(100.0, 104.0, 98.0), EPS);
    }

    @Test
    void netRRShortMirrorsLong() {
        assertEquals(3.9 / 2.1, ExecutionMathConstants.netRR(100.0, 96.0, 102.0), EPS);
    }

    @Test
    void netRRTightStopCostsMoreR() {
        assertEquals(1.0, ExecutionMathConstants.netRR(100.0, 100.3, 99.9), EPS);
    }

    @Test
    void netRRIsNotTheOldFlatHaircut() {
        // gross 2.0: old code gave 1.5; the fee model gives (4 - 0.1) / (2 + 0.1) = 1.857 for reward 4, risk 2 (gross 2.0)
        double old = 2.0 * 0.75;
        assertEquals(false, Math.abs(ExecutionMathConstants.netRR(100.0, 104.0, 98.0) - old) < EPS);
    }

    @Test
    void netRRZeroRisk() {
        assertEquals(0.0, ExecutionMathConstants.netRR(100.0, 104.0, 100.0), EPS);
    }
}
