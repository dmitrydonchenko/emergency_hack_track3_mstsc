from pathlib import Path
import argparse

import pandas as pd


def preprocess(input, output, protocol):
    for file in input.glob('*.pickle'):
        result = output / file.name
        df = pd.read_pickle(file)
        df.to_pickle(result, protocol=protocol)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Downgrade pickle protocol')
    parser.add_argument('-i', dest='input', required=True, type=Path, help='input folder to process')
    parser.add_argument('-o', dest='output', required=True, type=Path, help='output folder')
    parser.add_argument('-p', dest='protocol', required=True, type=int, help='pickle protocol version')

    args = parser.parse_args()
    if args.input == args.output:
        print('Input and output folders do not have to be the same')
        exit()
    if args.input.exists():
        preprocess(args.input, args.output, args.protocol)
    else:
        print(f'Folder {args.input} not found!')
