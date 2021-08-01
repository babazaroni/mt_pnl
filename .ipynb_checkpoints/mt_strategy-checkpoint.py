from datetime import datetime
from datetime import timedelta
from mt_data import search_underlying_cache,search_options_cache
import pandas as pd


#OPTION_PRICE_COL = 'close'
OPTION_PRICE_COL = 'mid'

multiplier = {'TSLA':5,'AAPL':4}



class Premium_only():
    column_title = 'premium'
    pnl = 0
    events = 0
    spread_sum = 0
    def trade(self,trade):
        self.events = self.events + 1
        self.spread_sum = self.spread_sum + abs(trade.order.strike_sell - trade.order.strike_buy)
        premium = trade.price_sell - trade.price_buy
        self.pnl = self.pnl + premium
        return premium
    def summary_results(self):
        return "Strategy Premium only: trades = {} average premium to strike_spread = {} spread sum = {}".format(self.events,round(self.spread_sum/self.pnl,2),self.spread_sum)
        
class Strategy_let_expire():
    name = 'expire'
    events_trade = 0
    events_breach = 0
    pnl = 0
    column_title = "expire"
    
    def trade(self,trade):
        
        expire_value = get_expire_result(trade)
                    
        if expire_value:
            self.events_breach = self.events_breach + 1
            self.pnl = self.pnl + expire_value
            
        self.events_trade = self.events_trade + 1
        
        return expire_value
    
    def description(self):
        return "Hold trade till expiration."
    
    def summary_results(self):
        return "Strategy Let Expire summary. trades: {}  breaches: {}  breach ratio: {} ".format(self.events_trade, self.events_breach, round(self.events_breach/(self.events_trade),3))
    
class Strategy_p_loss():
    multiple = None
    pnl = 0
    column_title = "2xLoss"
    def __init__(self,multiple):
        self.multiple = multiple
        
    def trade(self,trade):
        
        premium = trade.price_sell - trade.price_buy
        
        minute_count = 0
        for x,row in trade.bars_premium.iterrows():
            cost_to_close = row['mid']
            if cost_to_close >= (premium * self.multiple):
                minute_count = minute_count + 1
                if minute_count >= 30:
                    self.pnl = self.pnl - cost_to_close
                    #print("strategy 2xPrem closing",row['time'],cost_to_close)
                    return -cost_to_close
            else:
                minute_count = 0
                
                
        expire_result = get_expire_result(trade)
        
        self.pnl = self.pnl + expire_result
                
        return expire_result
        
    
    def description(self):
        return ("Close trade when cost to close is twice premium received")
    
    def summary_results(self):
        return ""
    
class Strategy_p_profit():
    
    multiple = None
    pnl = 0
    column_title = "2xGain"
    
    def __init__(self,multiple):
        self.multiple = multiple
        
    def trade(self,trade):
        
        premium = trade.price_sell - trade.price_buy
        
        minute_count = 0
        for x,row in trade.bars_premium.iterrows():
            cost_to_close = row['mid']
            if cost_to_close <= (premium * self.multiple):
                minute_count = minute_count + 1
                if minute_count >= 30:
                    self.pnl = self.pnl - cost_to_close
                    #print("strategy 2xPrem closing",row['time'],cost_to_close)
                    return -cost_to_close
            else:
                minute_count = 0
                
        expire_result = get_expire_result(trade)
        
        self.pnl = self.pnl + expire_result
                
        return expire_result
        
    
    def description(self):
        return ("Close trade when cost to close is half premium received")
    
    def summary_results(self):
        return ""
    
class Strategy_breakpoints():
    pnl = 0
    column_title = "bpoints"
    
    
class Order():
    ts_start = None
    symbol = None
    expiry = None
    spread_type = None
    strike_sell = None
    strike_buy = None
    
    def __init__(self,ts,sym,spread_type,strike_date,strikes):
        #print('order:',ts,sym,spread_type,strike_date,strikes)
        self.ts_start = ts
        self.symbol = sym
        self.expiry = datetime.strptime(strike_date, '%Y-%m-%d') + timedelta(hours=16)
        self.spread_type = spread_type
        
        if spread_type == 'CALL':
            self.strike_sell = min(strikes)
            self.strike_buy = max(strikes)
        if spread_type == 'PUT':
            self.strike_sell = max(strikes)
            self.strike_buy = min(strikes)
            
            
class Trade():
    order = None
    bars_underlying = None
    bars_sell = None
    bars_buy = None
    bars_premium = None
    
    price_sell = None
    price_buy = None
    price_underlying_close = None
    
    
    def __init__(self,order):
        
        self.order = order
        self.bars_underlying = search_underlying_cache(order.symbol,order.ts_start,order.expiry)
        self.bars_sell = search_options_cache(order.symbol,order.expiry.date(),order.strike_sell,order.spread_type,order.ts_start,order.expiry)
        self.bars_buy = search_options_cache(order.symbol,order.expiry.date(),order.strike_buy,order.spread_type,order.ts_start,order.expiry)
        
        s1 = pd.merge(self.bars_sell,self.bars_buy, how='inner', on=['time'])
        s1.dropna(inplace=True)
        frame = { 'time': s1['time'],'symbol': s1['symbol_x'],OPTION_PRICE_COL: s1[OPTION_PRICE_COL+'_x'] - s1[OPTION_PRICE_COL+'_y']}
        self.bars_premium = pd.DataFrame(frame)

    def has_data(self):
        return len(self.bars_underlying) and len(self.bars_sell) and len(self.bars_buy)
    
    def init_data(self):
#        print("class Trade",type(self.bars_sell),type(self.bars_buy),type(self.bars_underlying))
#        print("class Trade",len(self.bars_sell),len(self.bars_buy),len(self.bars_underlying))

        self.price_sell = self.bars_sell.iloc[0][OPTION_PRICE_COL]
        self.price_buy = self.bars_buy.iloc[0][OPTION_PRICE_COL]
        self.price_underlying_close = self.bars_underlying.iloc[-1]['close']
        
        if self.order.symbol in multiplier.keys():
            self.price_underlying_close = self.price_underlying_close * multiplier[self.order.symbol]
            
            
def calc_expire_result(strike_buy,strike_sell,close_price,not_breached_sell,not_breached_buy):
                
    if not_breached_sell:
        return 0
    
    if not_breached_buy:
        #print(strike_sell,"-",close_price)
        return strike_sell - close_price
    else:
        #print(strike_sell,"-",strike_buy)
        return strike_sell - strike_buy
    
def get_expire_result(trade):
    if trade.order.spread_type == 'CALL':
        expire_value = calc_expire_result(trade.order.strike_buy,trade.order.strike_sell,trade.price_underlying_close,trade.price_underlying_close <= trade.order.strike_sell,trade.price_underlying_close <= trade.order.strike_buy)
    else:
        expire_value = -calc_expire_result(trade.order.strike_buy,trade.order.strike_sell,trade.price_underlying_close,trade.price_underlying_close >= trade.order.strike_sell,trade.price_underlying_close >= trade.order.strike_buy)

    return expire_value

