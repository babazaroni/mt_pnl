
import pprint

from mt_parse import create_tokens,get_options,get_stop


def get_tokens(timestamps,texts):

    tokens_all = []
    for ts,text in zip(timestamps,texts):
        tokens = create_tokens(ts,text)
        tokens_all.append(tokens)

    return tokens_all

def get_actions(tokens_all,timestamps,texts):
    actions_all = []
    for ts,tokens,text in zip(timestamps,tokens_all,texts):
        actions = get_options(tokens,ts,text)
        stops = get_stop(tokens,ts,text)
        actions.extend(stops)
        actions_all.append(actions)


    return actions_all


def get_token_strings(tokens_all):
    strings = []
    for tokens in tokens_all:
        s = ""
        for token in tokens:
            s = s + str(token) + " "
        
        strings.append(s)

    return strings
