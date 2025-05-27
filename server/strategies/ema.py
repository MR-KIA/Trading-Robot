from server.utils.initializations import candle  


def ema20(timeframe,symbol):
    prices = []
    ohlc = candle(timeframe , limit=20 , symbol = symbol)
    i = -1
    for n in range(20) :
        prices.append((ohlc[i]['close']) )
        i -= 1

    if len(prices) < 20:
        return False
    
    sma = sum(prices[:20]) / 20
    
    k = 2 / (20 + 1)

    ema = sma

    for price in prices[20:]:
        ema = (price - ema) * k + ema
    
    return ema

def ema50(timeframe,symbol):
    prices = []
    ohlc = candle(timeframe , limit=50 , symbol = symbol)
    i = -1
    for n in range(50) :
        prices.append((ohlc[i]['close']) )
        i -= 1

    if len(prices) < 50:
        return False
    
    sma = sum(prices[:50]) / 50
    
    k = 2 / (50 + 1)

    ema = sma

    for price in prices[50:]:
        ema = (price - ema) * k + ema
    
    return ema

def ema100(timeframe,symbol):
    prices = []
    ohlc = candle(timeframe , limit=100 , symbol = symbol)
    i = -1
    for n in range(100) :
        prices.append((ohlc[i]['close']) )
        i -= 1

    if len(prices) < 100:
        return False
    
    sma = sum(prices[:100]) / 100
    
    k = 2 / (100 + 1)

    ema = sma

    for price in prices[100:]:
        ema = (price - ema) * k + ema
    
    return ema

def ema200(timeframe,symbol):
    prices = []
    ohlc = candle(timeframe , limit=200 , symbol = symbol)
    i = -1
    for n in range(200) :
        prices.append((ohlc[i]['close']) )
        i -= 1

    if len(prices) < 200:
        return False
    
    sma = sum(prices[:200]) / 200
    
    k = 2 / (200 + 1)

    ema = sma

    for price in prices[200:]:
        ema = (price - ema) * k + ema
    
    return ema

def ema(timeframe, window , symbol):
    prices = []
    ohlc = candle(timeframe , limit=window , symbol = symbol)
    i = -1
    for n in range(window) :
        prices.append((ohlc[i]['close']) )
        i -= 1

    if len(prices) < window:
        return False
    
    sma = sum(prices[:window]) / window
    
    k = 2 / (window + 1)

    ema = sma

    for price in prices[window:]:
        ema = (price - ema) * k + ema
    
    return ema
