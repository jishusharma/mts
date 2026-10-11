package datafeed;

import org.junit.jupiter.api.Test;

import java.lang.reflect.Constructor;
import java.lang.reflect.Field;
import java.lang.reflect.Method;

import static org.junit.jupiter.api.Assertions.assertEquals;

/**
 * Unit tests for the D4 directional countSignals() rule (SetupCandidatesBuilder.java,
 * task C3, CORE_READINESS_PLAN.md section 3 D4 / D1_D7_DECISION_BRIEF.md D4 ruling
 * "DIRECTIONAL-ONLY"). ProofResult is a private static nested class with no public
 * accessor, so these tests use reflection to construct it and set only the field(s)
 * relevant to each rule - the same reflection-based verification approach already
 * used in this project (scripts/tools/VerifyScbEdits.java, see CORE_READINESS_PLAN.md
 * F4) rather than widening ProofResult's visibility for testability alone.
 */
public class CountSignalsD4Test {

    private static Object newProofResult() throws Exception {
        Class<?> cls = Class.forName("datafeed.SetupCandidatesBuilder$ProofResult");
        Constructor<?> ctor = cls.getDeclaredConstructor();
        ctor.setAccessible(true);
        return ctor.newInstance();
    }

    private static void setField(Object obj, String name, Object value) throws Exception {
        Field f = obj.getClass().getDeclaredField(name);
        f.setAccessible(true);
        f.set(obj, value);
    }

    private static int countSignals(Object proofResult, String direction) throws Exception {
        Method m = proofResult.getClass().getDeclaredMethod("countSignals", String.class);
        m.setAccessible(true);
        return (int) m.invoke(proofResult, direction);
    }

    // --- Book imbalance: B131 removed it from the proof count (still in JSON) ---

    @Test
    void bookImbalance_longFavoured_doesNotCount_B131() throws Exception {
        Object p = newProofResult();
        setField(p, "bookImbalance", 2.0);
        assertEquals(0, countSignals(p, "long"));
    }

    @Test
    void bookImbalance_longAgainstTrade_doesNotCount() throws Exception {
        Object p = newProofResult();
        setField(p, "bookImbalance", 0.3); // <0.67: favours short, not long
        assertEquals(0, countSignals(p, "long"));
    }

    @Test
    void bookImbalance_shortFavoured_doesNotCount_B131() throws Exception {
        Object p = newProofResult();
        setField(p, "bookImbalance", 0.3);
        assertEquals(0, countSignals(p, "short"));
    }

    @Test
    void bookImbalance_shortAgainstTrade_doesNotCount() throws Exception {
        Object p = newProofResult();
        setField(p, "bookImbalance", 2.0); // >1.5: favours long, not short
        assertEquals(0, countSignals(p, "short"));
    }

    @Test
    void bookImbalance_neutral_doesNotCount() throws Exception {
        Object p = newProofResult();
        setField(p, "bookImbalance", 1.0); // inside 0.67-1.5, unchanged from old behaviour
        assertEquals(0, countSignals(p, "long"));
        assertEquals(0, countSignals(p, "short"));
    }

    // --- Finished auction: long favours a finished "sell" auction, short favours "buy" ---

    @Test
    void finishedAuction_longFavoured_counts() throws Exception {
        Object p = newProofResult();
        setField(p, "finishedAuctionDetected", true);
        setField(p, "finishedAuctionDirection", "sell");
        assertEquals(1, countSignals(p, "long"));
    }

    @Test
    void finishedAuction_longAgainstTrade_doesNotCount() throws Exception {
        Object p = newProofResult();
        setField(p, "finishedAuctionDetected", true);
        setField(p, "finishedAuctionDirection", "buy");
        assertEquals(0, countSignals(p, "long"));
    }

    @Test
    void finishedAuction_shortFavoured_counts() throws Exception {
        Object p = newProofResult();
        setField(p, "finishedAuctionDetected", true);
        setField(p, "finishedAuctionDirection", "buy");
        assertEquals(1, countSignals(p, "short"));
    }

    @Test
    void finishedAuction_shortAgainstTrade_doesNotCount() throws Exception {
        Object p = newProofResult();
        setField(p, "finishedAuctionDetected", true);
        setField(p, "finishedAuctionDirection", "sell");
        assertEquals(0, countSignals(p, "short"));
    }

    // --- Speed: no longer counted toward proof, in either direction ---

    @Test
    void speedPickingUp_longDirection_neverCounts() throws Exception {
        Object p = newProofResult();
        setField(p, "speedPickingUp", true);
        assertEquals(0, countSignals(p, "long"));
    }

    @Test
    void speedPickingUp_shortDirection_neverCounts() throws Exception {
        Object p = newProofResult();
        setField(p, "speedPickingUp", true);
        assertEquals(0, countSignals(p, "short"));
    }

    // --- Volume spike: B144 no source (operator D17), not counted; still emitted in the proof JSON ---

    @Test
    void volumeSpike_doesNotCount_B144() throws Exception {
        Object p = newProofResult();
        setField(p, "volumeSpikeDetected", true);
        setField(p, "volumeSpikeAtLevel", true);
        assertEquals(0, countSignals(p, "long"));
        assertEquals(0, countSignals(p, "short"));
    }

    // --- Unaffected signals still count regardless of direction (regression guard) ---

    @Test
    void rejectionWick_stillCountsRegardlessOfDirection() throws Exception {
        Object p = newProofResult();
        setField(p, "rejectionWick", "upper");
        assertEquals(1, countSignals(p, "long"));
        assertEquals(1, countSignals(p, "short"));
    }

    @Test
    void cvdAligned_stillCountsRegardlessOfDirection() throws Exception {
        Object p = newProofResult();
        setField(p, "cvdAligned", true);
        assertEquals(1, countSignals(p, "long"));
        assertEquals(1, countSignals(p, "short"));
    }

    @Test
    void multipleFavourableSignals_sumCorrectly() throws Exception {
        Object p = newProofResult();
        setField(p, "bookImbalance", 2.0);              // B131: never counted: +0
        setField(p, "finishedAuctionDetected", true);
        setField(p, "finishedAuctionDirection", "sell"); // favours long: +1
        setField(p, "cvdAligned", true);                  // unaffected: +1
        setField(p, "speedPickingUp", true);              // never counted: +0
        assertEquals(2, countSignals(p, "long"));
    }
}
