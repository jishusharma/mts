package datafeed;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import okhttp3.Dns;
import org.java_websocket.client.DnsResolver;

import java.net.InetAddress;
import java.net.URI;
import java.net.UnknownHostException;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.LongSupplier;

/**
 * Resolves *.binance.com / *.binance.vision through DNS-over-HTTPS (Cloudflare, then Google) because some ISPs (Jio) answer
 * those names with a block-page IP. Plugs into OkHttp ({@link Dns}) and Java-WebSocket ({@link DnsResolver}) as their DNS hook;
 * the returned InetAddress keeps the real host name, so SNI and the certificate hostname check stay on the real name.
 * Rejects the block IP and private/loopback answers; TTL cache; fails closed with a clear log line. No machine DNS/hosts change.
 */
public final class BinanceDoh implements Dns, DnsResolver {
    public record Rec(String ip, int ttl) {}

    /** Test seam: one DoH provider lookup. */
    public interface Fetcher { List<Rec> fetch(String provider, String host) throws Exception; }

    /** Test seam: system DNS. */
    public interface SystemDns { String[] lookup(String host); }

    static final Set<String> BLOCK_IPS = Set.of("49.44.79.236");
    static final int MIN_TTL = 30, MAX_TTL = 300;
    private static final String[] PROVIDERS = {"cloudflare", "google"};
    private static final ObjectMapper MAPPER = new ObjectMapper();
    private static final HttpClient HTTP = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(5)).build();
    private static final BinanceDoh DEFAULT = new BinanceDoh(BinanceDoh::httpFetch, BinanceDoh::systemLookup, System::currentTimeMillis);

    private record Entry(long expiresMs, List<String> ips) {}

    private final Fetcher fetcher;
    private final SystemDns system;
    private final LongSupplier nowMs;
    private final ConcurrentHashMap<String, Entry> cache = new ConcurrentHashMap<>();

    public BinanceDoh(Fetcher fetcher, SystemDns system, LongSupplier nowMs) {
        this.fetcher = fetcher;
        this.system = system;
        this.nowMs = nowMs;
    }

    /** Process-wide instance used by the feed classes. */
    public static BinanceDoh instance() { return DEFAULT; }

    public static boolean isBinanceHost(String host) {
        if (host == null) return false;
        String h = host.toLowerCase();
        if (h.endsWith(".")) h = h.substring(0, h.length() - 1);
        return h.equals("binance.com") || h.equals("binance.vision") || h.endsWith(".binance.com") || h.endsWith(".binance.vision");
    }

    public void clearCache() { cache.clear(); }

    static boolean safeIp(String ip) {
        if (BLOCK_IPS.contains(ip)) return false;
        if (ip == null || !ip.matches("\\d{1,3}(\\.\\d{1,3}){3}")) return false; // IPv4 literal only: no DNS lookup can happen here
        try {
            InetAddress a = InetAddress.getByName(ip);
            return !(a.isAnyLocalAddress() || a.isLoopbackAddress() || a.isLinkLocalAddress() || a.isSiteLocalAddress() || a.isMulticastAddress());
        } catch (UnknownHostException e) {
            return false;
        }
    }

    static List<Rec> parseDnsJson(String body) {
        List<Rec> out = new ArrayList<>();
        try {
            JsonNode root = MAPPER.readTree(body);
            if (root == null || root.path("Status").asInt(0) != 0 || !root.path("Answer").isArray()) return out;
            for (JsonNode r : root.get("Answer")) {
                if (r.path("type").asInt() == 1 && r.path("data").isTextual()) {
                    int ttl = Math.max(MIN_TTL, Math.min(MAX_TTL, r.path("TTL").asInt(MIN_TTL)));
                    out.add(new Rec(r.get("data").asText(), ttl));
                }
            }
        } catch (Exception e) {
            return new ArrayList<>();
        }
        return out;
    }

    private static List<Rec> httpFetch(String provider, String host) throws Exception {
        String url = provider.equals("cloudflare")
                ? "https://1.1.1.1/dns-query?name=" + host + "&type=A"
                : "https://8.8.8.8/resolve?name=" + host + "&type=A";
        HttpRequest req = HttpRequest.newBuilder(URI.create(url)).timeout(Duration.ofSeconds(5))
                .header("accept", "application/dns-json").GET().build();
        HttpResponse<String> res = HTTP.send(req, HttpResponse.BodyHandlers.ofString());
        if (res.statusCode() != 200) throw new java.io.IOException("DoH HTTP " + res.statusCode());
        return parseDnsJson(res.body());
    }

    private static String[] systemLookup(String host) {
        try {
            InetAddress[] all = InetAddress.getAllByName(host);
            String[] out = new String[all.length];
            for (int i = 0; i < all.length; i++) out[i] = all[i].getHostAddress();
            return out;
        } catch (UnknownHostException e) {
            return new String[0];
        }
    }

    @Override
    public List<InetAddress> lookup(String host) throws UnknownHostException {
        if (!isBinanceHost(host)) {
            List<InetAddress> out = toAddrs(host, List.of(system.lookup(host)));
            if (out.isEmpty()) throw new UnknownHostException(host);
            return out;
        }
        long now = nowMs.getAsLong();
        Entry hit = cache.get(host);
        if (hit != null && hit.expiresMs > now) return toAddrs(host, hit.ips);
        List<String> why = new ArrayList<>();
        for (String p : PROVIDERS) {
            List<Rec> recs;
            try {
                recs = fetcher.fetch(p, host);
            } catch (Exception e) {
                why.add(p + ": " + e.getClass().getSimpleName());
                continue;
            }
            List<String> ips = new ArrayList<>();
            int ttl = MAX_TTL;
            for (Rec r : recs) {
                if (safeIp(r.ip())) { ips.add(r.ip()); ttl = Math.min(ttl, r.ttl()); }
            }
            if (ips.isEmpty()) { why.add(p + ": no safe answer"); continue; }
            cache.put(host, new Entry(now + ttl * 1000L, ips));
            return toAddrs(host, ips);
        }
        List<String> sys = new ArrayList<>();
        for (String ip : system.lookup(host)) if (safeIp(ip)) sys.add(ip);
        if (!sys.isEmpty()) {
            System.err.println("[BinanceDoh] DoH failed for " + host + " (" + String.join("; ", why) + "); using validated system DNS " + sys);
            return toAddrs(host, sys);
        }
        String msg = "[BinanceDoh] FAIL CLOSED: no safe address for " + host + " (" + String.join("; ", why) + ")";
        System.err.println(msg);
        throw new UnknownHostException(msg);
    }

    @Override
    public InetAddress resolve(URI uri) throws UnknownHostException {
        return lookup(uri.getHost()).get(0);
    }

    private static List<InetAddress> toAddrs(String host, List<String> ips) throws UnknownHostException {
        List<InetAddress> out = new ArrayList<>();
        for (String ip : ips) out.add(InetAddress.getByAddress(host, InetAddress.getByName(ip).getAddress()));
        return out;
    }
}
