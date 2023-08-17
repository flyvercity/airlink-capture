import json
import argparse
import logging as lg
from pathlib import Path


class StatCounter:
    def __init__(self):
        self._count = 0
        self._sum = 0
        self._min = None
        self._max = None

    def update(self, value):
        self._count += 1
        self._sum += value
        self._min = min(self._min, value) if self._min is not None else value
        self._max = max(self._max, value) if self._max is not None else value

    def count(self):
        return self._count

    def min(self):
        return self._min

    def max(self):
        return self._max

    def avg(self):
        if self._count == 0:
            return None

        return self._sum / self._count

    def print(self):
        print('Count:', self.count())
        print('Min:', self.min())
        print('Max:', self.max())
        print('Avg:', self.avg())


class Stats:
    def __init__(self):
        self._total_count = 0
        self._link_loss_s = 0
        self._rpsp_4g_s = StatCounter()
        self._rpsp_5g_s = StatCounter()
        self._alt_s = StatCounter()
        self._rsrq_4g_s = StatCounter()
        self._rsrq_5g_s = StatCounter()

    def update(self, record):
        if not record:
            return

        try:
            self._total_count += 1

            if record['signal']['RSRP'] is None:
                self._link_loss_s += 1

            if record['signal']['RSRP_4G'] is not None:
                self._rpsp_4g_s.update(record['signal']['RSRP_4G'])

            if record['signal']['RSRP_5G'] is not None:
                self._rpsp_5g_s.update(record['signal']['RSRP_5G'])

            if record['position']['location']['alt'] is not None:
                self._alt_s.update(record['position']['location']['alt'])

            if record['signal']['RSRQ_4G'] is not None:
                self._rsrq_4g_s.update(record['signal']['RSRQ_4G'])

            if record['signal']['RSRQ_5G'] is not None:
                self._rsrq_5g_s.update(record['signal']['RSRQ_5G'])

        except Exception as exc:
            lg.warning('Failed to update statistics: %s (%s)', record, exc)

    def print(self):
        print('Total count:', self._total_count)
        print('Link loss:', self._link_loss_s)
        print('\nRSRP 4G:')
        self._rpsp_4g_s.print()
        print('\nRSRP 5G:')
        self._rpsp_5g_s.print()
        print('\nRSRQ 4G:')
        self._rsrq_4g_s.print()
        print('\nRSRQ 5G:')
        self._rsrq_5g_s.print()
        print('\nAltitude:')
        self._alt_s.print()


class GeoJsonConverter:
    def extension():
        return '.geo.json'

    def record_to_feature(record):
        pos = record['position']
        loc = pos['location']
        sign = record['signal']

        feature = {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [
                    loc['lon'],
                    loc['lat'],
                    loc['alt']
                ]
            },
            'properties': {
                'rsrp': sign['RSRP']
            }
        }

        return feature

    def write_features(features, geo_file):
        collection = {
            'type': 'FeatureCollection',
            'features': features
        }

        json_str = json.dumps(collection, indent=2)
        geo_file.write_text(json_str)


def parse_record(record_str):
    try:
        record = json.loads(record_str)
        return record

    except Exception as exc:
        lg.error('Failed to parse record: %s (%s)', record_str, exc)
        return None


def convert(converter, fcvf_file, stats):
    out_file = Path(fcvf_file.parent, str(fcvf_file.stem) + converter.extension())
    print('Transforming', fcvf_file, ' => ', out_file)

    features = []
    with fcvf_file.open() as file:
        for line in file.readlines():
            record = parse_record(line)
            stats.update(record)

            if record:
                features.append(converter.record_to_feature(record))

    valid_features = list(filter(lambda f: f is not None, features))
    converter.write_features(valid_features, out_file)


def process_fcvf_file(fcvf_file, args, stats):
    if args.type == 'geojson':
        convert(GeoJsonConverter, fcvf_file, stats)
        return

    raise RuntimeError('Unknown output type:', args.type)


def cli_getargs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', "--verbose", action='store_true', help="Sets logging level to debug")
    parser.add_argument('-f', "--file", help="fcvf log file")
    parser.add_argument('-d', "--dir", help="fcvf logs directory")
    parser.add_argument('-t', '--type', help="Output file type", required=True, choices=['geojson'])
    return parser.parse_args()


def run_either_mode(args, stats):
    if args.file:
        process_fcvf_file(Path(args.file), args, stats)
        return

    if args.dir:
        for fcvf_file in Path(args.dir).glob('*.txt'):
            process_fcvf_file(fcvf_file, args, stats)
        return

    raise RuntimeError('Either --file or --dir must be specified')


def main():
    args = cli_getargs()
    lg.basicConfig(level=lg.DEBUG if args.verbose else lg.INFO)

    stats = Stats()
    run_either_mode(args, stats)
    stats.print()


if __name__ == '__main__':
    main()
