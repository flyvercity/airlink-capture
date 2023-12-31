import sys
import logging as lg
import traceback
import subprocess
import time

import signal_parsers as sp
from airlink_utils import pprint


def send_command(at_command):
    ver = sys.version_info

    if ver.major == 2:
        raise Exception('Python 2 is not supported')

    command = [
        'mmcli',
        '-m', '0',
        '--command', at_command
    ]

    if ver.minor >= 10:
        response = subprocess.run(command, capture_output=True)
        answer = response.stdout.decode('utf-8')
    else:
        result = subprocess.run(command, stdout=subprocess.PIPE)
        answer = result.stdout.decode('utf-8')

    lg.debug(f'Raw response: {answer}')
    return answer


class SignalCapture:
    def __init__(self, args, event, logger):
        self.args = args
        self.event = event
        self.logger = logger

    def wait_10s(self):
        for i in range(10):
            lg.info(f'Waiting {10 - i} seconds')
            time.sleep(1)

            if self.event.is_set():
                return

    def _loop(self):
        lg.info('Signal :: Start')
        while True:
            try:
                if self.event.is_set():
                    lg.info('Signal :: Exiting')
                    return

                lg.debug('Signal :: Quality query')
                moni_string = send_command('AT#MONI')
                lg.debug(f'Signal :: Quality: {moni_string}')
                rsrp = sp.get_rsrp(moni_string)
                rsrq = sp.get_rsrq(moni_string)
                nr_rsrp = sp.get_nr_rsrp(moni_string)
                nr_rsrq = sp.get_nr_rsrq(moni_string)

                if rsrp and nr_rsrq:
                    radio = '5GNSA'
                elif nr_rsrp:
                    radio = '5GSA'
                elif rsrp:
                    radio = '4G'
                else:
                    radio = 'UNKNOWN'

                record = {
                    'radio': radio,
                    'RSRP': nr_rsrp if nr_rsrp else rsrp,
                    'RSRQ': nr_rsrq if nr_rsrq else rsrq,
                    'RSRP_4G': rsrp,
                    'RSRQ_4G': rsrq,
                    'RSRP_5G': nr_rsrp,
                    'RSRQ_5G': nr_rsrq,
                    'moni': moni_string
                }

                pprint(record)
                self.logger.set_signal(record)

                time.sleep(1)

            except Exception as exc:
                traceback.print_exc()
                lg.error(f'There was error: {exc}')
                self.wait_10s()

    def run(self):
        self._loop()
