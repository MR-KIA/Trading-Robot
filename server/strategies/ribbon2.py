import pandas as pd
import numpy as np

def moving_average(source, length, ma_type="SMA",volume=None):
    if ma_type == "SMA":
        return source.rolling(window=length).mean()
    elif ma_type == "EMA":
        return source.ewm(span=length, adjust=False).mean()
    elif ma_type == "SMMA (RMA)":
        return source.ewm(alpha=1/length, adjust=False).mean()
    elif ma_type == "WMA":
        weights = np.arange(1, length + 1)
        return source.rolling(window=length).apply(lambda prices: np.dot(prices, weights)/weights.sum(), raw=True)
    elif ma_type == "VWMA":
        # Assuming 'volume' is part of the input data
        return (source * volume).rolling(window=length).sum() / volume.rolling(window=length).sum()
    else:
        return pd.Series([np.nan] * len(source))

def moving_average_ribbon2(df, show_ma1=True, ma1_type="EMA", ma1_length=20, ma1_color="#f6c309",
                          show_ma2=True, ma2_type="EMA", ma2_length=20, ma2_color="#fb9800",
                          show_ma3=True, ma3_type="EMA", ma3_length=200, ma3_color="#fb6500",
                          show_ma4=True, ma4_type="EMA", ma4_length=1, ma4_color="#f60c0c"):
    
    # MA1 Calculation
    if show_ma1:
        df['MA1'] = moving_average(df['close'], ma1_length, ma1_type)
    else:
        df['MA1'] = np.nan
    
    # MA2 Calculation
    if show_ma2:
        df['MA2'] = moving_average(df['close'], ma2_length, ma2_type)
    else:
        df['MA2'] = np.nan
    
    # MA3 Calculation
    if show_ma3:
        df['MA3'] = moving_average(df['close'], ma3_length, ma3_type)
    else:
        df['MA3'] = np.nan
    
    # MA4 Calculation
    if show_ma4:
        df['MA4'] = moving_average(df['close'], ma4_length, ma4_type)
    else:
        df['MA4'] = np.nan
    
    return df

# Example usage:
# Assuming df is your DataFrame containing 'close' prices and 'volume' if using VWMA
# df = moving_average_ribbon(df)
