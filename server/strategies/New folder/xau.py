import numpy as np
import pandas as pd

class TrendlineBreakoutSignals:
    def __init__(self, period=20, extension='25', trend_type='Wicks'):
        self.period = period
        self.extension = extension
        self.trend_type = trend_type
        self.extension_map = {'25': 1, '50': 2, '75': 3}

    def pivot_high(self, data, left, right):
        ph = [False] * len(data)
        for i in range(left, len(data) - right):
            window = data[i-left:i+right+1]
            if data[i] == max(window):
                ph[i] = True
        return np.array(ph)

    def pivot_low(self, data, left, right):
        pl = [False] * len(data)
        for i in range(left, len(data) - right):
            window = data[i-left:i+right+1]
            if data[i] == min(window):
                pl[i] = True
        return np.array(pl)

    def atr(self, high, low, close, length):
        tr = np.maximum(high[1:], close[:-1]) - np.minimum(low[1:], close[:-1])
        tr = np.insert(tr, 0, high[0] - low[0])
        atr = pd.Series(tr).ewm(alpha=1/length, adjust=False).mean().values
        return atr

    def vol_adj(self, atr_val, close_val):
        return min(atr_val * 0.3, close_val * 0.003) / 2

    def get_line_price(self, start_time, start_price, slope, elapsed):
        return start_price + elapsed * slope

    def generate_signals(self, df):
        bar_times = df['time'].values
        high = df['high'].values
        low = df['low'].values
        close = df['close'].values
        open_ = df['open'].values

        if self.trend_type == 'Wicks':
            ph_src = high
            pl_src = low
        else:
            ph_src = np.where(close > open_, close, open_)
            pl_src = np.where(close > open_, open_, close)

        ph = self.pivot_high(ph_src, self.period, self.period // 2)
        pl = self.pivot_low(pl_src, self.period, self.period // 2)

        atr_vals = self.atr(high, low, close, 30)
        zband = self.vol_adj(atr_vals[-1], close[-1])
        ex_factor = self.extension_map.get(self.extension.strip(), 1)

        high_pivots_idx = np.where(ph)[0]
        low_pivots_idx = np.where(pl)[0]

        if len(high_pivots_idx) < 2 or len(low_pivots_idx) < 2:
            return []

        x1_h = bar_times[high_pivots_idx[-2]]
        y1_h = ph_src[high_pivots_idx[-2]]
        x2_h = bar_times[high_pivots_idx[-1]]
        y2_h = ph_src[high_pivots_idx[-1]]
        slope_h = (y2_h - y1_h) / (x2_h - x1_h)

        x1_l = bar_times[low_pivots_idx[-2]]
        y1_l = pl_src[low_pivots_idx[-2]]
        x2_l = bar_times[low_pivots_idx[-1]]
        y2_l = pl_src[low_pivots_idx[-1]]
        slope_l = (y2_l - y1_l) / (x2_l - x1_l)

        last_time = bar_times[-1]
        last_time_prev = bar_times[-2]
        last_close = close[-1]
        prev_close = close[-2]

        def line_price_at(t, start_t, start_p, slope):
            return start_p + (t - start_t) * slope

        line_price_high_now = line_price_at(last_time, x1_h, y1_h, slope_h)
        line_price_high_prev = line_price_at(last_time_prev, x1_h, y1_h, slope_h)
        long_signal = (prev_close < line_price_high_prev) and (last_close > line_price_high_now)

        line_price_low_now = line_price_at(last_time, x1_l, y1_l, slope_l)
        line_price_low_prev = line_price_at(last_time_prev, x1_l, y1_l, slope_l)
        short_signal = (prev_close > line_price_low_prev) and (last_close < line_price_low_now)

        target_long = high[-1] + zband * 20
        stop_long = low[-1] - zband * 20
        target_short = low[-1] - zband * 20
        stop_short = high[-1] + zband * 20

        trades = []

        if long_signal:
            trades.append({
                'type': 'LONG',
                'entry_time': last_time,
                'entry_price': last_close,
                'target': target_long,
                'stop': stop_long
            })

        if short_signal:
            trades.append({
                'type': 'SHORT',
                'entry_time': last_time,
                'entry_price': last_close,
                'target': target_short,
                'stop': stop_short
            })

        return trades
