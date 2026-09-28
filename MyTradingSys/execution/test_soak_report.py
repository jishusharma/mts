import unittest
import tempfile
import os
import json
from soak_report import load_journal_dir, summarize_plan, soak_verdict, format_report

class TestSoakReport(unittest.TestCase):
    
    def test_two_plans(self):
        # Create temp journal dir with two plans
        with tempfile.TemporaryDirectory() as tmpdir:
            # Plan 1: placed a,b / filled a / cancelled b -> unresolved []
            plan1_file = os.path.join(tmpdir, "plan1.jsonl")
            with open(plan1_file, 'w') as f:
                f.write(json.dumps({
                    "ts": 1000,
                    "ts_iso": "2026-09-27T19:31:32Z",
                    "plan_id": "plan1",
                    "event_type": "intent",
                    "data": {"compiled": {"plan_id": "plan1"}}
                }) + "\n")
                f.write(json.dumps({
                    "ts": 1001,
                    "ts_iso": "2026-09-27T19:31:33Z",
                    "plan_id": "plan1",
                    "event_type": "order_placed",
                    "data": {"order_id": "a"}
                }) + "\n")
                f.write(json.dumps({
                    "ts": 1002,
                    "ts_iso": "2026-09-27T19:31:34Z",
                    "plan_id": "plan1",
                    "event_type": "order_placed",
                    "data": {"order_id": "b"}
                }) + "\n")
                f.write(json.dumps({
                    "ts": 1003,
                    "ts_iso": "2026-09-27T19:31:35Z",
                    "plan_id": "plan1",
                    "event_type": "order_filled",
                    "data": {"order_id": "a"}
                }) + "\n")
                f.write(json.dumps({
                    "ts": 1004,
                    "ts_iso": "2026-09-27T19:31:36Z",
                    "plan_id": "plan1",
                    "event_type": "order_cancelled",
                    "data": {"order_id": "b"}
                }) + "\n")
            
            # Plan 2: placed x not filled/cancelled -> unresolved ["x"]
            plan2_file = os.path.join(tmpdir, "plan2.jsonl")
            with open(plan2_file, 'w') as f:
                f.write(json.dumps({
                    "ts": 1000,
                    "ts_iso": "2026-09-27T19:31:32Z",
                    "plan_id": "plan2",
                    "event_type": "intent",
                    "data": {"compiled": {"plan_id": "plan2"}}
                }) + "\n")
                f.write(json.dumps({
                    "ts": 1001,
                    "ts_iso": "2026-09-27T19:31:33Z",
                    "plan_id": "plan2",
                    "event_type": "order_placed",
                    "data": {"order_id": "x"}
                }) + "\n")
            
            journal_data = load_journal_dir(tmpdir)
            summaries = [summarize_plan(records) for records in journal_data.values()]
            
            # Check plan1
            summary1 = next(s for s in summaries if s['plan_id'] == 'plan1')
            self.assertEqual(summary1['unresolved_orders'], [])
            
            # Check plan2
            summary2 = next(s for s in summaries if s['plan_id'] == 'plan2')
            self.assertEqual(summary2['unresolved_orders'], ['x'])
    
    def test_unexpected_halt(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            plan_file = os.path.join(tmpdir, "p1.jsonl")
            with open(plan_file, 'w') as f:
                f.write(json.dumps({
                    "ts": 1000,
                    "ts_iso": "2026-09-27T19:31:32Z",
                    "plan_id": "p1",
                    "event_type": "intent",
                    "data": {"compiled": {"plan_id": "p1"}}
                }) + "\n")
                f.write(json.dumps({
                    "ts": 1001,
                    "ts_iso": "2026-09-27T19:31:33Z",
                    "plan_id": "p1",
                    "event_type": "mismatch_halt",
                    "data": {"reason": "test halt"}
                }) + "\n")
            
            journal_data = load_journal_dir(tmpdir)
            summaries = [summarize_plan(records) for records in journal_data.values()]
            verdict = soak_verdict(summaries, ("c5_",))
            
            self.assertFalse(verdict["clean"])
            self.assertIn("UNEXPECTED HALT p1: test halt", verdict["problems"])
    
    def test_expected_halt(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            plan_file = os.path.join(tmpdir, "c5_test.jsonl")
            with open(plan_file, 'w') as f:
                f.write(json.dumps({
                    "ts": 1000,
                    "ts_iso": "2026-09-27T19:31:32Z",
                    "plan_id": "c5_test",
                    "event_type": "intent",
                    "data": {"compiled": {"plan_id": "c5_test"}}
                }) + "\n")
                f.write(json.dumps({
                    "ts": 1001,
                    "ts_iso": "2026-09-27T19:31:33Z",
                    "plan_id": "c5_test",
                    "event_type": "mismatch_halt",
                    "data": {"reason": "test halt"}
                }) + "\n")
            
            journal_data = load_journal_dir(tmpdir)
            summaries = [summarize_plan(records) for records in journal_data.values()]
            verdict = soak_verdict(summaries, ("c5_",))
            
            self.assertTrue(verdict["clean"])
    
    def test_error_event(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            plan_file = os.path.join(tmpdir, "plan.jsonl")
            with open(plan_file, 'w') as f:
                f.write(json.dumps({
                    "ts": 1000,
                    "ts_iso": "2026-09-27T19:31:32Z",
                    "plan_id": "plan",
                    "event_type": "intent",
                    "data": {"compiled": {"plan_id": "plan"}}
                }) + "\n")
                f.write(json.dumps({
                    "ts": 1001,
                    "ts_iso": "2026-09-27T19:31:33Z",
                    "plan_id": "plan",
                    "event_type": "error",
                    "data": {"message": "test error"}
                }) + "\n")
            
            journal_data = load_journal_dir(tmpdir)
            summaries = [summarize_plan(records) for records in journal_data.values()]
            verdict = soak_verdict(summaries, ("c5_",))
            
            self.assertFalse(verdict["clean"])
            self.assertIn("ERROR plan: {'message': 'test error'}", verdict["problems"])
    
    def test_reconciliation_mismatch(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            plan_file = os.path.join(tmpdir, "p2.jsonl")
            with open(plan_file, 'w') as f:
                f.write(json.dumps({
                    "ts": 1000,
                    "ts_iso": "2026-09-27T19:31:32Z",
                    "plan_id": "p2",
                    "event_type": "intent",
                    "data": {"compiled": {"plan_id": "p2"}}
                }) + "\n")
                f.write(json.dumps({
                    "ts": 1001,
                    "ts_iso": "2026-09-27T19:31:33Z",
                    "plan_id": "p2",
                    "event_type": "reconciliation",
                    "data": {"mismatches": ["m"]}
                }) + "\n")
            
            journal_data = load_journal_dir(tmpdir)
            summaries = [summarize_plan(records) for records in journal_data.values()]
            verdict = soak_verdict(summaries, ("c5_",))
            
            self.assertFalse(verdict["clean"])
            self.assertIn("RECON MISMATCH p2: 1", verdict["problems"])
    
    def test_invalid_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            plan_file = os.path.join(tmpdir, "plan.jsonl")
            with open(plan_file, 'w') as f:
                f.write(json.dumps({
                    "ts": 1000,
                    "ts_iso": "2026-09-27T19:31:32Z",
                    "plan_id": "plan",
                    "event_type": "intent",
                    "data": {"compiled": {"plan_id": "plan"}}
                }) + "\n")
                f.write("invalid json line\n")  # Invalid JSON
                f.write(json.dumps({
                    "ts": 1002,
                    "ts_iso": "2026-09-27T19:31:34Z",
                    "plan_id": "plan",
                    "event_type": "order_placed",
                    "data": {"order_id": "a"}
                }) + "\n")
            
            with self.assertRaises(ValueError) as context:
                load_journal_dir(tmpdir)
            
            self.assertIn("plan.jsonl: line 2:", str(context.exception))
    
    def test_format_report_clean(self):
        summary = {
            "plan_id": "test_plan",
            "first_ts": 1000,
            "last_ts": 1050,
            "duration_s": 50.0,
            "counts": {"intent": 1, "order_placed": 2, "order_filled": 1},
            "placed": {"a", "b"},
            "filled": {"a"},
            "cancelled": set(),
            "unresolved_orders": [],
            "halts": [],
            "errors": [],
            "reconciliations": 0,
            "reconciliation_mismatches": 0
        }
        
        verdict = {
            "clean": True,
            "problems": [],
            "plans": 1,
            "events": 4
        }
        
        report = format_report([summary], verdict)
        self.assertEqual(report.split('\n')[0], "SOAK CLEAN")
    
    def test_out_of_order_records(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            plan_file = os.path.join(tmpdir, "plan.jsonl")
            with open(plan_file, 'w') as f:
                f.write(json.dumps({
                    "ts": 1002,
                    "ts_iso": "2026-09-27T19:31:34Z",
                    "plan_id": "plan",
                    "event_type": "order_placed",
                    "data": {"order_id": "b"}
                }) + "\n")
                f.write(json.dumps({
                    "ts": 1000,
                    "ts_iso": "2026-09-27T19:31:32Z",
                    "plan_id": "plan",
                    "event_type": "intent",
                    "data": {"compiled": {"plan_id": "plan"}}
                }) + "\n")
                f.write(json.dumps({
                    "ts": 1001,
                    "ts_iso": "2026-09-27T19:31:33Z",
                    "plan_id": "plan",
                    "event_type": "order_placed",
                    "data": {"order_id": "a"}
                }) + "\n")
            
            journal_data = load_journal_dir(tmpdir)
            summaries = [summarize_plan(records) for records in journal_data.values()]
            
            # Check that records are sorted by timestamp
            self.assertEqual(summaries[0]['first_ts'], 1000)
            self.assertEqual(summaries[0]['last_ts'], 1002)

    def test_unresolved_orders_on_closed_plan_is_problem(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            plan_file = os.path.join(tmpdir, "plan.jsonl")
            with open(plan_file, 'w') as f:
                f.write(json.dumps({
                    "ts": 1000,
                    "ts_iso": "2026-09-27T19:31:32Z",
                    "plan_id": "plan",
                    "event_type": "intent",
                    "data": {"compiled": {"plan_id": "plan"}}
                }) + "\n")
                f.write(json.dumps({
                    "ts": 1001,
                    "ts_iso": "2026-09-27T19:31:33Z",
                    "plan_id": "plan",
                    "event_type": "order_placed",
                    "data": {"order_id": "a"}
                }) + "\n")
                f.write(json.dumps({
                    "ts": 1002,
                    "ts_iso": "2026-09-27T19:31:34Z",
                    "plan_id": "plan",
                    "event_type": "order_placed",
                    "data": {"order_id": "b"}
                }) + "\n")
                f.write(json.dumps({
                    "ts": 1003,
                    "ts_iso": "2026-09-27T19:31:35Z",
                    "plan_id": "plan",
                    "event_type": "reconciliation",
                    "data": {"mismatches": []}
                }) + "\n")
            
            journal_data = load_journal_dir(tmpdir)
            summaries = [summarize_plan(records) for records in journal_data.values()]
            verdict = soak_verdict(summaries, ("c5_",))
            
            self.assertFalse(verdict["clean"])
            self.assertIn("ORPHAN ORDERS plan: a,b", verdict["problems"])

    def test_unresolved_orders_on_open_plan_is_fine(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            plan_file = os.path.join(tmpdir, "plan.jsonl")
            with open(plan_file, 'w') as f:
                f.write(json.dumps({
                    "ts": 1000,
                    "ts_iso": "2026-09-27T19:31:32Z",
                    "plan_id": "plan",
                    "event_type": "intent",
                    "data": {"compiled": {"plan_id": "plan"}}
                }) + "\n")
                f.write(json.dumps({
                    "ts": 1001,
                    "ts_iso": "2026-09-27T19:31:33Z",
                    "plan_id": "plan",
                    "event_type": "order_placed",
                    "data": {"order_id": "a"}
                }) + "\n")
                f.write(json.dumps({
                    "ts": 1002,
                    "ts_iso": "2026-09-27T19:31:34Z",
                    "plan_id": "plan",
                    "event_type": "order_placed",
                    "data": {"order_id": "b"}
                }) + "\n")
            
            journal_data = load_journal_dir(tmpdir)
            summaries = [summarize_plan(records) for records in journal_data.values()]
            verdict = soak_verdict(summaries, ("c5_",))
            
            self.assertTrue(verdict["clean"])

if __name__ == '__main__':
    unittest.main()
