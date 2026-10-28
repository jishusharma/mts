import unittest
from ref_ladder import fill_ladder

# Spec: Dumps/workers/NUC-QUEUE/specs/021-ref-ladder.md
# fill_ladder(side, rungs, bars, signal_t, deadline_bars, stop=None)
# - Scan bars with t > signal_t (never the signal bar), at most deadline_bars bars.
# - Long: rung fills first bar where low <= price; fill at open if open <= price
#   (better for long), else at price.
# - Short mirror: high >= price; fill at open if open >= price, else at price.
# - If stop hit (long: low <= stop; short: high >= stop), stop filling further
#   rungs from bars AFTER that one. Rungs filling in the SAME bar as the stop
#   are counted as filled (conservative).
# - avg_price is size-weighted sum(price*size)/sum(size), None if nothing filled.


class TestRefLadder(unittest.TestCase):

    def test_long_fill(self):
        # rungs 100/99/98 long. bar0 (t=1000) == signal_t -> excluded.
        # bar1 t=1060 o=99 h=100 l=98.5:
        #   rung100: low 98.5<=100 True; open 99<=100 -> fill at open=99
        #   rung99:  low 98.5<=99  True; open 99<=99  -> fill at open=99
        #   rung98:  low 98.5<=98  False -> no fill
        # avg = (99*1 + 99*1)/2 = 99.0
        rungs = [(100, 1), (99, 1), (98, 2)]
        bars = [
            {'t': 1000, 'o': 100, 'h': 101, 'l': 99.5, 'c': 100.5},
            {'t': 1060, 'o': 99, 'h': 100, 'l': 98.5, 'c': 99.5},
        ]
        result = fill_ladder('long', rungs, bars, 1000, 2)
        self.assertEqual(result['filled'], [(1060, 99, 1), (1060, 99, 1)])
        self.assertEqual(result['filled_size'], 2)
        self.assertEqual(result['avg_price'], 99.0)
        self.assertEqual(result['unfilled'], [(98, 2)])
        self.assertEqual(result['first_fill_t'], 1060)
        self.assertEqual(result['last_fill_t'], 1060)
        self.assertFalse(result['stopped_during_entry'])

    def test_gap_open_fill(self):
        # bar0 (t=1000) == signal_t -> excluded.
        # bar1 t=1060 o=97 h=98 l=97 gaps below all three rungs:
        #   rung100: low 97<=100 True; open 97<=100 -> fill at open=97
        #   rung99:  low 97<=99  True; open 97<=99  -> fill at open=97
        #   rung98:  low 97<=98  True; open 97<=98  -> fill at open=97
        # avg = (97*1 + 97*1 + 97*2)/4 = 97.0
        rungs = [(100, 1), (99, 1), (98, 2)]
        bars = [
            {'t': 1000, 'o': 100, 'h': 101, 'l': 99.5, 'c': 100.5},
            {'t': 1060, 'o': 97, 'h': 98, 'l': 97, 'c': 97.5},
        ]
        result = fill_ladder('long', rungs, bars, 1000, 2)
        self.assertEqual(
            result['filled'],
            [(1060, 97, 1), (1060, 97, 1), (1060, 97, 2)],
        )
        self.assertEqual(result['filled_size'], 4)
        self.assertEqual(result['avg_price'], 97.0)
        self.assertEqual(result['unfilled'], [])

    def test_deadline_cut_off(self):
        # rungs 100/99/98 long. bar0 (t=1000) == signal_t -> excluded.
        # bar1 t=1060 o=100 h=101 l=99.5:
        #   rung100: low 99.5<=100 True; open 100<=100 -> fill at open=100
        #   rung99:  low 99.5<=99  False -> no fill
        #   rung98:  low 99.5<=98  False -> no fill
        # bar2 t=1120 o=99 h=100 l=98.5 (only reachable if deadline_bars>=2):
        #   rung99: low 98.5<=99 True; open 99<=99 -> fill at open=99
        #   rung98: low 98.5<=98 False -> no fill
        #
        # With deadline_bars=1, bar2 must never be scanned, so rung99 must
        # stay unfilled even though it WOULD fill on bar2 (that is the actual
        # cut-off behaviour: a rung that fills after the deadline must not
        # fill). rung98 never fills in either bar within this data.
        rungs = [(100, 1), (99, 1), (98, 2)]
        bars = [
            {'t': 1000, 'o': 100, 'h': 101, 'l': 99.5, 'c': 100.5},
            {'t': 1060, 'o': 100, 'h': 101, 'l': 99.5, 'c': 100.2},
            {'t': 1120, 'o': 99, 'h': 100, 'l': 98.5, 'c': 99.5},
        ]
        # Sanity check: with deadline_bars=2 (bar2 included), rung99 DOES fill.
        result_uncut = fill_ladder('long', rungs, bars, 1000, 2)
        self.assertEqual(
            result_uncut['filled'], [(1060, 100, 1), (1120, 99, 1)]
        )
        self.assertEqual(result_uncut['unfilled'], [(98, 2)])

        # With deadline_bars=1, bar2 is cut off -> rung99 must NOT fill.
        result = fill_ladder('long', rungs, bars, 1000, 1)
        self.assertEqual(result['filled'], [(1060, 100, 1)])
        self.assertEqual(result['filled_size'], 1)
        self.assertEqual(result['avg_price'], 100.0)
        self.assertEqual(result['unfilled'], [(99, 1), (98, 2)])

    def test_signal_bar_excluded(self):
        # rung at 100. The signal bar itself (t=1000) has l=99.5 <= 100 and
        # o=100 <= 100, so if it were (wrongly) scanned it would fill at 100.
        # Per spec, only bars with t > signal_t are scanned, so this rung
        # must NOT fill on the signal bar.
        # bar1 t=1060 o=105 h=106 l=104.5: never touches the rung (low > 100)
        # so it proves the omission is specifically about excluding t==signal_t,
        # not merely a lack of any later bars.
        rungs = [(100, 1)]
        bars = [
            {'t': 1000, 'o': 100, 'h': 101, 'l': 99.5, 'c': 100.5},
            {'t': 1060, 'o': 105, 'h': 106, 'l': 104.5, 'c': 105.5},
        ]
        result = fill_ladder('long', rungs, bars, 1000, 2)
        self.assertEqual(result['filled'], [])
        self.assertEqual(result['filled_size'], 0)
        self.assertIsNone(result['avg_price'])
        self.assertEqual(result['unfilled'], [(100, 1)])

    def test_short_fill(self):
        # rungs 98/99/100 short. bar0 (t=1000) == signal_t -> excluded.
        # bar1 t=1060 o=100 h=101 l=99.5:
        #   rung98:  high 101>=98  True; open 100>=98  -> fill at open=100
        #   rung99:  high 101>=99  True; open 100>=99  -> fill at open=100
        #   rung100: high 101>=100 True; open 100>=100 -> fill at open=100
        # avg = (100*1 + 100*1 + 100*2)/4 = 100.0
        rungs = [(98, 1), (99, 1), (100, 2)]
        bars = [
            {'t': 1000, 'o': 98, 'h': 99, 'l': 97.5, 'c': 98.5},
            {'t': 1060, 'o': 100, 'h': 101, 'l': 99.5, 'c': 100.5},
        ]
        result = fill_ladder('short', rungs, bars, 1000, 2)
        self.assertEqual(
            result['filled'],
            [(1060, 100, 1), (1060, 100, 1), (1060, 100, 2)],
        )
        self.assertEqual(result['filled_size'], 4)
        self.assertEqual(result['avg_price'], 100.0)
        self.assertEqual(result['unfilled'], [])

    def test_stop_hit_same_bar(self):
        # rungs 98/97 long, stop=97.5. bar0 (t=1000) == signal_t -> excluded.
        # bar1 t=1060 o=98 h=98.5 l=97.2 c=97.5 (low stays above rung97, below the stop):
        #   rung98 fill check: low 97<=98 True; open 98<=98 -> fill at open=98
        #   rung97: low 97.2 > 97 -> no fill this bar (a bar reaching 97 WOULD count it: same-bar rule)
        #   stop check: low 97.2<=97.5 -> stop hit in THIS bar
        # Per spec "Rungs that fill in the SAME bar as the stop are counted
        # as filled (conservative...)", so rung98 must be in `filled` and
        # stopped_during_entry must be True.
        # bar2 t=1120 o=96 h=96.5 l=95.5 (later bar): rung97's price (97) is
        # below the stop (97.5) i.e. "beyond the stop" for a long, so per
        # spec it can never fill on this later bar even though low=95.5<=97
        # would otherwise fill it at open=96.
        rungs = [(98, 1), (97, 1)]
        bars = [
            {'t': 1000, 'o': 99, 'h': 99.5, 'l': 98.5, 'c': 99},
            {'t': 1060, 'o': 98, 'h': 98.5, 'l': 97.2, 'c': 97.5},
            {'t': 1120, 'o': 96, 'h': 96.5, 'l': 95.5, 'c': 96},
        ]
        result = fill_ladder('long', rungs, bars, 1000, 3, stop=97.5)
        # NOTE: this is expected PER SPEC. If the implementation breaks out
        # of the bar loop on stop-hit before evaluating that bar's rung
        # fills, this will fail -- see report (spec bullet on same-bar fills
        # being counted as filled).
        self.assertEqual(result['filled'], [(1060, 98, 1)])
        self.assertEqual(result['filled_size'], 1)
        self.assertEqual(result['avg_price'], 98.0)
        self.assertTrue(result['stopped_during_entry'])
        self.assertEqual(result['unfilled'], [(97, 1)])

    def test_stop_before_deeper_rung_not_hit_same_bar(self):
        # rungs 99/97 long, stop=98. This is a DIFFERENT scenario from the
        # same-bar case above: the stop is hit on a bar that does not touch
        # the deeper rung at all, and a LATER separate bar would otherwise
        # fill that deeper rung. It must not, regardless of how same-bar
        # fills are handled.
        # bar0 (t=1000) == signal_t -> excluded.
        # bar1 t=1060 o=99 h=99.5 l=98.5:
        #   rung99: low 98.5<=99 True; open 99<=99 -> fill at open=99
        #   stop check: low 98.5<=98 False -> not stopped yet
        # bar2 t=1120 o=98.2 h=98.5 l=97.8:
        #   rung97: low 97.8<=97 False -> does not touch this bar (no
        #   same-bar ambiguity)
        #   stop check: low 97.8<=98 True -> stop hit here, scanning stops
        #   for bars AFTER this one
        # bar3 t=1180 o=96 h=96.5 l=95.5 (later bar, must be skipped):
        #   rung97 would fill here (low 95.5<=97, open 96<=97 -> at open=96)
        #   if scanning continued, but per spec it must NOT since the stop
        #   was already hit on bar2 (a bar strictly before bar3).
        rungs = [(99, 1), (97, 1)]
        bars = [
            {'t': 1000, 'o': 99.5, 'h': 100, 'l': 99, 'c': 99.5},
            {'t': 1060, 'o': 99, 'h': 99.5, 'l': 98.5, 'c': 99},
            {'t': 1120, 'o': 98.2, 'h': 98.5, 'l': 97.8, 'c': 98},
            {'t': 1180, 'o': 96, 'h': 96.5, 'l': 95.5, 'c': 96},
        ]
        result = fill_ladder('long', rungs, bars, 1000, 4, stop=98)
        self.assertEqual(result['filled'], [(1060, 99, 1)])
        self.assertEqual(result['filled_size'], 1)
        self.assertEqual(result['avg_price'], 99.0)
        self.assertTrue(result['stopped_during_entry'])
        self.assertEqual(result['unfilled'], [(97, 1)])
        self.assertEqual(result['last_fill_t'], 1060)

    def test_no_fill(self):
        # rung at 90 long, i.e. a buy-limit well BELOW the market. bar0
        # (t=1000) == signal_t -> excluded. bar1 t=1060 o=98 h=99 l=97.5:
        # low 97.5<=90 is False, so the market never drops far enough to
        # touch the rung -> it must never fill.
        rungs = [(90, 1)]
        bars = [
            {'t': 1000, 'o': 98, 'h': 99, 'l': 97.5, 'c': 98.5},
            {'t': 1060, 'o': 98, 'h': 99, 'l': 97.5, 'c': 98.5},
        ]
        result = fill_ladder('long', rungs, bars, 1000, 1)
        self.assertEqual(result['filled'], [])
        self.assertIsNone(result['avg_price'])
        self.assertEqual(result['filled_size'], 0)
        self.assertFalse(result['stopped_during_entry'])
        self.assertEqual(result['unfilled'], [(90, 1)])


if __name__ == '__main__':
    unittest.main()
