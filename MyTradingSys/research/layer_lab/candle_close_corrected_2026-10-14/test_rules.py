import unittest
import numpy as np
import rules


class RulesTests(unittest.TestCase):
    def test_directional_structure_and_mirror(self):
        c=np.arange(21,dtype=float)+100
        out=rules.phase(c,c[1:]+.7,c[1:]-.7)
        self.assertEqual(out['phase'],'UP_TREND')
        self.assertAlmostEqual(out['efficiency'],1.)
        mirror=rules.phase(300-c,300-(c[1:]-.7),300-(c[1:]+.7))
        self.assertEqual(mirror['phase'],'DOWN_TREND')

    def test_bounded_range_vs_choppy_rise(self):
        c=np.array([100]+[100,100,102,102,100,100,98,98,100,100]*2,dtype=float)
        self.assertEqual(rules.phase(c,c[1:]+.2,c[1:]-.2)['phase'],'BOUNDED_RANGE')
        c=np.array([100+2*i+(10 if i%2 else 0) for i in range(21)],dtype=float)
        self.assertEqual(rules.phase(c,c[1:]+.2,c[1:]-.2)['phase'],'TRANSITION')

    def test_unknown_history(self):
        c=np.full(21,100.)
        self.assertEqual(rules.phase(c,c[1:],c[1:])['phase'],'UNKNOWN')
        c[5]=np.nan
        self.assertEqual(rules.phase(c,c[1:]+1,c[1:]-1)['phase'],'UNKNOWN')

    def test_joint_context(self):
        p=dict(phase='UP_TREND',atr=1.,lower=90.,upper=110.)
        self.assertEqual(rules.context(p,'UP_TREND',1,100,1),'TREND_ALIGNED')
        self.assertEqual(rules.context(p,'DOWN_TREND',1,100,1),'TREND_CONFLICT')
        p['phase']='BOUNDED_RANGE'
        self.assertEqual(rules.context(p,'TRANSITION',1,91,1),'RANGE_EDGE')
        self.assertEqual(rules.context(p,'TRANSITION',1,100,1),'RANGE_INTERIOR')
        self.assertEqual(rules.context(p,'TRANSITION',1,120,2),'TRANSITION_HIGH_VOL')

    def test_controls_distinct_days_and_calipers(self):
        f=np.zeros((8,4)); f[:,0]=.1
        days=np.array([0,1,1,2,3,4,5,6])
        clocks=np.zeros(8)
        out=rules.nearest_controls(f,days,clocks,0,np.arange(1,8))
        self.assertEqual(len(out),6)
        self.assertEqual(len(set(days[out])),6)
        f[7,0]=5
        out=rules.nearest_controls(f,days,clocks,0,np.arange(1,8))
        self.assertEqual(len(out),5)
        f[6,1]=np.log(3)
        self.assertEqual(len(rules.nearest_controls(f,days,clocks,0,np.arange(1,8))),0)

    def test_control_uncertainty_book(self):
        book=rules.contrast_book(np.array([10.,6.]),np.array([0,1]),np.array([0]),np.array([[1]]),2)
        np.testing.assert_allclose(book,[10,-6])
        self.assertEqual(book.sum(),4)
        # A resampled difference of averages needs both population denominators.
        w=np.array([[1.,1.],[2.,0.],[2.,1.]])
        out=rules.bootstrap_contrast(w,np.array([10.,0.]),np.array([1.,0.]),
                                     np.array([0.,6.]),np.array([0.,1.]))
        np.testing.assert_allclose(out[[0,2]],[4.,4.])
        self.assertTrue(np.isnan(out[1]))

    def test_constant_outcomes_have_zero_lift_under_unequal_counts(self):
        w=np.array([[1.,1.],[2.,1.],[1.,2.]])
        out=rules.bootstrap_contrast(w,np.array([1.,0.]),np.array([1.,0.]),
                                     np.array([0.,1.]),np.array([0.,1.]))
        np.testing.assert_equal(out,[0.,0.,0.])


if __name__=='__main__':
    unittest.main()
