import logging as lg
import traceback
import subprocess
import time


def send_command(at_command):
    return '#MONI: Test PLMN 1-1 NR_BAND:79 NR_BW:100 NR_ULBW:100 NR_CH:723360 NR_ULCH:723360 NR_PWR:-60dbm NR_RSRP:-71 NR_RSRQ:-10 NR_PCI:11 NR_SINR:56 NR_STATE:2 NR_TXPWR:239 NR_DLMOD:1 NR_ULMOD:0'
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
                    log.write(moni_string)
                    time.sleep(1)

            except Exception as exc:
                traceback.print_exc()
                lg.error(f'There was error: {exc}')
                self.wait_10s()

    def run(self):
        with open('signal.txt', 'at') as log:
            self._loop(log)
