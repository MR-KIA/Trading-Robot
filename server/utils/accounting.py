import MetaTrader5 as mt5
from server.utils.initializations import login


def total_positons():
    positions_total=mt5.positions_total()
    return positions_total


def balance():
    account_info = mt5.account_info()
    if account_info is None:
        raise ValueError("fuck u")
    balance = account_info._asdict().get('balance')
    if balance is None:
        raise ValueError("Balance information is missing.")
    return balance


def profit():
    positions = mt5.positions_get()
    profit = 0
    for position in positions:
        profit += position._asdict()['profit']
    return profit


class MT5Connection:
    def __init__(self, account_number, password, server):
        self.account_number = account_number
        self.password = password
        self.server = server
        self.connect()

    def connect(self):
        mt5.initialize(login=self.account_number, password=self.password, server=self.server)
        if not mt5.terminal_info():
            raise Exception("Failed to initialize MetaTrader 5 connection")

    def is_connected(self):
        terminal_info = mt5.terminal_info()
        return terminal_info is not None and terminal_info.connected

    def reconnect(self):
        mt5.shutdown() 
        self.connect()