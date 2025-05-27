import math


def calculate_lot_size(account_balance, risk_percentage, stop_loss_pips, pip_value):
    """
    prefered!
    
    Calculate the lot size for a trading bot based on risk management principles.

    Parameters:
    account_balance (float): The current balance of the trading account.
    risk_percentage (float): The percentage of the account balance to risk on a single trade.
    stop_loss_pips (float): The number of pips to set for the stop loss.
    pip_value (float): The value of one pip in the account currency.

    Returns:
    float: The calculated lot size.
    """
    risk_amount = (risk_percentage / 100) * account_balance
    pip_risk = stop_loss_pips * pip_value
    lot_size = risk_amount / pip_risk
    
    return lot_size


def qty(myBalance):
    lot = 0.0
    if myBalance < 300:
        lot =  0.01
    elif myBalance >= 300 and myBalance <= 499:
        lot =  0.02
    elif myBalance >= 500 and myBalance <= 999:
        lot = 0.03
    elif myBalance >= 1000 and myBalance <= 1499:
        lot = 0.04
    elif myBalance >= 1500 and myBalance <= 1999:
        lot = 0.05
    elif myBalance >= 2000 and myBalance <= 2499:
        lot = 0.06
    elif myBalance >= 2500 and myBalance <= 2999:
        lot = 0.07
    elif myBalance >= 3000 and myBalance <= 3999:
        lot = 0.08
    elif myBalance >= 4000 and myBalance <= 5000:
        lot = 0.09
    elif myBalance > 5000 and myBalance <= 9999:
        lot = 0.1 * (math.floor(myBalance/1000)+1)
    elif myBalance >= 10000 and myBalance <= 100000:
        lot = 1
    elif myBalance > 100000 and myBalance <= 500000:
        lot = 2
    else:
        lot = 3

    return lot
    