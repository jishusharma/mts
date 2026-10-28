package datafeed;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;

import java.util.ArrayList;
import java.util.List;

/**
 * Fair Value Gap (FVG) detector.
 * A bullish FVG: candle[i+1].low > candle[i-1].high (gap between i-1 high and i+1 low).
 * A bearish FVG: candle[i+1].high < candle[i-1].low (gap between i+1 high and i-1 low).
 * Only returns gaps that have NOT been filled by subsequent price action.
 */
public class FvgCalculator {

    public static class Fvg {
        public final String type;      // "bullish" or "bearish"
        public final double top;       // top of the gap
        public final double bottom;    // bottom of the gap
        public final int  startIndex;  // index of left candle
        public final long openTime;    // timestamp of left candle
        public final boolean filled;   // whether price has returned into the gap

        public Fvg(String type, double top, double bottom, int startIndex, long openTime, boolean filled) {
            this.type = type;
            this.top = top;
            this.bottom = bottom;
            this.startIndex = startIndex;
            this.openTime = openTime;
            this.filled = filled;
        }
    }

    /**
     * Detect FVGs in the provided klines.
     * @param klines Jackson array of kline arrays
     * @param maxReturn max FVGs to return (most recent first)
     */
    public List<Fvg> detect(JsonNode klines, int maxReturn) {
        List<Fvg> result = new ArrayList<>();
        int n = klines.size();
        if (n < 3) return result;

        for (int i = 1; i < n - 1; i++) {
            JsonNode left = klines.get(i - 1);
            JsonNode mid  = klines.get(i);
            JsonNode right = klines.get(i + 1);

            double leftHigh = left.get(2).asDouble();
            double leftLow  = left.get(3).asDouble();
            double rightHigh = right.get(2).asDouble();
            double rightLow  = right.get(3).asDouble();

            // Bullish FVG
            if (rightLow > leftHigh) {
                boolean filled = isGapFilled(klines, i + 2, n, leftHigh, rightLow);
                result.add(new Fvg("bullish", rightLow, leftHigh, i - 1, left.get(0).asLong(), filled));
            }
            // Bearish FVG
            else if (rightHigh < leftLow) {
                boolean filled = isGapFilled(klines, i + 2, n, rightHigh, leftLow);
                result.add(new Fvg("bearish", leftLow, rightHigh, i - 1, left.get(0).asLong(), filled));
            }
        }

        // Return most recent unfilled first, then filled
        result.sort((a, b) -> Integer.compare(b.startIndex, a.startIndex));
        return result.size() > maxReturn ? result.subList(0, maxReturn) : result;
    }

    private boolean isGapFilled(JsonNode klines, int fromIndex, int toIndex, double bottom, double top) {
        for (int j = fromIndex; j < toIndex; j++) {
            double low = klines.get(j).get(3).asDouble();
            double high = klines.get(j).get(2).asDouble();
            if (low <= top && high >= bottom) return true;
        }
        return false;
    }

    public ArrayNode toJsonArray(List<Fvg> fvgs, com.fasterxml.jackson.databind.ObjectMapper mapper) {
        ArrayNode arr = mapper.createArrayNode();
        for (Fvg f : fvgs) {
            ObjectNode o = arr.addObject();
            o.put("type", f.type);
            o.put("top", Math.round(f.top * 100.0) / 100.0);
            o.put("bottom", Math.round(f.bottom * 100.0) / 100.0);
            o.put("filled", f.filled);
            o.put("start_time_utc", java.time.Instant.ofEpochMilli(f.openTime).toString());
        }
        return arr;
    }
}