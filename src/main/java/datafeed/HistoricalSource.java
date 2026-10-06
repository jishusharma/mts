package datafeed;

import com.fasterxml.jackson.databind.JsonNode;

import java.io.IOException;

/**
 * Source of historical klines for the as-of (historical) snapshot path only.
 * Returns the Binance /fapi/v1/klines shape: a JSON array of arrays
 * [openTime, open, high, low, close, volume, closeTime, quoteVolume, count, takerBuyBase, takerBuyQuote, ignore].
 * BinanceClient is the default (REST) implementation; ArchiveHistoricalSource serves the local 1m archive.
 */
public interface HistoricalSource {
    JsonNode klinesRange(String symbol, String interval, long startMs, long endMs, int limit) throws IOException;
}
