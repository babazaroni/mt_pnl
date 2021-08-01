import json
import unidecode
import pandas as pd
import dateutil.parser


def reduce_message(message):
    """ recursively concat strings of any embedded dictionaries in messages
    """

    reduced = ""

    if type(message) is list:
        for m in message:
            reduced += reduce_message(m)
        return reduced
    
    if type(message) is dict:
        if 'text'  in message.keys():
            reduced += reduce_message(message['text'])
        return reduced

    if type(message) is str:
        return message

    return reduced




def get_messages_as_df():
    print('cache miss')

    with open("cl_weekly_1_9_22_20.json","r") as read_file:
        data = json.load(read_file)

    messages = [ {'date': message['date'],'text': unidecode.unidecode(reduce_message(message['text'])) }
                for message in data['messages'] if 'text' in message.keys()]

    return pd.DataFrame(messages)

def format_date_series(series):
    weekdays = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
    formatted = []
    year_last = 0
    for date_str in series:
        date_obj = dateutil.parser.parse(date_str)
        if year_last != date_obj.date():
            year_last = date_obj.date()
            date_display = date_obj.strftime("%Y-%m-%d %H:%M:%S")
            day_count = 0
        else:
            if day_count == 0:
                preamble  = weekdays[date_obj.weekday()]
            else:
                preamble = "   "
            #day_count += 1

            date_display= "    " + preamble + " " + date_obj.strftime("%H:%M:%S")

        formatted.append(date_display)
        
    return pd.Series(formatted)
