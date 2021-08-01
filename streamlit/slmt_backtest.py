from mt_strategy import *
from mt_parse import *
import pprint
import datetime as dt

HOURS_TO_EST = 3

def get_premiums(timestamps,action_lists):

    results = []

    for ts,action_list in zip(timestamps,action_lists):
        premium = 0
        for event in action_list:
            if type(event) is Event:
                if event.option['action'] == 'shorting':
                    ts_dt = dt.datetime.strptime(event.option['ts'], '%Y-%m-%dT%H:%M:%S') + timedelta(hours=HOURS_TO_EST)

                    orderx = Order(ts_dt,event.option['sym'],event.option['spread_type'],event.option['strike_date'],event.option['strikes'])
                    trade = Trade(orderx)
                    if trade.has_data():

                        trade.init_data()

                        premium_only = Premium_only()
                        premium = premium_only.trade(trade)

            if type(event) is StopEvent:
                pass

        results.append(premium)

    return results

def get_premiums_strings(premiums):
    results = []
    
    for premium in premiums:
        if premium == 0:
            results.append('')
        else:
            results.append(str(round(premium,2)))

    return results

def get_backtest_df(timestamps,action_lists):

    df = pd.DataFrame()

    df['premium_data'] = get_premiums(timestamps,action_lists)

    df['premiums'] = get_premiums_strings(df['premium_data'])

    pprint.pprint(df)

    return df,['premium_data']