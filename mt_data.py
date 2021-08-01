import requests
import json
from mt_utils import mt_dict_to_df,mt_df_to_dict

import datetime as dt
import pandas as pd
import pprint



REQUEST_MARKER = '_'


option_urls = [
#    "https://www.dropbox.com/s/ahlb9ldhnmemmwn/option_bars.json?dl=1"
#    "https://www.dropbox.com/s/43fxgji48itj3on/qc_option_bars.json?dl=1"
    "https://www.dropbox.com/s/1lszx4xveis9x5i/qc_option_bars_100.json?dl=1"

]

underlying_urls = [
#    "https://www.dropbox.com/s/ll8xa6xb1xhrhv7/underlying_bars.json?dl=1"
#     "https://www.dropbox.com/s/j4ivn1c68vl8svm/qc_underlying.json?dl=1"
]

options_cache = []
underlying_cache = []


#option_urls = ["/home/cc/Dropbox/option_bars.json"]
#underlying_urls = ["/home/cc/Dropbox/underlying_bars.json"]


def download(url):
    r = requests.get(url)
    return r.content

def download_data(urls):
    data = []
    for url in urls:
        print('download_data:', url)
        
        data.extend(json.loads(download(url)))
        print("download_data dict data: ",len(data))
        
        #with open(url,'r') as infile:
        #    data.extend(json.load(infile))
        
    df = mt_dict_to_df(data)
    
    print("Download data df len:",len(df))

    return df

def prepare_options_cache(options_cache):
    
    print("prepare_options_cache",options_cache.columns)

    options_cache['time'] = options_cache['time'].dt.to_pydatetime()
    options_cache['expiry'] = options_cache['expiry'].apply(lambda x: dt.datetime.strptime(x,'%Y-%m-%d %H:%M:%S').date())    
    options_cache['symbol'] = options_cache['symbol'].apply(lambda x: x.split()[0])
    
    
    print("sorting options_cache")
    options_cache.sort_values(by=['symbol','type','strike','expiry','time'],inplace=True)
    print("finished")
    options_cache.drop_duplicates(inplace=True)
    print("after drop",len(options_cache))

def prepare_underlying_cache(underlying_cache):
    
    print("prepare_underlying_cache",underlying_cache.columns)

    underlying_cache['time'] = underlying_cache['time'].apply(lambda x: x.to_pydatetime())
    
    print('sorting underlying_cache')
    underlying_cache.sort_values(by=['symbol','time'],inplace=True)
    print('finished')
    underlying_cache.drop_duplicates(inplace=True)
    print("after drop:",len(underlying_cache))
    
def is_business_day(date):
    return bool(len(pd.bdate_range(date,date)))

from pandas.tseries.holiday import USFederalHolidayCalendar
from datetime import date

cal = USFederalHolidayCalendar()
holidays = []

def find_holidays(df):
    global holidays
    
    print("entering find_holidays")
    
    print("find_holidays",type(df['time'][0]))
    
    holidays = [d.date() for d in cal.holidays(start = df['time'][0], end= date.today())]
    
    print("find_holidays:",holidays)
    
def get_holidays():
    return holidays
    
def missing_data_by_date(df,start_time,end_time): 
    dates = list(set([time.date() for time in df['time']]))
        
    after_hours_time = dt.time(16,31,0)
    
    if start_time.time() > after_hours_time:
        print("=================== missing_data_by_date skipping first day")
        skip_first_day = True
    else:
        skip_first_day = False
        
    
    for date in pd.bdate_range(start_time.date(),end_time.date()):
        if skip_first_day:
            skip_first_day = False
            continue
        
        if date.date() not in dates:
            if date.date() in holidays:
                print("found holiday",date.date())
            else:
                print("======================= could not find date ",date.date(),dates)
                return True
            
    print("missing_data_by_date found all days")
            
    return False

    
def search_underlying_cache(sym,start_time,end_time,request_marker = ''):
    global holidays
    
    if not len(underlying_cache):
#        return pd.DataFrame(),0
        return pd.DataFrame()
    
    sym = sym + request_marker
    
    
    df = underlying_cache[ (underlying_cache['symbol'] == sym) &
                        (underlying_cache['time'] >= start_time) &
                       (underlying_cache['time'] <= end_time)]
        
    if missing_data_by_date(df,start_time,end_time):
        return pd.DataFrame()
        
    return df
    
def search_options_cache(sym,expiry,strike,spread_type,ts_start,ts_end,request_marker = ''):

    
    if not len(options_cache):
        print("search_options_cache",sym,strike,spread_type,"NOT FOUND IN CACHE")
        return pd.DataFrame()
    
    sym = sym + request_marker
    
    df = options_cache[ (options_cache['symbol'] == sym)  &
                    (options_cache['type'] == ('Call' if spread_type == 'CALL' else 'Put'))  &
                    (options_cache['strike'] == strike)    &
                    (options_cache['expiry'] == expiry)   &
                    (options_cache['time'] >= ts_start)  &
                    (options_cache['time'] <= ts_end) ]
    
    print("search_options_cache found",sym,len(df))
    
    
    if missing_data_by_date(df,ts_start,ts_end):
        return pd.DataFrame()
    
    return df

def add_underlying_cache(df):
    global underlying_cache

    underlying_cache = concat_dfs(underlying_cache,df)
    
def get_underlying_cache():
    global underlying_cache
    print('get_underlying_cache len:',len(underlying_cache))
    return underlying_cache

def add_options_cache(df):
    global options_cache
    
    options_cache = concat_dfs(options_cache,df)
    
    print("add_options_cache",len(df),len(options_cache))
    
    
def get_options_cache():
    global options_cache
    return options_cache



def data_init():
    
    options_cache = download_data(option_urls)
    

    if len(options_cache):
        prepare_options_cache(options_cache)
        print('data_init')
        print("options_cache")
        print(options_cache)

    underlying_cache = download_data(underlying_urls)

    if len(underlying_cache):
        prepare_underlying_cache(underlying_cache)
        
        find_holidays(underlying_cache)
        
    return options_cache,underlying_cache

def data_global_set(options_data,underlying_data):
    global options_cache,underlying_cache
    
    
    options_cache = options_data
    underlying_cache = underlying_data
    
    print('data_global_set',options_cache,underlying_cache)
    
def data_info():
    print(len(options_cache),len(underlying_cache))
    



def save_underlying_cache(file_path):
    global underlying_cache

    try:
        underlying_cache.set_index(['symbol','time'],inplace = True)
    except:
        pass #already indexed by symbol and time

    underlying_cache_dict = mt_df_to_dict(underlying_cache)

    with open(file_path,'w') as outfile:
        json.dump(underlying_cache_dict,outfile)
        
def save_options_cache(file_path):
    global options_cache

    try:
        options_cache.set_index(['symbol','time'],inplace = True)
    except:
        pass #already indexed by symbol and time

    options_cache_dict = mt_df_to_dict(options_cache)

    with open(file_path,'w') as outfile:
        json.dump(options_cache_dict,outfile)

        
        
def convert_underlying_cache():
    global underlying_cache
    try:
        underlying_cache.set_index(['symbol','time'],inplace = True)
    except:
        pass #already indexed by symbol and time

    underlying_cache_dict = mt_df_to_dict(underlying_cache)
    
    underlying_cache = mt_dict_to_df(underlying_cache_dict)

    





