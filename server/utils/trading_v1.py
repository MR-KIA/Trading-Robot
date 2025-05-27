from .initializations import candle 
from ..utils.ordering import place_order, close_order, update_order, log_order, adjust_stop_loss, monitor_and_adjust, place_dual_order
# import MetaTrader5 as mt5
from ..utils.lot_size import calculate_lot_size
from ..utils.accounting import balance
from ..vars.currency import ENT
from ..strategies.watson import nadaraya_watson_envelope
from ..strategies.rsi import rsi, candle, rsi_divergence_indicator
from ..utils.controllers import check_and_close_trades, check_daily_draw_down, close_position, is_weekday, monitor_trading_draw_down, oposite_position, time_check, is_order_open
from ..utils.stp import stp
import numpy as np
from ..strategies.ut_bot import calculate_ut_bot_alerts, get_heikin_ashi
from ..strategies.ribbon import apply_ma_ribbon
from datetime import datetime, timedelta
from ..strategies.candle_stick import check_pullback, monitor_pullbacks, wait_for_next_candle


class Strategy:
    def __init__(self, account, symbol, lot=1, strategies="NWE", tf=None, validator="rsi", stp=False):
        self.account = account
        self.symbol = symbol
        self.lot = lot
        self.strategies = strategies
        if not tf:
            self.time_frame = '5m'
        else:
            self.time_frame = tf
        self.validator = validator
        self.stp = stp

    def trade(self):
        account_balance = balance(self.account) 
        current_price = float(self.account.symbol_info_tick(self.symbol).bid)
        candles = np.array(candle(self.time_frame, 10, self.symbol))
        date_to = datetime.now()
        date_from = date_to - timedelta(days=30)
        heikenashi = get_heikin_ashi(self.account, self.symbol, self.time_frame, date_from, date_to)

        for strategy in self.strategies:
            if strategy == "NWE":
                upper, lower = nadaraya_watson_envelope(candles)
                upper_val = float(upper[-1])
                lower_val = float(lower[-1])
                isSignal = current_price >= upper_val or current_price <= lower_val
                print(isSignal)
                print(lower_val)
                print(upper_val)
                print(current_price)
                kind = "sell" if current_price >= upper_val else "buy"
                ok = self._check()
                if isSignal and ok: 
                    self._place_order(current_price, kind, account_balance)
                    self.adjust()

            elif strategy == "UTMA":
                signal = calculate_ut_bot_alerts(heikenashi, heikin_ashi=True)
                ma_signal = apply_ma_ribbon(heikenashi)     
                
                buySignal = signal['buy']
                sellSignal = signal['sell']
                upper = ma_signal["MA1"]
                lower = ma_signal["MA2"]
                trend = ma_signal["MA3"]

                if buySignal or sellSignal:
                    kind = "buy" if buySignal else "sell"
                    isSignal = (kind == "buy" and current_price >= trend) or (kind == "sell" and current_price <= trend)
                    
                    ok = self._check()
                    if isSignal and ok:
                        _ = monitor_pullbacks(self.symbol, self.time_frame, 5, 30, 6)
                        self._place_order(current_price, kind, account_balance)
                        self.adjust()



    def _place_order(self, current_price, kind, account_balance, loss_pip, profit_pip):
        sl = current_price + (0.0001*loss_pip) if kind == "sell" else current_price - (0.0001 *loss_pip)
        tp1 = current_price - (0.0001*profit_pip) if kind == "sell" else current_price + (0.0001*profit_pip)
        tp2 = current_price - (0.0002*profit_pip) if kind == "sell" else current_price + (0.0002*profit_pip)
        pip = 10
        lot = calculate_lot_size(account_balance, 0.5, 0.0001, pip)
        ord_type = self.account.ORDER_TYPE_BUY if kind == "buy" else self.account.ORDER_TYPE_SELL
        ticket1, ticket2 = place_dual_order(self.symbol, ord_type, lot, current_price, sl, tp1, tp2)

        if ticket1 and ticket2:
            self._temp_ticket1 = ticket1
            self._temp_ticket2 = ticket2
            self._temp_init_price = current_price


    def adjust(self):
        monitor_and_adjust(self.symbol, self._temp_ticket1, self._temp_ticket2, self._temp_init_price)
    
    def _check(self):
        condition1 = is_weekday()    
        condition2 = check_daily_draw_down(self.account)  
        condition3 = time_check()  
        condition4 =  is_order_open(self.symbol, self.account) 
        if condition1 and condition2 and condition3 and condition4:
            return True
        else :
            return False
        
    def _is_valid(self, kind):
        isValid = False
        if self.validator == "rsi":
            isValid = rsi(kind, self.time_frame, self.symbol)
        return isValid