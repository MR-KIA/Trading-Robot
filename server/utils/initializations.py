import time
import MetaTrader5 as mt5
from datetime import datetime, timedelta
import pandas as pd
import joblib
import schedule
from sklearn.preprocessing import MinMaxScaler
import joblib
import json


def get_hist_data(symbol, interval):
    current_time = datetime.now()
    end_time = current_time
    start_time = end_time - timedelta(minutes=15 * 15)

    candles = mt5.copy_rates_from(symbol, interval, start_time, 15)

    if candles is None or len(candles) == 0:
        raise ValueError(
            "No historical data fetched. Please check the symbol and interval.")

    candles_df = pd.DataFrame(candles)

    if candles_df.empty or len(candles_df) < 15:
        print(candles_df.shape)
        raise ValueError(
            "Insufficient data fetched. Ensure at least 51 candles are available.")

    # print("DataFrame columns:", candles_df.columns)
    # print("First few rows of the DataFrame:\n", candles_df.tail())

    close_prices = candles_df['close'].values.reshape(-1, 1)
    # scaler = MinMaxScaler()
    scaler = joblib.load('./artifacts/scaler_X.pkl')
    scaled_data = scaler.fit_transform(close_prices)

    reshaped_data = scaled_data.reshape(1, 1, 15)
    # print(reshaped_data.shape)
    return reshaped_data, scaler



def candle(timeframe='30m', limit=10, symbol='GBPUSD'):
    try:        
        timeframe_mapping = {
            '1m': mt5.TIMEFRAME_M1,
            '3m': mt5.TIMEFRAME_M3,
            '5m': mt5.TIMEFRAME_M5,
            '15m': mt5.TIMEFRAME_M15,
            '30m': mt5.TIMEFRAME_M30,
            '1h': mt5.TIMEFRAME_H1,
            '4h': mt5.TIMEFRAME_H4,
            '1d': mt5.TIMEFRAME_D1,
            '1w': mt5.TIMEFRAME_W1,
        }
        
        
        if timeframe not in timeframe_mapping:
            raise ValueError(f"Invalid timeframe '{timeframe}' provided")
        
        time = timeframe_mapping[timeframe]

        
        candles = mt5.copy_rates_from_pos(symbol, time, 0, limit)
        if candles is None or len(candles) == 0:
            raise ValueError("Failed to retrieve candle data. Check the symbol and timeframe.")

        
        df = pd.DataFrame(candles, columns=['time', 'open', 'high', 'low', 'close'])
        return df

    except Exception as e:
        print(f"Error occurred: {e}")
        raise


def get_heikin_ashi(symbol, start, end, timeframe="5m"):
    timeframe_mapping = {
            '1m': mt5.TIMEFRAME_M1,
            '3m': mt5.TIMEFRAME_M3,
            '5m': mt5.TIMEFRAME_M5,
            '15m': mt5.TIMEFRAME_M15,
            '30m': mt5.TIMEFRAME_M30,
            '1h': mt5.TIMEFRAME_H1,
            '4h': mt5.TIMEFRAME_H4,
            '1d': mt5.TIMEFRAME_D1,
            '1w': mt5.TIMEFRAME_W1,
        }
        
        
    if timeframe not in timeframe_mapping:
        raise ValueError(f"Invalid timeframe '{timeframe}' provided")
        
    timeframe = timeframe_mapping[timeframe]

    if not mt5.initialize():
        print("Initialize() failed, error code =", mt5.last_error())
        quit()

    ohlc_data = mt5.copy_rates_range(symbol, timeframe, start, end)
    if ohlc_data is None:
        print("No data available, error code =", mt5.last_error())
        mt5.shutdown()
        return None

    df = pd.DataFrame(ohlc_data)
    df['time'] = pd.to_datetime(df['time'], unit='s')

    ha_close = (df['open'] + df['high'] + df['low'] + df['close']) / 4
    ha_open = (df['open'].shift(1) + df['close'].shift(1)) / 2
    ha_open.iloc[0] = (df['open'].iloc[0] + df['close'].iloc[0]) / 2 
    ha_high = df[['high', 'open', 'close']].max(axis=1)
    ha_low = df[['low', 'open', 'close']].min(axis=1)

    ha_df = pd.DataFrame({
        'time': df['time'],
        'open': ha_open,
        'high': ha_high,
        'low': ha_low,
        'close': ha_close
    })

    mt5.shutdown()

    return ha_df




def login(login=187004, password="k!e9abU0", server="AronMarkets-Demo"):

    # login = 6633926
    # password = '6tG!WtXa'
    # server = 'AMarkets-Demo'
    result = mt5.login(login, password, server)
    return result


def initialize_and_login(account_number, password, server):
    if not mt5.initialize():
        print("initialize() failed")
        mt5.shutdown()
        return False

    login_status = mt5.login(account_number, password=password, server=server)
    if login_status:
        print("Logged in successfully!")
        return True
    else:
        print("Login failed")
        mt5.shutdown()
        return False
    
def ensure_connected(connection):
    terminal_info = mt5.terminal_info()
    if terminal_info is None:
        print("Reconnecting...")
        connection.reconnect()
    else:
        print(f"Connected to server: {terminal_info}")

def reconnect(account_number, password, server):
    mt5.shutdown()
    initialize_and_login(account_number, password, server)

# def establish_connections():
#     try:
#         with open('./db.json', 'r') as file:
#             account_data = json.load(file)
        
#         accounts = account_data.get('accounts', [])
#         if not accounts:
#             print("No accounts found in the JSON file.")
#             return connections
        
#         for account in accounts:
#             account_number = account['login']
#             password = account['password']
#             server = account['server']
#             res = login(account_number, password, server)
#             if res:
#                 print(f"Successfully connected to account {account_number}")
#             else:
#                 print(f"Failed to connect to account {account_number}")
    
#     except FileNotFoundError:
#         print("Error: db.json file not found.")
#     except json.JSONDecodeError:
#         print("Error: Failed to parse JSON file.")
#     except Exception as e:
#         print(f"An unexpected error occurred: {e}")

#     return connections

        

def load_json(filename="db.json"):
    with open(filename, 'r') as file:
        return json.load(file)

def save_json(data, filename="db.json"):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

def get_accounts():
    data = load_json()
    accounts = data.get("accounts", [])
        
    account_list = [{"server": acc["server"], "login": acc["login"]} for acc in accounts]        
    return account_list

def update_account(login_no, new_password, filename="db.json"):
    data = load_json(filename)
    account_found = False
    for account in data['accounts']:
        if account['login'] == login_no:
            account['password'] = new_password
            account_found = True
            break
    if account_found:
        save_json(data, filename)
        print(f"Account {login_no} updated with new password.")
        return True 
    else:
        print(f"Account {login_no} not found.")
        return False

def add_account(new_account, filename="db.json"):
    data = load_json(filename)
    for account in data['accounts']:
        if account['login'] == new_account['login']:
            print(f"Account with login {new_account['login']} already exists.")
            return False  
    data['accounts'].append(new_account)
    save_json(data, filename)
    return True  

def delete_account(filename, account_number):
    data = load_json(filename)
    data['accounts'] = [acc for acc in data['accounts'] if acc['account_number'] != account_number]
    save_json(filename, data)

def verify_account(login_no, password, filename="db.json"):
    data = load_json(filename)
    for account in data['accounts']:
        if account['login'] == login_no and account['password'] == password:
            return True
    return False  