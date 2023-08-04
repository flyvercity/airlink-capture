import time
from argparse import ArgumentParser
from threading import Thread, Event, Lock
import logging as lg
import json
import datetime

import signal_capture
import coord_capture


class Logger:
    def __init__(self, args):
        self.args = args
        self.lock = Lock()
        self.signal = None
        self.coords = None
        self.log = None

    def __enter__(self):
        now = datetime.datetime.utcnow().timetuple()
        date_str = time.strftime('%Y-%m-%d_%H-%M-%S', now)
        self.log = open(f'data/log_{date_str}.txt', 'w+')
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.log.close()

    def set_signal(self, signal):
        with self.lock:
            self.signal = signal

    def set_coords(self, coords):
        with self.lock:
            self.coords = coords

    def submit(self):
        with self.lock:
            record_str = json.dumps({
                'position': self.coords,
                'signal': self.signal
            })

        self.log.write(record_str + '\n')


def main():
    parser = ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('--src', type=int, default=coord_capture.default_src())
    parser.add_argument('--remote', type=str, default='127.0.0.1:14560')
    parser.add_argument('--nomavlink', action='store_true', default=False)
    parser.add_argument('--nomodem', action='store_true', default=False)
    args = parser.parse_args()
    lg.basicConfig(level=lg.DEBUG if args.verbose else lg.INFO)
    event = Event()

    with Logger(args) as logger:
        if not args.nomavlink:
            coords = coord_capture.CoordCapture(args, event, logger)
            coord_thread = Thread(target=coords.run)
            coord_thread.daemon = True
            coord_thread.start()

        if not args.nomodem:
            signal = signal_capture.SignalCapture(args, event, logger)
            signal_thread = Thread(target=signal.run)
            signal_thread.daemon = True
            signal_thread.start()

        while True:
            try:
                print('Press Ctrl+C to exit')

                while True:
                    time.sleep(1)
                    logger.submit()
                    print('.', end='', flush=True)

            except KeyboardInterrupt:
                lg.info('Exiting')
                event.set()
                break

        if not args.nomavlink:
            coord_thread.join()

        if not args.nomodem:
            signal_thread.join()


if __name__ == '__main__':
    main()
