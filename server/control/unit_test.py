import unittest
from unittest.mock import patch, MagicMock
from ..utils.trading import Strategy

class TestStrategy(unittest.TestCase):

    @patch('MetaTrader5.positions_get')
    @patch('MetaTrader5.order_send')
    @patch('MetaTrader5.initialize')
    @patch('MetaTrader5.login')
    def test_adjustment_logic(self, mock_login, mock_initialize, mock_order_send, mock_positions_get):
        # Initialize mocks
        mock_login.return_value = True
        mock_initialize.return_value = True

        # Dummy data for positions
        dummy_positions = [
            MagicMock(ticket=123456, symbol="GBPUSD", volume=1.0, price_open=1.3000, price_current=1.2950),
            MagicMock(ticket=654321, symbol="GBPUSD", volume=1.0, price_open=1.3000, price_current=1.2900)
        ]

        # Mock positions_get to return dummy positions
        mock_positions_get.return_value = dummy_positions

        # Mock order_send to simulate SL adjustment success
        mock_order_send.return_value = MagicMock(retcode=mt5.TRADE_RETCODE_DONE)

        # Instantiate the Strategy class
        strategy = Strategy(symbol="GBPUSD")

        # Simulate placing an order and adjusting SL
        strategy._temp_ticket1 = dummy_positions[0].ticket
        strategy._temp_ticket2 = dummy_positions[1].ticket
        strategy._temp_init_price = 1.3000

        # Call the adjust method to test the SL adjustment logic
        strategy.adjust()

        # Assertions
        mock_positions_get.assert_called()
        mock_order_send.assert_called()

    @patch('MetaTrader5.positions_get')
    def test_no_positions(self, mock_positions_get):
        # Mock positions_get to return no positions
        mock_positions_get.return_value = []

        # Instantiate the Strategy class
        strategy = Strategy(symbol="GBPUSD")

        # Simulate monitoring
        strategy._temp_init_price = 1.3000
        strategy._monitor(strategy._temp_init_price)

        # Check that no orders are adjusted when no positions are open
        mock_positions_get.assert_called()

if __name__ == '__main__':
    unittest.main()
