import json, urllib.request, datetime as dt, statistics as st

k = json.load(urllib.request.urlopen("https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=240", timeout=20))
T = lambda x: dt.datetime.fromtimestamp(x[0] / 1000, dt.UTC)
print("last bar", T(k[-1]).strftime("%H:%M"), "O", k[-1][1], "H", k[-1][2], "L", k[-1][3], "C", k[-1][4])
cl = [float(x[4]) for x in k]
w = cl[-20:]
m = sum(w) / 20
sd = st.pstdev(w)
print(f"BB20,2 incl forming: mid {m:.1f} up {m+2*sd:.1f} lo {m-2*sd:.1f}")
# hlc3 VWAP anchored 00:00Z
day = [x for x in k if T(x).date() == dt.datetime.now(dt.UTC).date()]
print("note: only last 240m fetched; day VWAP skipped")
for hh, mm in [(12, 30), (13, 0), (13, 30), (13, 36), (13, 38), (13, 40), (13, 45), (14, 0)]:
    for x in k:
        if T(x).hour == hh and T(x).minute == mm:
            print(f"{hh}:{mm:02d} O{float(x[1]):.1f} H{float(x[2]):.1f} L{float(x[3]):.1f} C{float(x[4]):.1f} vol{float(x[5]):.0f} tbv{float(x[9])/float(x[5]):.2f}")
lo = min(k[-60:], key=lambda x: float(x[3]))
print("60m low", lo[3], T(lo).strftime("%H:%M"))
hi = max(k[-60:], key=lambda x: float(x[2]))
print("60m high", hi[2], T(hi).strftime("%H:%M"))
# since 13:30
s = [x for x in k if T(x).hour == 13 and T(x).minute == 30][0]
print(f"since 13:30 open {float(s[1]):.1f} -> {float(k[-1][4]):.1f} = {(float(k[-1][4])/float(s[1])-1)*100:+.2f}%")
tb = sum(float(x[9]) for x in k if T(x) >= T(s)); tv = sum(float(x[5]) for x in k if T(x) >= T(s))
print(f"taker buy share since 13:30 {tb/tv:.2f}")
