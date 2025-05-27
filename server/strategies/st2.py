import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from scipy.stats import norm

# Fetch historical data
def fetch_data(ticker, period='1y'):
    data = yf.download(ticker, period=period)
    data['Close'] = data['Adj Close']  # Use Adjusted Close for accuracy
    return data

# Gaussian window function
def gauss(x, h):
    return np.exp(-(x * 2 / (h * 2 * 2)))

# Nadaraya-Watson Envelope calculation
def nadaraya_watson_envelope(src, h, mult):
    n = len(src)
    coefs = np.array([gauss(i, h) for i in range(500)])
    den = coefs.sum()
    
    out = np.array([np.sum(src[max(0, i-499):i+1] * coefs[:min(500, i+1)]) / den for i in range(n)])
    mae = pd.Series(np.abs(src - out)).rolling(window=500).mean() * mult
    
    upper = out + mae
    lower = out - mae
    
    return out, upper, lower

# Trading signals
def trading_signals(data, out, upper, lower):
    signals = pd.DataFrame(index=data.index)
    signals['Close'] = data['Close']
    signals['Upper'] = upper
    signals['Lower'] = lower
    signals['Signal'] = 0  # Default to 0, no signal
    
    signals['Signal'] = np.where(signals['Close'] > signals['Lower'], 1, signals['Signal'])  # Buy signal
    signals['Signal'] = np.where(signals['Close'] < signals['Upper'], -1, signals['Signal'])  # Sell signal
    
    signals['Position'] = signals['Signal'].shift()  # Delay by one time step to avoid lookahead bias
    
    return signals

# Backtesting the strategy
def backtest(signals, initial_capital=10000):
    positions = pd.DataFrame(index=signals.index).fillna(0)
    positions['Stock'] = signals['Position']  # Number of stocks to hold
    
    portfolio = positions.multiply(signals['Close'], axis=0)
    pos_diff = positions.diff()
    
    portfolio['Holdings'] = positions.multiply(signals['Close'], axis=0).sum(axis=1)
    portfolio['Cash'] = initial_capital - (pos_diff.multiply(signals['Close'], axis=0)).sum(axis=1).cumsum()
    portfolio['Total'] = portfolio['Cash'] + portfolio['Holdings']
    
    return portfolio

# Plotting function
def plot_signals(data, signals, portfolio):
    plt.figure(figsize=(14, 7))
    plt.plot(data['Close'], label='Close Price', alpha=0.5)
    plt.plot(signals['Upper'], label='Upper Envelope', linestyle='--', alpha=0.5)
    plt.plot(signals['Lower'], label='Lower Envelope', linestyle='--', alpha=0.5)
    plt.plot(portfolio['Total'], label='Portfolio Value', linewidth=2, alpha=0.7)
    
    buy_signals = signals[signals['Position'] == 1]
    sell_signals = signals[signals['Position'] == -1]
    
    plt.scatter(buy_signals.index, buy_signals['Close'], label='Buy Signal', marker='^', color='green', alpha=1)
    plt.scatter(sell_signals.index, sell_signals['Close'], label='Sell Signal', marker='v', color='red', alpha=1)
    
    plt.title('Nadaraya-Watson Envelope Trading Signals')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid()
    plt.show()

# Main function
def main():
    ticker = 'AAPL'
    period = '1y'
    bandwidth = 8
    multiplier = 3
    
    data = fetch_data(ticker, period)
    out, upper, lower = nadaraya_watson_envelope(data['Close'].values, bandwidth, multiplier)
    signals = trading_signals(data, out, upper, lower)
    portfolio = backtest(signals)
    
    plot_signals(data, signals, portfolio)

if __name__ == "main":
    main()