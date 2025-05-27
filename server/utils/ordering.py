import datetime
import MetaTrader5 as mt5
import uuid
import time

from server.utils.initializations import login


def place_order( symbol, order_type, volume, price=None, sl=None, tp=None):

    if not mt5.symbol_select(symbol, True):
        print("Failed to select symbol:", symbol)
        return False

    real_volume = volume / 2.0
    tp1 = tp + ((tp-price) / 2) 
    tp2 = tp
    request1 = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": real_volume,
        "type": order_type,
        "price": price,
        "sl": sl,
        "tp": tp1,
        "deviation": 20,
        "magic": uuid.uuid4().int,
        "comment": "bot open",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    request2 = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": real_volume,
        "type": order_type,
        "price": tp1,
        "sl": price,
        "tp": tp2,
        "deviation": 20,
        "magic": uuid.uuid4().int,
        "comment": "bot open",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result1 = mt5.order_send(request1)
    result2 = mt5.order_send(request2)

    if result1.retcode != mt5.TRADE_RETCODE_DONE and result2.retcode != mt5.TRADE_RETCODE_DONE:
        print("Order failed")
        print("retcode 1 =", result1.retcode)
        print("retcode 2 =", result2.retcode)
        return False
    else:
        print("Order1 placed successfully!")
        print("Order2 placed successfully!")
        return True


def log_order( orders_collection, order_id, symbol, order_type, volume, price, sl, tp):
    order_data = {
        "order_id": order_id,
        "symbol": symbol,
        "order_type": order_type,
        "volume": volume,
        "price": price,
        "stop_loss": sl,
        "take_profit": tp,
        "open_time": datetime.datetime.now(),
        "close_time": None,
        "close_price": None,
        "profit": None,
        "status": "open"
    }
    orders_collection.insert_one(order_data)
    print("Order logged:", order_data)


def close_order(symbol , lot , order_type , price , ticket):
    request={
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": order_type,
        "position": ticket,
        "price": price,
        "comment": "close by hashem",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Can not close the order, retcode={result.retcode}")
        return None, None
    
    
def update_order(orders_collection, order_id, close_price, profit):
    result = orders_collection.update_one(
        {"order_id": order_id},
        {"$set": {
            "close_time": datetime.datetime.now(),
            "close_price": close_price,
            "profit": profit,
            "status": "closed"
        }}
    )
    if result.modified_count > 0:
        print(f"Order {order_id} updated successfully!")
    else:
        print(f"Failed to update order {order_id}.")


def place_dual_order(connection, symbol, strategy, order_type, volume, price, sl, tp1, tp2):
    if not connection.is_connected():
        print("Reconnecting to MetaTrader terminal...")
        connection.reconnect()
    
    real_volume = volume / 2.0
    magic_number = uuid.uuid4().int % 2147483647
    
    request1 = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": real_volume,
        "type": order_type,
        "price": price,
        "sl": sl,
        "tp": tp1,
        "deviation": 100,  
        "magic": magic_number,
        "comment": f"Trade 1, {strategy}",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }

    request2 = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": real_volume,
        "type": order_type,
        "price": price,
        "sl": sl,
        "tp": tp2,
        "deviation": 100,
        "magic": magic_number,
        "comment": f"Trade 2, {strategy}",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,  
    }

    result1 = mt5.order_send(request1)
    if result1 is None or result1.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Order1 failed, retcode={result1.retcode if result1 else 'None'}")
        return None, None
    
    result2 = mt5.order_send(request2)
    if result2 is None or result2.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Order2 failed, retcode={result2.retcode if result2 else 'None'}")
        return None, None

    print("Both orders placed successfully")
    return result1.order, result2.order
 

def close_all_positions():
    positions = mt5.positions_get()
    if positions is None:
        print("No open positions, error code =", mt5.last_error())
        return
    
    for position in positions:
        symbol = position.symbol
        ticket = position.ticket
        volume = position.volume
        order_type = mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
        
        close_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": order_type,
            "position": ticket,
            "deviation": 20,
            "magic": 0,
            "comment": "Close all positions",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(close_request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"Failed to close position {ticket}, error code =", result.retcode)
        else:
            print(f"Position {ticket} closed successfully")