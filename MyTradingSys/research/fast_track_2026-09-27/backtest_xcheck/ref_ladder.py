def fill_ladder(side, rungs, bars, signal_t, deadline_bars, stop=None):
    filled = []
    unfilled = rungs[:]
    filled_size = 0
    total_value = 0.0
    first_fill_t = None
    last_fill_t = None
    stopped_during_entry = False

    # Scan bars after the signal bar, up to deadline_bars
    scan_bars = [b for b in bars if b['t'] > signal_t]
    scan_bars = scan_bars[:deadline_bars]

    for bar in scan_bars:
        t = bar['t']
        open_p = bar['o']
        high = bar['h']
        low = bar['l']

        # Check if stop is hit; same-bar rung fills still count (spec: filled, then stopped),
        # so the break happens after this bar's rungs are processed
        stop_hit = stop is not None and ((side == 'long' and low <= stop) or (side == 'short' and high >= stop))

        # Process rungs for this bar
        new_unfilled = []
        for price, size in unfilled:
            fill_price = None
            if side == 'long':
                if low <= price:
                    if open_p <= price:
                        fill_price = open_p
                    else:
                        fill_price = price
            elif side == 'short':
                if high >= price:
                    if open_p >= price:
                        fill_price = open_p
                    else:
                        fill_price = price

            if fill_price is not None:
                filled.append((t, fill_price, size))
                filled_size += size
                total_value += fill_price * size
                if first_fill_t is None:
                    first_fill_t = t
                last_fill_t = t
            else:
                new_unfilled.append((price, size))

        unfilled = new_unfilled
        if stop_hit:
            stopped_during_entry = True
            break

    avg_price = total_value / filled_size if filled_size > 0 else None

    return {
        'filled': filled,
        'filled_size': filled_size,
        'avg_price': avg_price,
        'first_fill_t': first_fill_t,
        'last_fill_t': last_fill_t,
        'unfilled': unfilled,
        'stopped_during_entry': stopped_during_entry
    }
