from .initializations import candle 
from server.utils.ordering import place_dual_order
# import MetaTrader5 as mt5
from ..utils.lot_size import calculate_lot_size, qty
from ..utils.accounting import balance, MT5Connection
from ..vars.currency import ENT
from ..strategies.watson import nadaraya_watson_envelope
from ..strategies.rsi import rsi, candle, rsi_divergence_indicator
from ..utils.controllers import check_and_close_trades, check_daily_draw_down, close_position, is_weekday, monitor_trading_draw_down, oposite_position, time_check, is_order_open, per_currency_daily_draw_down
from ..utils.stp import stp
import numpy as np
from ..strategies.ut_bot import calculate_ut_bot_alerts, get_heikin_ashi
from ..strategies.ribbon import apply_ma_ribbon
from datetime import datetime, timedelta
from ..strategies.candle_stick import check_pullback, monitor_pullbacks, wait_for_next_candle
from ..utils.initializations import login, ensure_connected
from ..strategies.osgfc import one_sided_gaussian_filter
from ..strategies.qtrend import q_trend
import MetaTrader5 as mt5
import pandas as pd
import winsound
import threading
import time


class Strategy:
    def __init__(self, symbol, lot=1, strategy="NWE", tf=None, validator="rsi", stp=False, account= {"login_no": 6859719, "password": "6!MyBeMg", "server": "AMarkets-Demo"}):
        self.account_balance = balance() 
        self.account = account
        self.symbol = symbol
        self.lot = lot
        self.strategy = strategy
        self.time_frame = tf if tf else '5m'
        self.validator = validator
        self.stp = stp
        self.connection = MT5Connection(account["login_no"], account["password"], account["server"])
        self._temp_ticket1 = None
        self._temp_ticket2 = None
        self._temp_init_price = None
        self._stop_event = threading.Event()  

    def trade(self):
        if not self.connection.connect():
            print(f"Reconnecting to server for symbol: {self.symbol}")
            ensure_connected(self.connection)

        if not mt5.symbol_select(self.symbol, True):
            print(f"Failed to select symbol: {self.symbol}")
            return
        
        tick = mt5.symbol_info_tick(self.symbol)
        if tick is None:
            print(f"Failed to retrieve tick information for symbol: {self.symbol}")
            return

        current_price_bid = float(tick.bid)
        current_price_ask = float(tick.ask)
        candles = np.array(candle(self.time_frame, 10, self.symbol))
        candles_df = candle(self.time_frame, 10, self.symbol)
        date_to = datetime.now()
        date_from = date_to - timedelta(days=30)
        heikenashi = get_heikin_ashi(symbol=self.symbol, timeframe=self.time_frame, start=date_from, end=date_to)

        if self.strategy == "NWE":
            df = nadaraya_watson_envelope(candles_df)
            upper = df["upper"]
            lower = df["lower"]
            upper_val = upper.iloc[-1]
            lower_val = lower.iloc[-1]
            print(upper_val)
            print(current_price_ask, current_price_bid)
            print(lower_val)
            isSignal = current_price_ask >= upper_val or current_price_bid <= lower_val
            kind = "sell" if current_price_ask >= upper_val else "buy"
            ok = self._check()
            print(ok, isSignal)

            if ok :
                
                self._place_order(current_price_ask if kind == "sell" else current_price_bid, kind)

                winsound.Beep(1000, 500)

        elif self.strategy == "QTOG":
            gussian_result = one_sided_gaussian_filter(candles_df)[["GoLong", "GoShort"]].iloc[-1]
            q_trend_result = dict(list(q_trend(candles_df["close"]).items())[2:])

            sell = q_trend_result["sell_signal"][-1] and gussian_result["GoShort"]
            buy = q_trend_result["buy_signal"][-1] and gussian_result["GoLong"]

            isSignal = buy | sell
            kind = "sell" if sell else "buy"
            ok = self._check()
            print(ok, isSignal)

            if ok and isSignal:
                
                self._place_order(current_price_ask if kind == "sell" else current_price_bid, kind)

                winsound.Beep(1000, 500)

        elif self.strategy == "UTMA":
            if not self.connection.connect():
                print(f"Reconnecting to server for symbol: {self.symbol}")
                ensure_connected(self.connection)
                
            signal = calculate_ut_bot_alerts(heikenashi)
            ma_signal = apply_ma_ribbon(heikenashi)

            buySignal = signal['buy'].iloc[-1]
            sellSignal = signal['sell'].iloc[-1]

            upper = ma_signal['MA1'].iloc[-1]
            lower = ma_signal['MA2'].iloc[-1]
            trend = ma_signal['MA3'].iloc[-1]
            print(f"buy: {buySignal}")
            print(f"sell: {sellSignal}")

            if buySignal or sellSignal:  
                kind = "buy" if buySignal else "sell"
                
                if isinstance(current_price_bid, pd.Series):
                    current_price_bid = current_price_bid.iloc[-1]
                if isinstance(current_price_ask, pd.Series):
                    current_price_ask = current_price_ask.iloc[-1]

                isSignal = (kind == "buy" and current_price_bid >= trend) or (kind == "sell" and current_price_ask <= trend)
                current_price = current_price_ask if kind == "sell" else current_price_bid
                ok = self._check()
                
                if isSignal and ok:
                    # _ = monitor_pullbacks(self.connection, self.symbol, self.time_frame, 5, 30, 6)
                    self._place_order(current_price, kind)

                    winsound.Beep(1000, 500)

    def _place_order(self, current_price, kind):
        if not self.connection.is_connected():
            self.connection.reconnect()

        if self.symbol == "NZDUSDb":
            sl = current_price + 0.002 if kind == "sell" else current_price - 0.002
            tp1 = current_price - 0.0015 if kind == "sell" else current_price + 0.0015
            tp2 = current_price - 0.0025 if kind == "sell" else current_price + 0.0025
        elif self.symbol == "XAUUSDb":
            sl = current_price + 6 if kind == "sell" else current_price - 6
            tp1 = current_price - 6 if kind == "sell" else current_price + 6
            tp2 = current_price - 10 if kind == "sell" else current_price + 10
        elif self.symbol == "AUDUSDb":
            sl = current_price + 0.001 if kind == "sell" else current_price - 0.001
            tp1 = current_price - 0.0008 if kind == "sell" else current_price + 0.0008
            tp2 = current_price - 0.0016 if kind == "sell" else current_price + 0.0016
        elif self.symbol == "USDCADb":
            sl = current_price + 0.001 if kind == "sell" else current_price - 0.001
            tp1 = current_price - 0.0008 if kind == "sell" else current_price + 0.0008 #------------
            tp2 = current_price - 0.0016 if kind == "sell" else current_price + 0.0016
        elif self.symbol == "USDCHFb":
            sl = current_price + 0.001 if kind == "sell" else current_price - 0.001
            tp1 = current_price - 0.001 if kind == "sell" else current_price + 0.001
            tp2 = current_price - 0.00135 if kind == "sell" else current_price + 0.00135
        elif self.symbol == "USDJPYb":
            sl = current_price + 0.150 if kind == "sell" else current_price - 0.150
            tp1 = current_price - 0.17 if kind == "sell" else current_price + 0.17
            tp2 = current_price - 0.25 if kind == "sell" else current_price + 0.25
        elif self.symbol == "GBPUSDb":
            sl = current_price + 0.002 if kind == "sell" else current_price - 0.002
            tp1 = current_price - 0.002 if kind == "sell" else current_price + 0.002
            tp2 = current_price - 0.004 if kind == "sell" else current_price + 0.004
        elif self.symbol == "EURUSDb":
            sl = current_price + 0.001 if kind == "sell" else current_price - 0.001
            tp1 = current_price - 0.0006 if kind == "sell" else current_price + 0.0006
            tp2 = current_price - 0.001 if kind == "sell" else current_price + 0.001
        else:
            sl = current_price + 0.001 if kind == "sell" else current_price - 0.001
            tp1 = current_price - 0.001 if kind == "sell" else current_price + 0.001
            tp2 = current_price - 0.002 if kind == "sell" else current_price + 0.002

        lot = 1 #----------------------------------------------
        ord_type = mt5.ORDER_TYPE_BUY if kind == "buy" else mt5.ORDER_TYPE_SELL
        ticket1, ticket2 = place_dual_order(self.connection, self.symbol, self.strategy, ord_type, lot, current_price, sl, tp1, tp2)

        if ticket1 and ticket2:
            self._temp_init_price = current_price
            self._sl_adjusted = False

    def _check(self):
        return all([
            is_weekday(),
            time_check(),
            # check_daily_draw_down(self.connection, self.account_balance),
            # per_currency_daily_draw_down(self.connection, self.symbol, self.account_balance), 
            is_order_open(self.connection, self.symbol)
        ])
    
    def adjust(self):
        if self._temp_ticket1 is not None or self._temp_ticket2 is not None:
            self.start_monitoring(self._temp_init_price)

    def _adjust_stop_loss(self, position_id, new_sl):
        position = None
        positions = mt5.positions_get(ticket=position_id)
        if positions is not None and len(positions) > 0:
            position = positions[0]
        else:
            print(f"Position {position_id} not found.")
            return False

        current_tp = position.tp
        current_price = position.price_open
        lot_size = position.volume
        symbol = position.symbol
        ord_type = position.type

        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "position": position_id,
            "sl": new_sl,
            "tp": current_tp,
            "price": current_price,
            "volume": lot_size,
            "symbol": symbol,
            "type": ord_type,
            "deviation": 10
        }

        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"Failed to modify SL for position {position_id}, retcode={result.retcode}")
            return False
        else:
            print(f"SL adjusted for position {position_id} to {new_sl}")
            return True

    def start_monitoring(self, entry_price, interval=5):
        self._stop_event.clear()
        self._monitor_thread = threading.Thread(
            target=self._run_monitoring, args=(entry_price, interval), daemon=False
        )
        self._monitor_thread.start()
        while not self._stop_event.is_set():
            
            if not self.connection.is_connected():
                print("Reconnecting to MetaTrader terminal...")
                self.connection.reconnect()

            positions = mt5.positions_get(symbol=self.symbol)
            if positions:
                tickets = [pos.ticket for pos in positions]
                ticket1 = tickets[0] if len(tickets) > 0 else None
                ticket2 = tickets[1] if len(tickets) > 1 else None
        
                if ticket1 is None and ticket2 is not None and not self._sl_adjusted:
                    print(f"TP hit for first order {ticket1}, adjusting SL for second order {ticket2}")
                    self._temp_ticket1 = None
                    if self._adjust_stop_loss(ticket2, entry_price):
                        self._sl_adjusted = True  
                        self._temp_ticket2 = None
            time.sleep(interval)


    def stop_monitoring(self):
        if self._monitor_thread.is_alive():
            self._stop_event.set()
            self._monitor_thread.join()
            print("Monitoring stopped")