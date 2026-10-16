from patterns import engulfing, pin_bar, inside_bar, doji
from event_table import build_event_table


def b(o,h,l,c,t): return {'o':o,'h':h,'l':l,'c':c,'t':t}


def test_engulf_and_nearmiss():
    bars=[b(10,11,8,9,0),b(8.5,11,8,10.5,1)]
    assert engulfing(bars,1)==1
    assert engulfing([bars[0],b(8.5,10,8,9.5,1)],1)==0


def test_pin_bar_and_nearmiss():
    assert pin_bar([b(9,10,5,9.5,0)],0)==1
    assert pin_bar([b(9,10,8.5,9.5,0)],0)==0


def test_inside_bar_and_nearmiss():
    bars=[b(5,10,2,6,0),b(5,9,3,7,1)]
    assert inside_bar(bars,1)==1
    assert inside_bar([bars[0],b(5,11,3,7,1)],1)==0


def test_doji_and_nearmiss():
    assert doji([b(5,10,0,5.5,0)],0)==1
    assert doji([b(5,10,0,7,0)],0)==0


def test_event_stamped_close_forward_begins_next_bar():
    bars=[b(1,2,0,1,10),b(1,3,0.5,2,20),b(2,5,1,4,30)]
    event={'pattern':'doji','index':0,'side':1}
    row=build_event_table([event],bars,horizon=2)[0]
    assert row['event_time']==10
    assert row['mfe_R']==2.0
    assert row['bars_forward']==2


def test_short_event_excursions_use_favorable_low_and_adverse_high():
    bars=[b(10,12,8,10,10),b(10,11,7,8,20)]
    row=build_event_table([{'pattern':'bear','index':0,'side':-1}],bars,horizon=1)[0]
    assert row['event_time']==10
    assert row['mfe_R']==0.75
    assert row['mae_R']==0.25
    assert row['bars_forward']==1
