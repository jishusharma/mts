package datafeed;

/**
 * Single shared home for execution-math constants that were previously
 * duplicated (hardcoded) independently in Java and Python.
 *
 * W2 finding (FORMULA_INVENTORY.md priority 2): SetupCandidatesBuilder.java
 * computed net R:R as `grossRR * 0.75` (a hardcoded literal) while
 * MyTradingSys/runtime/mts_math.py:calculate_net_rr computed the same thing
 * as `gross_rr * (1.0 - friction)` with `friction: float = 0.25` (a named,
 * overridable parameter). Both currently agree numerically (0.75 == 1-0.25),
 * but they are two unsynced copies of the same constant with no single
 * source of truth - a change to one silently drifts from the other.
 *
 * Canonical source for the number itself: FORMULAS.md's Core section
 * ("Net R:R (Python)" / "Net R:R (Java)" rows) - this class does not
 * change the value (0.25 friction / 0.75 multiplier), only its ownership.
 *
 * STAGED (.new) - not wired into SetupCandidatesBuilder.java yet; that is
 * SetupCandidatesBuilder.java.new (also staged). Pending Opus review before
 * either file is promoted (W2 brief: never promote/rename/commit execution
 * or Java sources here).
 */
public final class ExecutionMathConstants {

    private ExecutionMathConstants() {
    }

    /**
     * Fraction of gross R:R removed to account for trading friction (fees +
     * slippage) when computing net R:R. Matches Python's
     * mts_math.calculate_net_rr default (`friction=0.25`).
     */
    public static final double NET_RR_FRICTION = 0.25;

    /**
     * netRR = grossRR * (1 - NET_RR_FRICTION). Kept as a named helper so
     * both Java call sites (SetupCandidatesBuilder today; any future one)
     * compute it identically, rather than re-deriving `1 - NET_RR_FRICTION`
     * inline each time.
     */
    public static double netRR(double grossRR) {
        return grossRR * (1.0 - NET_RR_FRICTION);
    }
}
