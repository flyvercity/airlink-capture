import logging as lg
import traceback
import subprocess
import time

import signal_parsers as sp


def send_command(at_command):
    response = subprocess.run(
        [
            'mmcli',
            '-m', '0',
            '--command', at_command

        ],
        capture_output=True
    )

    answer = response.stdout.decode('utf-8')
    print('Raw response:', answer)
    return answer


class SignalCapture:
    def __init__(self, args, event):
        self.args = args
        self.event = event

    def wait_10s(self):
        for i in range(10):
            lg.info(f'Waiting {10 - i} seconds')
            time.sleep(1)

            if self.event.is_set():
                return

    def _loop(self, log):
        while True:
            try:
                self.wait_10s()
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
                    
                    record = {
                        'RSRP': rsrp,
                        'RSRQ': rsrq
                    }

                    time.sleep(1)

            except Exception as exc:
                traceback.print_exc()
                lg.error(f'There was error: {exc}')
                self.wait_10s()

    def run(self):
        with open('signal.txt', 'at') as log:
            self._loop(log)
