package datafeed;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

/**
 * Tom-verdict fee per market. Hand values:
 * GER40 24229 -> 24111 (stop 24257): c = 2*0.000005*24229 = 0.24229; (118-c)/(28+c) = 117.75771/28.24229 = 4.1696.
 * BTCUSDT 100 -> 104 stop 98: c = 0.1 ; (4-0.1)/(2+0.1) = 3.9/2.1. BTCUSDT 60000 -> 59000 stop 60500: c = 60;
 * (1000-60)/(500+60) = 940/560.
 */
public class NetRRPerMarketFeeTest {

    private static final double EPS = 1e-9;

    @Test
    void ger40UsesFdaxFee() {
        double c = 2 * 0.000005 * 24229;
        assertEquals((118 - c) / (28 + c), ExecutionMathConstants.netRR("GER40", 24229, 24111, 24257), EPS);
        assertEquals(4.1696, ExecutionMathConstants.netRR("GER40", 24229, 24111, 24257), 5e-5);
    }

    @Test
    void btcAndUnknownKeepDeribitFee() {
        assertEquals(3.9 / 2.1, ExecutionMathConstants.netRR("BTCUSDT", 100.0, 104.0, 98.0), EPS);
        assertEquals(940.0 / 560.0, ExecutionMathConstants.netRR("BTCUSDT", 60000, 59000, 60500), EPS);
        assertEquals(940.0 / 560.0, ExecutionMathConstants.netRR("XYZ", 60000, 59000, 60500), EPS);
        assertEquals(940.0 / 560.0, ExecutionMathConstants.netRR(null, 60000, 59000, 60500), EPS);
    }

    /** Live path bit-identity: the 3-arg overload and the BTC symbol equal the pre-change formula exactly (==, not EPS). */
    @Test
    void btcBitIdenticalToPreChangeFormula() {
        double[][] cases = {{60000, 59000, 60500}, {100, 104, 98}, {23871.35, 23902.1, 23850.7}, {67432.1, 67890.5, 67100.3}};
        for (double[] k : cases) {
            double risk = Math.abs(k[0] - k[2]);
            double cost = 2.0 * 0.0005 * k[0];
            double old = (Math.abs(k[1] - k[0]) - cost) / (risk + cost);
            assertEquals(Double.doubleToLongBits(old), Double.doubleToLongBits(ExecutionMathConstants.netRR(k[0], k[1], k[2])));
            assertEquals(Double.doubleToLongBits(old), Double.doubleToLongBits(ExecutionMathConstants.netRR("BTCUSDT", k[0], k[1], k[2])));
        }
    }
}
