from flask import Blueprint, jsonify, request
from ..vars.strategy import STRATEGY
from ..vars.currency import ENT 
from ..vars.status import STATUS
import schedule
import time
import threading
import MetaTrader5 as mt5
from joblib import load
from ..utils.predictions import predict
from datetime import datetime, timedelta
from ..utils.reporting import make_report 
import pandas as pd
from ..utils.controllers import DEATH_TIME, add_red_time, time_check
from ..utils.trading_v2 import Strategy
from server.variables import APP_STRATEGY, APP_STATUS
from ..utils.ordering import close_all_positions
from threading import Event, Lock
import logging
from flask import current_app


bp1 = Blueprint('bp1', __name__)

pred_truth_report = []

SYMBOL = 'GBPUSDb'
INTERVAl = mt5.TIMEFRAME_M15

logger = logging.getLogger('trading_log')
logger.setLevel(logging.DEBUG)  
file_handler = logging.FileHandler('trading.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

# model_1 = load('./artifacts/lstm_model_v9.json',
            #    './artifacts/lstm_model_v9.weights.h5')

status_lock = Lock()
stop_event = Event()
trading_flag = threading.Event()
adjustment_flag = threading.Event()

def set_status(new_status):
    with status_lock:
        global APP_STATUS
        APP_STATUS = new_status

def get_status():
    with status_lock:
        return APP_STATUS

@bp1.route('/trade', methods=['GET'])
def start_auto_trade():
    global trading_flag, adjustment_flag
    if get_status() != STATUS["trading"]:
        set_status(STATUS["trading"])
        print(f"Status set to {get_status()}")

        stop_event.clear()
        
        strategies = []
        for currency in ENT:

            #if currency in ["GBPUSD", "XAUUSD", "USDCAD", "NZDUSD", "USDCHF", "EURUSD", "AUDUSD", "USDCHF"]:
                #strategy = Strategy(currency, strategy="NWE")

            if currency in ["GBPUSD","EURUSD", 'USDCAD',"USDCHF"]:
                strategy = Strategy(currency, strategy="QTOG")
                strategy1 = Strategy(currency, strategy="UTMA")

            if currency in ["AUDUSD"]:
                #strategy = Strategy(currency, strategy="UTMA")
                strategy1 = Strategy(currency, strategy="UTMA")
            

            print(f"currency: {strategy.symbol} strategy: {strategy.strategy}")
            strategies.append(strategy)
            strategies.append(strategy1)     
            
        def trade_task():
            while not stop_event.is_set():
                for strategy in strategies:
                    strategy.trade()
                    time.sleep(5)
        
        def adjustment_task():
            while not stop_event.is_set():
                for strategy in strategies:
                    strategy.adjust()
                    print(f"{strategy.strategy} adjusting")
                    time.sleep(3)  

        trading_flag = threading.Thread(target=trade_task, daemon=True)
        # adjustment_flag = threading.Thread(target=adjustment_task, daemon=True)
        trading_flag.start()
        # adjustment_flag.start()

        return jsonify({"status": "Task started"}), 202
    else:
        return jsonify({"status": "Task already running"}), 200
    

@bp1.route('/end-trade', methods=['GET'])
def end_auto_trade():
    global trading_flag, adjustment_flag

    if get_status() == STATUS["trading"]:
        set_status(STATUS["suspended"])
        stop_event.set()
        trading_flag.clear()

        if trading_flag is not None:
            trading_flag.join()
            trading_flag = None
        
        if adjustment_flag is not None:
            adjustment_flag.join()
            adjustment_flag = None

        return jsonify({"status": "Task stopped"}), 200
    else:
        return jsonify({"status": "Task is not running"}), 200

@bp1.route('/force-end-trade', methods=['GET'])
def force_end_auto_trade():
    global trading_flag, adjustment_flag

    if get_status() == STATUS["trading"]:
        set_status(STATUS["suspended"])
        stop_event.set()  
        trading_flag.clear()

        close_all_positions()  

        if trading_flag is not None:
            trading_flag.join()
            trading_flag = None

        if adjustment_flag is not None:
            adjustment_flag.join()
            adjustment_flag = None

        return jsonify({"status": "Task stopped (force!!!) and all positions closed"}), 200
    else:
        return jsonify({"status": "Task is not running"}), 200
    

def make_prediction():
    with bp1.app_context():
        # pred = predict(SYMBOL, INTERVAl, model_1)
        pred = [[1]] # dummy data!!!

        global predicted_price
        predicted_price = pred[0][0]

        print(predicted_price)
        return predicted_price


def start_prediction_process():
    global pred_truth_report

    def get_time_to_next_candle():
        now = datetime.now()
        next_candle_time = (now + timedelta(minutes=15 -
                            now.minute % 15)).replace(second=0, microsecond=0)
        time_to_next_candle = (next_candle_time - now).total_seconds()
        return time_to_next_candle

    def wait_for_candle_close():
        time_to_next_candle = get_time_to_next_candle()
        time.sleep(time_to_next_candle)

    def retrieve_current_candle():
        rates = mt5.copy_rates_from_pos(SYMBOL, INTERVAl, 1, 1)
        if rates is None or len(rates) == 0:
            print("Failed to get candle data")
            return None
        else:
            return rates[0]

    def make_prediction_and_store():
        with bp1.app_context():
            wait_for_candle_close()

            current_candle = retrieve_current_candle()
            if current_candle is None:
                return

            predicted_value = make_prediction()

            truth_value = current_candle['close']
            pred_truth_report.append([predicted_value, truth_value])

            print(pred_truth_report)
            pred_truth_report_df = pd.DataFrame(
                columns=['predicted', 'truth'], data=pred_truth_report)
            make_report(pred_truth_report_df)

    make_prediction_and_store()

    print("Completed 1 day of predictions.")


# @bp1.route('/trade', methods=['GET'])
# def start_auto_trade():
#     global APP_STATUS
#     print("Received request to start auto trade")

#     if APP_STATUS != STATUS["trading"]:
#         print("Auto trade is not currently running. Starting new task...")
#         APP_STATUS = STATUS["trading"]

#         def run_continuously():
#             print("Starting the run_continuously loop...")
#             while APP_STATUS == STATUS["trading"]:
#                 schedule.run_pending()
#                 print("Running scheduled tasks...")
#                 time.sleep(1)

#         def tr():
#             print("Executing trade function - placeholder")
#             # Simulate a trade task
#             print("Trade executed")

#         # Test the schedule setup independently
#         schedule.every(5).seconds.do(tr)
#         print("Scheduled trading task")

#         thread = threading.Thread(target=run_continuously)
#         thread.start()
#         print("Started trading thread")

#         return jsonify({"status": "Task started"}), 202
#     else:
#         print("Auto trade is already running")
#         return jsonify({"status": "Task already running"}), 200


@bp1.route('/test/auto-predict', methods=['GET', 'POST'])
def start_auto_predict():
    global APP_STATUS
    if APP_STATUS == STATUS["stopped"]:
        APP_STATUS = STATUS["running"]

        def run_continuously():
            while APP_STATUS == STATUS["running"]:
                schedule.run_pending()
                time.sleep(1)

        schedule.every(1).minutes.do(start_prediction_process)
        thread = threading.Thread(target=run_continuously)
        thread.start()
        return jsonify({"status": "Task started"}), 202
    else:
        return jsonify({"status": "Task already running"}), 200


@bp1.route('/test/end-predict', methods=['GET'])
def end_auto_predict():
    global APP_STATUS
    if APP_STATUS == STATUS["running"]:
        APP_STATUS = STATUS["stopped"]
        return jsonify({"status": "Task stopped"}), 200
    else:
        return jsonify({"status": "Task is not running"}), 200


@bp1.route('/add-time', methods=['POST'])
def add_bad_time():
    start_time = request.args.get('st')
    end_time = request.args.get('et') 
    add_red_time(start_time, end_time)
