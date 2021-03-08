class Market_base():
    timestamp = None
    event = None
        
class Market(Market_base):
    info = {}



class expiration():
    month = None
    day = None
    

    
class vertical():
    expiration = None
    strike1 = None
    strike2 = None
    stop = None
    
class stop_fixed():
    value = None
    
class stop_bar():
    bar_length = None # minute width
    description = None # high, low

class conditional():
    above = None # true, false for below
    level = None
    
class event():
    symbol = None
    conditional = None
    action = None #buy/sell
    option  = None # vertical, iron condor, etc
