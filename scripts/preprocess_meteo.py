from pathlib import Path
import argparse

import pandas as pd

from extra import coords


def preprocess(input, output):
    print(f'step 01: load {input}')
    df = pd.read_pickle(input)

    print('step 02: add missing lat,lon')
    df.loc[df.station == 'MOSKBAL', 'lat'] = coords['MOSKBAL']['lat']
    df.loc[df.station == 'MOSKBAL', 'lon'] = coords['MOSKBAL']['lon']
    df.loc[df.station == 'MONCHEG', 'lat'] = coords['MONCHEG']['lat']
    df.loc[df.station == 'MONCHEG', 'lon'] = coords['MONCHEG']['lon']

    print('step 03: validate *_q values')
    # условия поиска невал невалидных значений
    weather_range_cond = (df.weather_range.isnull()) & (df.weather_range_q == 'Значение элемента достоверно')
    weather_on_cond = (df.weather_on_measure.isnull()) & (df.weather_on_measure_q == 'Значение элемента достоверно')
    max_wind_cond = (df.max_wind.isnull()) & (df.max_wind_q == 'Значение элемента достоверно и восстановлено автоматически')
    # фиксим их
    missing_label = 'Значение элемента отсутствует'
    df.loc[weather_range_cond, 'weather_range_q'] = missing_label
    df.loc[weather_on_cond, 'weather_on_measure_q'] = missing_label
    df.loc[max_wind_cond, 'max_wind_q'] = missing_label

    print('step 04: categorise')
    # чистим текст и преобразуем в категории
    columns = [
        'vsp_1_q', 'vsp_2_q', 'vsp_3_q', 'visib_q', 'clouds_q', 'weather_range_q', 'weather_on_measure_q',
        'wind_dir_q', 'avg_wind_q', 'max_wind_q', 'precip_q', 'temp_on_measure_q', 'temp_min_q', 'temp_max_q',
        'humidity_q', 'pressure_q'
    ]
    df[columns] = df[columns].applymap(lambda x: x.replace('.', '').strip()).astype('category')

    print('step 05: to_datetime')
    # всё очевидно
    df.measure_dt = df.measure_dt.apply(pd.to_datetime)

    print('step 06: drop')
    # и дропаем ненужные колонки
    df = df.drop(columns=['Unnamed: 0'])
    # а также убираем данные раньше 2016 года
    df = df[df.measure_dt >= pd.to_datetime('2016-01-01 00:00:00')]

    print(f'step 07: save to {output}')
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
