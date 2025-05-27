import pandas as pd
import numpy as np

def sma(source, length):
    return source.rolling(window=length).mean()

def ema(source, length):
    return source.ewm(span=length, adjust=False).mean()

def rma(source, length):
    alpha = 1 / length
    return source.ewm(alpha=alpha, adjust=False).mean()

def wma(source, length):
    weights = pd.Series(range(1, length+1))
    return source.rolling(window=length).apply(lambda prices: np.dot(prices, weights) / weights.sum(), raw=True)

def vwma(source, volume, length):
    return (source * volume).rolling(window=length).sum() / volume.rolling(window=length).sum()

def ma(source, length, ma_type, volume=None):
    if ma_type == "SMA":
        return sma(source, length)
    elif ma_type == "EMA":
        return ema(source, length)
    elif ma_type == "SMMA (RMA)":
        return rma(source, length)
    elif ma_type == "WMA":
        return wma(source, length)
    elif ma_type == "VWMA":
        return vwma(source, volume, length)
    else:
        raise ValueError(f"Unsupported MA type: {ma_type}")


def apply_ma_ribbon(data, volume=None):

    ma1 = ma(data['high'], 20, "EMA")
    ma2 = ma(data['low'], 20, "EMA")
    ma3 = ma(data['close'], 200, "EMA")

    data['MA1'] = ma1
    data['MA2'] = ma2
    data['MA3'] = ma3

    return data