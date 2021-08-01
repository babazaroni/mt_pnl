import requests
import pandas as pd
import pystore
import datetime as dt
from pandas.tseries.holiday import USFederalHolidayCalendar
from pandas_market_calendars.exchange_calendar_nyse import NYSEExchangeCalendar
from dask import dataframe as dd
from mt_utils import concat_dfs


cal = USFederalHolidayCalendar()
holidays = [d.date() for d in cal.holidays(start = dt.datetime(2000,1,1) , end = dt.date.today())]

nysecal = NYSEExchangeCalendar()
nysesch = nysecal.schedule('2000-01-01', '2030-01-01')
dt.datetime(year = 2020,month = 7,day = 3) in nysesch.index


def download(url):
    r = requests.get(url)
    return r.content

def get_holidays():
    return holidays

def is_holiday(date):
    return not date in nysesch.index

def missing_data_by_date(df,start_time,end_time): 
    dates = list(set([time.date() for time in df['time']]))
#    print("missing_data_by date, dates in df:",dates)
        
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
            if date not in nysesch.index:
                continue
            
            print("========================= missind data for ",date)
            
            return True
        
 #       if date.date() not in dates:
 #           if date.date() in holidays:
 #               print("found holiday",date.date())
 #           else:
 #               print("======================= could not find date ",date.date(),dates)
 #               return True
            
#    print("missing_data_by_date: found all days")
            
    return False

def search_underlying_cache(collection,sym,start_time,end_time):
    try:
        item = collection.item(sym)
    except ValueError:
        return pd.DataFrame()
    
    data = item.data  # <-- Dask dataframe (see dask.pydata.org)
    metadata = item.metadata
    underlying_cache = item.to_pandas()
    
    df = underlying_cache[ (underlying_cache['symbol'] == sym)  &
                    (underlying_cache['time'] >= start_time)  &
                    (underlying_cache['time'] <= end_time) ]

    if missing_data_by_date(df,start_time,end_time):
        return pd.DataFrame()

    return df

def add_underlying_cache(collection,sym,df):
    #sd = dd.from_pandas(df,npartitions = 1)
    
#    print("add_options_cache sym,df:",sym)
#    print(df)
    try:
        item = collection.item(sym)
        data = item.data  # <-- Dask dataframe (see dask.pydata.org)
        metadata = item.metadata
        underlying_cache = item.to_pandas()
        underlying_cache = concat_dfs(underlying_cache,df)
        underlying_cache = underlying_cache.reset_index(drop=True)
        print("add_underlyint_cache add",len(df),len(underlying_cache))
        collection.write(sym, underlying_cache, metadata={'source': 'qc'},overwrite = True)
    except ValueError:
        print("add_underlying_cache wrote:",sym,len(df))
        collection.write(sym, df, metadata={'source': 'qc'})

def search_options_cache(collection,sym,expiry,strike,spread_type,ts_start,ts_end,request_marker = ''):
    
    try:
        item = collection.item(sym)
    except ValueError:
        return pd.DataFrame()
    
    data = item.data  # <-- Dask dataframe (see dask.pydata.org)
    metadata = item.metadata
    options_cache = item.to_pandas()
    
    sym = sym + request_marker
    
    expiry = dt.datetime.combine(expiry,dt.datetime.min.time())
    
    df = options_cache[ (options_cache['symbol'] == sym)  &
                    (options_cache['type'] == ('Call' if spread_type == 'CALL' else 'Put'))  &
                    (options_cache['strike'] == strike)    &
                    (options_cache['expiry'] == expiry)  &
                    (options_cache['time'] >= ts_start)  &
                    (options_cache['time'] <= ts_end) ]

        
    
    if missing_data_by_date(df,ts_start,ts_end):
        return pd.DataFrame()

    return df

def add_options_cache(collection,sym,df):
    #sd = dd.from_pandas(df,npartitions = 1)
    
#    print("add_options_cache sym,df:",sym)
#    print(df)
    try:
        item = collection.item(sym)
        data = item.data  # <-- Dask dataframe (see dask.pydata.org)
        metadata = item.metadata
        options_cache = item.to_pandas()
        options_cache = concat_dfs(options_cache,df)
        options_cache = options_cache.reset_index(drop=True)
        collection.write(sym, options_cache, metadata={'source': 'qc'},overwrite = True)
    except ValueError:
        print("add_options_cache wrote:",sym,len(df))
        collection.write(sym, df, metadata={'source': 'qc'})
        
def search_futures_cache(collection,sym,start_time,end_time):
    try:
        item = collection.item(sym)
    except ValueError:
        return pd.DataFrame()
    
    data = item.data  # <-- Dask dataframe (see dask.pydata.org)
    metadata = item.metadata
    underlying_cache = item.to_pandas()
    
    df = underlying_cache[ (underlying_cache['symbol'] == sym)  &
                    (underlying_cache['time'] >= start_time)  &
                    (underlying_cache['time'] <= end_time) ]

    if missing_data_by_date(df,start_time,end_time):
        return pd.DataFrame()

    return df

def add_futures_cache(collection,sym,df):
    #sd = dd.from_pandas(df,npartitions = 1)
    
#    print("add_options_cache sym,df:",sym)
#    print(df)
    try:
        item = collection.item(sym)
        data = item.data  # <-- Dask dataframe (see dask.pydata.org)
        metadata = item.metadata
        futures_cache = item.to_pandas()
        futures_cache = concat_dfs(futures_cache,df)
        futures_cache = futures_cache.reset_index(drop=True)
        print("add_futures_cache add",len(df),len(futures_cache))
        collection.write(sym, futures_cache, metadata={'source': 'qc'},overwrite = True)
    except ValueError:
        print("add_futures_cache wrote:",sym,len(df))
        collection.write(sym, df, metadata={'source': 'qc'})

        
def search_options_error(collection,error,sym,start_time,end_time,strike_date,spread_type,strike):

    try:
        item = collection.item(sym)
    except:
        return pd.DataFrame()
    
    options_cache = item.to_pandas()
    
            
    df = options_cache[
                    (options_cache['error'] == error) &
                    (options_cache['symbol'] == sym)  &
                    (options_cache['type'] == ('Call' if spread_type == 'CALL' else 'Put'))  &
                    (options_cache['strike'] == strike)    &
                    (options_cache['expiry'] == strike_date)]
    
    return df


        
def add_options_error(collection,error,sym,start_time,end_time,strike_date,spread_type,strike,info):
    
    
    ef = {'error': error,
        'symbol': [sym],
        'expiry': [strike_date],
        'start_time': [start_time],
        'end_time': [end_time],
        'type': ['Call' if spread_type == 'CALL' else 'Put'],
        'strike': [strike],
        'info': [info]}

    df = pd.DataFrame.from_dict(ef)

    try:
        
        search_df = search_options_error(collection,error,sym,start_time,end_time,strike_date,spread_type,strike)
        
        if len(search_df):
            return        
        
        options_cache = collection.item(sym).to_pandas()
        options_cache = concat_dfs(options_cache,df)
        options_cache = options_cache.reset_index(drop=True)
        
        collection.write(sym, options_cache, metadata={'source': 'qc'},overwrite = True)
        
        
    except ValueError:
        collection.write(sym,df,metadata = {'source': 'qc'})
        
        



