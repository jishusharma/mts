"""Write T04_ambiguity_log.md. Markdown headings are assembled from chr(35) so no source line here starts with #."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path

H = chr(35)
OUT = Path(__file__).parent / "T04_ambiguity_log.md"

lines = [
    H*1 + " T04 ambiguity log (live; appended as each twin is written)",
    "",
    "Reading the PRE_REG for each study before any code, I noted every point where more than one reading was possible. Each entry: ambiguity, readings, decision (OURS).",
    "",
    H*2 + " mal_bb_mid_engulf_2026-10-16, arm A1",
    "",
    "1. **Entry timing.** PRE_REG section 3 says 'SHORT at the engulf-bar close' AND section 1 says 'fill at the open of the second following 1m bar (template d = 1)'. These conflict. Readings: (a) enter at engulf 5m close = open of the next 1m bar; (b) d=1 = 1-minute delay = open of the 1m bar 1 minute after the 5m close. DECISION (OURS): (b).",
    "2. **Exit timing.** Section 1 says 'fixed-horizon exit', no price rule. Readings: (a) close of the 60th 1m bar after entry; (b) open of the 61st. DECISION (OURS): (a), exit at close of 1m bar i_entry + 59.",
    "3. **Doji bars.** 'previous bar green, this bar red' with green = close > open, red = close < open. Doji (close == open) is neither. DECISION (OURS): doji prev breaks engulf; doji signal is not a red.",
    "4. **Engulf strictness.** 'close below the previous green open' - strict < or <=? DECISION (OURS): strict <.",
    "5. **Cooldown scope.** '60-minute cooldown between events within each set'. Readings: (a) separate cooldown for A1 and CTL_A1; (b) shared. DECISION (OURS): (a).",
    "6. **HTF last-closed indexing.** At a 5m close that coincides with a 1h close, is the 1h bar considered closed? DECISION (OURS): yes, use close_time <= 5m_close_time.",
    "7. **net taker delta over the last 6 bars.** Sum of (2*tbv - v) over 5m bars [i-5 .. i]. DECISION (OURS).",
    "8. **BB population SD.** '2 population SD' - ddof=0. DECISION (OURS): np.std with ddof=0.",
    "9. **Bounce touch.** 'high of one of last 3 bars >= that bar own BB mid'. Strict >=. DECISION (OURS).",
    "10. **A2 entry.** 'SHORT at that next bar close' + d=1. DECISION (OURS): entry at open of 1m bar 1 min after the (i+1)th 5m bar close.",
    "11. **CTL_A2 timing.** 'entered at the same bar close (same elapsed time)' - DECISION (OURS): CTL_A2 enters at offset 1 like A2, from A1 events without second break.",
    "12. **COUNT.md sample sizes.** A1 n=1,179, CTL_A1 n=2,486, A2 n=807 in COUNT.md; CTL_A2 not stated. DECISION (OURS): CTL_A2 = A1 events without second break, count printed by twin.",
    "13. **Dedup.** No rule. DECISION (OURS): drop_duplicates on 1m open_time.",
    "",
    H*2 + " opr_weekly_low_round_sweep_2026-10-16, arm RL",
    "",
    "(To be filled when that twin is written.)",
]

OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"wrote {OUT}")
