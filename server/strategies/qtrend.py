import numpy as np

def q_trend(src, p=200, atr_p=14, mult=1.0, mode="Type A", use_ema_smoother=False, src_ema_period=3):
    src = np.array(src)
    
    if use_ema_smoother:
        src = ema(src, src_ema_period)
    
    h = highest(src, p)
    l = lowest(src, p)
    d = h - l

    atr = calculate_atr(src, atr_p)

    m = (h + l) / 2

    epsilon = mult * atr

    if mode == "Type B":
        change_up = cross(src, m + epsilon)
        change_down = cross(src, m - epsilon)
    else:
        change_up = crossover(src, m + epsilon)
        change_down = crossunder(src, m - epsilon)

    ls = ""
    if change_up.any():  # Use .any() to check if any element is True
        ls = "B"
    elif change_down.any():  # Use .any() to check if any element is True
        ls = "S"
    
    if change_up.any() or change_down.any():  # Use .any() to check if any element is True
        m = m + epsilon if change_up.any() else m - epsilon
    
    return {
        "trend_line": m,
        "last_signal": ls,
        "buy_signal": change_up,
        "sell_signal": change_down
    }


# Helper functions
def ema(src, period):
    return np.convolve(src, np.ones(period)/period, mode='valid')

def highest(src, period):
    return np.array([max(src[max(0, i-period+1):i+1]) for i in range(len(src))])

def lowest(src, period):
    return np.array([min(src[max(0, i-period+1):i+1]) for i in range(len(src))])

def calculate_atr(src, period):
    tr = np.zeros(len(src))
    for i in range(1, len(src)):
        high = src[i]
        low = src[i]
        prev_close = src[i-1]
        tr[i] = max(high - low, abs(high - prev_close), abs(low - prev_close))
    atr = np.convolve(tr, np.ones(period)/period, mode='valid')
    return np.pad(atr, (len(src) - len(atr), 0), 'constant')

def crossover(src, level):
    return np.array([(src[i-1] < level[i-1]) and (src[i] >= level[i]) for i in range(1, len(src))])

def crossunder(src, level):
    return np.array([(src[i-1] > level[i-1]) and (src[i] <= level[i]) for i in range(1, len(src))])

def cross(src, level):
    return np.array([(src[i-1] < level[i] and src[i] >= level[i]) or (src[i-1] > level[i] and src[i] <= level[i]) for i in range(1, len(src))])
