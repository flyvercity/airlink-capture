import pymavlink.mavutil as mavutil
from pymavlink.dialects.v20 import common as mavlink

import logging as lg
import traceback
import time


def default_src():
    return mavlink.MAV_COMP_ID_USER1


class CoordCapture:
    def __init__(self, args, event, logger):
        self.args = args
        self.event = event
        self.logger = logger
        self._mav = None

    def _get_position(self):
        message = self.recv_match(type='GLOBAL_POSITION_INT')
        print('GPS_DUMP', message)

    def _loop(self, log):
        while True:
            try:
                lg.debug('Coords :: Entering the cycle')
                while True:
                    if self.event.is_set():
                        lg.debug('Coords :: Exiting')
                        return

                    message = self._get_position()

                    # NB: Applying MAVlink 2.0 Spec conversions
                    coords = {
                        'lat': message.lat / 1.0e7,
                        'lon': message.lon / 1.0e7,
                        'alt': message.alt / 1000.0
                    }

                    self.logger.set_coords(coords)
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
