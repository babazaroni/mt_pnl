import re
import dateutil.parser
import datetime
from IPython.display import display, Markdown, Latex
import itertools



class Obj_base():
    valid = False
    index = None
    
    def __init__(self,pos):
        self.index = pos
    
    def __bool__(self):
        return self.valid
    
    
    def correct_date(self,timestamp,month,day):
        ts = dateutil.parser.isoparse(timestamp) # ISO 8601 exteended form
        ts2 = dateutil.parser.isoparse(timestamp)
        ts2 = ts2.replace(month=month,day=day)
        if ts2 < ts:
            ts2 = ts2.replace(year = int(ts2.year) + 1)
        return ts2
    
    def __repr__(self):
        return type(self).__name__

class Symbol(Obj_base):
    sym = None
    def __init__(self,pos,text):
        super().__init__(pos)
        
        text = text.rstrip('-')  #sometimes there is a dash
        
        if any(char.isdigit() for char in text):
            return
        
        if text.upper() != text:
            return
    
        if text.startswith('DTE'):
            return
            
        if text.startswith('ADJ'):
            return
            
        if text == 'I':
            return
            
        if text.isalpha() is False:
            return

        self.sym = text
        
        self.valid = True
        
        
    def __repr__(self):
        return self.sym


class Slash_pair(Obj_base):
    left = None
    right = None
    def __init__(self,pos,text,form,s = None):
        super().__init__(pos)

        s = text.split('/')
        
        
        if len(s)!=2:
            return
        
        
        try:
            self.left = form(s[0])
        except:
            return
        
        try:
            self.right = form(s[1])
        except:
            return

        
        self.valid = True
        
    def __repr__(self):
        return str(self.left) + '/' + str(self.right)

    
class Month_slash_day(Obj_base):
    sp = None
    
    def __init__(self,pos,text):
        super().__init__(pos)
        
        text1 = text.rstrip(':')
        if text1 == text:
            return
        
        self.sp = Slash_pair(pos,text1,int)
        if not self.sp.valid:
            return
        
        
        if self.sp.left > 12:
            return
        if self.sp.right > 31:
            return
    
        self.valid = True
        
    def __repr__(self):
#        return 'Month_slash_day'
        return str(self.sp) + ':'
        
class Action_shorting(Obj_base):
    shorting = None
    
    def __init__(self,pos,text):
        super().__init__(pos)
    
        self.valid = True
    
        if text.lower() == 'shorting' or text.lower() == 'shoring' or text =='short':
            self.shorting = True
            return
            
        if text.lower() == 'selling':
            self.shorting = True
            return
        
        self.valid = False
        
    def __repr__(self):
        if self.valid:
            return "shorting"
        else:
            return "invalid shorting"

        
class Action_shorted(Obj_base):
    shorted = None
    
    def __init__(self,pos,text):
        super().__init__(pos)
    
        self.valid = True
    
        if text.lower() == 'shorted':
            self.shorted = True
            return
            
        if text.lower() == 'sold':
            self.shorted = True
            return
        
        self.valid = False
        
    def __repr__(self):
        if self.valid:
            return "shorted"
        else:
            return "invalid shorted"

        
class Month(Obj_base):
    month_num = None
    def __init__(self,pos,text):
        super().__init__(pos)
        
        for i,m in enumerate(['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec']):
            if text.lower() == m:
                if i==4:
                    if text[0] == 'm':  # May must have capitol 'M'
                        return
                self.month_num = i+1
                self.valid = True
                return
                
    def __repr__(self):
        return 'Month[' + str(self.month_num) + ']'
                
class Strikes(Obj_base):
    sp = None
    def __init__(self,pos,text):
        super().__init__(pos)
#        if text[0]!='$':
#            return
        text = text.lstrip('$')
        text = text.rstrip('.,')
        text = text.replace('bull','')  # incase of typo of no space after strikes
        text = text.replace('bear','')
        self.sp = Slash_pair(pos,text,float)
        
        if self.sp.valid:
        
            #if abs(self.sp.left - self.sp.right) < 50:  # in case of typo   # let typos thru, will check later
                self.valid = self.sp.valid
        
    def aslist(self):
        return [self.sp.left,self.sp.right]
        
    def __repr__(self):
        if self.sp is None:
            return '(None/None)'
        #return '(' + str(self.sp.left) + '/' + str(self.sp.right) + ')'
        strikes = str([self.sp.left,self.sp.right])
        return strikes
    
class Strike_day(Obj_base):
    year = None
    month = None
    day = None
    
    def __init__(self,pos,text,timestamp,last):
        super().__init__(pos)
        
        text = text.lower()
        
        if text.endswith('th'):
            text = text.rstrip('th')
        if text.endswith('rd'):
            text = text.rstrip('rd')
        if text.endswith('nd'):
            text = text.rstrip('nd')
            
        try:
            self.day = int(text)
        except:
            return
        
        month = Month(pos,last)
        
        if month.valid:
            ts = self.correct_date(timestamp,month.month_num,self.day)
            self.year = ts.year
            self.month = ts.month
            self.day = ts.day

            self.valid = True
            
    def __repr__(self):
        d = datetime.date(self.year,self.month,self.day)
        return str(d)
        #return str(self.month) + '/' + str(self.day) + '/' + str(self.year)
            
            
