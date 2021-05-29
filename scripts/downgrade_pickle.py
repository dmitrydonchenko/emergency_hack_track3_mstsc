from pathlib import Path
import argparse

import pandas as pd


def convert_file(input, output, protocol):
    result = output / input.name
    df = pd.read_pickle(input)
    df.to_pickle(result, protocol=protocol)

def convert(input, output, protocol):
    for file in input.glob('*.pickle'):
        process_file(file, output, protocol)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Downgrade pickle protocol')
    parser.add_argument('-i', dest='input', required=True, type=Path, help='input folder to process')
    parser.add_argument('-o', dest='output', required=True, type=Path, help='output folder')
    parser.add_argument('-p', dest='protocol', required=True, type=int, help='pickle protocol version')

    args = parser.parse_args()
    if args.input == args.output:
        print('Input and output folders do not have to be the same')
        exit()

    if not args.input.exists():
        print(f'{args.input} not found!')
        exit()

    if args.input.is_dir():
        convert(args.input, args.output, args.protocol)
    elif args.input.is_file():
        convert_file(args.input, args.output, args.protocol)
    else:
        print(f"{args.input} doesn't seem like file or folder!")
