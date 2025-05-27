from datetime import datetime, timedelta
import time
from .initializations import get_hist_data, login
import MetaTrader5 as mt5


def predict(symbol, interval, model):
    hist_data, scaler = get_hist_data(symbol, interval)

    pred = model.predict(hist_data)
    inv_pred = scaler.inverse_transform(pred)
    return inv_pred
