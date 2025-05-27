import numpy as np
import pandas as pd

def one_sided_gaussian_filter(prices, smthtype='Kaufman', srcoption='close', smthper=10, extrasmthper=10, atrper=21, mult=0.628, kfl=0.666, ksl=0.0645, amafl=2, amasl=30):
    """
    One-Sided Gaussian Filter with Channels

    :param prices: pandas DataFrame containing OHLC data.
    :param smthtype: Type of smoothing ('AMA', 'T3', 'Kaufman').
    :param srcoption: Source price ('Close', 'Open', etc.).
    :param smthper: Gaussian Levels Depth.
    :param extrasmthper: Extra Smoothing (2-Pole Ehlers Super Smoother) Period.
    :param atrper: ATR Period.
    :param mult: ATR Multiplier.
    :param kfl: Kaufman's Adaptive MA - Fast End.
    :param ksl: Kaufman's Adaptive MA - Slow End.
    :param amafl: Adaptive Moving Average - Fast.
    :param amasl: Adaptive Moving Average - Slow.
    :return: DataFrame with the smoothed prices, signal line, and channels.
    """

    def gaussian(size, x):
        return np.exp(-x * x * 9 / ((size + 1) * (size + 1)))

    def calc_fib_levels(length):
        fib_levels = [0, 1]
        for i in range(2, length):
            fib_levels.append(fib_levels[-1] + fib_levels[-2])
        return fib_levels[:length]

    def gaussian_moving_average(level, src, per):
        fib_levels = calc_fib_levels(per)
        sum_values = 0
        for i in range(len(fib_levels)):
            if i >= per:
                break
            sum_values += gaussian(fib_levels[level], i) * src.shift(i)
        return sum_values

    def ehlers_2pole_supersmoother(src, length):
        a1 = np.exp(-1.414 * np.pi / length)
        b1 = 2 * a1 * np.cos(1.414 * np.pi / length)
        coef2 = b1
        coef3 = -a1 * a1
        coef1 = 1 - coef2 - coef3
        filt = coef1 * src + coef2 * src.shift(1) + coef3 * src.shift(2)
        return filt.fillna(src)

    def calculate_atr(high, low, close, period):
        tr = np.maximum(high - low, np.maximum(np.abs(high - close.shift(1)), np.abs(low - close.shift(1))))
        atr = tr.rolling(window=period, min_periods=1).mean()
        return atr
    if srcoption == 'close':
        src = prices['close']
    elif srcoption == 'open':
        src = prices['open']

    lmax = smthper + 1
    out1 = gaussian_moving_average(smthper, src, lmax)
    
    out = ehlers_2pole_supersmoother(out1, extrasmthper)
    sig = out.shift(1)

    atr = calculate_atr(prices['high'], prices['low'], prices['close'], atrper)

    smax = out + atr * mult
    smin = out - atr * mult

    go_long = (out > sig) & (out.shift(1) <= sig.shift(1))
    go_short = (out < sig) & (out.shift(1) >= sig.shift(1))

    result = pd.DataFrame({
        'Smoothed': out,
        'Signal': sig,
        'Smax': smax,
        'Smin': smin,
        'GoLong': go_long,
        'GoShort': go_short
    }, index=prices.index)

    return result