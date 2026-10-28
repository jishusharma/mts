import json
import pathlib
import collections
import time
import argparse
import tempfile

def load_journal_dir(path):
    path = pathlib.Path(path)
    result = {}
    
    for file_path in path.glob("*.jsonl"):
        records = []
        with open(file_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as e:
                    raise ValueError(f"{file_path}: line {line_num}: {str(e)}")
                records.append(record)
        
        # Sort by timestamp
        records.sort(key=lambda x: x['ts'])
        
        plan_id = records[0]['plan_id'] if records else None
        if plan_id is not None:
            result[plan_id] = records
    
    return result

def summarize_plan(records):
    plan_id = records[0]['plan_id']
    
    first_ts = records[0]['ts']
    last_ts = records[-1]['ts']
    duration_s = last_ts - first_ts
    
    counts = collections.defaultdict(int)
    placed = set()
    filled = set()
    cancelled = set()
    halts = []
    errors = []
    reconciliations = 0
    reconciliation_mismatches = 0
    
    for record in records:
        event_type = record['event_type']
        counts[event_type] += 1
        
        if event_type == 'order_placed':
            placed.add(record['data']['order_id'])
        elif event_type == 'order_filled':
            filled.add(record['data']['order_id'])
        elif event_type == 'order_cancelled':
            cancelled.add(record['data']['order_id'])
        elif event_type == 'mismatch_halt':
            halts.append(record['data'])
        elif event_type == 'error':
            errors.append(record['data'])
        elif event_type == 'reconciliation':
            reconciliations += 1
            if record['data'].get('mismatches'):
                reconciliation_mismatches += 1
    
    unresolved_orders = sorted(list(placed - filled - cancelled))
    
    return {
        "plan_id": plan_id,
        "first_ts": first_ts,
        "last_ts": last_ts,
        "duration_s": duration_s,
        "counts": dict(counts),
        "placed": placed,
        "filled": filled,
        "cancelled": cancelled,
        "unresolved_orders": unresolved_orders,
        "halts": halts,
        "errors": errors,
        "reconciliations": reconciliations,
        "reconciliation_mismatches": reconciliation_mismatches
    }

def soak_verdict(summaries, expected_halt_prefixes=("c5_",)):
    problems = []
    
    for summary in summaries:
        plan_id = summary['plan_id']
        
        # Check for unexpected halts
        if summary['halts']:
            if not any(plan_id.startswith(prefix) for prefix in expected_halt_prefixes):
                for halt in summary['halts']:
                    reason = halt.get('reason', '?')
                    problems.append(f"UNEXPECTED HALT {plan_id}: {reason}")
        
        # Check for errors
        for error in summary['errors']:
            problems.append(f"ERROR {plan_id}: {error}")
        
        # Check for reconciliation mismatches
        if summary['reconciliation_mismatches'] > 0:
            if not any(plan_id.startswith(prefix) for prefix in expected_halt_prefixes):
                problems.append(f"RECON MISMATCH {plan_id}: {summary['reconciliation_mismatches']}")
        
        # Check for unresolved orders in closed/halted plans
        if (summary['halts'] or summary['reconciliations'] > 0) and summary['unresolved_orders']:
            problems.append(f"ORPHAN ORDERS {plan_id}: {','.join(summary['unresolved_orders'])}")
    
    return {
        "clean": len(problems) == 0,
        "problems": problems,
        "plans": len(summaries),
        "events": sum(sum(summary['counts'].values()) for summary in summaries)
    }

def format_report(summaries, verdict):
    lines = []
    
    if verdict["clean"]:
        lines.append("SOAK CLEAN")
    else:
        lines.append("SOAK NOT CLEAN")
    
    lines.append(f"plans={verdict['plans']} events={verdict['events']}")
    
    for summary in summaries:
        plan_id = summary['plan_id']
        dur = int(summary['duration_s'])
        placed = len(summary['placed'])
        filled = len(summary['filled'])
        cancelled = len(summary['cancelled'])
        unresolved = len(summary['unresolved_orders'])
        halts = len(summary['halts'])
        errors = len(summary['errors'])
        
        lines.append(f"{plan_id} dur={dur}s placed={placed} filled={filled} cancelled={cancelled} unresolved={unresolved} halts={halts} errors={errors}")
    
    for problem in verdict["problems"]:
        lines.append(f"- {problem}")
    
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('journal_dir', nargs='?', default='journal/')
    parser.add_argument('--expect-halt-prefix', action='append', default=['c5_'])
    
    args = parser.parse_args()
    
    try:
        journal_data = load_journal_dir(args.journal_dir)
        summaries = [summarize_plan(records) for records in journal_data.values()]
        verdict = soak_verdict(summaries, tuple(args.expect_halt_prefix))
        print(format_report(summaries, verdict))
        
        if not verdict["clean"]:
            exit(1)
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
