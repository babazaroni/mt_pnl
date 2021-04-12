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
    
    
def create_tokens(timestamp,text):
    
    
#    print('create_tokens:',text)

    obs = []
    
    
    text_split = text.split()
    
    last = None

    for i,w in enumerate(text_split):
        
        
        if i:
            last = text_split[i-1]
                
        if w.startswith('ADJ'):
            obs.append(Adj(i,w))
            continue
            
        if det_symbol(i,w):
            obs.append(Symbol(i,w))
            continue
            
        if det_date_event(i,w):
            obs.append(Month_slash_day(i,w))
            continue
            
        if det_shorting(i,w):
            obs.append(Action_shorting(i,w))
            continue
            
        if det_shorted(i,w):
            obs.append(Action_shorted(i,w))
            continue

        if det_month(i,w):
            obs.append(Month(i,w))
            continue
            
        if det_strike_day(i,w,timestamp,last):
            obs.append(Strike_day(i,w,timestamp,last))
            continue
            
        if det_strike_date(i,w,timestamp,last):
            obs.append(Strike_date(i,w,timestamp,last))
            continue
            
        if det_strikes(i,w):
            obs.append(Strikes(i,w))
            continue
            
        if det_spread_type(i,w):
            print("create_tokens: detected spread type:",w)
            obs.append(Spread_type(i,w))
            continue
            
        if det_stop(i,w):
            obs.append(Stop(i,w))
            continue
            
        if det_close(i,w):
            obs.append(Close(i,w))
            continue
            
        if det_period(i,w):
            print("appending")
            obs.append(Period(i,w))
            continue

            
        if det_price_per_share(i,w):
            obs.append(Price_per_share(i,w))
            continue

        if det_price(i,w):
            obs.append(Price(i,w))
            continue
            
        if det_condition(i,w):
            obs.append(Condition(i,w))
            continue
            
        if det_watch(i,w):
            obs.append(Watch(i,w))
            continue
            
        if det_cover(i,w):
            obs.append(Cover(i,w))
            continue
            
        if det_premium(i,w):
            obs.append(Premium(i,w))
            continue

        if det_condor(i,w):
            obs.append(Condor(i,w))
            continue
            
        if det_midpoint(i,w):
            obs.append(MidPoint(i,w))
            continue
            
    return obs
