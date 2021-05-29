from pathlib import Path
import argparse

import pandas as pd


def preprocess(input, output):
    print(f'step 01: load {input}')
    df = pd.read_pickle(input)

    print('step 02: columns to categories')
    # нам нужны категории, а не текст
    df.start_q = df.start_q.astype('category')
    df.end_q = df.start_q.astype('category')
    df.station = df.station.astype('category')
    df.phenomenon_q = df.phenomenon_q.astype('category')
    df.intensity_q = df.intensity_q.astype('category')

    print('step 04: update phenomenon')
    # заполянем пробелы
    df.phenomenon.fillna('unknown', inplace=True)
    # переформатируем
    df.phenomenon = df.phenomenon.apply(lambda x: x.strip()).astype('category')

    print('step 05: update intensity')
    # заполянем пробелы
    df.intensity.fillna('unknown', inplace=True)
    # переформатируем
    df.intensity = df.intensity.apply(lambda x: x.strip()).astype('category')

    print('step 06: merge to dt_start')
    # если start_ts = NaN, то определяем его как 00:00
    df.start_ts.fillna('00:00', inplace=True)
    # и мёржим start_date и start_ts
    df['dt_start'] = df[['start_date', 'start_ts']].apply(lambda x: pd.to_datetime(' '.join(x)), axis=1)

    print('step 07: merge to dt_end')
    # если end_ts = NaN, то берём 23:59
    df.end_ts.fillna('23:59', inplace=True)
    # и мёржим end_date и end_ts
    df['dt_end'] = df[['end_date', 'end_ts']].apply(lambda x: pd.to_datetime(' '.join(x)), axis=1)

    print('step 08: add missing lat,lon')
    df.loc[df.station == 'MOSKBAL', 'lat'] = 55.8
    df.loc[df.station == 'MOSKBAL', 'lon'] = 37.5
    df.loc[df.station == 'MONCHEG', 'lat'] = 67.9
    df.loc[df.station == 'MONCHEG', 'lon'] = 32.9

    print('step 09: drop')
    # и дропаем ненужные колонки
    df = df.drop(columns=['Unnamed: 0', 'start_date', 'start_ts', 'end_date', 'end_ts'])
    # а также убираем данные раньше 2016 года
    df = df[df.dt_start >= pd.to_datetime('2016-01-01 00:00:00')]

    print(f'step 10: save to {output}')
    df.to_pickle(output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Prepare atmos file')
    parser.add_argument('-i', dest='input', required=True, type=Path, help='file to process')
    parser.add_argument('-o', dest='output', required=True, type=Path, help='output filepath')

    args = parser.parse_args()
    if args.input.exists():
        preprocess(args.input, args.output)
    else:
        print(f'File {args.input} not found!')
