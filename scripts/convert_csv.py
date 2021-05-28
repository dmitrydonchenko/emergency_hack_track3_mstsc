from pathlib import Path
import argparse

import pandas as pd


def convert_file(file, sep):
    print(f'process {file.name}')
    df = pd.read_csv(file, sep=sep)
    output = file.parent / str(file.stem + '.pickle')
    df.to_pickle(output)


def convert(folder, separator):
    for file in folder.glob('*.csv'):
        convert_file(file, separator)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert csv files to pickle')
    parser.add_argument('-i', dest='input', required=True, type=Path, help='file/folder with csv')
    parser.add_argument('-s', dest='separator', required=False, default=',', type=str,\
        help="separator symbol (default is ',')")

    args = parser.parse_args()
    if args.input.is_dir():
        convert(args.input, args.separator)
    elif args.input.is_file():
        convert_file(args.input, args.separator)
    else:
        print(f"{args.input} doesn't seem like file or folder!")
