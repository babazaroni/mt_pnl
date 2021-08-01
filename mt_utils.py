import pandas as pd
from datetime import datetime
from datetime import timedelta


def test_import():
    test_df = pd.DataFrame()
    return test_df

def mt_dict_to_df(dct_array):
    
    df = pd.DataFrame()
    
    for d in dct_array:
        
         
        if 'time' in d.keys():
            
            df_time = pd.DataFrame()

            time = datetime.strptime(d['time'][0], '%Y-%m-%d %H:%M:%S')
            vals = d['time'][1]
            #print("found time",time,vals)
            for key in vals.keys():
                series = pd.Series(vals[key])
                series.name = key
                #print(series)
                df_time[key] = series
            
            time_vals = []
            for x in range(len(df_time)):
                time_vals.append(time)
                time = time + timedelta(minutes=1)
    
            df_time.insert(loc=0,column = 'time', value = time_vals)
            
            df = pd.concat([df,df_time])
            df.reset_index(drop = True, inplace = True)
            
            continue
            
        
        for k in d.keys():
            #print(k)
            v = d[k]
            
            df_fragment = mt_dict_to_df(v[1])
            
            var_vals = [v[0]] * len(df_fragment)
            
            df_fragment.insert(loc=0,column = k,value = var_vals)
            
            df = pd.concat([df,df_fragment])
            df.reset_index(drop = True, inplace = True)

            
    return df

def mt_df_to_dict(df,level=0):
    
    def time_group(level):
        
            t = []
            
            time = None
            for index, row in g.iterrows():
                
                if time != index[level]:
                    
                    time = index[level]
                    
                    v = {}
                    for r in range(len(df.columns)):
                        v[df.columns[r]] = []
                    
                    td = {'time':(str(index[level]),v)}
                    
                    t.append(td)
                    
                for r in range(len(df.columns)):
                    v[df.columns[r]].append(row[df.columns[r]])
    
                time = time + timedelta(minutes=1)
            return t
        
    r = []
    cols = list(df.index.names) + list(df.columns)
    for n,g in df.groupby(cols[level]):
        d = {}
        r.append(d)
        
        if isinstance(n,datetime):
            #print('should be datetime',type(n))
            n = str(n)

        
        d[ cols[level] ] = (n,[])
        
        if cols[level+1] == "time":
            d[ cols[level] ][1].extend(time_group(level+1))
        else:
            x = mt_df_to_dict(g,level+1)
            d[ cols[level] ][1].extend(x)
            
    return r

#https://towardsdatascience.com/reordering-pandas-dataframe-columns-thumbs-down-on-standard-solutions-1ff0bc2941d5
def movecol(df, cols_to_move=[], ref_col='', place='After'):
    
    cols = df.columns.tolist()
    
    if place == 'After':
        seg1 = cols[:list(cols).index(ref_col) + 1]
        seg2 = cols_to_move
    if place == 'Before':
        seg1 = cols[:list(cols).index(ref_col)]
        seg2 = cols_to_move + [ref_col]
    
    seg1 = [i for i in seg1 if i not in seg2]
    seg3 = [i for i in cols if i not in seg1 + seg2]
    
    return(df[seg1 + seg2 + seg3])

def concat_dfs(df1,df2):
    
    if not len(df1):
        return df2
    
    if not len(df2):
        return df1
                        
    df3 = pd.concat([df1,df2]).drop_duplicates()
    
    
    return df3

