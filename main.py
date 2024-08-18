"""
DO NOT import this! Import parsing.py instead!

This is just used to check if the code is reading a full file.
"""

from sys import exit, argv
from parsing import *

if __name__ != "__main__":
    raise RuntimeError("Import parsing.py instead!") # keep it clean

if len(argv) < 2:
    print(f"Usage: {argv[0]} [demo name]")
    exit(1)

            
demo_file = open(argv[1], "rb")

all_data = ReadDemoFile(demo_file)
curr_demoheader = all_data[0]

header_parsed = f"Game directory: [{curr_demoheader.game_dir}] - Map name: [{curr_demoheader.map_name}]\n" + \
                f"Server name: [{curr_demoheader.server_name}] - Client name: [{curr_demoheader.client_name}]\n" + \
                f"Demo length - In seconds: [{curr_demoheader.demo_length}] - In ticks: [{curr_demoheader.demo_ticks}] - In frames: [{curr_demoheader.demo_frames}]\n" + \
                f"Sign-on data length: {curr_demoheader.sign_on_length}\n" + \
                 "-----------------------\n"
print(header_parsed)

for packet_index in range(1, len(all_data)):
    packet = all_data[packet_index]
    print(f"PACKET {packet_index} -> {hex(packet.address)} | Packet type: {packet.message_type} | Data: {packet.data if not packet.is_binary else 'Binary :P'}")

demo_file.close()
