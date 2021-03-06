from extra import *
import pandas as pd
import numpy as np
import functools


if __name__ == '__main__':
    # данные двух геокодеров
    geo = pd.read_pickle('geo_data.pickle')
    # для примера загрузим метеорологические данные Росгидромета, в которых содержится полный список метеостанций, и сэмпл обучающей выборки
    meteo = pd.read_pickle('meteo.pickle')
    # тренировочные данные
    train = pd.read_pickle('train.pickle')

    # удаляем наблюдения по трассе М-4
    train = train[(train['road_id'] != 5)]

    # используем данные первого геокодера
    geo = geo.dropna(subset=['lat_geoc'])
    geo = geo.dropna(subset=['lon_geoc'])
    geo = coord_km(geo)
    geo = geo[['road_id', 'road_km', 'lat_long']]

    # добавляем координаты в тренировочную выборку
    train_cord = pd.merge(train, geo, on=['road_id', 'road_km'], how='left')

    print('stage 1')
    coord_merge(meteo)
    print('stage 2')
    full_stations_list = stations_list(meteo)
    # мёржим
    print('stage 3')
    train_cord['station'] = train_cord['lat_long'].map(functools.partial(stat_km, stat_list=full_stations_list))
    print('stage 4')
    train_cord['station'] = train_cord['station'].where(pd.notnull(train_cord['station']), np.nan)
    print('stage 5')

    train_cord.to_pickle('train-with-station.pickle')
