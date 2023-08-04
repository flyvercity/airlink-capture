import sys
import logging as lg
import traceback
import subprocess
import time

import signal_parsers as sp


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
        response = subprocess.run(
            command,
            capture_output=True
        )

        answer = response.stdout.decode('utf-8')
    else:
        result = subprocess.run(command, stdout=subprocess.PIPE)
        answer = result.stdout.decode('utf-8')

    print('Raw response:', answer)
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
        while True:
            try:
                lg.debug('Signal :: Entering the cycle')
                while True:
                    if self.event.is_set():
                        lg.debug('Signal :: Exiting')
                        return

                    lg.debug('Signal :: Quality query')
                    moni_string = send_command('AT#MONI')
                    lg.info(f'Signal :: Quality: {moni_string}')
                    rsrp = sp.get_rsrp(moni_string)
                    rsrq = sp.get_rsrq(moni_string)
                    nr_rsrp = sp.get_nr_rsrp(moni_string)
                    nr_rsrq = sp.get_nr_rsrq(moni_string)

                    record = {
                        'Radio': '5G' if nr_rsrp else '4G',
                        'RSRP': nr_rsrp if nr_rsrp else rsrp,
                        'RSRQ': nr_rsrq if nr_rsrq else rsrq
                    }

                    self.logger.set_signal(record)

                    time.sleep(1)

            except Exception as exc:
                traceback.print_exc()
                lg.error(f'There was error: {exc}')
                self.wait_10s()

    def run(self):
        self._loop()
