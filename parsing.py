"""
This is where all the parsing is done. Import this if you just want to read a demo from another file.
"""

from common       import *
from stringtables import *
from datatables   import *

from bitarray import bitarray

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

class democmdinfo:
    flags = None

    viewOrigin = None
    viewAngles = None
    localViewAngles = None

    viewOrigin2 = None
    viewAngles2 = None
    localViewAngles2 = None

    def __init__(self, file_to_read):
        flags = unpack_int(file_to_read.read(4))
        
        viewOrigin = unpack_vector(file_to_read)
        viewAngles = unpack_vector(file_to_read)
        localViewAngles = unpack_vector(file_to_read)

        viewOrigin2 = unpack_vector(file_to_read)
        viewAngles2 = unpack_vector(file_to_read)
        localViewAngles2 = unpack_vector(file_to_read)

# there should never be a message addressed to 0, so ignore "fuck"
demo_messages = ["fuck", "dem_signon", "dem_packet", "dem_synctick", "dem_consolecmd",
                 "dem_usercmd", "dem_datatables", "dem_stop", "dem_stringtables", "dem_lastcmd"]
    
class DemoPacket:
    stop = False
    address = 0x0 # yeah
    is_binary = False
    
    def __init__(self, file_to_read):
        if not file_to_read: return

        self.address = file_to_read.tell()

        self.message_type = demo_messages[ unpack_char_int(file_to_read.read(1)) ]
        
        self.data = []

        if self.message_type == "dem_stop" or self.message_type == "dem_lastcmd":
            self.stop = True
            return
        
        self.tick = unpack_int(file_to_read.read(4))

        match self.message_type:
            case "dem_signon":
                self.stop = True
                return # TODO: implement parsing dem_signon (do i really need to..?)
                
            case "dem_packet":
                self.is_binary = True
                self.data.append(democmdinfo(file_to_read))
                self.data.append((unpack_int(file_to_read.read(4)), unpack_int(file_to_read.read(4)))) # in-going sequence, out-going sequence, respectivelly.
                self.data.append(ReadRawDataInt32(file_to_read))
                
            case "dem_synctick":
                return # since we're just parsing, we can out-right ignore tick syncs.
                
            case "dem_consolecmd":
                self.data.append(ReadRawDataInt32(file_to_read).decode("UTF-8")) # just the command
            
            case "dem_usercmd":
                self.is_binary = True
                self.data.append(unpack_int(file_to_read.read(4))) # some sequence we use to decode the command
                self.data.append(ReadRawDataInt32(file_to_read)) # actual command
            
            case "dem_datatables":
                raise NotImplementedError("TODO: implement datatables")
                """
                self.is_binary = True
                loaded_data = bitarray(endian="little")
                loaded_data.frombytes(ReadRawDataInt32(file_to_read))

                loaded_datatable = BitArrayBuffer( loaded_data )
                self.data += ParseDatatables(file_to_read)
                """
            
            case "dem_stringtables":
                loaded_data = bitarray(endian="little")
                loaded_data.frombytes(ReadRawDataInt32(file_to_read))
                
                loaded_stringtables = BitArrayBuffer( loaded_data )
                
                if len(loaded_stringtables.bitArray) > 5000000 * 8: # 5 megabytes, source treats this as the maximum limit for stringtables
                    raise RuntimeError("Loaded a stringtable above the 5MB limit.")
                
                self.data.append(ParseStringtables(loaded_stringtables))

"""
Input: demoFileToParse - a readable buffer that implements `read()` and returns bytes. (just do open("foo.dem", "rb"))
Output: an array with all the parsed packets
"""
def ReadDemoFile(demoFileToParse):
    return_data = []
    
    parsed_demoheader = DemoHeader(demoFileToParse)
    return_data.append(parsed_demoheader)
    
    sign_on_packet = DemoPacket(None)
    sign_on_packet.address = demoFileToParse.tell()
    sign_on_packet.message_type = "dem_signon"
    sign_on_packet.data = demoFileToParse.read(parsed_demoheader.sign_on_length)
    sign_on_packet.is_binary = True

    return_data.append(sign_on_packet)
    del(sign_on_packet) # this is mostly pointless, but i'd feel guilty for not throwing this out of scope as soon as i can

    parsing_done = False

    while not parsing_done:
        curr_demopacket = DemoPacket(demoFileToParse)
        return_data.append(curr_demopacket)
        parsing_done = curr_demopacket.stop

    return return_data
