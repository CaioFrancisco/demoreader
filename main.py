from sys import exit, argv
from bitarray import bitarray

from common       import *
from stringtables import *
from datatables   import *

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
demo_messages = ["fuck", "dem_signon", "dem_packet", "dem_synctick", "dem_consolecmd",
                 "dem_usercmd", "dem_datatables", "dem_stop", "dem_stringtables", "dem_lastcmd"]
    
class DemoPacket:
    data = []
    stop = False
    address = 0x0 # yeah
    def __init__(self, file_to_read, demoheader):
        self.address = file_to_read.tell()
        self.message_type = unpack_char_int(file_to_read.read(1))
        try:
            self.message_type = demo_messages[ self.message_type ]
        except IndexError:
            print(f"Invalid DemoPacket:\nMessage type: {hex(self.message_type)} - Address: {hex(file_to_read.tell())}")
            exit(1)
        self.tick = unpack_int(file_to_read.read(4))

        match self.message_type:
            case "dem_signon":
                return # TODO: implement parsing dem_signon (do i really need to..?)
                
            case "dem_packet":
                _ = ReadRawDataInt32(file_to_read)
                return # TODO: also implement parsing this
                
            case "dem_synctick":
                return # since we're just parsing, we can out-right ignore tick syncs.
                
            case "dem_consolecmd":
                self.data.append(ReadRawDataInt32(file_to_read).decode("UTF-8")) # just the command
            
            case "dem_usercmd":
                self.data.append(unpack_int(file_to_read.read(4))) # outgoing sequence, source code documentation says we can discard this
                self.data.append(file_to_read.read(256).decode("utf-8")) # actual command
            
            case "dem_datatables":
                loaded_data = bitarray(endian="little")
                loaded_data.frombytes(ReadRawDataInt32(file_to_read))

                loaded_datatable = BitArrayBuffer( loaded_data )
                return # TODO
                self.data += ParseDatatables(file_to_read)
        
            case "dem_stop" | "dem_lastcmd":
                self.stop = True
                return # this is the end of the demo!
            
            case "dem_stringtables":
                loaded_data = bitarray(endian="little")
                loaded_data.frombytes(ReadRawDataInt32(file_to_read))
                
                loaded_stringtables = BitArrayBuffer( loaded_data )
                
                if len(loaded_stringtables.bitArray) > 5000000 * 8: # 5 megabytes, source treats this as the maximum limit for stringtables
                    raise RuntimeError("Loaded a stringtable above the 5MB limit.")
                
                self.data += ParseStringtables(loaded_stringtables)
            
demo_file = open(argv[1], "rb")
curr_demoheader = DemoHeader(demo_file)

header_parsed = f"Game directory: [{curr_demoheader.game_dir}] - Map name: [{curr_demoheader.map_name}]\n" + \
                f"Server name: [{curr_demoheader.server_name}] - Client name: [{curr_demoheader.client_name}]\n" + \
                f"Demo length - In seconds: [{humanize_floats(curr_demoheader.demo_length)}] - In ticks: [{curr_demoheader.demo_ticks}] - In frames: [{curr_demoheader.demo_frames}]\n" + \
                f"Sign-on data length: {curr_demoheader.sign_on_length}\n" + \
                 "-----------------------\n"
                
demo_file.seek(curr_demoheader.sign_on_length, 1)

while True:
    curr_demopacket = DemoPacket(demo_file, curr_demoheader)
    if curr_demopacket.message_type: print(f"{curr_demopacket.message_type} -> {hex(curr_demopacket.address)}")
    if curr_demopacket.data: print(curr_demopacket.data)
    if curr_demopacket.stop: break # it means we reached a final message

demo_file.close()