class Strike_date(Obj_base):
    year = None
    month = None
    day = None
    
    def process_dte(self,timestamp,last):

        try:
            num = int(last)
        except:
            return
        
        ts = dateutil.parser.isoparse(timestamp)
        end_date = ts + datetime.timedelta(days=num)
        
        self.year = end_date.year
        self.month = end_date.month
        self.day = end_date.day
    
        self.valid = True
        
        
    def __init__(self,pos,text,timestamp,last):
        super().__init__(pos)
        
        
        if text.lower()=='dte':
            self.process_dte(timestamp,last)
        else:
            if text[0] != '(':
                return
            text = text.lstrip('(')
            text.rstrip('.,:')
            if text[-1] != ')':
                return
            
           
            text = text.rstrip(')')

            sp = Slash_pair(pos,text,int)
            if sp.valid:
                #print("Strike_date",timestamp)
                ts2 = self.correct_date(timestamp,sp.left,sp.right)

                self.year = ts2.year
                self.month = ts2.month
                self.day = ts2.day
        
                self.valid = sp.valid
            
    def __repr__(self):
        d = datetime.date(self.year,self.month,self.day)
        return str(d)

        return str(self.month) + '/' + str(self.day) + '/' + str(self.year)
                
        
class Spread_type(Obj_base):
    put = None
    def __init__(self,pos,text):
        super().__init__(pos)
        
        if text.lower()=='put':
            self.put = True
        if text.lower()=='call':
            self.put = False
            
        if text.lower()=='bull':
            self.put = True
            
        if text.lower()=='bear':
            self.put = False
            
        if self.put != None:
            self.valid = True
            
    def __repr__(self):
        if self.put is True: return 'PUT'
        if self.put is False: return 'CALL'
        return 'None'
            
    
            
class Price(Obj_base):
    price = None
    def __init__(self,pos,text):
        super().__init__(pos)

        if text[0]!='$':
            return
#        text = text.lstrip('$')
#        text = text.rstrip('.,)')
        
        non_decimal = re.compile(r'[^\d.]+')
        text = non_decimal.sub('',text)

        text = text.rstrip('.')
        try:
            self.price = float(text)
            self.valid = True
        except:
            pass
        
    def __repr__(self):
        if self.price is not None:
            #return '$' + str(self.price)
            return 'Price'
        return '$None'
        
class Price_per_share(Obj_base):
    price = None
    def __init__(self,pos,text):
        
        super().__init__(pos)

        sp = text.split('/')
        if len(sp)!=2:
            return
        
        if sp[1].lower().rstrip(',.').endswith('hare'):  # sometimes share is typoed to hare
            p = Price(pos,sp[0])
            self.valid = p.valid
            self.price = p.price
        
    def __repr__(self):
        if self.price is not None:
            return '$' + str(self.price) + '/share'
        else:
            return 'None'
        
class Period(Obj_base):
    minutes = None
    def __init__(self,pos,text):
        super().__init__(pos)
        
        text_split = text.split('-')
        
        if len(text_split) == 2 and text_split[1].lower().startswith('min'):
            try:
                self.minutes = int(text_split[0])
            except:
                return
            
            self.valid = True
            
    def __repr__(self):
        return 'Period(' + str(self.minutes) + ')'
    
class Close(Obj_base):
    def __init__(self,pos,text):
        super().__init__(pos)
        
        if text.lower() == 'close':
            self.valid = True
        
    def __repr__(self):
        return 'Close'

        
class Stop(Obj_base):

    def __init__(self,pos,text):
        super().__init__(pos)

        text = text.lstrip('(')
        if text.lower() == 'stop':
            self.valid = True
    def __repr__(self):
        if self.valid:
#            return "<font color='red'>Stop</font>"
            return 'Stop'
        else:
            return 'None'
            
class Condition(Obj_base):
    over = None
    def __init__(self,pos,text):
        super().__init__(pos)

        if text.lower() == 'over':
            self.over = True
        if text.lower() == 'under':
            self.over = False
            
        self.valid = (self.over != None)
                    

            
class Watch(Obj_base):
    def __init__(self,pos,text):
        super().__init__(pos)

        if text.lower().startswith('watch'):
            self.valid = True
            
class Cover(Obj_base):
    def __init__(self,pos,text):
        super().__init__(pos)

        if text.lower().startswith('cover'):
            self.valid = True
            
class Premium(Obj_base):
    def __init__(self,pos,text):
        super().__init__(pos)

        if text.lower().startswith('premium'):
            self.valid = True

            
class Condor(Obj_base):
    def __init__(self,pos,text):
        super().__init__(pos)
        if text.lower().startswith('condor'):
            self.valid = True
            
class Adj(Obj_base):
    def __init__(self,pos,text):
        super().__init__(pos)
        if text.lower().startswith('adj'):
            self.valid = True
            
class MidPoint(Obj_base):
    def __init__(self,pos,text):
        super().__init__(pos)
        text = text.rstrip(',.')
        if text.lower().startswith('mid') and text.lower().endswith('nt'):
            self.valid = True

