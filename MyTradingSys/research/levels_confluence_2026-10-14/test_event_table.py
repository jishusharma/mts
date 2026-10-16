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
