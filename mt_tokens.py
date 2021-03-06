from mt_classes import *
import re


def det_symbol(pos,text): sym = Symbol(pos,text); return sym.valid
def det_month(pos,text):month = Month(pos,text);return month.valid;
def det_date_event(pos,text):msd = Month_slash_day(pos,text);return msd.valid
def det_shorting(pos,text):action = Action_shorting(pos,text);return action.valid
def det_shorted(pos,text): action = Action_shorted(pos,text);return action.valid
def det_strike_day(pos,text,timestamp,last): strike_day = Strike_day(pos,text,timestamp,last);return strike_day.valid
def det_strike_date(pos,text,timestamp,last):strike_date = Strike_date(pos,text,timestamp,last);return strike_date.valid
def det_strikes(pos,text):strikes = Strikes(pos,text);return strikes.valid
def det_spread_type(pos,text):spread_type = Spread_type(pos,text);return spread_type.valid
def det_price(pos,text):price = Price(pos,text);return price.valid
def det_price_per_share(pos,text):pps = Price_per_share(pos,text);return pps.valid
def det_stop(pos,text): stop = Stop(pos,text);return stop.valid
def det_close(pos,text): close = Close(pos,text);return close.valid
def det_condition(pos,text): condition = Condition(pos,text);return condition.valid
def det_watch(pos,text): watch = Watch(pos,text);return watch.valid
def det_cover(pos,text): cover = Cover(pos,text);return cover.valid
def det_premium(pos,text): premium = Premium(pos,text);return premium.valid
def det_condor(pos,text): condor = Condor(pos,text);return condor.valid
def det_period(pos,text): period = Period(pos,text);return period.valid
def det_midpoint(pos,text): mp = MidPoint(pos,text);return mp.valid
    
    
def create_tokens(timestamp,tokens):
    
    
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
            
        if det_symbol(i,w.text):
            tokens[i] = Symbol(i,w.text)
            continue
            
        if det_date_event(i,w.text):
            tokens[i] = Month_slash_day(i,w.text)
            continue
            
        if det_shorting(i,w.text):
            tokens[i] = Action_shorting(i,w.text)
            continue
            
        if det_shorted(i,w.text):
            tokens[i] = Action_shorted(i,w.text)
            continue

        if det_month(i,w.text):
            tokens[i] = Month(i,w.text)
            continue
            
        #if det_strike_day(i,w,timestamp,last):
        #    obs.append(Strike_day(i,w,timestamp,last))
        #    continue
            
        #if det_strike_date(i,w,timestamp,last):
        #    obs.append(Strike_date(i,w,timestamp,last))
        #    continue
            
        if det_strikes(i,w.text):
            tokens[i] = Strikes(i,w.text)
            continue
            
        if det_spread_type(i,w.text):
            #print("create_tokens: detected spread type:",w.text)
            tokens[i] = Spread_type(i,w.text)
            continue
            
        if det_stop(i,w.text):
            tokens[i]= Stop(i,w.text)
            continue
            
        if det_close(i,w.text):
            tokens[i] = Close(i,w.text)
            continue
            
        if det_period(i,w.text):
            tokens[i] = Period(i,w.text)
            continue
            
        if det_price_per_share(i,w.text):
            tokens[i] = Price_per_share(i,w.text)
            continue

        if det_price(i,w.text):
            tokens[i] = Price(i,w.text)
            continue
            
        if det_condition(i,w.text):
            tokens[i] = Condition(i,w.text)
            continue
            
        if det_watch(i,w.text):
            tokens[i] = Watch(i,w.text)
            continue
            
        if det_cover(i,w.text):
            tokens[i] = Cover(i,w.text)
            continue
            
        if det_premium(i,w.text):
            tokens[i] = Premium(i,w.text)
            continue

        if det_condor(i,w.text):
            tokens[i] = Condor(i,w.text)
            continue
            
        if det_midpoint(i,w.text):
            tokens[i] = MidPoint(i,w.text)
            continue
            
    return tokens
