from datetime import datetime, timedelta
import os
import sys
from flask import Flask, request, jsonify, redirect, url_for
import numpy as np
#import tensorflow as tf
from .utils.predictions import predict
#from .utils.load_model import load
import MetaTrader5 as mt5
import requests
import pytz
import pandas as pd
import time
from .utils.initializations import get_hist_data, login
from sklearn.preprocessing import MinMaxScaler
import joblib
from .vars.status import STATUS
from .vars.strategy import STRATEGY
# from utils.redis_client import db
from .utils.controllers import close_position, clear_red_times
import schedule
from .utils.reporting import round_down_to_nearest_15_minutes, print_and_save_account, make_report
import threading
from .utils.controllers import check_and_close_trades
from .utils.ordering import place_order, update_order, log_order
from .utils.lot_size import qty
from .strategies.watson import nadaraya_watson_envelope
from .strategies.candle_stick import body, candle, candle, body 
# from utils.strategies import strategy_a, strategy_b
from .utils.controllers import DEATH_TIME
from server.app import create_app
from flask_cors import CORS




application = create_app()
application.url_map.strict_slashes = False
CORS(application, resources={r"/*": {"origins": "*"}})

@application.after_request
def reset_output(response):
    sys.stdout = sys.__stdout__
    return response


def background_tasks():
    schedule.every(1).day.do(clear_red_times)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    APP_STATUS = STATUS["running"]
    print(APP_STATUS)
    
    threading.Thread(target=background_tasks, daemon=True).start()

    application.run(debug=True)
        