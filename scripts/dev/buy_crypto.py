"""Buy Crypto page feed: CoinGecko public API -> one JSON file OUTSIDE the repo (default ~/.mts_private/buy_crypto.json).
Then push it into the page db:  ArtifactData set  collection=market doc_id=latest file_path=<that file>.
Plan numbers (buckets, betas, triggers) are from MyTradingSys/research/cbp/ALT_PICKS_2026-11-03.md (OURS, not advice).
Usage: python scripts/dev/buy_crypto.py [--out PATH]"""
import argparse, json, pathlib, sys, time, urllib.request, urllib.error, datetime

BASE = "https://api.coingecko.com/api/v3"
SINCE_TS = int(datetime.datetime(2026, 11, 3, tzinfo=datetime.timezone.utc).timestamp())
# (symbol, coingecko id, bucket)
COINS = [
    ("ETH", "ethereum", "anchor"), ("SOL", "solana", "anchor"), ("LINK", "chainlink", "anchor"), ("HBAR", "hedera-hashgraph", "anchor"),
    ("HYPE", "hyperliquid", "leader"), ("UNI", "uniswap", "leader"), ("ZEC", "zcash", "leader"), ("NEAR", "near", "leader"), ("QNT", "quant-network", "leader"),
    ("GMX", "gmx", "darkhorse"), ("TAO", "bittensor", "darkhorse"), ("RENDER", "render-token", "darkhorse"),
    ("INJ", "injective-protocol", "watch"), ("JST", "just", "watch"), ("SKY", "sky", "watch"), ("GEOD", "geodnet", "watch"),
    ("VVV", "venice-token", "watch"), ("MORPHO", "morpho", "watch"), ("ETHFI", "ether-fi", "watch"), ("AKT", "akash-network", "watch"),
    ("OP", "optimism", "avoid"), ("TIA", "celestia", "avoid"), ("FET", "fetch-ai", "avoid"), ("ENA", "ethena", "avoid"), ("PLUME", "plume", "avoid"),
]
# measured 2026-11-03 (ALT_PICKS section 1): (down-beta, up-beta); None = not measured
BETAS = {"ZEC": (1.44, 1.84), "QNT": (0.78, 0.56), "UNI": (1.27, 1.20), "ENA": (1.50, 1.41), "NEAR": (1.02, 1.27), "GMX": (0.77, 0.93),
         "LINK": (1.28, 1.21), "PLUME": (None, 1.30), "ETH": (1.28, 1.31), "HYPE": (0.87, 1.16), "SOL": (1.33, 1.17), "TIA": (1.58, 1.22),
         "OP": (1.39, 1.08), "TAO": (1.53, 1.14), "HBAR": (1.18, 1.00), "RENDER": (1.25, 1.00), "FET": (1.08, 0.98)}
STABLES = {"usdt", "usdc", "usds", "dai", "usde", "fdusd", "pyusd", "usd1", "tusd", "usdd", "susds", "susde", "usdtb", "buidl", "usdf", "usdg", "rlusd", "bsc-usd"}
WRAPPED = {"wrapped-bitcoin", "staked-ether", "wrapped-steth", "weth", "wrapped-eeth"}


def pct(new, old):
    """Percent change, None when either side is missing or old is zero."""
    if new is None or old in (None, 0):
        return None
    return (new / old - 1.0) * 100.0


def rel_vs_btc(coin_pct, btc_pct):
    """Gap in percentage points (coin minus BTC)."""
    if coin_pct is None or btc_pct is None:
        return None
    return coin_pct - btc_pct


def price_at(prices, ts):
    """prices = [[ms, price], ...]; the point closest to ts (seconds); None if empty."""
    if not prices:
        return None
    return min(prices, key=lambda p: abs(p[0] / 1000.0 - ts))[1]


def scenario(sym, btc_now, level):
    """Coin move if BTC goes btc_now -> level, using the measured beta (down-beta below, up-beta above). Scenario, not a forecast."""
    b = BETAS.get(sym)
    if not b:
        return None
    move = (level / btc_now - 1.0) * 100.0
    beta = b[0] if move < 0 else b[1]
    return None if beta is None else move * beta


