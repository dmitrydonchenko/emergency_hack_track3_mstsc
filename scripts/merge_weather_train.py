from geopy.distance import geodesic
import pandas as pd
import numpy as np
import functools
import re


def insert_space(string):
    return string[0:3] + ' ' + string[3:]


def insert_dot(string):
    return string[0:2] + '.' + string[2:]


# функция, склеивающая колонки с координатами в кортеж
def coord_merge(dataframe):
    dataframe['lat_long'] = dataframe[['lat', 'lon']].apply(tuple, axis=1)
    return dataframe


# аналогичная функция для датасета, содержащего координаты, соответствующие километрам трассы (данные первого геокодера)
def coord_km(dataframe):
    dataframe['lat_geoc'] = round(dataframe['lat_geoc'], 2)
    dataframe['lon_geoc'] = round(dataframe['lon_geoc'], 2)
    dataframe['lat_long'] = dataframe[['lat_geoc', 'lon_geoc']].apply(tuple, axis=1)
    return dataframe


# получаем список метеостанций с координатами из поданного датасета Росгидромета
def stations_list(dataframe):
    dataframe = dataframe[['station', 'lat_long']]
    dataframe = dataframe.drop_duplicates()
    dataframe = dataframe.set_axis(range(0, len(dataframe)))
    return dataframe


# находим ближайшую метеостанцию, сопоставляя координаты километра трассы с координатами метеостанций из списка
def stat_km(point, stat_list):
    stations_list = stat_list
    lst = []
    if pd.isnull(point) == True:
        lst.append(np.nan)
    else:
        for i in stations_list['lat_long']:
            x = geodesic(point, i).km
            lst.append(x)
            stations_list['dist'] = pd.DataFrame(lst)
            y = stations_list['station'][stations_list['dist'] == stations_list['dist'].min()]
        y = y.to_string()
        y = re.sub('[0-9]', '', y)
        y = re.sub(' ', '', y)
        return y


if __name__ == '__main__':
    # данные двух геокодеров
    geo = pd.read_pickle('../../data-original/geo_data.pickle')
    # для примера загрузим метеорологические данные Росгидромета, в которых содержится полный список метеостанций, и сэмпл обучающей выборки
    meteo = pd.read_pickle('../../data-preprocessed/meteo.pickle')
    # тренировочные данные
    train = pd.read_pickle('../../data-original/train.pickle')

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
