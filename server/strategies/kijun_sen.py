from server.utils.initializations import candle 

def kijun_sen(symbol ,timeframe ,num):
    kandels = candle(timeframe =timeframe , limit=num , symbol = symbol)
    high = []
    low = []
    i = -1
    for n in range(num) :
        high.append(kandels[i]['high'])
        low.append(kandels[i]['low'])
        i -= 1
    mini = min(low)
    maxi = max(high)
    sen = (maxi + mini ) / 2 
    return sen



def kijun_sen_befor(symbol ,timeframe ,num):
    x = num + 2
    kandels = candle(timeframe =timeframe , limit=x , symbol = symbol)
    high = []
    low = []
    i = -3
    for n in range(num) :
        high.append(kandels[i]['high'])
        low.append(kandels[i]['low'])
        i -= 1
    mini = min(low)
    maxi = max(high)
    sen = (maxi + mini ) / 2 
    return sen