def build_coin(sym, bucket, usd_row, inr_price, hist_prices, btc_usd_now, btc_chg7, btc_since):
    price = usd_row.get("current_price")
    since = pct(price, price_at(hist_prices, SINCE_TS))
    chg7 = usd_row.get("price_change_percentage_7d_in_currency")
    return {
        "sym": sym, "bucket": bucket, "id": usd_row.get("id"), "usd": price, "inr": inr_price,
        "since_1103": since, "chg7": chg7, "chg30": usd_row.get("price_change_percentage_30d_in_currency"),
        "off_ath": usd_row.get("ath_change_percentage"), "mcap": usd_row.get("market_cap"),
        "vs_btc_7d": rel_vs_btc(chg7, btc_chg7), "vs_btc_since": rel_vs_btc(since, btc_since),
        "betas": list(BETAS.get(sym) or []),
        "scen": {str(lv): scenario(sym, btc_usd_now, lv) for lv in (77000, 72000, 60000)},
    }


def alt_proxy(top_rows, btc_chg30):
    """Share (0-100) of top alts (BTC, stablecoins, wrapped excluded) that beat BTC over 30 d. A proxy, NOT the CMC or Blockchaincenter index."""
    k = "price_change_percentage_30d_in_currency"
    alts = [r for r in top_rows if r.get("symbol", "").lower() != "btc" and r.get("id") not in WRAPPED
            and r.get("symbol", "").lower() not in STABLES and r.get(k) is not None]
    if not alts or btc_chg30 is None:
        return None
    return 100.0 * sum(1 for r in alts if r[k] > btc_chg30) / len(alts)


def get(url, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "mts-buy-crypto/1"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429 and i < tries - 1:
                try:
                    wait = int(e.headers.get("Retry-After", "0"))
                except ValueError:
                    wait = 0
                time.sleep(max(wait + 2, 20 * (i + 1)))  # keyless CoinGecko throttles hard; honour Retry-After
                continue
            raise
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(pathlib.Path.home() / ".mts_private" / "buy_crypto.json"))
    out = pathlib.Path(ap.parse_args().out)
    ids = ",".join(["bitcoin"] + [c[1] for c in COINS])
    usd = {r["id"]: r for r in get(f"{BASE}/coins/markets?vs_currency=usd&price_change_percentage=7d,30d&per_page=250&ids={ids}")}
    time.sleep(2)
    inr = {r["id"]: r["current_price"] for r in get(f"{BASE}/coins/markets?vs_currency=inr&per_page=250&ids={ids}")}
    time.sleep(2)
    glob = get(f"{BASE}/global")["data"]
    time.sleep(2)
    top = get(f"{BASE}/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=60&page=1&price_change_percentage=30d")
    btc = usd["bitcoin"]
    hist = {}
    for cid in ["bitcoin"] + [c[1] for c in COINS]:
        time.sleep(2.5)
        try:
            hist[cid] = get(f"{BASE}/coins/{cid}/market_chart?vs_currency=usd&days=9&interval=daily")["prices"]
        except Exception as e:  # one missing history must not sink the pull
            hist[cid] = []
            print("history missing", cid, e, file=sys.stderr)
    btc_now = btc["current_price"]
    btc_chg7 = btc.get("price_change_percentage_7d_in_currency")
    btc_since = pct(btc_now, price_at(hist["bitcoin"], SINCE_TS))
    coins, missing = [], []
    for sym, cid, bucket in COINS:
        if cid not in usd:
            missing.append(sym)
            continue
        coins.append(build_coin(sym, bucket, usd[cid], inr.get(cid), hist.get(cid), btc_now, btc_chg7, btc_since))
    mc = glob.get("market_cap_percentage", {})
    doc = {
        "generated_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
        "source": "CoinGecko public API", "since": "2026-11-03",
        "btc": {"usd": btc_now, "inr": inr.get("bitcoin"), "chg7": btc_chg7, "chg30": btc.get("price_change_percentage_30d_in_currency"),
                "since_1103": btc_since, "off_ath": btc.get("ath_change_percentage")},
        "usd_inr": (inr.get("bitcoin") / btc_now) if inr.get("bitcoin") and btc_now else None,
        "dominance": {"btc": mc.get("btc"), "eth": mc.get("eth"), "stable": (mc.get("usdt") or 0) + (mc.get("usdc") or 0)},
        "alt_proxy_30d_beating_btc": alt_proxy(top, btc.get("price_change_percentage_30d_in_currency")),
        "coinglass": "not pulled: no keyless CoinGlass endpoint tried",
        "coins": coins, "missing": missing,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=1)
    print(f"wrote {out} ({len(coins)} coins, missing {missing})")


if __name__ == "__main__":
    main()
