"""T9 counting step: signal and unit counts only (no exit path, no return, no outcome). Prints numbers for PRE_REG."""
import sys
import json
import pathlib
import numpy as np

sys.dont_write_bytecode = True
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import t9_core as core  # noqa: E402
import t9_stats as st  # noqa: E402

WAVE2 = r"F:/MTS/data_cache/binance/wave2-1114"
MINER = r"F:/MTS/data_cache/binance/combo-edge-miner-1114"
PHASE = r"F:/MTS/data_cache/mts_brains/phase_daily.csv"


def main():
    cls = core.set_low_priority()
    print("priority class 0x%x (0x4000 = BELOW_NORMAL)" % (cls or 0))
    slot = core.acquire_slot("t9-count")
    try:
        state = core.load_btc_state(PHASE)
        uni = core.universe(WAVE2, MINER)
        sigs, flagged_weeks, alive_by_week, kept = [], {}, {}, []
        for name, (sp, fp) in uni.items():
            c = core.load_coin(sp, name)
            if c.nw <= core.FIRST_FLAG_WEEK:
                continue
            kept.append(name)
            sigs.extend(core.signals(c, state))
            for w in range(core.FIRST_FLAG_WEEK, c.nw - 1):
                ms = int(c.ms[7 * (w + 1)])
                wk = st.week_index(ms)
                if c.flag[w] and not c.dd20[w] and state.get(core.day_str(ms)) in ("BULL", "BASE"):
                    flagged_weeks.setdefault(wk, set()).add(name)
            for d in range(core.ALIVE_DAYS, c.n, 7):
                alive_by_week[st.week_index(int(c.ms[d]) // 1)] = alive_by_week.get(st.week_index(int(c.ms[d])), 0) + 1
        out = dict(universe=len(uni), coins_with_flag_defined=len(kept))
        for sp in ("DEV", "VAL"):
            s = [x for x in sigs if x["split"] == sp]
            wk = sorted({st.week_index(x["entry_ms"]) for x in s})
            blocks = len({(w - wk[0]) // 4 for w in wk}) if wk else 0
            alive_ok = sum(1 for x in s if alive_by_week.get(st.week_index(x["entry_ms"]), 0) >= core.MIN_ALIVE_COINS)
            out[sp] = dict(signals=len(s), entry_weeks=len(wk), blocks4=blocks, signals_on_dates_with_30_alive=alive_ok,
                           mean_fee_R=float(np.mean([core.FEE_RT / x["risk"] for x in s])) if s else None,
                           median_stop_pct=float(np.median([x["risk"] for x in s])) if s else None,
                           by_state={k: sum(1 for x in s if x["btc_state"] == k) for k in ("BULL", "BASE")},
                           weeks_with_ge5_flagged=sum(1 for w, v in flagged_weeks.items()
                                                      if len(v) >= 5 and (core.DEV_END_MS <= (w * 7 - 3) * core.DAY) == (sp == "VAL")))
        print(json.dumps(out, indent=1))
        (pathlib.Path(__file__).resolve().parent / "counts.json").write_text(json.dumps(out, indent=1))
    finally:
        core.release_slot(slot)


if __name__ == "__main__":
    main()
