import sys
import json
import argparse
import logging
from pathlib import Path

from pygeodesy.formy import hubeny

sys.path.append('..')
from unetstatsrv.core.common import GOOD_RSRP


NO_SIGNAL_RSRP = -150
INF_DISTANCE = 100000


def distance(lat1, lon1, lat2, lon2):
    distance = hubeny(lat1, lon1, lat2, lon2)
    return distance


def gen_feature_collecion(features):
    return {
        'type': 'FeatureCollection',
        'features': features
    }

        
def get_feature(record_5g):
    feature = {
        'type': 'Feature',
        'geometry': {
            'type': 'Point', 
            'coordinates': [
                record_5g['lon'],
                record_5g['lat'],
                record_5g['alt']
            ]
        },
        'properties': {
            'rsrp': record_5g['rsrp']
        }
    }

    return feature


def parse_record_5g(record_str):
    record_data = json.loads(record_str)
    bd = record_data['basicData']

    rsrp = NO_SIGNAL_RSRP

    for ci in record_data['cellInfos']:
        if 'nrSsRsrp' in ci:
            this_rsrp = int(ci['nrSsRsrp'])
            if this_rsrp > rsrp:
                rsrp = this_rsrp

    return {
        'id': record_data['id'],
        'lat': float(bd['lat']),
        'lon': float(bd['lon']),
        'alt': float(bd['alt']),
        'bearing': float(bd['bearing']),
        'speed': float(bd['speed']),
        'rsrp': rsrp
    }


def record_to_feature(record_str):
    record = parse_record_5g(record_str)
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


def generate_dataset(fcvf_file, config_path):
    csv_file = Path(fcvf_file.parent, 'dataset_' + str(fcvf_file.stem) + '.csv')
    print('Generating', fcvf_file, ' => ', csv_file)

    columns=[
        'index',
        'lat', 'lon', 'alt', 'bearing', 'speed',
        'd0', 'd1', 'd2',
        'rsrp', 'rsrp_good'
    ]

    with csv_file.open('w') as outfile:
        outfile.write(','.join(columns) + '\n')
        config = json.loads(config_path.read_text())
        stations = config['stations']

        index = 0
        with fcvf_file.open() as file:
            for line in file.readlines():
                record = parse_record_5g(line)

                d = {
                    i: distance(record['lat'], record['lon'], s['lat'], s['lon'])
                    for i, s in enumerate(stations)
                }

                values = [
                    index,
                    record['lat'],
                    record['lon'],
                    record['alt'],
                    record['bearing'],
                    record['speed'],
                    d.get(0, INF_DISTANCE),
                    d.get(1, INF_DISTANCE),
                    d.get(2, INF_DISTANCE),
                    record['rsrp'],
                    1 if record['rsrp'] > GOOD_RSRP else 0
                ]

                outfile.write(','.join(map(str, values)) + '\n')


def process_fcvf_file(fcvf_file, args):
    if args.type == 'geojson':
        convert_to_geojson(fcvf_file)
        return

    raise RuntimeError('Unknown output type:', args.type)


def cli_getargs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', "--verbose", action='store_true', help="Sets logging level to debug")
    parser.add_argument('-f', "--file", help = "fcvf log file")
    parser.add_argument('-d', "--dir", help="fcvf logs directory")
    parser.add_argument('-t', '--type', help="Output file type", required=True, choices=['geojson'])
    parser.add_argument('-c', '--config', help="Configuration file", required=True)
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
