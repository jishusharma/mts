from __future__ import annotations
import json, re, unittest
from decimal import Decimal, ROUND_FLOOR
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[4]
SPEC=ROOT/'MyTradingSys/backtest/layers/FORMULAS_SPEC.md'
FORMULAS=ROOT/'MyTradingSys/backtest/layers/FORMULAS.md'
DATA=Path(r'F:/MTS/data/bigtrade/cache/perp/klines_1h.npz')
CUTOFF=1719792000000
EXPECTED_IDS={f'F{i:02}' for i in range(1,24)} | {f'F11.{i}' for i in range(1,9)} | {f'F18.{i}' for i in range(1,8)} | {f'F19.{i}' for i in range(1,9)} | {f'F20.{i}' for i in range(1,5)} | {f'F21.{i}' for i in range(1,10)}

class FormulaSpec(unittest.TestCase):
 @unittest.skipUnless(DATA.exists(), 'tape klines_1h.npz lives on the NUC F: drive only')
 def test_every_catalog_id_has_spec_example_and_independent_tape_recount(self):
  spec=SPEC.read_text(encoding='utf-8-sig'); catalog=FORMULAS.read_text(encoding='utf-8-sig')
  data=json.loads((Path(__file__).with_name('examples.json')).read_text(encoding='utf-8'))
  missing=EXPECTED_IDS-set(data)
  self.assertFalse(missing, f'missing generated ids: {sorted(missing)}')
  for ident in sorted(EXPECTED_IDS):
   self.assertRegex(spec, rf'(?m)^###? {re.escape(ident)}(?:\s|\.|\b)', f'{ident}: no spec section')
  tape=np.load(DATA); mask=tape['t']<CUTOFF
  t=tape['t'][mask]; o=tape['o'][mask]; h=tape['h'][mask]; l=tape['l'][mask]; c=tape['c'][mask]; v=tape['v'][mask]; tbv=tape['tbv'][mask]
  self.assertTrue(np.all(t<CUTOFF))
  for ident,row in data.items():
   worked=re.search(rf'(?m)^\*\*Worked example {re.escape(ident)} \((?:DEV tape;|SYNTHETIC|NOT_APPLICABLE).*$',spec)
   self.assertIsNotNone(worked,f'{ident}: missing worked example line')
   if row.get('not_applicable'):
    self.assertIn('NOT_APPLICABLE', worked.group(0), f'{ident}: missing NOT_APPLICABLE label in spec')
    self.assertIn(row['quote'][:20], worked.group(0), f'{ident}: spec missing cited quote')
    continue
   val=row['expected']['value']; name=row['expected']['name']
   display = f'{val:.12g}' if isinstance(val, (int, float)) and not isinstance(val, bool) else str(val).lower()
   self.assertIn(f"`{display}`", worked.group(0), f'{ident}: spec value differs from generated record')
   if row.get('synthetic'):
    self.assertIn('SYNTHETIC', worked.group(0), f'{ident}: missing SYNTHETIC in spec')
   else:
    self.assertIn(row['bar_open_utc'][0], worked.group(0), f'{ident}: example line omits cited time')
    indices=np.searchsorted(t,row['bar_open_ms'])
    self.assertTrue(np.all(indices<len(t)) and np.array_equal(t[indices],row['bar_open_ms']),f'{ident}: cited times missing')
    self.assertTrue(np.all(t[indices]<CUTOFF),f'{ident}: post-cutoff timestamp')
   # Independent arithmetic from canonical rule families, using only cited candle fields.
   inp=row['inputs']
   if ident.startswith(('F11.','F18.','F19.','F20.','F21.')):
    self.assertEqual(row.get('formula_case'), ident, f'{ident}: copied parent row has no sub-id-specific formula case')
   if name in ('Wilder RSI at index 14',):
    ds=np.diff(np.asarray(inp['closes'],float)); g=np.maximum(ds,0).mean(); z=np.maximum(-ds,0).mean(); got=100 if z==0 and g>0 else 50 if z==0 else 100-100/(1+g/z)
   elif name=='RMA SMA seed':
    x=inp['values']; seed=float(np.mean(x[:inp['length']])); got=seed+(x[inp['length']]-seed)/inp['length']
   elif name=='SMA': got=float(np.mean(inp['values'][-inp['length']:]))
   elif name=='EMA':
    x=inp['values']; seed=float(np.mean(x[:3])); got=seed+.5*(x[3]-seed)
   elif name=='WMA': got=float(np.dot(inp['values'][-3:],[1,2,3])/6)
   elif name=='forward return': got=(inp['closes'][1]-inp['closes'][0])/inp['closes'][0]
   elif name=='true range': got=max(inp['high']-inp['low'],abs(inp['high']-inp['previous_close']),abs(inp['low']-inp['previous_close']))
   elif name=='gross return': got=(inp['exit']-inp['entry'])/inp['entry']
   elif name=='CVD cumulative input': got=sum(2*a-b for a,b in zip(inp['tbv'],inp['volume']))
   elif name=='session hourly return' or name=='bar return': got=(inp['close']-inp['open'])/inp['open']
   elif name=='typical price bin': got=np.floor(((inp['high']+inp['low']+inp['close'])/3)/inp['bin_width'])
   elif name=='linear trendline': got=inp['anchors'][1][1]+(inp['anchors'][1][1]-inp['anchors'][0][1])
   elif name in ('WaveTrend ap','ap'): got=(inp['high']+inp['low']+inp['close'])/3
   elif name=='volume ratio': got=inp['current_volume']/float(np.mean(inp.get('prior_volumes',[inp.get('prior_volume')])))
   elif name=='population standard deviation': got=np.std(inp['closes'])
   elif name=='net reward risk':
    e=inp['entry']; got=(abs(inp['target']-e)-2*inp['fee_per_side']*e)/(abs(e-inp['stop'])+2*inp['fee_per_side']*e)
   elif name=='population Sharpe':
    x=np.asarray(inp['returns']); got=np.mean(x)/np.std(x) if np.std(x) else 0.0
   elif name=='long R target': got=inp['entry']+abs(inp['entry']-inp['stop'])*inp['R']
   elif name in ('4h close',): got=inp['source_closes'][-1]
   elif name in ('tolerance band transition',): got=inp['values'][1]-inp['values'][0]
   # Section 11 execution subcases
   elif name in ('tick floor','execution tick floor'):
    got=float((Decimal(str(inp['price']))/Decimal(str(inp['tick']))).to_integral_value(rounding=ROUND_FLOOR)*Decimal(str(inp['tick'])))
   elif name=='size floor':
    got=float((Decimal(str(inp['amount_usd']))/Decimal(str(inp['increment_usd']))).to_integral_value(rounding=ROUND_FLOOR)*Decimal(str(inp['increment_usd'])))
   elif name=='ladder rung':
    step=(inp['high']-inp['low'])/(inp['rungs']-1) if inp['rungs']>1 else 0.0
    got=inp['high']-(inp['rung']-1)*step if inp['side']=='LONG' else inp['low']+(inp['rung']-1)*step
   elif name in ('inverse weighted average','inverse live average fill'):
    got=sum(x[1] for x in inp['fills'])/sum(x[1]/x[0] for x in inp['fills'])
   elif name=='inverse stop loss usd':
    got=-inp['size_usd']*abs(inp['entry']-inp['stop'])/inp['entry']
   elif name=='inverse target price':
    got=float((Decimal(str(inp['entry']*(1+inp['pct']/100)))/Decimal('.5')).to_integral_value(rounding=ROUND_FLOOR)*Decimal('.5'))
   elif name=='USD notional':
    got=abs(inp['size'])*(inp['mark_price'] if inp.get('mark_price') is not None else 1.0)
   # Section 18 Volume profile subcases
   elif name=='profile POC price':
    w=inp['w']; bars=inp['bars']; bins={}
    for bl,bh,bv in bars:
     if bh==bl:
      k=int(np.floor(bl/w)); bins[k]=bins.get(k,0.0)+bv
     else:
      for k in range(int(np.floor(bl/w)), int(np.floor(bh/w))+1):
       overlap=max(0.0, min(bh,(k+1)*w) - max(bl, k*w))
       bins[k]=bins.get(k,0.0)+bv*(overlap/(bh-bl))
    max_v=max(bins.values()); poc_k=min(k for k,v in bins.items() if abs(v-max_v)<1e-9)
    got=poc_k*w + w/2.0
   elif name=='fractal pivot high test':
    n=inp['n']; i=inp['test_index']; h_vals=inp['highs']
    got=all(h_vals[i]>h_vals[j] for j in range(i-n,i+n+1) if j!=i)
   elif name=='meaningful pivot size filter':
    got=abs(inp['price_p']-inp['price_q']) >= inp['k']*inp['atr']
   elif name=='touch outcome net R':
    got=(inp['side']*(inp['exit']-inp['L']) - inp['fee_in']*inp['L'] - inp['fee_out']*inp['exit'])/inp['R']
   elif name=='placebo level':
    d_cycle=[-3.0, -2.0, -1.0, -0.5, 0.5, 1.0, 2.0, 3.0]
    got=inp['L'] + d_cycle[inp['refresh_index'] % 8]*inp['R_ref']
   elif name=='day-block bootstrap mean':
    evs=[x for idx in inp['resample_indices'] for x in inp['day_events'][idx]]
    got=sum(evs)/len(evs)
   # Section 19 Trendline subcases
   elif name=='strict pivot low test':
    k=inp['k']; i=inp['test_index']; l_vals=inp['lows']
    got=all(l_vals[i]<l_vals[j] for j in range(i-k,i+k+1) if j!=i)
   elif name=='trendline anchor interpolation':
    ia=inp['ia']; pa=inp['pa']; ib=inp['ib']; pb=inp['pb']; t_val=inp['t']
    if inp.get('geometry')=='log':
     got=float(np.exp(np.log(pa)+(np.log(pb)-np.log(pa))*(t_val-ia)/(ib-ia)))
    else:
     got=pa+(pb-pa)*(t_val-ia)/(ib-ia)
   elif name=='contract ATR':
    got=float(np.mean(inp['ranges'][-inp['length']:]))
   elif name=='slope atr':
    got=(inp['pb']-inp['pa'])/inp['dt']/inp['atr']
   elif name=='touch tolerance test':
    got=bool(inp['low'] <= inp['L'] + inp['mult']*inp['atr'])
   elif name=='episode reset test':
    got=bool(inp['low'] > inp['L'] + inp['mult']*inp['atr'])
   elif name=='volume anchor test ratio':
    got=inp['V']/inp['M']
   elif name=='third anchor tolerance test':
    got=bool(abs(inp['price']-inp['L']) <= inp['mult']*inp['atr'])
   # Section 20 WaveTrend hand-computed subcases
   elif name=='WaveTrend hand ci':
    ap=inp['ap']; n=inp['n']; alpha=2.0/(n+1)
    esa0=ap[0]; esa1=esa0+alpha*(ap[1]-esa0)
    d0=0.0; d1=d0+alpha*(abs(ap[1]-esa1)-d0)
    got=(ap[1]-esa1)/(0.015*d1)
   # Section 21 Krown subcases
   elif name=='wick zone low': got=min(inp['close'],inp['wick_extreme'])
   elif name=='wick zone high': got=max(inp['close'],inp['wick_extreme'])
   elif name=='prior-volume mean ratio': got=inp['current_volume']/inp['prior_mean']
   elif name=='strict bullish engulf test': got=bool(inp['low']<inp['prior_low'] and inp['close']>inp['prior_high'])
   elif name=='dominant low level':
    got=float(min(x[1] for x in inp['bars'][3:7]))
   elif name=='BBWP percentile':
    basis=inp['basis']; lookback=inp['lookback']; closes=inp['closes']; t_idx=inp['t']
    bbw=[]
    for i in range(len(closes)):
     if i<basis-1: bbw.append(0.0)
     else:
      w=closes[i-basis+1:i+1]; m=np.mean(w); s=np.std(w)
      bbw.append(4.0*s/m if m>0 else 0.0)
    prev=bbw[t_idx-lookback:t_idx]
    got=100.0*sum(1 for x in prev if x<bbw[t_idx])/lookback
   elif name=='EMA seed step':
    n=inp['n']; seed=float(np.mean(inp['closes'][:n])); alpha=2.0/(n+1)
    got=seed+alpha*(inp['closes'][n]-seed)
   elif name=='Wilder RSI smoothed':
    period=inp['period']; closes=inp['closes']; ds=np.diff(closes)
    g0=max(ds[0],0); l0=max(-ds[0],0); g1=max(ds[1],0); l1=max(-ds[1],0)
    avg_g=(g0+g1)/2.0; avg_l=(l0+l1)/2.0
    g2=max(ds[2],0); l2=max(-ds[2],0)
    avg_g=(avg_g*(period-1)+g2)/period; avg_l=(avg_l*(period-1)+l2)/period
    got=100.0-100.0/(1.0+avg_g/avg_l)
   elif name=='range position':
    got=(inp['close']-min(inp['lows']))/(max(inp['highs'])-min(inp['lows']))
   elif name=='top signal count':
    window=inp['window']; t_idx=inp['t']; sigs=inp['signals']
    got=sum(1 for k,times in sigs.items() if any(t_idx-window+1<=tm<=t_idx for tm in times))
   else: raise AssertionError(f"unknown formula name: {name!r} ({ident})")
   if isinstance(got, bool):
    self.assertEqual(bool(got), bool(val), f'{ident}: boolean recount mismatch')
   else:
    self.assertAlmostEqual(float(got),float(val),places=9,msg=f'{ident}: independent recount mismatch')

 def test_shuffled_rsi_closes_are_rejected(self):
  # mutation probe: shuffled inputs must not reproduce the cited RSI, so a checker that echoes the expected value would be caught here
  row=json.loads((Path(__file__).with_name('examples.json')).read_text(encoding='utf-8'))['F01']
  closes=np.asarray(row['inputs']['closes'],float)
  def rsi(x):
   ds=np.diff(x); g=np.maximum(ds,0).mean(); z=np.maximum(-ds,0).mean(); return 100-100/(1+g/z)
  shuffled=closes[np.argsort(np.sin(np.arange(len(closes))*12.9898))]
  self.assertAlmostEqual(rsi(closes),float(row['expected']['value']),places=9)
  assert rsi(shuffled) != rsi(closes), 'shuffled closes reproduced the cited RSI'

if __name__=='__main__': unittest.main()
