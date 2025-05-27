from server.utils.initializations import candle
import statistics


def average26(timeframe , symbol ='BTCUSD.'):
        
    ohlc = candle(timeframe , limit=26 , symbol = symbol)
    average = statistics.mean(item['low'] for item in ohlc)
    return average


def average12(timeframe , symbol ='BTCUSD.'):
        
    ohlc = candle(timeframe , limit=12 , symbol = symbol)
    average = statistics.mean(item['close'] for item in ohlc)
    return average


def average50(timeframe , symbol ='BTCUSD.'):
        
    ohlc = candle(timeframe , limit=50 , symbol = symbol)
    average = statistics.mean(item['close'] for item in ohlc)
    return average


def average60(timeframe , symbol ='BTCUSD.'):
        
    ohlc = candle(timeframe , limit=60 , symbol = symbol)
    average = statistics.mean(item['close'] for item in ohlc)
    return average


def average162(timeframe , symbol ='BTCUSD.'):
        
    ohlc = candle(timeframe , limit=162 , symbol = symbol)
    average = statistics.mean(item['close'] for item in ohlc)
    return average


def average100(timeframe , symbol ='BTCUSD.'):
        
    ohlc = candle(timeframe , limit=100 , symbol = symbol)
    average = statistics.mean(item['close'] for item in ohlc)
    return average


def average200(timeframe , symbol ='BTCUSD.'):
        
    ohlc = candle(timeframe , limit=200 , symbol = symbol)
    average = statistics.mean(item['close'] for item in ohlc)
    return average