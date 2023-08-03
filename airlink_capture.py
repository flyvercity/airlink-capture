import time
from argparse import ArgumentParser
from threading import Thread, Event
import logging as lg

import signal_capture
import coord_capture


def main():
    parser = ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('--src', type=int, default=coord_capture.default_src())
    parser.add_argument('--remote', type=str, default='127.0.0.1:14560')
    args = parser.parse_args()
    lg.basicConfig(level=lg.DEBUG if args.verbose else lg.INFO)
    event = Event()
    coords = coord_capture.CoordCapture(args, event)
    coord_thread = Thread(target=coords.run)
    coord_thread.daemon = True
    coord_thread.start()
    signal = signal_capture.SignalCapture(args, event)
    signal_thread = Thread(target=signal.run)
    signal_thread.daemon = True
    signal_thread.start()

    while True:
        try:
            print('Press Ctrl+C to exit')
            time.sleep(10)
        except KeyboardInterrupt:
            lg.info('Exiting')
            event.set()
            break

    coord_thread.join()
    signal_thread.join()


if __name__ == '__main__':
    main()
