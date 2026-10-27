import unittest
import numpy as np
import json
import tempfile
from pathlib import Path
from unittest.mock import patch
try:
    import pandas as pd
except ImportError:
    pd=None
if pd is not None:
    import engine


@unittest.skipIf(pd is None,'pandas required for pipeline tests; explicit research gate forbids skips')
class EngineTests(unittest.TestCase):
    @staticmethod
    def bars(n=40*1440):
        x=np.arange(n); px=100+np.sin(x/50)+.4*np.sin(x/2000)
        return pd.DataFrame(dict(o=px,c=px+.01,h=px+.1,l=px-.1,v=np.ones(n)),
                            index=pd.date_range('2022-01-01',periods=n,freq='min',tz='UTC'))

    def test_future_truncation_preserves_all_historic_decisions(self):
        a=self.bars(); cutoff=a.index[37*1440]
        full,_=engine.feature_ledger(a)
        short,_=engine.feature_ledger(a.loc[a.index<cutoff])
        cols=[x for x in full.columns if x!='event_id']
        keys=['tf','family','edge','source','side','encounter']
        old=full.loc[pd.to_datetime(full.decision,utc=True)<cutoff,cols].sort_values(keys).reset_index(drop=True)
        new=short.loc[pd.to_datetime(short.decision,utc=True)<cutoff,cols].sort_values(keys).reset_index(drop=True)
        self.assertGreater(len(new),0)
        pd.testing.assert_frame_equal(old,new)

    def test_funding_entry_excluded_exit_included_and_mirror(self):
        times=pd.date_range('2022-01-01',periods=3,freq='8h',tz='UTC')
        rates=np.array([.5,.001,.002]); prices=np.array([100.,110.,90.])
        self.assertAlmostEqual(engine.funding_charge(times,rates,prices,times[0],times[2],100,1),.0029)
        self.assertAlmostEqual(engine.funding_charge(times,rates,prices,times[0],times[2],100,-1),-.0029)

    def test_funding_archive_millisecond_jitter(self):
        expected=pd.date_range('2022-01-01',periods=3,freq='8h',tz='UTC')
        reported=expected+pd.to_timedelta([6,31,0],unit='ms')
        pd.testing.assert_index_equal(engine.settlement_slots(reported),expected,exact=False)
        with self.assertRaises(ValueError): engine.settlement_slots(expected+pd.Timedelta(minutes=1))

    def test_censoring_and_ambiguous_barrier(self):
        a=self.bars(1500)
        a[['o','c']]=100.; a['h']=100.1; a['l']=99.9
        start=a.index[5]; a.loc[a.index[6],['h','l']]=[102.,98.]
        out=engine.outcome(a,start,1,1.,99.9,1440,None)
        self.assertEqual(out['barrier_status'],'AMBIGUOUS')
        self.assertEqual(out['barrier_low'],0)
        self.assertEqual(out['barrier_high'],1)
        self.assertEqual(out['persist'],0)
        self.assertTrue(engine.outcome(a,a.index[-1],1,1.,99.,60,None)['censored'])

    def test_inference_on_independent_known_fixture(self):
        rows=[]
        for i in range(10):
            row=dict(event_id=i,tf=1,family='day',edge='l',side=1,approach=1,context='TREND_ALIGNED',
                     source='REAL',distance=.1,vol_ratio=1.,decision=str(pd.Timestamp('2022-01-01',tz='UTC')+pd.Timedelta(days=i)))
            for sig in ['rejection','break','acceptance','reclaim','retest','strong_break']: row[sig]=sig=='break' and i<5
            for h in engine.HORIZONS:
                row.update({f'gross_{h}':.0214 if i<5 else -.005,
                            f'win_{h}':float(i<5),f'net14_{h}':.02 if i<5 else -.0064,
                            f'net20_{h}':.0194 if i<5 else -.007})
            row.update(barrier_low_1440=float(i<5),barrier_high_1440=float(i<5),persist_1440=float(i<5))
            rows.append(row)
        original=engine.OUT
        with tempfile.TemporaryDirectory(prefix='mts_inference_fixture_') as td:
            target=Path(td)
            for name in ['engine.py','rules.py','PRE_REG.md']:
                (target/name).write_bytes((original/name).read_bytes())
            with patch.object(engine,'OUT',target): engine.analyze(pd.DataFrame(rows),self.bars(20*1440),{})
            result=json.loads((target/'results.json').read_text())
            self.assertEqual(len(result['rows']),2016)
            r=next(x for x in result['rows'] if x['tf']==1 and x['family']=='day' and x['context']=='TREND_ALIGNED' and x['signature']=='break' and x['horizon']==60)
            self.assertEqual(r['n'],5)
            self.assertAlmostEqual(r['win'],1.)
            self.assertAlmostEqual(r['lift'],1.)
            self.assertAlmostEqual(r['net14'],.02)
            self.assertEqual(r['win_ci'],[1.,1.])
            self.assertFalse(r['candidate'])


if __name__=='__main__': unittest.main()
