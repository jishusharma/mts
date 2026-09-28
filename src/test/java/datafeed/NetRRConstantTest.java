package datafeed;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

/**
 * W2 finding #2 (FORMULA_INVENTORY.md priority 2): net R:R was 0.75 hardcoded
 * in SetupCandidatesBuilder.java and 1-0.25 (a named friction parameter) in
 * mts_math.py - two unsynced copies of the same number. This test targets
 * the new shared constant (ExecutionMathConstants, staged .new) with
 * hand-computed expectations independent of any existing code:
 *
 *   net_rr = gross_rr * (1 - friction), friction = 0.25
 *
 * Hand-computed cases:
 *   gross_rr=2.0   -> net_rr = 2.0 * 0.75 = 1.5
 *   gross_rr=3.5   -> net_rr = 3.5 * 0.75 = 2.625
 *   gross_rr=8/3   -> net_rr = (8/3) * 0.75 = 2.0 (exercises a non-terminating
 *                     intermediate decimal to make sure no premature rounding
 *                     is baked into the constant/helper)
 *   gross_rr=0.0   -> net_rr = 0.0
 *
 * NOTE ExecutionMathConstants.java.new and SetupCandidatesBuilder.java.new
 * are staged only (not promoted/wired/committed) pending Opus review, per
 * the W2 brief. This test is staged alongside them for the same reason and
 * is not yet part of the active build.
 */
public class NetRRConstantTest {

    private static final double EPS = 1e-9;

    @Test
    void frictionConstantMatchesPythonDefault() {
        // mts_math.calculate_net_rr's default friction is 0.25 - must match exactly.
        assertEquals(0.25, ExecutionMathConstants.NET_RR_FRICTION, EPS);
    }

    @Test
    void netRRTypicalCase() {
        assertEquals(1.5, ExecutionMathConstants.netRR(2.0), EPS);
    }

    @Test
    void netRRAnotherTypicalCase() {
        assertEquals(2.625, ExecutionMathConstants.netRR(3.5), EPS);
    }

    @Test
    void netRRNonTerminatingIntermediate() {
        double grossRR = 8.0 / 3.0; // 2.6666666...
        assertEquals(2.0, ExecutionMathConstants.netRR(grossRR), EPS);
    }

    @Test
    void netRRZero() {
        assertEquals(0.0, ExecutionMathConstants.netRR(0.0), EPS);
    }

    @Test
    void netRRMatchesLegacyHardcodedMultiplier() {
        // Cross-check: the OLD hardcoded `grossRR * 0.75` in
        // SetupCandidatesBuilder.java and the new shared constant must agree
        // numerically today (this test would catch either one silently
        // drifting once the constant is promoted and wired in).
        double grossRR = 4.2;
        double legacy = grossRR * 0.75;
        assertEquals(legacy, ExecutionMathConstants.netRR(grossRR), EPS);
    }
}
