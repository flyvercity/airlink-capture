import json
import argparse
import logging
from pathlib import Path

from pygeodesy.formy import hubeny

GOOD_RSRP = -90


NO_SIGNAL_RSRP = -150
INF_DISTANCE = 100000


def gen_feature_collecion(features):
    return {
        'type': 'FeatureCollection',
        'features': features
    }


def get_feature(record):
    pos = record['position']
    sign = record['signal']

    feature = {
        'type': 'Feature',
        'geometry': {
            'type': 'Point',
            'coordinates': [
                pos['lon'],
                pos['lat'],
                pos['alt']
            ]
        },
        'properties': {
            'rsrp': sign['rsrp']
        }
    }

    return feature


def record_to_feature(record_str):
    record = json.loads(record_str)
    return get_feature(record)


def parse_fcvf(fcvf_file, geo_file):
    with fcvf_file.open() as file:
        features = [record_to_feature(line) for line in file.readlines()]

    json_str = json.dumps(gen_feature_collecion(features), indent=2)
    geo_file.write_text(json_str)


def convert_to_geojson(fcvf_file):
    geo_file = Path(fcvf_file.parent, 'geo_' + str(fcvf_file.stem) + '.json')
    print('Transforming', fcvf_file, ' => ', geo_file)
    parse_fcvf(fcvf_file, geo_file)


def process_fcvf_file(fcvf_file, args):
    if args.type == 'geojson':
        convert_to_geojson(fcvf_file)
        return

    raise RuntimeError('Unknown output type:', args.type)


def cli_getargs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', "--verbose", action='store_true', help="Sets logging level to debug")
    parser.add_argument('-f', "--file", help="fcvf log file")
    parser.add_argument('-d', "--dir", help="fcvf logs directory")
    parser.add_argument('-t', '--type', help="Output file type", required=True, choices=['geojson'])
    return parser.parse_args()


def main():
    args = cli_getargs()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    if args.file:
        process_fcvf_file(Path(args.file))
        return

    if args.dir:
        for fcvf_file in Path(args.dir).glob('*.txt'):
            process_fcvf_file(fcvf_file, args)
        return

    raise RuntimeError('Either --file or --dir must be specified')


if __name__ == '__main__':
    main()
