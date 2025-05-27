import MetaTrader5 as mt5

def stp(ticket, current_price, profit_threshold_percentage): #yet to be completed!
    
    position = mt5.positions_get(ticket=ticket)
    
    if position:
        initial_tp = position[0].tp
        open_price = position[0].price_open
        
        
        current_profit_percentage = ((current_price - open_price) / open_price) * 100
        
        if current_profit_percentage >= profit_threshold_percentage:
            adjusted_tp = initial_tp + (current_profit_percentage - profit_threshold_percentage)
        else:
            adjusted_tp = initial_tp
        
        
        request = {
                "action": mt5.TRADE_ACTION_SLTP,
                "position": position[0].ticket,
                "sl": position[0].sl,
                "tp": adjusted_tp
            }
            
        result = mt5.positions_modify(request)
            
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            print(f"Take profit updated successfully to {adjusted_tp}")
        else:
            print(f"Failed to update take profit. Error: {result}")
        
    
    else:
        print(f"Position with ticket {ticket} not found")
        
        return None