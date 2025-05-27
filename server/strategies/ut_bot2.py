import pandas as pd
import ta
import numpy as np
import matplotlib.pyplot as plt

def ut_bot_alerts(df, key_value=2, atr_period=10, heikin_ashi=False):
    # Function to calculate ATR Trailing Stop and signals
    def heikin_ashi_bars(df):
        ha_df = pd.DataFrame(index=df.index)
        ha_df['close'] = (df['open'] + df['high'] + df['low'] + df['close']) / 4
        ha_df['open'] = (df['open'].shift(1) + df['close'].shift(1)) / 2
        ha_df['high'] = df[['open', 'close', 'high']].max(axis=1)
        ha_df['low'] = df[['open', 'close', 'low']].min(axis=1)
        return ha_df

    # Use Heikin Ashi Candles if required
    if heikin_ashi:
        df = heikin_ashi_bars(df)

    # ATR calculation
    df['ATR'] = ta.volatility.AverageTrueRange(df['high'], df['low'], df['close'], window=atr_period).average_true_range()
    
    # Calculate nLoss
    df['nLoss'] = key_value * df['ATR']

    # Calculate ATR Trailing Stop
    df['xATRTrailingStop'] = 0.0
    for i in range(1, len(df)):
        if df['close'].iloc[i] > df['xATRTrailingStop'].iloc[i-1] and df['close'].iloc[i-1] > df['xATRTrailingStop'].iloc[i-1]:
            df['xATRTrailingStop'].iloc[i] = max(df['xATRTrailingStop'].iloc[i-1], df['close'].iloc[i] - df['nLoss'].iloc[i])
        elif df['close'].iloc[i] < df['xATRTrailingStop'].iloc[i-1] and df['close'].iloc[i-1] < df['xATRTrailingStop'].iloc[i-1]:
            df['xATRTrailingStop'].iloc[i] = min(df['xATRTrailingStop'].iloc[i-1], df['close'].iloc[i] + df['nLoss'].iloc[i])
        else:
            df['xATRTrailingStop'].iloc[i] = df['close'].iloc[i] - df['nLoss'].iloc[i] if df['close'].iloc[i] > df['xATRTrailingStop'].iloc[i-1] else df['close'].iloc[i] + df['nLoss'].iloc[i]

    # Position calculation
    df['pos'] = 0
    for i in range(1, len(df)):
        if df['close'].iloc[i-1] < df['xATRTrailingStop'].iloc[i-1] and df['close'].iloc[i] > df['xATRTrailingStop'].iloc[i-1]:
            df['pos'].iloc[i] = 1
        elif df['close'].iloc[i-1] > df['xATRTrailingStop'].iloc[i-1] and df['close'].iloc[i] < df['xATRTrailingStop'].iloc[i-1]:
            df['pos'].iloc[i] = -1
        else:
            df['pos'].iloc[i] = df['pos'].iloc[i-1]

    # Define colors for buy and sell signals
    df['color'] = np.where(df['pos'] == 1, 'green', np.where(df['pos'] == -1, 'red', 'blue'))

    # Exponential Moving Average (EMA)
    df['ema'] = ta.trend.EMAIndicator(df['close'], window=1).ema_indicator()

    # Buy and sell signals
    df['buy'] = (df['close'] > df['xATRTrailingStop']) & (df['ema'] > df['xATRTrailingStop'])
    df['sell'] = (df['close'] < df['xATRTrailingStop']) & (df['ema'] < df['xATRTrailingStop'])

    return df