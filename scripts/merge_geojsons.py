from pathlib import Path
import argparse
import json

import pandas as pd


def get_coord_or_none(x, k1, k2):
    value = x.get(k1)
    if value:
        return value.get(k2)
    return None


def process(folder, output):
    items = []
    for file in folder.glob('*.geojson'):
        print(f'process {file.name}')
        with file.open() as f:
            data = json.load(f)
            for item in data.get('features', []):
                item = item.get('properties', [])
                health_status = []
                violations = []
                vehicles_year = []
                vehicles_brand = []
                vehicles_category = []
                for vehicle in item.get('vehicles', []):
                    for participant in vehicle.get('participants', []):
                        if (value := participant.get('health_status')):
                            health_status.append(value)
                        violations.extend(participant.get('violations', []))
                    if (value := vehicle.get('2012')):
                        vehicles_year.append(value)
                    if (value := vehicle.get('brand')):
                        vehicles_brand.append(value)
                    if (value := vehicle.get('category')):
                        vehicles_category.append(value)
                items.append({
                    'id': item.get('id'),
                    'tags': '|'.join(set(item.get('tags', []))),
                    'light': item.get('light'),
                    'lat': get_coord_or_none(item, 'point', 'lat'),
                    'lon': get_coord_or_none(item, 'point', 'long'),
                    'nearby': '|'.join(set(item.get('nearby', []))),
                    'region': item.get('region'),
                    'address': item.get('address'),
                    'weather': '|'.join(set(item.get('weather', []))),
                    'category': item.get('category'),
                    'datetime': item.get('datetime'),
                    'severity': item.get('severity'),
                    'health_status': '|'.join(set(health_status)),
                    'violations': '|'.join(set(violations)),
                    'vehicles_year': '|'.join(set(vehicles_year)),
                    'vehicles_brand': '|'.join(set(vehicles_brand)),
                    'vehicles_category': '|'.join(set(vehicles_category)),
                    'dead_count': item.get('dead_count'),
                    'injured_count': item.get('injured_count'),
                    'parent_region': '|'.join(set(item.get('parent_region', []))),
                    'road_conditions': '|'.join(set(item.get('road_conditions', []))),
                    'participants_count': item.get('participants_count'),
                    'participant_categories': '|'.join(set(item.get('participant_categories', [])))
                })
    df = pd.DataFrame(items)
    df.datetime = df.datetime.apply(lambda x: pd.to_datetime(x))
    df.to_pickle(output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Merge geojsons from dtp-stat.ru')
    parser.add_argument('-f', dest='folder', required=True, type=Path, help='folder to process')
    parser.add_argument('-o', dest='output', required=True, type=Path, help='output file')

    args = parser.parse_args()
    if args.folder.exists():
        process(args.folder, args.output)
    else:
        print(f'Folder {args.folder} not found!')
