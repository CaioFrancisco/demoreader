"""
COMMON FUNCTIONS WHICH ARE USED BY OTHER MODULES
"""


"""
aliases for simple/common operations.
"""
def humanize_floats(to_round):
	return int(to_round * 100) / 100

def unpack_int(four_byte_int):
	return unpack("<i", four_byte_int)[0]

def unpack_char_int(char_int):
	return unpack("<B", char_int)[0]

def unpack_short_int(short_int):
	return unpack("<H", short_int)[0]

# ahahaha fuck you 5-bit reads
def ReadUBitInt(bitarray_to_read, amt_bits):
	return int(bitarray_to_read.to01(), 2)

"""
this data structure is very used in demo packet headers.
the first few bytes determine the length of the data stored.
the function just reads those bytes, reads the data stored, then returns the data.
"""
def ReadRawData(file_to_read, data_length_size):
	data_length = unpack_int(file_to_read.read(data_length_size))
	return file_to_read.read(found_data_length)

# aliases for common data length sizes
ReadRawDataInt32 = lambda file_to_read: dem_ReadRawData(file_to_read, 4)
ReadRawDataInt16 = lambda file_to_read: dem_ReadRawData(file_to_read, 2)

def ReadAndAllocateString(buf_to_read):
	MAX_READ = 2048 # max amount of bytes we can read
	char_counter = 0
	return_value = ""

	while char_counter < MAX_READ:
		char_counter += 1
		character = chr(unpack_char_int(buf_to_read.read(1)))
		return_value += character
		if character == "\n": return return_value # \n is the string terminator

	raise RuntimeError("ReadAndAllocateString over-read. Probably read an invalid chunk of memory.")	

# just because i'm used to reading stuff like files
class BitArrayBuffer:
	bitArray = None
	index = 0
	
	def __init__(self, obj_to_inherit):
		if type(obj_to_inherit) != type(bitarray()):
			obj_to_inherit = bitarray()
			
		self.bitArray = obj_to_inherit
	
	def readbit(self, bits_to_read):
		return_value = bitarray()
		
		if self.index + bits_to_read > len(self.bitArray): # adjusts for going over-bound
			bits_to_read -= (self.index + bits_to_read) - len(self.bitArray) 

		# adds the right chunk of the bitarray into the return value, and adjusts the index accordingly
		return_value += self.bitArray[self.index : self.index + bits_to_read]
		self.index += bits_to_read
			
		return return_value
	
	def read(self, bytes_to_read): # read as bytes
		return self.read(bytes_to_read * 8).tobytes()
	
	def seek(self, bits_to_seek):
		self.index += bits_to_seek