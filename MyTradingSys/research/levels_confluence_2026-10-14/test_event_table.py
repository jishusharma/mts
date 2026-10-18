"""Hand-derived indicator and point-in-time regression tests for LC2."""
import importlib.util
from pathlib import Path

P=Path(__file__).with_name('event_table.py')
S=importlib.util.spec_from_file_location('lc_event_table',P); m=importlib.util.module_from_spec(S); S.loader.exec_module(m)


def test_bollinger_position_known_population_sd():
    # Closes 1..20: mean=10.5; population SD=sqrt(33.25); band width=4*SD.
    got=m.bollinger_position(list(range(1,21)))
    assert abs(got-(20-10.5+2*(33.25**.5))/(4*(33.25**.5)))<1e-12


def test_touch_bar_excluded_from_entry_indicator():
    bars=[{'t':i*60000,'o':100.,'h':101.,'l':99.,'c':float(100+i%2),'v':1.,'tbv':.6} for i in range(60)]
    before=m._features(bars,50); changed=[dict(x) for x in bars]; changed[50]['c']=10000.
    after=m._features(changed,50)
    assert before==after


def test_bias_only_completed_aggregate_bars():
    bars=[{'t':i*60000,'o':100.,'h':101.,'l':99.,'c':float(i+1),'v':1.,'tbv':.5} for i in range(3000)]
    t=bars[120]['t']
    one=m._bias_at(bars,t,None)
    altered=[dict(x) for x in bars]; altered[120]['c']=-1e9; altered[120]['h']=1e9
    two=m._bias_at(altered,t,None)
    assert one==two


def test_q79_side_from_previous_close_and_no_touch_bar_mfe():
    # Day 1; level 100.0 first touched by bar 70. Previous close 99.0 (below) => side -1 (short).
    # Touch bar closes 100.4 (old code: side +1) and dips to 98.0 inside the touch bar: that
    # in-bar move must not count toward MFE. Later bars are flat near 99.8 (low 99.75).
    D=m.DAY
    bars=[{'t':0,'o':99.,'h':99.,'l':99.,'c':99.,'v':1.,'tbv':.5}]
    bars+=[{'t':D+i*60000,'o':99.,'h':99.05,'l':98.95,'c':99.,'v':1.,'tbv':.5} for i in range(70)]
    bars.append({'t':D+70*60000,'o':99.0,'h':100.1,'l':98.0,'c':100.4,'v':1.,'tbv':.5})
    bars+=[{'t':D+(71+i)*60000,'o':99.8,'h':99.85,'l':99.75,'c':99.8,'v':1.,'tbv':.5} for i in range(10)]
    m.levels_by_day=lambda b:{1:[{'family':'prior_day_high','source':'TOM','price':100.0}]}
    m._profile=lambda b:{'vah':1e9,'val':-1e9}
    rows=m.make_events(bars)
    assert len(rows)==1 and rows[0]['side']==-1
    R=rows[0]['R_price']
    assert abs(rows[0]['MFE_R']-0.25/R)<1e-9
