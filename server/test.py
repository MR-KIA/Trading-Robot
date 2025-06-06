# import MetaTrader5 as mt5
# from datetime import datetime, timedelta
# import pytz

# print(mt5.initialize())

# symbol = 'GBPUSD'

# login = 6633926
# password = '6tG!WtXa'
# server = 'AMarkets-Demo'
# print(mt5.login(login, password, server))

# timeframe = mt5.TIMEFRAME_M15  # 15-minute timeframe

# current_time = datetime.now()

# start_time = current_time - timedelta(minutes=100 * 15)


# candles = mt5.copy_rates_range(symbol, timeframe, start_time, current_time)
# print(candles)

# for candle in candles:
#     print(f"Time: {datetime.fromtimestamp(candle[0])}, Open: {candle[1]}, High: {
#           candle[2]}, Low: {candle[3]}, Close: {candle[4]}, Volume: {candle[5]}")

# Disconnect from MetaTrader 5
# mt5.shutdown()

import pytz
import pandas as pd
from datetime import datetime
import MetaTrader5 as mt5

print("MetaTrader5 package author: ", mt5.__author__)
print("MetaTrader5 package version: ", mt5.__version__)

# import the 'pandas' module for displaying data obtained in the tabular form
pd.set_option('display.max_columns', 500)  # number of columns to be displayed
pd.set_option('display.width', 1500)      # max table width to display
# import pytz module for working with time zone

# establish connection to MetaTrader 5 terminal
if not mt5.initialize():
    print("initialize() failed, error code =", mt5.last_error())
    quit()

symbol = 'GBPUSDb'

login = 6633926
password = '6tG!WtXa'
server = 'AMarkets-Demo'
print(mt5.login(login, password, server))
# set time zone to UTC
timezone = pytz.timezone("Etc/UTC")
# create 'datetime' objects in UTC time zone to avoid the implementation of a local time zone offset
utc_from = datetime(2020, 1, 10, tzinfo=timezone)
utc_to = datetime(2020, 1, 11, hour=13, tzinfo=timezone)
# get bars from USDJPY M5 within the interval of 2020.01.10 00:00 - 2020.01.11 13:00 in UTC time zone
rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M15, utc_from, utc_to)

# shut down connection to the MetaTrader 5 terminal
mt5.shutdown()

# display each element of obtained data in a new line
print("Display obtained data 'as is'")
counter = 0
for rate in rates:
    counter += 1
    if counter <= 10:
        print(rate)

# create DataFrame out of the obtained data
rates_frame = pd.DataFrame(rates)
# convert time in seconds into the 'datetime' format
rates_frame['time'] = pd.to_datetime(rates_frame['time'], unit='s')

# display data
print("\nDisplay dataframe with data")
print(rates_frame.head(10))
