from functools import wraps
from flask import jsonify
import MetaTrader5 as mt5


def strategy_a(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Pre-trade logic for strategy A
        print("Applying Strategy A")
        result = f(*args, **kwargs)
        # Post-trade logic for strategy A
        print("Completed Strategy A")
        return result
    return decorated_function


def strategy_b(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Pre-trade logic for strategy B
        print("Applying Strategy B")
        result = f(*args, **kwargs)
        # Post-trade logic for strategy B
        print("Completed Strategy B")
        return result
    return decorated_function


buy = mt5.ORDER_TYPE_BUY
sell = mt5.ORDER_TYPE_SELL
