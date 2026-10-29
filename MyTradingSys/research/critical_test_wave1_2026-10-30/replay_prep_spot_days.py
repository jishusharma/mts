"""Item 4 prep: convert data-api.binance.vision SPOT 1m JSON (list of rows) into Binance-archive CSV day files.
Usage: python -I replay_prep_spot_days.py outKlinesDir json1 [json2 ...]   (rows merged, split by UTC day, deduped)
Writes BTCUSDT-1m-YYYY-MM-DD.csv with the futures-archive header/columns. Spot data: label it as such."""
import json, sys, datetime, os
out = sys.argv[1]
rows = {}
for p in sys.argv[2:]:
    for r in json.load(open(p, encoding='utf-8')):
        rows[int(r[0])] = r
days = {}
for t in sorted(rows):
    d = datetime.datetime.fromtimestamp(t / 1000, datetime.timezone.utc).strftime('%Y-%m-%d')
    days.setdefault(d, []).append(rows[t])
hdr = 'open_time,open,high,low,close,volume,close_time,quote_volume,count,taker_buy_volume,taker_buy_quote_volume,ignore'
for d, rs in days.items():
    with open(os.path.join(out, 'BTCUSDT-1m-%s.csv' % d), 'w', newline='\n') as f:
        f.write(hdr + '\n')
        for r in rs:
            f.write(','.join(str(x) for x in r) + '\n')
    print(d, len(rs), 'first', rs[0][0], 'last', rs[-1][0], 'max_high', max(float(x[2]) for x in rs))
