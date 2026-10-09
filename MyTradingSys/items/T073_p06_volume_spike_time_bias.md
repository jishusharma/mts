# T073 - P06 volume-spike proof: time-of-day bias and NO-SOURCE status

Opened 2026-10-09 by MTS-2026-10-09-APP-ANA-btc-volume. Status QUEUED, supervisor deploy window only (Java, live path). Source: VOLUME_RESEARCH_REPORT_2026-10-09.md section 5 A3; T5_CVD_DEFINITION_2026-10-01.md finding 2.

## Finding
P06 (SetupCandidatesBuilder.java:804-816) counts a proof point when the last 1m volume is > 2.0x the mean of the previous 240 one-minute bars with close within 0.1% of the spike level. Tom's words give "exhaustion seen with a volume spike" and no threshold (PROVENANCE_AUDIT_TOM P06, verdict TOM-CONCEPT-ONLY), so 2.0x / 240 / 0.1% are engineering choices.
The 4-hour baseline is shorter than BTC's daily volume cycle. 1h analog on DEV (v >= 2x the mean of the previous 4 hours): 21% of the hours at 13-14 UTC, 14% at 00 UTC, 4% at 04 UTC, 6-7% at 17-21 UTC; with a same-hour median baseline the share is 14-19% at every hour. So the proof point is partly a clock: it fires most at the US open.
BTC volume spikes carry no tested directional information (V1, 4h and 1d, no pass), only a larger next-bar range (V0).

## Do
1. Replay P06 hits by UTC hour on the 1m archive (1m not yet downloaded: needs operator approval, 250-400 MB) to confirm the 1m figure; the 1h analog is only an indication.
2. Decide with the supervisor: keep as a labelled NO-SOURCE proof point, give it a same-slot baseline, or drop it from the proof count. Nothing changes without the Java restart window.
3. Update B063 / T5: no CVD-divergence or volume-spike rule has edge on 4h or 1d (volume_2026-10-09 V1).
