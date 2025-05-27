from server.utils.accounting import MT5Connection
from server.utils.ordering import close_all_positions
from ..vars.strategy import STRATEGY
import MetaTrader5 as mt5
from datetime import datetime, time as dt_time
from .initializations import save_json, load_json
import pandas as pd


DEATH_TIME = []

def set_strategy(pred_price, balance):
    if pred_price > balance and ((pred_price - balance) > 0.0001):
        return STRATEGY["buy"]
    elif pred_price < balance and ((balance - pred_price) > 0.0001):
        return STRATEGY["sell"]
    else:
        return STRATEGY["na"]

def close_position(connection, ticket):
    if not connection.is_connected():
        connection.reconnect()
    
    position = mt5.positions_get(ticket=ticket)
    if position:
        position = position[0]
        symbol = position.symbol
        volume = position.volume
        action = mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": action,
            "position": ticket,
            "deviation": 10,
            "magic": 123456,
            "comment": "Closing position due to loss limit",
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"Failed to close position {ticket}, retcode={result.retcode}")
        else:
            print(f"Position {ticket} closed successfully")
    else:
        print(f"No position found with ticket {ticket}")

def check_and_close_trades(connection):
    if not connection.is_connected():
        connection.reconnect()
    
    positions = mt5.positions_get()
    if positions is None or len(positions) == 0:
        print("No open positions found")
        return

    for position in positions:
        ticket = position.ticket
        open_price = position.price_open
        current_price = mt5.symbol_info_tick(position.symbol).bid if position.type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(position.symbol).ask
        loss_threshold = 0.04

        pnl_percentage = ((current_price - open_price) / open_price) if position.type == mt5.ORDER_TYPE_BUY else ((open_price - current_price) / open_price)

        if pnl_percentage <= -loss_threshold:
            print(f"Loss threshold reached for position {ticket}. Current P&L: {pnl_percentage:.2%}")
            close_position(ticket)

def check_daily_draw_down(connection, account_balance):
    if not connection.is_connected():
        connection.reconnect()

    current_time = datetime.now()
    start_of_day = current_time.replace(hour=0, minute=0, second=0, microsecond=0)

    positions = mt5.history_deals_get(from_date=start_of_day, to_date=current_time)
    total_profit_loss = 0.0

    if positions:
        for position in positions:
            if position.time < start_of_day.timestamp():
                continue

            profit_loss = position.profit
            total_profit_loss += profit_loss

    current_balance = account_balance + total_profit_loss

    drawdown_percentage = ((account_balance - current_balance) / account_balance) * 100

    if drawdown_percentage >= 4.5:
        print(f"Drawdown has reached {drawdown_percentage:.2f}%. Trading should be stopped.")
        return False
    return True


def monitor_trading_draw_down(connection):

    if not connection.is_connected():
        connection.reconnect()

    positions = mt5.positions_get()

    if positions is None:
        print("No positions found, error code =", mt5.last_error())
        return

    positions_df = pd.DataFrame(list(positions), columns=positions[0]._asdict().keys())
    positions_df['profit_percentage'] = (positions_df['profit'] / positions_df['price_open']) * 100

    for index, position in positions_df.iterrows():
        print(f"Symbol: {position['symbol']}, Ticket: {position['ticket']}, Profit: {position['profit']} USD, Profit Percentage: {position['profit_percentage']:.2f}%")

    return positions_df


def add_red_time(new_time, filename="db.json"):
    data = load_json(filename)
    
    new_start_time = str_to_time(new_time['start-time'])
    new_end_time = str_to_time(new_time['end-time'])
    
    for times in data['red-times']:
        start_time = str_to_time(times['start-time'])
        end_time = str_to_time(times['end-time'])
        
        if (new_start_time < end_time and new_end_time > start_time):
            print("Collision detected!")
            
            merged_start_time = min(new_start_time, start_time)
            merged_end_time = max(new_end_time, end_time)
            times['start-time'] = merged_start_time.strftime("%H:%M:%S")
            times['end-time'] = merged_end_time.strftime("%H:%M:%S")
            print(f"Intervals merged into: {times['start-time']} - {times['end-time']}")
            break
        
        else:
            data['red-times'].append(new_time)
            print(f"Added new time interval: {new_time['start-time']} - {new_time['end-time']}")
            break
            
    save_json(data, filename)

def clear_red_times():
    try:
        data = load_json()
        data['red-times'] = []
        save_json(data)
        print(f"Cleared red-times at {datetime.now()}")
    except Exception as e:
        print(f"Failed to clear red-times: {e}")

def get_all_red_times(filename="db.json"):
    data = load_json(filename)
    red_times = data.get('red-times', [])
    
    formatted_red_times = []
    for time_block in red_times:
        start_time = time_block.get('start_time')
        end_time = time_block.get('end_time')
        
        formatted_red_times.append({
            'start_time': start_time,
            'end_time': end_time
        })
    
    return formatted_red_times

def str_to_time(time_str):
    return datetime.strptime(time_str, "%H:%M:%S").time()

def time_check():
    now = datetime.now().time()
    
    for start_time, end_time in DEATH_TIME:
        if start_time <= now <= end_time:
            if start_time <= now <= end_time:
                return True
        else:  
            if now >= start_time or now <= end_time:
                connection = MT5Connection(account_number=6633926, password="6tG!WtXa", server="AMarkets-Demo")
                if not connection.is_connected():
                    connection.reconnect()
                close_all_positions()
                return False
    return True

def per_currency_daily_draw_down(connection, symbol, account_balance):
    if not connection.is_connected():
        connection.reconnect()

    current_time = datetime.now()
    start_of_day = current_time.replace(hour=0, minute=0, second=0, microsecond=0)

    positions = mt5.history_deals_get(from_time=start_of_day, to_date=current_time, symbol=symbol)
    total_profit_loss = 0.0

    if positions:
        for position in positions:
            if position.time < start_of_day.timestamp():
                continue

            profit_loss = position.profit
            total_profit_loss += profit_loss
    
    current_balance = account_balance + total_profit_loss

    drawdown_percentage = ((account_balance - current_balance) / account_balance) * 100

    if drawdown_percentage >= 0.5:
        print(f"Drawdown has reached {drawdown_percentage:.2f}%. Trading should be stopped.")
        return False
    return True        


def oposite_position(connection, sell_or_buy, symbol):  
    if not connection.is_connected():
        connection.reconnect()

    positions = mt5.positions_get()

    if positions is not None:
        for position in positions:
            if sell_or_buy != position.type:
                if position.symbol == symbol:
                    return False
    else:
        return True
    

def is_weekday():

    current_day = datetime.today().weekday()

    return current_day < 5    


def is_order_open(connection, symbol):
    if not connection.is_connected():
        connection.reconnect()
    positions = mt5.positions_get()
    
    if positions is None:
        raise ValueError("cant extract positions ")

    for position in positions:
        if position.symbol == symbol:
            return False
    
    return True

def is_not_in_night_hours():
    """Return False if the current time is between 00:00 and 06:00, otherwise True."""
    now = datetime.now()
    return not (0 <= now.hour < 6)