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

    def _loop(self, log):
        while True:
            try:
                lg.debug('Coords :: Entering the cycle')
                while True:
                    time.sleep(1)
                    if self.event.is_set():
                        lg.debug('Coords :: Exiting')
                        return

            except Exception as exc:
                traceback.print_exc()
                lg.error('Coords :: There was error', exc)

    def run(self):
        lg.info(f'MAVlink : Connecting to {self.args.remote}')

        with open('coords.txt', 'at') as log:
            self._loop(log)
