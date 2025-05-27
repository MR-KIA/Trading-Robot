import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from ..utils.initializations import get_heikin_ashi

def calculate_ut_bot_alerts(data, atr_period=10, key_value=2):
    data['atr'] = data['high'].rolling(window=atr_period).max() - data['low'].rolling(window=atr_period).min()
    data['nLoss'] = key_value * data['atr']
    
    data['xATRTrailingStop'] = np.nan
    data['pos'] = 0

    for i in range(1, len(data)):
        if data.loc[i, 'close'] > data.loc[i-1, 'xATRTrailingStop'] and data.loc[i-1, 'close'] > data.loc[i-1, 'xATRTrailingStop']:
            data.loc[i, 'xATRTrailingStop'] = max(data.loc[i-1, 'xATRTrailingStop'], data.loc[i, 'close'] - data.loc[i, 'nLoss'])
        elif data.loc[i, 'close'] < data.loc[i-1, 'xATRTrailingStop'] and data.loc[i-1, 'close'] < data.loc[i-1, 'xATRTrailingStop']:
            data.loc[i, 'xATRTrailingStop'] = min(data.loc[i-1, 'xATRTrailingStop'], data.loc[i, 'close'] + data.loc[i, 'nLoss'])
        else:
            data.loc[i, 'xATRTrailingStop'] = data.loc[i, 'close'] - data.loc[i, 'nLoss'] if data.loc[i, 'close'] > data.loc[i-1, 'xATRTrailingStop'] else data.loc[i, 'close'] + data.loc[i, 'nLoss']

        if data.loc[i-1, 'close'] < data.loc[i-1, 'xATRTrailingStop'] and data.loc[i, 'close'] > data.loc[i-1, 'xATRTrailingStop']:
            data.loc[i, 'pos'] = 1
        elif data.loc[i-1, 'close'] > data.loc[i-1, 'xATRTrailingStop'] and data.loc[i, 'close'] < data.loc[i-1, 'xATRTrailingStop']:
            data.loc[i, 'pos'] = -1
        else:
            data.loc[i, 'pos'] = data.loc[i-1, 'pos']

    data['buy'] = (data['close'] > data['xATRTrailingStop']) & (data['close'].shift(1) <= data['xATRTrailingStop'].shift(1))
    data['sell'] = (data['close'] < data['xATRTrailingStop']) & (data['close'].shift(1) >= data['xATRTrailingStop'].shift(1))

    return data
