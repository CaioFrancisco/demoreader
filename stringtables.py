"""
Stringtables are pretty complicated, so here's a separate module just to read them.
"""
from common import *

def ParseStringtables(buf_to_parse):
    return_value = []
    numtables = unpack_char_int(buf_to_parse.read(1))
    base_stringtable = {"name" : "", "data" : None}

    for i in range(0, numtables):
        stringtable = base_stringtable
        stringtable["name"] = ReadString(buf_to_parse)
        stringtable["data"] = ParseStringtable(buf_to_parse)
        return_value.append(stringtable)

    return return_value

def ParseStringtable(buf_to_parse, clientside_data = False):
    return_value = []
    numstrings = unpack_short_int(buf_to_parse.read(2))
    for i in range(0, numstrings):
        # base stringtable
        curr_stringtable = { "data": None, "userdataPresent": False, "userdata": None }
        
        curr_stringtable["data"] = ReadString(buf_to_parse)
        curr_stringtable["userdataPresent"] = buf_to_parse.readbit(1).any()

        if curr_stringtable["userdataPresent"]:
            curr_stringtable["userdata"] = ReadRawDataInt16(buf_to_parse)

        if i <= 1 and clientside_data:
            continue

        return_value.append(curr_stringtable)
        
    if not clientside_data: # so we're parsing client entries...
        if buf_to_parse.readbit(1).any():
            return_value += ParseStringtable(buf_to_parse, True) # it's identical to normal entries, so parse it again.
    
    return return_value

