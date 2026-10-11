package datafeed;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

/** B066: the 2026-09-20 case (pf_vah 80373.47 vs price 80524, 150.53 pts) must not be trigger_ready. */
public class SetupCandidatesBuilderTierTest {

    @Test
    public void zone150PointsAwayIsConditionalNotTriggerReady() {
        double distPct = Math.abs(80524.0 - 80373.47) / 80524.0 * 100.0;  // 0.1869
        assertEquals("conditional", SetupCandidatesBuilder.tierFor(distPct, 0.5));
    }

    @Test
    public void tierBoundaries() {
        assertEquals("trigger_ready", SetupCandidatesBuilder.tierFor(0.1, 0.5));
        assertEquals("conditional", SetupCandidatesBuilder.tierFor(0.1001, 0.5));
        assertEquals("conditional", SetupCandidatesBuilder.tierFor(0.5, 0.5));
        assertEquals("ignore", SetupCandidatesBuilder.tierFor(0.5001, 0.5));
    }
}
