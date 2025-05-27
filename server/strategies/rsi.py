import pandas as pd
import numpy as np
import statistics
from server.utils.initializations import candle 


def rsi_divergence_indicator(close_prices, rsi_period=14, pivot_lookback_right=5, pivot_lookback_left=5, max_lookback_range=60, min_lookback_range=5):
    # Calculate RSI
    delta = close_prices.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.ewm(span=rsi_period, min_periods=rsi_period).mean()
    avg_loss = loss.ewm(span=rsi_period, min_periods=rsi_period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    # Initialize divergence signals
    regular_bullish_divergence = np.zeros_like(close_prices)
    hidden_bullish_divergence = np.zeros_like(close_prices)
    regular_bearish_divergence = np.zeros_like(close_prices)
    hidden_bearish_divergence = np.zeros_like(close_prices)
    
    # Pivot points
    def find_pivot_lows(series, left, right):
        pivots = series[(series.shift(-left) > series) & (series.shift(right) > series)]
        return pivots
    
    def find_pivot_highs(series, left, right):
        pivots = series[(series.shift(-left) < series) & (series.shift(right) < series)]
        return pivots
    
    pivot_lows = find_pivot_lows(rsi, pivot_lookback_left, pivot_lookback_right)
    pivot_highs = find_pivot_highs(rsi, pivot_lookback_left, pivot_lookback_right)
    
    # Function to check if a condition is within specified range
    def in_range(condition):
        bars_since = (condition == True).cumsum()
        return (bars_since >= min_lookback_range) & (bars_since <= max_lookback_range)
    
    # Regular Bullish Divergence
    osc_hl = (rsi.shift(-pivot_lookback_right) > pivot_lows.shift(1)) & in_range(pivot_lows)
    price_ll = (close_prices.shift(-pivot_lookback_right) < close_prices.shift(1)) & in_range(pivot_lows)
    regular_bullish_divergence = pivot_lows.shift(-pivot_lookback_right) if osc_hl & price_ll else np.nan
    
    # Hidden Bullish Divergence
    osc_ll = (rsi.shift(-pivot_lookback_right) < pivot_lows.shift(1)) & in_range(pivot_lows)
    price_hl = (close_prices.shift(-pivot_lookback_right) > close_prices.shift(1)) & in_range(pivot_lows)
    hidden_bullish_divergence = pivot_lows.shift(-pivot_lookback_right) if osc_ll & price_hl else np.nan
    
    # Regular Bearish Divergence
    osc_lh = (rsi.shift(-pivot_lookback_right) < pivot_highs.shift(1)) & in_range(pivot_highs)
    price_hh = (close_prices.shift(-pivot_lookback_right) > close_prices.shift(1)) & in_range(pivot_highs)
    regular_bearish_divergence = pivot_highs.shift(-pivot_lookback_right) if osc_lh & price_hh else np.nan
    
    # Hidden Bearish Divergence
    osc_hh = (rsi.shift(-pivot_lookback_right) > pivot_highs.shift(1)) & in_range(pivot_highs)
    price_lh = (close_prices.shift(-pivot_lookback_right) < close_prices.shift(1)) & in_range(pivot_highs)
    hidden_bearish_divergence = pivot_highs.shift(-pivot_lookback_right) if osc_hh & price_lh else np.nan
    
    return {
        'Regular Bullish Divergence': regular_bullish_divergence,
        'Hidden Bullish Divergence': hidden_bullish_divergence,
        'Regular Bearish Divergence': regular_bearish_divergence,
        'Hidden Bearish Divergence': hidden_bearish_divergence
    }


def rsi(signal, timeframe = '15m', symbol = 'GBPUSD'):
            
    ohlc = candle(timeframe, limit=50, symbol=symbol)
    if timeframe == "1h":
        kandle = 10
    elif timeframe == "4h":
        kandle = 8
    elif timeframe == "1d":
        kandle = 10
    elif timeframe == "1w":
        kandle = 10
    elif timeframe == "30m":
        kandle = 10
    elif timeframe == "15m":
        kandle = 15
    elif timeframe == "5m":
        kandle = 14
    elif timeframe == "3m":
        kandle = 14
    elif timeframe == "1m":
        kandle = 14

    profit = []
    loss = []
    
    for i in range(len(ohlc)-1, len(ohlc)-61, -1):
        if i < 0:
            break
        
        if ohlc.iloc[i]['open'] > ohlc.iloc[i]['close']:
            if len(loss) < kandle:
                loss.append(ohlc.iloc[i]['open'] - ohlc.iloc[i]['close'])
        else:
            if len(profit) < kandle:
                profit.append(ohlc.iloc[i]['close'] - ohlc.iloc[i]['open'])
    
    if not profit or not loss:
        return False  

    profitAvg = statistics.mean(profit)
    lossAvg = statistics.mean(loss)
    RS = profitAvg / lossAvg
    RSI = 100 - (100 / (1 + RS))

    if (RSI <= 35 and signal == "buy") or (RSI >= 65 and signal == "sell"):
        return True
    else:
        return False