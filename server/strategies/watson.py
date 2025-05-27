import numpy as np
import pandas as pd

def gaussian_window(x, h):
    return np.exp(-((x ** 2) / (h ** 2 * 2)))

def nadaraya_watson_envelope(df, bandwidth=8.0, multiplier=4.5, repaint=True):
    df = df.drop(df.index[-1])
    src = df['close'].values
    n = len(src)

    upper = np.full(n, np.nan)
    lower = np.full(n, np.nan)

    if repaint:
        nwe = np.zeros(n)
        sae = 0.0

        for i in range(n):
            sum_w = 0.0
            sum_src_w = 0.0

            for j in range(n):
                w = gaussian_window(i - j, bandwidth)
                sum_src_w += src[j] * w
                sum_w += w

            y = sum_src_w / sum_w
            sae += abs(src[i] - y)
            nwe[i] = y

        sae = sae / n * multiplier

        for i in range(1, n):
            upper[i] = nwe[i] + sae
            lower[i] = nwe[i] - sae

    else:
        coefs = np.array([gaussian_window(i, bandwidth) for i in range(n)])
        den = np.sum(coefs)
        out = np.convolve(src, coefs[::-1], 'valid') / den
        mae = pd.Series(np.abs(src[-len(out):] - out)).rolling(window=len(out)).mean().iloc[-1] * multiplier

        upper[-len(out):] = out + mae
        lower[-len(out):] = out - mae

    df['upper'] = upper
    df['lower'] = lower

    return df
