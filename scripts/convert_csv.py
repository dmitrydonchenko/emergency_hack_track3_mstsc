from pathlib import Path
import argparse

import pandas as pd


def convert(folder):
    for file in folder.glob('*.csv'):
        print(f'process {file.name}')
        df = pd.read_csv(file)
        output = folder.parent / str(file.stem + '.pickle')
        df.to_pickle(output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert csv files to pickle')
    parser.add_argument('-f', dest='folder', required=True, type=Path, help='folder with csv files')

    args = parser.parse_args()
    if args.folder.is_dir()
        convert(args.folder)
    else:
        print(f"{args.folder} doesn't seem like folder!")
