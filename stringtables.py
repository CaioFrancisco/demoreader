"""
THIS MODULE WAS JUST MADE TO PARSE STRINGTABLES!!!

It turns out, stringtables are weirdly complex, so here's a poor explanation on it's data structure:

First, the amount of stringtables is written in a 16-bit integer..
Then, the 0th stringtable is written, in a 4096 bytes of allocated space.
Then, a bit is written, being a flag marking whether this stringtable has userdata or not. If it is 0, skip ahead 2 lines in this explanation.
If it is 1, then it has userdata. The userdata's length is written in a 16-bit integer, right after the bit.
Then, the userdata is written. The userdata appears to just be another stringtable, so you can decode it as normal text as well.
Then the cycle begins once again. 1th stringtable is written in 4096 bytes, a bit flag is written marking whether there's userdata, if there's no userdata, restart the cycle, if there is, just read above.
That is, until the last stringtable is written (and it's userdata, if it has any.)
Then, a bit flag is written, marking whether there's client stringtables.
The process begins, once again, from the very start, if there are client stringtables. If not, then congratulations, your stringtables have been successfuly parsed.
"""

def ParseStringtables(file_to_read):
	return_value = []
	numstrings = unpack("<H", loaded_stringtables.read(2))[0] # 16 bit integer
				
	for i in range(0, numstrings):
		# base stringtable
		curr_stringtable = { "data": None, "userdataPresent": False, "userdata": None }
		
		curr_stringtable["data"] = loaded_stringtables.read(4096).decode("utf-8")
		curr_stringtable["userdataPresent"] = loaded_stringtables.readbit(1).any()
		
		if curr_stringtable["userdataPresent"]:
			curr_stringtable["userdata"] = ReadRawDataInt16(loaded_stringtables).decode("utf-8")
	
		return_value.append(curr_stringtable)
	
	if loaded_stringtables.read(1).any(): # so we're parsing client entries
		# source code also does a ctrl+c and ctrl+v, don't judge me.
		numstrings = unpack("<H", loaded_stringtables.read(2))[0] # 16 bit integer
		
		for i in range(0, numstrings):
			# base stringtable
			curr_stringtable = { "data": None, "userdataPresent": False, "userdata": None }
			
			curr_stringtable["data"] = loaded_stringtables.read(4096).decode("utf-8")
			curr_stringtable["userdataPresent"] = loaded_stringtables.readbit(1).any()
			
			if curr_stringtable["userdataPresent"]:
				curr_stringtable["userdata"] = ReadRawDataInt16(loaded_stringtables).decode("utf-8")
			
			if i >= 2: # source code does this, for some reason??????????????????????
				return_value.append(curr_stringtable)
	
	return return_value