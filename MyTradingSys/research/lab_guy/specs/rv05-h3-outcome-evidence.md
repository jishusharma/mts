# Lab_Guy spec detail for card rv05-h3-outcome-evidence (2026-10-18, labguy-pass-b)

Full text of the items the card shortens (card item limit 400 chars). The card is the contract; this file is the detail.

## steps item 1

baseline (already repaired by fabio-ledger-f13-outcome-provenance-2910 / AUDIT H2): CSV file line 51 (F13-x) has exit price '-', cause INFERRED/UNKNOWN and -2910 vs the -1760 label, but the difference 1150 is written nowhere (grep 1150 in the CSV and .md finds nothing). Re-check by hand: 20668 - 17758 = 2910, 2910 - 1760 = 1150; frame DyS79Eb92Ug_w10_00 t=3525/3550/3575; caption F:/MTS/data/fabio_videos/DyS79Eb92Ug.txt lines 1455-1457 (17,758)

## steps item 2

add to the F13-x CSV note and the .md F13 paragraph: unexplained difference 1150 USD = NOT_IN_DATA (not slippage, not cost, not a discretionary fill: none is proven); exit price cell stays '-'; if rv05-h2 changed F13 or F13-m1 entry or the 8-covered vs 10-open reading, restate the -1760 label denominator with h2's convention

## steps item 3

no cost, slippage or fill price is assumed anywhere
