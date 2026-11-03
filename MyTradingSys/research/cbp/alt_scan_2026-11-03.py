import json, time, urllib.request, statistics as st, datetime as dt
IDS = {'BTC':'bitcoin','ETH':'ethereum','SOL':'solana','NEAR':'near','ZEC':'zcash','UNI':'uniswap','RAY':'raydium','QNT':'quant-network',
       'TAO':'bittensor','SUI':'sui','AAVE':'aave','AERO':'aerodrome-finance','GMX':'gmx','EIGEN':'eigenlayer','ONDO':'ondo-finance',
       'OP':'optimism','TIA':'celestia','HBAR':'hedera-hashgraph','RENDER':'render-token','FET':'fetch-ai','LINK':'chainlink','ENA':'ethena',
       'HYPE':'hyperliquid','AVAX':'avalanche-2','PLUME':'plume'}
def get(cid):
    u = 'https://api.coingecko.com/api/v3/coins/%s/market_chart?vs_currency=usd&days=365&interval=daily' % cid
    for k in range(4):
        try:
            r = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
            return json.load(urllib.request.urlopen(r, timeout=30))
        except Exception as e:
            time.sleep(15 * (k + 1))
    return None
data = {}
for s, cid in IDS.items():
    d = get(cid)
    if not d: print('FAIL', s); continue
    px = [(int(t // 1000), p) for t, p in d['prices']]; vol = [v for _, v in d['total_volumes']]; mc = [m for _, m in d['market_caps']]
    data[s] = (px, vol, mc); time.sleep(2.5)
json.dump({s: {'px': v[0], 'vol': v[1], 'mc': v[2]} for s, v in data.items()}, open('alt_scan.json', 'w'))
btc = dict(data['BTC'][0]); bd = sorted(btc)
def day(ts): return dt.datetime.fromtimestamp(ts, dt.timezone.utc).date()
jul1 = [t for t in bd if day(t) >= dt.date(2026, 7, 1)][0]
oct10 = [t for t in bd if day(t) >= dt.date(2026, 10, 10)][0]
rows = []
for s, (px, vol, mc) in data.items():
    p = dict(px); ts = sorted(p); c = [p[t] for t in ts]
    r1y = c[-1] / c[0] - 1
    peak = c[0]; mdd = 0
    for x in c: peak = max(peak, x); mdd = min(mdd, x / peak - 1)
    low = min(c[-130:]); r_low = c[-1] / low - 1
    hi = max(c); off_hi = c[-1] / hi - 1
    pj = p.get(jul1) or c[-125]; rj = c[-1] / pj - 1
    po = p.get(oct10); r30 = c[-1] / c[-31] - 1
    # downside beta vs BTC on BTC's down days
    rets = {t: p[t] / p[tp] - 1 for tp, t in zip(ts, ts[1:])}
    brets = {t: btc[t] / btc[tp] - 1 for tp, t in zip(bd, bd[1:])}
    com = [t for t in rets if t in brets]
    dn = [t for t in com if brets[t] < -0.02]
    dbeta = (sum(rets[t] for t in dn) / sum(brets[t] for t in dn)) if dn else 0
    up = [t for t in com if brets[t] > 0.02]
    ubeta = (sum(rets[t] for t in up) / sum(brets[t] for t in up)) if up else 0
    # Oct 10 crash day
    i = ts.index(oct10) if oct10 in ts else None
    crash = (c[i + 1] / c[i - 1] - 1) if i else 0
    vm = st.median(v / m for v, m in zip(vol[-30:], mc[-30:]) if m)
    rows.append((s, r1y, mdd, off_hi, rj, r30, dbeta, ubeta, crash, vm, mc[-1] / 1e9))
print('%-7s %7s %7s %7s %7s %7s %6s %6s %7s %6s %7s' % ('sym', '1y', 'maxDD', 'offHi', 'sinceJul', '30d', 'dBeta', 'uBeta', 'oct10', 'vol/mc', 'mcap$B'))
for r in sorted(rows, key=lambda r: -r[4]):
    print('%-7s %+6.0f%% %6.0f%% %6.0f%% %+7.0f%% %+6.0f%% %6.2f %6.2f %+6.0f%% %5.1f%% %7.1f' % (r[0], r[1]*100, r[2]*100, r[3]*100, r[4]*100, r[5]*100, r[6], r[7], r[8]*100, r[9]*100, r[10]))
