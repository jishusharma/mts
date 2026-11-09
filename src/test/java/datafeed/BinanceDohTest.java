package datafeed;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.net.InetAddress;
import java.net.URI;
import java.net.UnknownHostException;
import java.util.ArrayList;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

/** ISP DNS block fix: Binance hosts resolve via DoH; block/private answers rejected; fail closed; SNI keeps the real name. */
public class BinanceDohTest {
    static final String GOOD = "54.192.142.53";
    static final String BLOCK = "49.44.79.236";

    private final List<String> calls = new ArrayList<>();

    @BeforeEach
    void reset() { calls.clear(); }

    private BinanceDoh.Fetcher fetcher(java.util.Map<String, Object> answers) {
        return (provider, host) -> {
            calls.add(provider);
            Object r = answers.get(provider);
            if (r instanceof RuntimeException e) throw e;
            @SuppressWarnings("unchecked") List<BinanceDoh.Rec> l = (List<BinanceDoh.Rec>) r;
            return l;
        };
    }

    private static List<BinanceDoh.Rec> recs(String ip, int ttl) { return List.of(new BinanceDoh.Rec(ip, ttl)); }

    @Test
    void binanceHostMatching() {
        assertTrue(BinanceDoh.isBinanceHost("fstream.binance.com"));
        assertTrue(BinanceDoh.isBinanceHost("data.binance.vision"));
        assertFalse(BinanceDoh.isBinanceHost("evilbinance.com"));
        assertFalse(BinanceDoh.isBinanceHost("test.deribit.com"));
    }

    @Test
    void blockIpRejectedThenGoogleFallback() throws Exception {
        var d = new BinanceDoh(fetcher(java.util.Map.of("cloudflare", recs(BLOCK, 60), "google", recs(GOOD, 60))),
                h -> new String[0], System::currentTimeMillis);
        List<InetAddress> out = d.lookup("fapi.binance.com");
        assertEquals(GOOD, out.get(0).getHostAddress());
        assertEquals(List.of("cloudflare", "google"), calls);
    }

    @Test
    void addressKeepsRealHostNameForSniAndCertCheck() throws Exception {
        var d = new BinanceDoh(fetcher(java.util.Map.of("cloudflare", recs(GOOD, 60), "google", recs(GOOD, 60))),
                h -> new String[0], System::currentTimeMillis);
        assertEquals("fapi.binance.com", d.lookup("fapi.binance.com").get(0).getHostName());
    }

    @Test
    void privateAnswersRejectedAndFailClosed() {
        for (String bad : new String[]{"10.1.1.1", "192.168.0.4", "127.0.0.1", "169.254.2.2", "0.0.0.0", "172.16.5.5"}) {
            var d = new BinanceDoh(fetcher(java.util.Map.of("cloudflare", recs(bad, 60), "google", recs(bad, 60))),
                    h -> new String[0], System::currentTimeMillis);
            assertThrows(UnknownHostException.class, () -> d.lookup("fapi.binance.com"), bad);
        }
    }

    @Test
    void dohDownFailsClosedEvenWhenSystemDnsReturnsBlockIp() {
        var d = new BinanceDoh(fetcher(java.util.Map.of("cloudflare", new RuntimeException("down"), "google", new RuntimeException("down"))),
                h -> new String[]{BLOCK}, System::currentTimeMillis);
        UnknownHostException e = assertThrows(UnknownHostException.class, () -> d.lookup("fstream.binance.com"));
        assertTrue(e.getMessage().contains("FAIL CLOSED"));
    }

    @Test
    void dohDownCleanSystemAnswerAccepted() throws Exception {
        var d = new BinanceDoh(fetcher(java.util.Map.of("cloudflare", new RuntimeException("down"), "google", new RuntimeException("down"))),
                h -> new String[]{GOOD}, System::currentTimeMillis);
        assertEquals(GOOD, d.lookup("fapi.binance.com").get(0).getHostAddress());
    }

    @Test
    void ttlCacheHitExpiryAndResetAndFailureNotCached() throws Exception {
        long[] t = {1_000_000L};
        var d = new BinanceDoh(fetcher(java.util.Map.of("cloudflare", recs(GOOD, 30), "google", recs(GOOD, 30))),
                h -> new String[0], () -> t[0]);
        d.lookup("fapi.binance.com");
        t[0] += 29_000;
        d.lookup("fapi.binance.com");
        assertEquals(1, calls.size());
        t[0] += 2_000;
        d.lookup("fapi.binance.com");
        assertEquals(2, calls.size());
        d.clearCache(); // restart/reset state
        d.lookup("fapi.binance.com");
        assertEquals(3, calls.size());

        calls.clear();
        var bad = new BinanceDoh(fetcher(java.util.Map.of("cloudflare", new RuntimeException("x"), "google", new RuntimeException("x"))),
                h -> new String[0], () -> t[0]);
        for (int i = 0; i < 2; i++) assertThrows(UnknownHostException.class, () -> bad.lookup("fapi.binance.com"));
        assertEquals(4, calls.size());
    }

    @Test
    void nonBinanceHostUsesSystemResolverUntouched() throws Exception {
        var d = new BinanceDoh(fetcher(java.util.Map.of()), h -> new String[]{"1.2.3.4"}, System::currentTimeMillis);
        assertEquals("1.2.3.4", d.lookup("test.deribit.com").get(0).getHostAddress());
        assertTrue(calls.isEmpty());
    }

    @Test
    void parseDnsJsonIgnoresCnameClampsTtlAndGarbage() {
        String ok = "{\"Status\":0,\"Answer\":[{\"type\":5,\"data\":\"x.cloudfront.net.\",\"TTL\":5},{\"type\":1,\"data\":\"" + GOOD + "\",\"TTL\":1}]}";
        List<BinanceDoh.Rec> r = BinanceDoh.parseDnsJson(ok);
        assertEquals(1, r.size());
        assertEquals(GOOD, r.get(0).ip());
        assertEquals(BinanceDoh.MIN_TTL, r.get(0).ttl());
        assertTrue(BinanceDoh.parseDnsJson("{\"Status\":3}").isEmpty());
        assertTrue(BinanceDoh.parseDnsJson("not json").isEmpty());
    }

    @Test
    void webSocketDnsResolverHookReturnsDohAddress() throws Exception {
        var d = new BinanceDoh(fetcher(java.util.Map.of("cloudflare", recs(GOOD, 60), "google", recs(GOOD, 60))),
                h -> new String[0], System::currentTimeMillis);
        InetAddress a = d.resolve(new URI("wss://fstream.binance.com/market/ws/btcusdt@aggTrade"));
        assertEquals(GOOD, a.getHostAddress());
        assertEquals("fstream.binance.com", a.getHostName());
    }

    @Test
    void feedClassesAreWired() throws Exception {
        for (String f : new String[]{"BinanceLiquidationAccumulator", "StateCodeEmitter", "BinanceClient"}) {
            String src = java.nio.file.Files.readString(java.nio.file.Path.of("src/main/java/datafeed/" + f + ".java"));
            assertTrue(src.contains("BinanceDoh"), f + " must use BinanceDoh");
        }
    }
}
