from geopy.distance import geodesic
import numpy as np
import functools
import re


coords = {
    'MOSKBAL': {'lat': 55.8, 'lon': 37.5},
    'MONCHEG': {'lat': 67.9, 'lon': 32.9},
}


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
