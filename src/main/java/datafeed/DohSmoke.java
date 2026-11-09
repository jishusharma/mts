package datafeed;

import org.java_websocket.client.WebSocketClient;
import org.java_websocket.handshake.ServerHandshake;

import java.net.URI;
import java.util.concurrent.atomic.AtomicInteger;

/** Smoke for the DoH path: one live fapi 4h kline + N seconds of fstream aggTrade messages. Public data only. */
public final class DohSmoke {
    public static void main(String[] args) throws Exception {
        int secs = args.length > 0 ? Integer.parseInt(args[0]) : 30;
        BinanceClient c = new BinanceClient();
        System.out.println("SMOKE fapi 4h kline: " + c.klines("BTCUSDT", "4h", 1).toString().substring(0, 90));
        c.shutdown();
        AtomicInteger n = new AtomicInteger();
        WebSocketClient ws = new WebSocketClient(new URI("wss://fstream.binance.com/market/ws/btcusdt@aggTrade")) {
            public void onOpen(ServerHandshake h) { System.out.println("SMOKE fstream open"); }
            public void onMessage(String m) { n.incrementAndGet(); }
            public void onClose(int code, String r, boolean remote) { System.out.println("SMOKE fstream closed " + code + " " + r); }
            public void onError(Exception e) { System.out.println("SMOKE fstream error " + e); }
        };
        ws.setDnsResolver(BinanceDoh.instance());
        if (!ws.connectBlocking(15, java.util.concurrent.TimeUnit.SECONDS)) { System.out.println("SMOKE FAIL fstream connect"); System.exit(2); }
        Thread.sleep(secs * 1000L);
        ws.closeBlocking();
        System.out.println("SMOKE fstream messages in " + secs + "s: " + n.get());
        System.exit(n.get() > 0 ? 0 : 3);
    }
}
