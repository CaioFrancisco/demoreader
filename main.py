from sys import exit, argv
from os import system
from struct import unpack
from bitarray import bitarray

_bitarray = bitarray
# i'm a dirty trickster
bitarray = lambda usr_input: _bitarray.bitarray(usr_input, endian="little")

from "./common.py"       import *
from "./stringtables.py" import *

if len(argv) < 2:
	print(f"Usage: {argv[0]} [demo name]")
	exit(1)
	
class DemoHeader:
	def __init__(self, file_to_read):
		file_header = file_to_read.read(8)
		
		if file_header != b"HL2DEMO\x00":
			raise RuntimeError("Invalid .dem file.")
		
		self.demo_protocol = unpack_int(file_to_read.read(4))
		self.net_protocol  = unpack_int(file_to_read.read(4))
		self.server_name   = file_to_read.read(260).decode("UTF-8")
		self.client_name   = file_to_read.read(260).decode("UTF-8")
		self.map_name      = file_to_read.read(260).decode("UTF-8")
		self.game_dir      = file_to_read.read(260).decode("UTF-8")
		self.demo_length   = unpack("f", file_to_read.read(4))[0] # measured in seconds
		self.demo_ticks    = unpack_int(file_to_read.read(4))
		self.demo_frames   = unpack_int(file_to_read.read(4))
		self.sign_on_length = unpack_int(file_to_read.read(4))

# there should never be a message addressed to 0, so ignore "fuck"
demo_messages = ["fuck", "dem_signon", "dem_packet", "dem_synctick", "dem_consolecmd"
                 "dem_usercmd", "dem_datatables", "dem_stop", "dem_stringtables", "dem_lastcmd"]
	
class DemoPacket:
	data = []
	def __init__(self, file_to_read):
		self.message_type = demo_messages[ unpack_char_int(file_to_read.read(1)) ]
		self.tick = unpack_int(file_to_read.read(4))
		
		match self.message_type:
			case "dem_signon":
				return # TODO: implement parsing dem_signon (do i really need to..?)
				
			case "dem_packet":
				return # TODO: also implement parsing this
				
			case "dem_synctick":
				return # since we're just parsing, we can out-right ignore tick syncs.
				
			case "dem_consolecmd":
				self.data.append(ReadRawDataInt32(file_to_read).decode("UTF-8")) # just the command
			
			case "dem_usercmd":
				self.data.append(unpack_int(file_to_read.read(4))) # outgoing sequence, source code documentation says we can discard this
				self.data.append(file_to_read.read(256).decode("utf-8")) # actual command
			
			case "dem_datatables":
				#datatable_buffersize = 256*1024
				loaded_datatable = ReadRawDataInt32(file_to_read)
				# TODO: follow the datatable rabbithole, gotta parse whatever we just loaded
				
			case "dem_stop" | "dem_lastcmd":
				return True # this is the end of the demo!
			
			case "dem_stringtables":
				loaded_stringtables = BitArrayBuffer( bitarray().from_bytes( ReadRawDataInt32(file_to_read) ) )
				
				if len(loaded_stringtables) > 5000000 * 8: # 5 megabytes, source treats this as the maximum limit for stringtables
					raise RuntimeError("Loaded a stringtable above the 5MB limit.")
				
				data += ParseStringtables(file_to_read)
			
demo_file = open(argv[1], "rb")
curr_demoheader = DemoHeader(demo_file)

header_parsed = f"Game directory: [{curr_demoheader.game_dir}] - Map name: [{curr_demoheader.map_name}]\n" + \
                f"Server name: [{curr_demoheader.server_name}] - Client name: [{curr_demoheader.client_name}]\n" + \
                f"Demo length - In seconds: [{humanize_floats(curr_demoheader.demo_length)}] - In ticks: [{curr_demoheader.demo_ticks}] - In frames: [{curr_demoheader.demo_frames}]\n" + \
                f"Sign-on data length: {curr_demoheader.sign_on_length}\n" + \
                 "-----------------------\n"
				

print(header_parsed)

demo_file.close()