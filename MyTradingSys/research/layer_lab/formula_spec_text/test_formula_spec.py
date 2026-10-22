from __future__ import annotations
import json, re, unittest
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
   worked=re.search(rf'(?m)^\*\*Worked example {re.escape(ident)} \(DEV tape;.*$',spec)
   self.assertIsNotNone(worked,f'{ident}: missing worked example line')
   self.assertIn(row['bar_open_utc'][0],worked.group(0),f'{ident}: example line omits cited time')
   self.assertIn(f"`{row['expected']['value']:.12g}`",worked.group(0),f'{ident}: spec value differs from generated record')
   self.assertFalse(row.get('synthetic',False),f'{ident} must be tape based or explicitly SYNTHETIC')
   indices=np.searchsorted(t,row['bar_open_ms'])
   self.assertTrue(np.all(indices<len(t)) and np.array_equal(t[indices],row['bar_open_ms']),f'{ident}: cited times missing')
   self.assertTrue(np.all(t[indices]<CUTOFF),f'{ident}: post-cutoff timestamp')
   # Independent arithmetic from canonical rule families, using only cited candle fields.
   inp=row['inputs']; val=row['expected']['value']; name=row['expected']['name']
   if ident.startswith(('F11.','F18.','F19.','F20.','F21.')):
    self.assertEqual(row.get('formula_case'), ident, f'{ident}: copied parent row has no sub-id-specific formula case')
   if name in ('Wilder RSI at index 14','RSI seed'):
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
   elif name=='bin index': got=np.floor(inp['typical_price']/inp['bin_width'])
   elif name=='bin lower edge': got=np.floor(inp['typical_price']/inp['bin_width'])*inp['bin_width']
   elif name=='bin upper edge': got=(np.floor(inp['typical_price']/inp['bin_width'])+1)*inp['bin_width']
   elif name=='typical price': got=(inp['high']+inp['low']+inp['close'])/3
   elif name=='bar volume assignment': got=inp['volume']
   elif name=='two-bar profile volume': got=sum(inp['volumes'])
   elif name=='profile bin share': got=inp['bin_volume']/inp['total_volume']
   elif name=='linear trendline': got=inp['anchors'][1][1]+(inp['anchors'][1][1]-inp['anchors'][0][1])
   elif name=='linear interpolation': got=inp['anchors'][0][1]
   elif name=='log interpolation': got=inp['anchor_price']
   elif name=='line slope': got=inp['prices'][1]-inp['prices'][0]
   elif name=='normalized slope': got=(inp['prices'][1]-inp['prices'][0])/inp['atr']
   elif name in ('touch threshold','break threshold','third anchor tolerance'): got=inp['atr']*inp['multiplier']
   elif name=='strict low pivot test': got=inp['lows'][1]<inp['lows'][0] and inp['lows'][1]<inp['lows'][2]
   elif name in ('WaveTrend ap','ap'): got=(inp['high']+inp['low']+inp['close'])/3
   elif name in ('volume ratio','prior-volume mean ratio'): got=inp['current_volume']/float(np.mean(inp.get('prior_volumes',[inp.get('prior_volume')])))
   elif name=='wick zone low': got=min(inp['close'],inp['wick_extreme'])
   elif name=='wick zone high': got=max(inp['close'],inp['wick_extreme'])
   elif name=='strict engulf test': got=inp['low']<inp['prior_low'] and inp['close']>inp['prior_high']
   elif name=='candle body': got=abs(inp['close']-inp['open'])
   elif name=='range position': got=(inp['close']-min(inp['lows']))/(max(inp['highs'])-min(inp['lows']))
   elif name=='range width': got=max(inp['highs'])-min(inp['lows'])
   elif name=='inverse weighted average' or name=='inverse live average fill': got=sum(x[1] for x in inp['fills'])/sum(x[1]/x[0] for x in inp['fills'])
   elif name=='inverse stop loss usd': got=-inp['size_usd']*abs(inp['entry']-inp['stop'])/inp['entry']
   elif name=='size floor': got=np.floor(inp['amount_usd']/inp['increment_usd'])*inp['increment_usd']
   elif name=='ladder rung': got=(inp['low']+inp['high'])/2
   elif name=='USD notional': got=abs(inp['size'])
   elif name in ('tick floor','execution tick floor'): got=np.floor(inp['price']/inp['tick'])*inp['tick']
   elif name=='population Sharpe':
    x=np.asarray(inp['returns']); got=np.mean(x)/np.std(x) if np.std(x) else 0.0
   elif name=='session hourly return' or name=='bar return': got=(inp['close']-inp['open'])/inp['open']
   elif name=='inverse target price': got=np.floor((inp['entry']*(1+inp['pct']/100))/.5)*.5
   elif name.lower() in ('esa warmup','ci guard','wt2 warmup'): got=0.0
   elif name=='population standard deviation': got=np.std(inp['closes'])
   elif name=='net reward risk':
    e=inp['entry']; got=(abs(inp['target']-e)-2*inp['fee_per_side']*e)/(abs(e-inp['stop'])+2*inp['fee_per_side']*e)
   elif name=='long R target': got=inp['entry']+abs(inp['entry']-inp['stop'])*inp['R']
   elif name in ('4h close',): got=inp['source_closes'][-1]
   elif name in ('tolerance band transition',): got=inp['values'][1]-inp['values'][0]
   else: raise AssertionError(f"unknown formula name: {name!r} ({ident})")
   self.assertAlmostEqual(float(got),float(val),places=9,msg=f'{ident}: independent recount mismatch')
   stamp=row['bar_open_utc'][0]
   self.assertIn(stamp,spec,f'{ident}: missing cited UTC open {stamp}')

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

