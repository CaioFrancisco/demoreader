"""
THIS MODULE WAS JUST MADE TO PARSE STRINGTABLES!!!

It turns out, stringtables are weirdly complex, so here's a poor explanation on it's data structure:

First, the amount of strings is written in a 16-bit integer..
Then, the first string is written.
Then, a bit is written, being a flag marking whether this string has userdata or not. If it is 0, skip ahead 2 lines in this explanation.
If it is 1, then it has userdata. The userdata's length is written in a 16-bit integer, right after the bit.
Then, the userdata is written. The userdata appears to just be another stringtable, so you can decode it as normal text as well.
Then the cycle begins once again. 1th stringtable is written in 4096 bytes, a bit flag is written marking whether there's userdata, if there's no userdata, restart the cycle, if there is, just read above.
That is, until the last stringtable is written (and it's userdata, if it has any.)
Then, a bit flag is written, marking whether there's client stringtables.
The process begins, once again, from the very start, if there are client stringtables. If not, then congratulations, your stringtables have been successfuly parsed.
"""
from common import *

def ParseStringtables(buf_to_parse):
    return_value = []
    numtables = unpack_char_int(buf_to_parse.read(1))
    base_stringtable = {"name" : "", "data" : None}

    for i in range(0, numtables):
        stringtable = base_stringtable
        stringtable["name"] = ReadString(buf_to_parse)
        print("STRINGTABLE: ", stringtable["name"])
        stringtable["data"] = ParseStringtable(buf_to_parse)
        return_value.append(stringtable)

    return return_value

def ParseStringtable(buf_to_parse, clientside_data = False):
    return_value = []
    numstrings = unpack_short_int(buf_to_parse.read(2))
    print(numstrings)             
    for i in range(0, numstrings):
        # base stringtable
        curr_stringtable = { "data": None, "userdataPresent": False, "userdata": None }
        
        curr_stringtable["data"] = ReadString(buf_to_parse)
        curr_stringtable["userdataPresent"] = buf_to_parse.readbit(1).any()

        if curr_stringtable["userdataPresent"]:
            curr_stringtable["userdata"] = ReadRawDataInt16(buf_to_parse)

        if i <= 1 and clientside_data:
            continue
        
        """
        if not clientside_data: print(curr_stringtable["data"])

        if curr_stringtable["userdataPresent"]:
            hexified_userdata = ""
            asciified_userdata = ""
            for i in curr_stringtable["userdata"]:
                hexified_userdata += ("0" if i < 10 else "") + hex(i)[2:4].upper() + " " 
                asciified_userdata += chr(i)

            print("USERDATA:")
            print(hexified_userdata, "|", asciified_userdata)
        """
        return_value.append(curr_stringtable)
        
    if not clientside_data: # so we're parsing client entries...
        if buf_to_parse.readbit(1).any():
            print("PARSING CLIENTSIDE DATA")
            return_value += ParseStringtable(buf_to_parse, True) # it's identical to normal entries, so parse it again.
    
    return return_value

