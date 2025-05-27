from server.utils.initializations import candle
import MetaTrader5 as mt5
import time
from datetime import datetime


def whatcandle(timeframe = '30m' , candle = -1 , symbol ='BTCUSD.'):
    ohlc = candle(timeframe , limit=10 , symbol = symbol)
    if ohlc[candle]['open'] > ohlc[candle]['close']:
        return 'short'
    else:
        return 'long'
    

def isBeta(timeframe , candel , symbol ='BTCUSD.' , m = 50):
    candles = candle(timeframe , limit=10 , symbol = symbol)
    res = candles[candel]
    if res['open'] > res['close']:
        # short candle
        if res['open'] == res['high'] and (res['close'] - res['low']) <= res['open'] - res['close'] and body(timeframe , candel ,symbol ) >= m :
            return True
        else:
            return False
    elif res['open'] < res['close']:
        # long candle
        if res['open'] == res['low']  and (res['high'] - res['close']) <= res['close'] - res['open'] and body(timeframe , candel ,symbol ) >= m :
            return True
        else:
            return False
    else:
        return False
    



def isBack(timeframe , candel , upOrDown , symbol ='BTCUSD.'):
    candles = candle(timeframe , limit=10 , symbol = symbol)
    res = candles[candel]
    if res['open'] > res['close']:
        # short candle
        if upOrDown == 'up'and (res['open'] - res['close'])*3 < res['high'] - res['open'] and (res['close'] - res['low']) * 3 <= res['high'] - res['open'] :
            return True
        
        elif upOrDown == 'down'and (res['open'] - res['close'])*4 < res['close'] - res['low'] and (res['high'] - res['open'])*3 <= res['close'] - res['low'] :
            return True
        else:
            return False
        
    elif res['open'] < res['close']:
        # long candle
        if upOrDown == 'up'and (res['close'] - res['open'])*4 < res['high'] - res['close'] and res['high'] - res['close'] > (res['open'] - res['low'])*3 :
            return True
        
        elif upOrDown == 'down'and (res['close'] - res['open'])*3 < res['open'] - res['low'] and (res['high'] - res['close'])*3 < res['open'] - res['low']:
            return True
        
        else:
            return False
    else:
        return False



def body(timeframe , candel , symbol ='BTCUSD.'):
    candles = candle(timeframe , limit=10 , symbol = symbol)
    res = candles[candel]
    if res['open'] > res['close']:
        # short candle
        body = res['open'] - res['close']
        return body
        
    elif res['open'] < res['close']:
        # long candle
        body = res['close'] - res['open']
        return body
    else:
        return 0


def support(symbol):
    candled = candle('1d' , 5 , symbol )
    candlew = candle('1w' , 5 , symbol )
    kande4h = candle('4h' , 5 , symbol )
    kande1h = candle('1h' , 5 , symbol )
    lines = [candled[-2]['high'] , candled[-2]['low'] , candlew[-1]['high'] , candlew[-1]['low'] , candlew[-2]['high'] , candlew[-2]['low'] , kande4h[-2]['high'] , kande4h[-2]['low'] , kande1h[-2]['high'] , kande1h[-2]['low']]
    price = mt5.symbol_info_tick(symbol).ask
    line = []
    for i in lines:
        if i < price:
            line.append(i)
    if len(line) == 0:
        return False
    else:
        return max(line)
        

def resistance(symbol):
    candled = candle('1d' , 5 , symbol )
    candlew = candle('1w' , 5 , symbol )
    kande4h = candle('4h' , 5 , symbol )
    kande1h = candle('1h' , 5 , symbol )
    lines = [candled[-2]['high'] , candled[-2]['low'] , candlew[-1]['high'] , candlew[-1]['low'] , candlew[-2]['high'] , candlew[-2]['low'] , kande4h[-2]['high'] , kande4h[-2]['low'] , kande1h[-2]['high'] , kande1h[-2]['low']]
    price = mt5.symbol_info_tick(symbol).ask
    line = []
    for i in lines:
        if i > price:
            line.append(i)
    if len(line) == 0:
        return False
    else:
        return min(line)
        
def check_pullback(connection, symbol, timeframe, period):
    if not connection.is_connected():
        print("Reconnecting to MetaTrader terminal...")
        connection.reconnect()

    try:
        period = int(period)
    except ValueError:
        print(f"Invalid period value: {period}")
        return False

    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, period)
    if rates is None or len(rates) < 3:
        return False

    last_candle = rates[-1]
    previous_candle = rates[-2]
    before_previous_candle = rates[-3]

    if previous_candle['close'] < previous_candle['open'] and last_candle['close'] > last_candle['open']:
        if before_previous_candle['close'] > before_previous_candle['open']:
            return True
    return False


def monitor_pullbacks(connection, symbol, timeframe, period, fr, rg):
    if not connection.is_connected():
        connection.reconnect()
    
    try:
        fr = int(fr)
        rg = int(rg)
    except ValueError:
        print(f"Invalid values for fr or rg: fr={fr}, rg={rg}")
        return False

    for i in range(rg):
        pullback = check_pullback(connection, symbol, timeframe, period)
        if pullback:
            return True
        time.sleep(fr)
    return False


def wait_for_next_candle(timeframe):
    """
    Waits until the start of the next candle based on the given timeframe.
    
    Args:
    timeframe (str): The timeframe string (e.g., '5m' for 5 minutes, '1h' for 1 hour)
    
    Returns:
    bool: True when the next candle starts.
    """

    unit = timeframe[-1]
    amount = int(timeframe[:-1])

    if unit == 'm':
        timeframe_seconds = amount * 60  
    elif unit == 'h':
        timeframe_seconds = amount * 3600  
    else:
        raise ValueError("Invalid timeframe format. Use 'm' for minutes or 'h' for hours.")
    
    now = datetime.utcnow()
    
    seconds_since_last_candle = now.timestamp() % timeframe_seconds
    seconds_until_next_candle = timeframe_seconds - seconds_since_last_candle
    
    time.sleep(seconds_until_next_candle)