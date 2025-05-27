from flask import Blueprint, jsonify, request
from server.utils.controllers import get_all_red_times
from ..vars.strategy import STRATEGY
from ..vars.status import STATUS
import schedule
import time
import os
import threading
import MetaTrader5 as mt5
from joblib import load
from ..utils.predictions import predict
from datetime import datetime, timedelta
from ..utils.reporting import make_report 
import pandas as pd
from ..utils.reporting import print_and_save_account
from ..utils.initializations import login, add_account, initialize_and_login, get_accounts, verify_account, save_json, load_json
from ..utils.accounting import MT5Connection
from ..utils.trading import Strategy
import json
from server.variables import APP_STRATEGY, APP_STATUS
from flask import current_app

bp2 = Blueprint('bp2', __name__)

SYMBOL = 'GBPUSDb'
INTERVAl = mt5.TIMEFRAME_M15


@bp2.route('/account')
def get_account_info():
    print('GETTING ACCOUNT INFO...')
    i = 1
    while i <= 5:
        print(f'attempt{i}')
        account_info = mt5.account_info()
        if account_info is None:
            print('the bot is not logged into the account yet')
        else:
            account_info_dict = account_info._asdict()
            print_and_save_account(account_info_dict)
            return jsonify(account_info_dict)
        i = i + 1

    print('failed to get account info X')
    return jsonify({"error": "failed to get account info after 5 attempts"}), 500

@bp2.route('/statement', methods=['GET'])
def get_statement():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if not start_date and not end_date:
        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = datetime.now()

    try:

        from_date = pd.to_datetime(start_date)
        to_date = pd.to_datetime(end_date)
        trades = mt5.history_deals_get(from_date, to_date)

        if trades is None:
            return jsonify({'error': 'No trades found'}), 404
        df = pd.DataFrame(list(trades), columns=trades[0]._asdict().keys())
        trades_json = df.to_dict(orient='records')

        return jsonify(trades_json)

    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    

@bp2.route('/login', methods=['POST'])
def login_fn():

    try:
        data = request.get_json()
        login_no = int(data.get("login")) if data.get("login") else data.get("login")
        password = data.get("password")
        server = data.get("server")
        other_accounts = int(data.get("other_accounts")) if data.get("other_accounts") else data.get("other_accounts")

        if (server and password and login_no) and other_accounts == 0:
            new_account = {
                "login": login_no,
                "password": password,
                "server": server
            }
            add_account(new_account)
            verification_res = verify_account(login_no, password)
            if verification_res:
                connection = MT5Connection(login_no, password, server)
                print(mt5.terminal_info())
                account_info = mt5.account_info()
                if account_info:
                    return jsonify({'message': f'logged into {login_no}!', 'account': account_info._asdict()}), 200
                else:
                    return jsonify({'message': 'login failed!'}), 500
            else:
                return jsonify({'message': 'false credentials!'}), 401
        
        elif not server and not login_no and not password:
            if other_accounts == 1:
                connection = MT5Connection(6633926, "6tG!WtXa", "AMarkets-Demo")
                print(mt5.terminal_info())
                message = ''.join("6633926")            
                return jsonify({'message': f'logged into {message}!'}), 200
            else:
                return jsonify({'message': 'bad request'}), 401    
        else:
            print(login_no, password, server, other_accounts)
            return jsonify({'message': 'bad request'}), 402

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred', 'details': str(e)}), 500



@bp2.route('/trade', methods=['GET'])
def trade_fn():
    strategy = Strategy("GBPUSD")
    strategy.trade()

@bp2.route('/status', methods=['GET'])
def status():
    return jsonify({"app-status":APP_STATUS})


@bp2.route('/strategy', methods=['GET'])
def strategy():
    return jsonify({"app-strategy":APP_STRATEGY})

@bp2.route('/accounts', methods=['GET'])
def accounts():
    try:
        account_list = get_accounts()
        
        return jsonify({"accounts": account_list}), 200

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@bp2.route('/servers', methods=['GET'])
def servers():
    try:
        with open('./db.json', 'r') as f:
            data = json.load(f)  

        servers = {account['server'] for account in data['accounts']}

        return jsonify({"servers": list(servers)}), 200
    except Exception as e:
        print(f"Error reading servers: {e}")
        return jsonify({"error": "Failed to fetch servers"}), 500


@bp2.route('/add-red-times', methods=['POST'])
def add_red_time():
    try:
        data = request.get_json()
        start_time = data.get("start_time")
        end_time = data.get("end_time")

        db_data = load_json('db.json')

        if "red-times" not in db_data:
            db_data["red-times"] = []

        db_data["red-times"].append({
            "start_time": start_time,
            "end_time": end_time
        })

        save_json(db_data, 'db.json')

        return jsonify({"status": "Red time added successfully"}), 200
    except Exception as e:
        print(f"Error adding red times: {e}")
        return jsonify({"error": "Failed to add red times"}), 500


@bp2.route('/get-red-times', methods=['GET'])
def red_times():
    red_times = get_all_red_times()
    return jsonify(red_times)

@bp2.route('/delete-red-time', methods=['POST'])
def delete_red_time():
    try:
        data = load_json()
        request_data = request.get_json()
        start_time = request_data.get('start_time')
        end_time = request_data.get('end_time')
        
        if not start_time or not end_time:
            return jsonify({"error": "Invalid data"}), 400
        
        red_times = [rt for rt in data.get('red-times', []) if not (rt['start_time'] == start_time and rt['end_time'] == end_time)]
        data['red-times'] = red_times
        save_json(data)
        
        return jsonify({"status": "Red time deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# @bp2.route('/accounts', methods=['GET'])
# def accounts():
#     data = json.loads("./db")

#     unique_logins = set(account["login"] for account in data["accounts"])

#     unique_logins_list = list(unique_logins)

#     print(unique_logins_list)
    