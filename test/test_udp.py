#!/usr/bin/python3
# Usage example of MAVLink UDP port for user applications
# To execute:
#     python3 heartbeat_example_udp.py
# or
#     python3 heartbeat_example.py 127.0.0.1:14560 35
#     in this case: 127.0.0.1:14560 - address and port of mavlink source,
#                                     now available 14560 and 14561 udp ports
#                                     for user applications
#                   35 - system-id for signature
#

import pymavlink.mavutil as mavutil
from pymavlink.dialects.v20 import common as mavlink
import sys
import time
from threading import Thread


if len(sys.argv) != 3:
    # use default arguments if no arguments given from command line
    srcSystem = mavlink.MAV_COMP_ID_USER1
    remote_address = "127.0.0.1:14560"
else:
    # use arguments from command line
    srcSystem = int(sys.argv[2])
    remote_address = sys.argv[1]

# create connection
mav = mavutil.mavlink_connection(
    'udpout:' + remote_address, source_system=srcSystem)


def sender_loop():
    while True:
        mav.mav.heartbeat_send(mavlink.MAV_TYPE_GENERIC,
                               mavlink.MAV_AUTOPILOT_INVALID,
                               mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
                               0,
                               mavlink.MAV_STATE_STANDBY)
        time.sleep(2)


send_thread = Thread(target=sender_loop)
send_thread.daemon = True
send_thread.start()

while True:
    msg = mav.recv_match(blocking=True)
    print(f'Received message {msg}')

    if msg.get_type() == 'HEARTBEAT':
        print("HEARTBEAT from %d: %s" % (msg.get_srcSystem(), msg))


