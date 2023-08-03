import pymavlink.mavutil as mavutil
from pymavlink.dialects.v20 import common as mavlink

import logging as lg
import traceback
import time


def default_src():
    return mavlink.MAV_COMP_ID_USER1


class CoordCapture:
    def __init__(self, args, event):
        self.args = args
        self.event = event
        self._mav = None

    def _loop(self, log):
        while True:
            try:
                lg.debug('Coords :: Entering the cycle')
                while True:
                    if self.event.is_set():
                        lg.debug('Coords :: Exiting')
                        return

                    m = self.recv_match(type='SENSOR_OFFSETS')
                    print('M', m)
                    time.sleep(1)

            except Exception as exc:
                traceback.print_exc()
                lg.error('Coords :: There was error', exc)

    def run(self):
        lg.info(f'MAVlink : Connecting to {self.args.remote}')

        self._mav = mavutil.mavlink_connection(
            'udpout:' + self.args.remote,
            source_system=self.args.src,
        )

        lg.info('MAVlink : Waiting for heartbeat')
        self._mav.wait_heartbeat()

        with open('coords.txt', 'at') as log:
            self._loop(log)
