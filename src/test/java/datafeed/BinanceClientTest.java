package datafeed;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Protocol;
import okhttp3.Response;
import okhttp3.ResponseBody;
import org.junit.jupiter.api.Test;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

/** B136: futures-data endpoints must use /futures/data/, and OI fetch failure must not look like a healthy flat reading. */
public class BinanceClientTest {

    private static BinanceClient capturing(List<String> urls) {
        OkHttpClient http = new OkHttpClient.Builder().addInterceptor(chain -> {
            urls.add(chain.request().url().toString());
            return new Response.Builder().request(chain.request()).protocol(Protocol.HTTP_1_1)
                    .code(200).message("OK")
                    .body(ResponseBody.create("[]", MediaType.get("application/json"))).build();
        }).build();
        return new BinanceClient(http);
    }

    @Test
    void futuresDataEndpointsUseFuturesDataPath() throws IOException {
        List<String> urls = new ArrayList<>();
        BinanceClient c = capturing(urls);
        c.openInterestHist("BTCUSDT", "1h", 2);
        c.longShortRatio("BTCUSDT", "1h", 2);
        c.takerBuySellVol("BTCUSDT", "1h", 2);
        c.topLongShortPositionRatio("BTCUSDT", "1h", 2);
        c.topLongShortAccountRatio("BTCUSDT", "1h", 2);
        assertEquals(5, urls.size());
        for (String u : urls) {
            assertTrue(u.contains("/futures/data/"), u);
            assertFalse(u.contains("runtime_data"), u);
        }
    }

    @Test
    void oiFetchFailureYieldsUnavailableAndLowConfidence() {
        BinanceClient failing = new BinanceClient() {
            @Override
            public JsonNode openInterestHist(String s, String p, int l) throws IOException {
                throw new IOException("HTTP 404");
            }
        };
        ObjectNode oi = MarketDataSnapshot.oiFromHistory(failing, "BTCUSDT", new ObjectMapper());
        assertEquals("UNAVAILABLE", oi.get("direction").asText());
        assertEquals("LOW", oi.get("confidence").asText());
        assertTrue(oi.get("change_1h_pct").isNull());
    }

    @Test
    void oiFetchSuccessKeepsHighConfidence() throws Exception {
        ObjectMapper m = new ObjectMapper();
        BinanceClient ok = new BinanceClient() {
            @Override
            public JsonNode openInterestHist(String s, String p, int l) throws IOException {
                return m.readTree("[{\"sumOpenInterest\":\"100\"},{\"sumOpenInterest\":\"110\"}]");
            }
        };
        ObjectNode oi = MarketDataSnapshot.oiFromHistory(ok, "BTCUSDT", m);
        assertEquals("rising", oi.get("direction").asText());
        assertEquals("HIGH", oi.get("confidence").asText());
        assertEquals(10.0, oi.get("change_1h_pct").asDouble(), 1e-9);
    }
}
