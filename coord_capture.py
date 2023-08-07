import pymavlink.mavutil as mavutil
from pymavlink.dialects.v20 import common as mavlink

import logging as lg
import traceback
import time
from threading import Thread, Event

from airlink_utils import pprint


def default_src():
    return mavlink.MAV_COMP_ID_USER1


class CoordCapture:
    def __init__(self, args, event: Event, logger):
        self.args = args
        self.event = event
        self.logger = logger
        self._mav = None
        self._heartbeat_thread = None  # type: Thread
        self._heartbeat_event = None  # type: Event

    def abort(self):
        lg.info('Coords :: Exiting')

        if self._heartbeat_thread:
            self._heartbeat_event.set()
            self._heartbeat_thread.join()

    def _get_position(self):
        lg.debug('Coords :: Requesting global position')
        location = None
        attitude = None

        while True:
            lg.debug('Coords :: Waiting for message')
            msg = self._mav.recv_match(blocking=True)
            lg.debug(f'Received message {msg.get_type()}: {msg}')

            if msg.get_type() == 'HEARTBEAT':
                lg.debug("HEARTBEAT from %d: %s" % (msg.get_srcSystem(), msg))

            if msg.get_type() == 'GPS_RAW_INT':
                # NB: Applying MAVlink 2.0 Spec conversions
                location = {
                    'lat': msg.lat / 1.0e7,
                    'lon': msg.lon / 1.0e7,
                    'alt': msg.alt / 1000.0
                }

                pprint(location)

            if msg.get_type() == 'ATTITUDE':
                attitude = {
                    'roll': msg.roll,
                    'pitch': msg.pitch,
                    'yaw': msg.yaw
                } 

                pprint(attitude)

            if self.event.is_set():
                return None

            if location and attitude:
                break

        return {
            'location': location,
            'attitude': attitude
        }

    def _loop(self):
        lg.info('Coords :: Starting')
        while True:
            try:
                position = self._get_position()

                if not position:
                    self.abort()
                    return

                self.logger.set_position(position)
                time.sleep(1)

            except Exception as exc:
                traceback.print_exc()
                lg.error('Coords :: There was error', exc)
                # TODO: Add some delay here
                time.sleep(1)

    def sender_loop(self):
        lg.info('Heartbead sender starting')

        while True:
            lg.debug('Sending heartbeat')
            self._mav.mav.heartbeat_send(mavlink.MAV_TYPE_GENERIC,
                                mavlink.MAV_AUTOPILOT_INVALID,
                                mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
                                0,
                                mavlink.MAV_STATE_STANDBY)
            time.sleep(2)

            if self._heartbeat_event.is_set():
                break

        lg.info('Heartbead sender exiting')

    def run(self):
        lg.info(f'MAVlink : Connecting to {self.args.remote} (src={self.args.src}))')

        self._mav = mavutil.mavlink_connection(
            'udpout:' + self.args.remote,
            source_system=self.args.src,
        )

        self._heartbeat_event = Event()
        self._heartbeat_thread = Thread(target=self.sender_loop)
        self._heartbeat_thread.daemon = True
        self._heartbeat_thread.start()
        self._loop()
