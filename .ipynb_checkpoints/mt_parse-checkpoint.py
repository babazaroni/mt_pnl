from mt_classes import *

def has_class(tokens,cl):
    for token in tokens:
        if type(token) is cl:
            return True
    return False

def get_token(tokens,cl):
    for token in tokens:
        if type(token) is cl:
            return token
        
    return None

def get_token_after(tokens,cl1,cl2):
    
    found = False
    for token in tokens:
        if found is False:
            #print("get token after:",type(cl1).__name__,type(cl2).__name__)
            
            if type(cl1).__name__ == 'type':
 #           if inspect.isclass(cl1):
                if type(token) is cl1:
                    found = True
            else:
                if token is cl1:
                    found = True
        else:
            if type(token) is cl2:
                return token
    return None
    

count = 0


def count_shorted(tokens,timestamp,text):
    
    shorted1 = get_token(tokens,Action_shorting)
    shorted2 = get_token_after(tokens,shorted1,Action_shorting)
    
    if shorted1 and shorted2:
        print(text)
    pass

class StopEvent():
    def __init__(self):
        self.stop_fields = {}
    def __repr__(self):
        s = 'stop,{},'.format(self.stop_fields['sym'])
        if self.stop_fields['type'] == 'price':
            return s +'{}'.format(self.stop_fields['price'])
        else:
            return s + '{}'.format(self.stop_fields['type'])

        
def get_stop(tokens,timestamp,text):
    
    symbol = get_token(tokens,Symbol)
    
    stop = get_token(tokens,Stop)
    if stop:
        price = get_token_after(tokens,stop,Price)
        if price:
            se = StopEvent()
            se.stop_fields['sym'] = '{}'.format(symbol)
            se.stop_fields['type'] = 'price'
            se.stop_fields['price'] = price.price
            return [se]
        
        number = get_token_after(tokens,stop,Number)
        if number:
            se = StopEvent()
            se.stop_fields['sym'] = '{}'.format(symbol)
            se.stop_fields['type'] = 'price'
            se.stop_fields['price'] = number.number
            return [se]

            

    return []
        
def get_stopx(tokens,timestamp,text):
    
    return []
    
    print('get_stop')
    print(text)

    text_split = text.split()

    symbol = get_token(tokens,Symbol)
    
    if not symbol:
        print('get stop: no symbol',text)
        return options
    
    stop = get_token(tokens,Stop)
    
    stops = []
    
    
    if stop:
        #print("get_stop: found stop at:",stop.index,len(text_split))
        se = StopEvent()
    
        se.stop_fields['ts'] = timestamp
        se.stop_fields['sym'] = '{}'.format(symbol)
        if len(text_split)-1 > stop.index:
            #print("get_stop more words")
            next = text_split[stop.index + 1]
            print("get_stop next:",next)
            next = next.rstrip(',.')
            price = Price(0,next)
            if price.valid:
                se.stop_fields['type'] = 'price'
                se.stop_fields['price'] = price.price
                #print(symbol,'stop1:',price,next)
            else:
                if get_token_after(tokens,stop,Premium):
                    se.stop_fields['type'] = '2xpremium'
                else:
                    if next.lower() == 'breakeven':
                        #print('get stop breakeven')
                        se.stop_fields['type'] = 'breakeven'
                    else:
                        if next.lower() == 'tighter':
                            price = get_token_after(tokens,stop,Price)
                            if price:
                                se.stop_fields['type'] = 'tighter'
                                se.stop_fields['price'] = price.price
                        else:
                            if next.lower() == 'low':
                                se.stop_fields['type'] = 'low'
                            else:
                                if next.lower() == 'high':
                                    se.stop_fields['type'] = 'high'
                                else:
                                    print(symbol,'stop word:[',next,']',text)
        
        stops.append(se)       
    else:
        #print(symbol,"no stop")
        pass
        
        
    return stops

    
class Event():
    def __init__(self):
        self.option = {}
    def __repr__(self):
        s = str(self.option['condition']) + ',' if self.option['condition'] is not None else ''
        return s + self.option['action'] + ',' + self.option['sym'] + ',' + self.option['spread_type'] + ',' + self.option['strike_date'] + ',' + str(self.option['strikes'])
    

def get_options(tokens,timestamp,text):
    global count
    
    
    options = []
    
    action = None
    symbol = None
    condition = None
    
#    print("get option entry: ",text)
    
    for i,token in enumerate(tokens):
        
        if not symbol:
            if type(token) is Symbol:
                symbol = token

        if action:
            
            if i+1 < len(tokens):
                next_token = tokens[i+1]
            else:
                next_token = None
            
            if type(token) is Strike_date or type(token) is Strike_day:
                strike_date = token
                if type(next_token) is Spread_type:
                    spread_type = next_token
                
            if type(token) is Strikes:
                strikes = token
                if type(next_token) is Spread_type:
                    spread_type  = next_token
                
            #if symbol and spread_type and strike_date and strikes:
            if type(action) is Action_shorting and symbol and strike_date and strikes:  # if no spread_type, then deduce from strikes and current price

                #if type(action) is Action_shorting:
                count = count + 1
                #print("get options, found option",count,symbol,spread_type,strike_date,strikes)
                e = Event()

                e.option['ts'] = timestamp
                e.option['action'] = str(action)
                e.option['sym'] = '{}'.format(symbol)
                e.option['spread_type'] = str(spread_type)
                e.option['strike_date'] = '{}'.format(str(strike_date))
                e.option['strikes'] = strikes.aslist()
                e.option['condition'] = condition

                options.append(e)
                
                action = None

        else:
            
            if not condition:
                if type(token) is Condition:

                    condition = token;
                
                
            if type(token) is Action_shorting:
                action = token
            if type(token) is Action_shorted:
                action = token
                
