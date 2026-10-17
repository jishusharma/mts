import sys,statistics
sys.path.insert(0,'MyTradingSys/research/layer_lab/bb_top_reversal_event_table')
import event_table as et
bars=et.load_dev_npz(); rows=et.build_event_table(bars)
ok=[r for r in rows if r['status']=='OK']
days={r['timestamp']//86400000 for r in rows}
dist=[r['risk_r']/r['entry'] for r in ok]
print(len(rows),len(ok),len(days),statistics.median(dist), 0.001/statistics.median(dist))
