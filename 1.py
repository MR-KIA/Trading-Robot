import MetaTrader5 as mt5
from server.utils.initializations import login
from server.utils.ordering import place_dual_order
from server.utils.accounting import balance, MT5Connection
from server.utils.trading import Strategy 


if __name__ == "__main__":
    # Initialize MetaTrader 5
    connection = MT5Connection(6633926, "6tG!WtXa", "AMarkets-Demo")
    print(connection.is_connected())

    # Print terminal and account information
    terminal_info = mt5.terminal_info()
    account_info = mt5.account_info()
    account_balance = balance() 
    print(account_balance)
    # if terminal_info:
    #     print(f"Terminal info: {terminal_info}")
    # if account_info:
    #     print(f"Account info: {account_info}")
    
    # if account_balance:
    #     print(f"Account info: {account_balance}")
    # Define symbol and other parameters
    symbol = "GBPUSDb"
    if not mt5.symbol_select(symbol, True):
        print(f"Failed to select symbol {symbol}")
        mt5.shutdown()
        exit()

    tick_info = mt5.symbol_info_tick(symbol)
    if tick_info is None:
        print(f"Failed to get tick information for symbol: {symbol}")
        mt5.shutdown()
        exit()

    strategy = Strategy(symbol, strategy="NWE")
    # strategy.trade()
    strategy.adjust()
    # print(mt5.symbol_info_tick(symbol))
    # price = 1.3090
    # order_type = mt5.ORDER_TYPE_BUY  
    # volume = 1.0
    # sl = 1.30860
    # tp1 = 1.3100
    # tp2 = 1.3096 

    # order_id1, order_id2 = place_dual_order(connection, symbol, order_type, volume, price, sl, tp1, tp2)
    # print(order_id1, order_id2)
    # if order_id1 and order_id2:
    #     print(f"Order 1 placed successfully with ID: {order_id1}")
    #     print(f"Order 2 placed successfully with ID: {order_id2}")
    # else:
    #     print("Failed to place orders")
    # print(balance())
    # positions = mt5.positions_get(symbol=symbol)
    # if positions:
    #     print("Open positions:")
    #     for position in positions:
    #         print(position)
    # else:
    #     print("No open positions")

    mt5.shutdown()