#            print('action',str(action))
                
            spread_type = strike_date = strikes = None
            
    if len(options):
        pass
    else:
#        mt = GREEN + 'no options foune: ' + str(symbol) + ' ' + text + END
#        display(Markdown(mt))
#        print("no options found for [{0}] text:".format(symbol),text)
        pass
    
            
    return options

def check_pair_cents(timestamp,tokens,i,token1,token2):
    
    if type(token1) is not Unknown or type(token2) is not Unknown: return False

    
    if token2.text.lower().startswith('cents'):
        #print('found cents:',token1.text)
        number = Number(i,token1.text.lstrip('('))
        if number.valid:
            price = Price(i,'$0')
            price.price = number.number/100.0
            tokens[i].valid = False
            tokens[i+1] = price
            #print('check_pair_cents ',str(price))
        
    return False

def check_pair_dte(timestamp,tokens,i,token1,token2):
    
    if type(token1) is not Unknown or type(token2) is not Unknown: return False
    
    if token2.text.upper().startswith('DTE'):
        strike_date = Strike_date(i,token2.text,timestamp,token1.text)
        if strike_date.valid:
            tokens[i].valid = False
            tokens[i+1] = strike_date
            return True
    
    return False

def check_pair_date_strikes(timestamp,tokens,i,token1,token2):
    
    if type(token2) is Unknown:
        if type(token1) is Unknown:
            
            pair1 = token1.text.split('/')
            pair2 = token2.text.split('/')
            
            if len(pair1) == 2 and len(pair2) ==2:
                if pair1[0].startswith('(') and pair1[1].endswith(')'):
                
                    sd = Strike_date(i,token1.text,timestamp,"")
                    strikes = Strikes(i,token2.text)
                    if sd.valid and strikes.valid:
                        tokens[i] = sd
                        tokens[i+1] = strikes
                        return True
        else:
            if type(token1) is Strike_date:
                strikes = Strikes(i,token2.text)
                if strikes.valid:
                    tokens[i+1] = strikes
                    return True
    return False

    

def check_pair_lot_quantity(timestamp,tokens,i,token1,token2):
    
    if type(token1) is Unknown and type(token2) is Unknown:
            
        lotQuantity = LotQuantity(i,token1.text,token2.text)
        if lotQuantity.valid:
            token1.valid = False
            tokens[i+1] = lotQuantity
            return True
        
    return False

def check_pair_condition(timestamp,tokens,i,token1,token2):
    
    if type(token1) is Unknown and type(token2) is Unknown:
        
        condition = Condition(i,token1.text)
        price = Price(i+1,token2.text)
        if condition.valid and price.valid:
            print('check_pair_condition ------------------------------------------',str(condition),str(price))
            condition.price = price
            tokens[i] = condition
            token2.valid = False
            return True
        
    return False
    
            
            
def analyse_pairs(timestamp,tokens,function):
    
    for i in range(len(tokens)-1):
        token1 = tokens[i]
        token2 = tokens[i+1]
        
        if function(timestamp,tokens,i,token1,token2):
            break
            
    tokens = [token for token in tokens if token.valid] #remove any invalid tokens
    
    return tokens

def det_class(c,tokens,pos,text):
    obj = c(pos,text)
    if obj.valid:
        tokens[pos] = obj
    return obj.valid
  
    
def create_action_tokens(timestamp,tokens):
    
    
#    print('create_tokens:',text)

    
    last = None

    for i,w in enumerate(tokens):
        
        if type(w) != Unknown:
            continue
        
        
        if i:
            last = tokens[i-1]
                
        if w.text.startswith('ADJ'):
            tokens[i] = Adj(i,w.text)
            continue
            
        if det_class(Symbol,tokens,i,w.text): continue
        if det_class(Month_slash_day,tokens,i,w.text): continue
        if det_class(Action_shorting,tokens,i,w.text):continue
        if det_class(Action_shorted,tokens,i,w.text):continue
        if det_class(Month,tokens,i,w.text):continue
        if det_class(Strikes,tokens,i,w.text):continue
        if det_class(Spread_type,tokens,i,w.text):continue
        if det_class(Stop,tokens,i,w.text):continue
        if det_class(Close,tokens,i,w.text):continue
        if det_class(Period,tokens,i,w.text):continue
        if det_class(Price_per_share,tokens,i,w.text):continue
        if det_class(Price,tokens,i,w.text):continue
        #if det_class(Condition,tokens,i,w.text):continue
        if det_class(Watch,tokens,i,w.text):continue
        if det_class(Cover,tokens,i,w.text):continue
        if det_class(Premium,tokens,i,w.text):continue
        if det_class(Condor,tokens,i,w.text):continue
        if det_class(MidPoint,tokens,i,w.text):continue
        if det_class(Number,tokens,i,w.text):continue
            
    return tokens

        
        

def create_tokens(timestamp,text):
    
    # ignore single characters .  Probably typos that interfere with pairing.
    tokens = [Unknown(pos,fragment) for pos,fragment in enumerate(text.split()) if fragment.isnumeric() or len(fragment) != 1 or (fragment.isalpha())]
    
    tokens = analyse_pairs(timestamp,tokens,check_pair_condition)
    
    tokens = analyse_pairs(timestamp,tokens,check_pair_cents)
    
    tokens = analyse_pairs(timestamp,tokens,check_pair_dte)
    
    tokens = analyse_pairs(timestamp,tokens,check_pair_lot_quantity)
    
    tokens = analyse_pairs(timestamp,tokens,check_pair_date_strikes)
                                        
    tokens = create_action_tokens(timestamp,tokens)
    
            
    tokens = [token for token in tokens if type(token) != Unknown]
    
    return tokens
    
    
