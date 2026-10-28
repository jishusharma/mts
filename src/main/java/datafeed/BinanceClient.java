package datafeed;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;

import java.io.IOException;
import java.util.concurrent.TimeUnit;

public class BinanceClient implements HistoricalSource {
    private static final String BASE = "https://fapi.binance.com";
    private final OkHttpClient client;
    private final ObjectMapper mapper;

    public BinanceClient() {
        this.client = new OkHttpClient.Builder()
                .connectTimeout(30, TimeUnit.SECONDS)
                .readTimeout(30, TimeUnit.SECONDS)
                .build();
        this.mapper = new ObjectMapper();
    }

    /** Test seam: inject an HTTP client (e.g. one with a stubbing interceptor). */
    BinanceClient(OkHttpClient client) {
        this.client = client;
        this.mapper = new ObjectMapper();
    }

    public JsonNode klines(String symbol, String interval, int limit) throws IOException {
        String url = BASE + "/fapi/v1/klines?symbol=" + symbol + "&interval=" + interval + "&limit=" + limit;
        return get(url);
    }

    public JsonNode currentFundingRate(String symbol) throws IOException {
        return get(BASE + "/fapi/v1/premiumIndex?symbol=" + symbol);
    }

    public JsonNode fundingRateHistory(String symbol, int limit) throws IOException {
        return get(BASE + "/fapi/v1/fundingRate?symbol=" + symbol + "&limit=" + limit);
    }

    public JsonNode openInterest(String symbol) throws IOException {
        return get(BASE + "/fapi/v1/openInterest?symbol=" + symbol);
    }

    public JsonNode openInterestHist(String symbol, String period, int limit) throws IOException {
        return get(BASE + "/futures/data/openInterestHist?symbol=" + symbol + "&period=" + period + "&limit=" + limit);
    }

    public JsonNode longShortRatio(String symbol, String period, int limit) throws IOException {
        return get(BASE + "/futures/data/globalLongShortAccountRatio?symbol=" + symbol + "&period=" + period + "&limit=" + limit);
    }

    public JsonNode takerBuySellVol(String symbol, String period, int limit) throws IOException {
        return get(BASE + "/futures/data/takerBuySellVol?symbol=" + symbol + "&period=" + period + "&limit=" + limit);
    }
    /** Recent aggregate trades (limit max 1000). */
    public JsonNode aggTrades(String symbol, int limit) throws IOException {
        return get(BASE + "/fapi/v1/aggTrades?symbol=" + symbol + "&limit=" + limit);
    }

    /** Aggregate trades within an explicit time window (limit max 1000). */
    public JsonNode aggTradesRange(String symbol, long startTime, long endTime, int limit) throws IOException {
        String url = BASE + "/fapi/v1/aggTrades?symbol=" + symbol + "&startTime=" + startTime + "&endTime=" + endTime + "&limit=" + limit;
        return get(url);
    }

    /** Top trader long/short position ratio (whale positions). */
    public JsonNode topLongShortPositionRatio(String symbol, String period, int limit) throws IOException {
        return get(BASE + "/futures/data/topLongShortPositionRatio?symbol=" + symbol + "&period=" + period + "&limit=" + limit);
    }

    /** Top trader long/short account ratio (retail accounts). */
    public JsonNode topLongShortAccountRatio(String symbol, String period, int limit) throws IOException {
        return get(BASE + "/futures/data/topLongShortAccountRatio?symbol=" + symbol + "&period=" + period + "&limit=" + limit);
    }
    /** Order book depth for S05 thick/thin analysis. limit can be 5, 10, 20, 50, 100, 500, 1000 */
    public JsonNode orderBookDepth(String symbol, int limit) throws IOException {
        return get(BASE + "/fapi/v1/depth?symbol=" + symbol + "&limit=" + limit);
    }

    /** Klines with explicit startTime and endTime (ms). */
    public JsonNode klinesRange(String symbol, String interval, long startTime, long endTime, int limit) throws IOException {
        String url = BASE + "/fapi/v1/klines?symbol=" + symbol + "&interval=" + interval + "&startTime=" + startTime + "&endTime=" + endTime + "&limit=" + limit;
        return get(url);
    }
    /** Spot price for symbol. */
    public JsonNode spotPrice(String symbol) throws IOException {
        return get("https://api.binance.com/api/v3/ticker/price?symbol=" + symbol);
    }

    /** Mark price / premium index for futures symbol. */
    public JsonNode premiumIndex(String symbol) throws IOException {
        return get(BASE + "/fapi/v1/premiumIndex?symbol=" + symbol);
    }
    private JsonNode get(String url) throws IOException {
        Request req = new Request.Builder().url(url).get().build();
        try (Response res = client.newCall(req).execute()) {
            if (!res.isSuccessful()) throw new IOException("HTTP " + res.code() + " for " + url);
            String body = res.body().string();
            return mapper.readTree(body);
        }
    }

    public void shutdown() {
        client.dispatcher().executorService().shutdown();
        client.connectionPool().evictAll();
    }
}
