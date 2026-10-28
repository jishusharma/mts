import json
import math
from collections import defaultdict, Counter
from argparse import ArgumentParser
from typing import List, Dict, Tuple

def load_labels(path: str) -> List[Dict]:
    with open(path, 'r') as f:
        data = json.load(f)
    records = []
    for key, record in data.items():
        if record.get('ts') is None or record.get('fwd_return_pct') is None:
            continue
        if record.get('vp_shape') is None or record.get('price_vs_va') is None or record.get('cvd_slope') is None:
            continue
        records.append(record)
    return sorted(records, key=lambda x: x['ts'])

def outcome(ret_pct: float, band: float = 0.2) -> str:
    if ret_pct > band:
        return "UP"
    elif ret_pct < -band:
        return "DOWN"
    else:
        return "FLAT"

def build_table(records: List[Dict], features: Tuple[str, ...] = ("vp_shape","price_vs_va","cvd_slope"), horizon: str = "60m", band: float = 0.2, alpha: float = 1.0) -> Dict:
    # Initialize table structure
    table = defaultdict(lambda: Counter())
    total_counts = Counter()
    
    for record in records:
        if record.get('ts') is None:
            continue
        try:
            ret_pct = record['fwd_return_pct'][horizon]
        except (KeyError, TypeError):
            continue
            
        # Skip if return is None or NaN
        if ret_pct is None or math.isnan(ret_pct):
            continue
            
        # Get feature values
        feature_vals = tuple(record.get(feat) for feat in features)
        
        # Skip records with missing features
        if any(val is None for val in feature_vals):
            continue
            
        # Compute outcome
        out = outcome(ret_pct, band)
        
        # Update counts
        table[feature_vals][out] += 1
        total_counts[out] += 1
        table[feature_vals]["n"] += 1
    
    # Add baseline entry
    table["__baseline__"] = dict(total_counts)
    
    # Compute probabilities with Dirichlet smoothing
    for cell, counts in table.items():
        if cell == "__baseline__":
            continue
        n = counts["n"]
        up_count = counts["UP"]
        flat_count = counts["FLAT"]
        down_count = counts["DOWN"]
        
        # Apply smoothing
        up_prob = (up_count + alpha) / (n + 3 * alpha)
        flat_prob = (flat_count + alpha) / (n + 3 * alpha)
        down_prob = (down_count + alpha) / (n + 3 * alpha)
        
        table[cell] = {
            "UP": up_prob,
            "FLAT": flat_prob,
            "DOWN": down_prob,
            "n": n
        }
    
    # Add baseline probabilities
    if "__baseline__" in table:
        total_n = sum(total_counts.values())
        table["__baseline__"] = {
            "UP": (total_counts["UP"] + alpha) / (total_n + 3 * alpha),
            "FLAT": (total_counts["FLAT"] + alpha) / (total_n + 3 * alpha),
            "DOWN": (total_counts["DOWN"] + alpha) / (total_n + 3 * alpha),
            "n": total_n
        }
    
    return table

def evaluate(train: List[Dict], test: List[Dict], **kw) -> Dict:
    # Extract parameters
    features = kw.get("features", ("vp_shape","price_vs_va","cvd_slope"))
    horizon = kw.get("horizon", "60m")
    band = kw.get("band", 0.2)
    alpha = kw.get("alpha", 1.0)
    min_n = kw.get("min_n", 100)
    
    # Build table on training data
    table = build_table(train, features, horizon, band, alpha)
    
    # Compute log-loss on test set
    n_test = len(test)
    logloss_table = 0.0
    logloss_baseline = 0.0
    
    cells_ge_min_n = 0
    total_logloss = 0.0
    n_scored = 0
    
    for record in test:
        try:
            ret_pct = record['fwd_return_pct'][horizon]
        except (KeyError, TypeError):
            continue
            
        if ret_pct is None or math.isnan(ret_pct):
            continue
            
        feature_vals = tuple(record.get(feat) for feat in features)
        
        if any(val is None for val in feature_vals):
            continue
            
        out = outcome(ret_pct, band)
        n_scored += 1
        
        # Get cell probabilities
        if feature_vals in table and table[feature_vals]["n"] >= min_n:
            probs = table[feature_vals]
            cells_ge_min_n += 1
        else:
            probs = table["__baseline__"]
            
        # Compute log-loss contribution
        prob = probs[out]
        if prob > 0:
            logloss_table -= math.log(prob)
        else:
            logloss_table -= 1e6  # Very large penalty for zero probability
            
        # Baseline log-loss (using overall distribution)
        baseline_prob = table["__baseline__"][out]
        if baseline_prob > 0:
            logloss_baseline -= math.log(baseline_prob)
        else:
            logloss_baseline -= 1e6
            
    # Average log-loss
    avg_logloss_table = logloss_table / n_scored if n_scored > 0 else 0.0
    avg_logloss_baseline = logloss_baseline / n_scored if n_scored > 0 else 0.0
    
    improvement = avg_logloss_baseline - avg_logloss_table if n_scored > 0 else 0.0
    
    # Get top cells by n
    cell_list = [(cell, table[cell]) for cell in table if cell != "__baseline__"]
    cell_list.sort(key=lambda x: x[1]["n"], reverse=True)
    top_cells = cell_list[:10]
    
    return {
        "n_train": len(train),
        "n_test": n_test,
        "cells": top_cells,
        "cells_ge_min_n": cells_ge_min_n,
        "logloss_table": avg_logloss_table,
        "logloss_baseline": avg_logloss_baseline,
        "improvement": improvement
    }

def main():
    parser = ArgumentParser()
    parser.add_argument('--labels', default='runtime_data/outcome_labels.json')
    parser.add_argument('--horizon', default='60m')
    parser.add_argument('--band', type=float, default=0.2)
    args = parser.parse_args()
    
    # Load data
    records = load_labels(args.labels)
    
    # Chronologically split 70/30
    split_idx = int(len(records) * 0.7)
    train = records[:split_idx]
    test = records[split_idx:]
    
    # Evaluate
    result = evaluate(train, test, horizon=args.horizon, band=args.band)
    
    # Print results
    import json
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
