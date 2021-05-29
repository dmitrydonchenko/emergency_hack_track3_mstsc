from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.svm import SVC
from catboost import CatBoostClassifier
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


# фичи обыкновенные
d_features = [
    'road_id', 'road_km', 'vsp_1', 'vsp_2', 'vsp_3', 'visib', 'clouds', 'wind_dir', 'avg_wind', 'max_wind', 'precip',
    'temp_on_measure', 'temp_min', 'temp_max', 'pressure'
]
# фичи категориальные
c_features = [
    'vsp_1_q', 'vsp_2_q', 'vsp_3_q', 'visib_q', 'clouds_q', 'weather_range_q', 'weather_on_measure_q', 'wind_dir_q',
    'avg_wind_q', 'max_wind_q', 'precip_q', 'temp_on_measure_q', 'temp_min_q', 'temp_max_q', 'humidity_q', 'pressure_q'
]
# колонки из atmos.pickle
atmos_cols = ['phenomenon', 'phenomenon_q', 'intensity', 'intensity_q']
# все фичи
a_features = d_features + c_features
# ...
prepared_train = 'train-merged.pickle'


def plot_feature_importance(X, model, feature_names, features_num):
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1][:features_num]

    # Print the feature ranking
    print('Feature ranking:')

    labels = []
    for indice in indices:
        labels.append(feature_names[indice])

    for f in range(features_num):
        print('%d. feature %s (%f)' % (f + 1, labels[f], importances[indices[f]]))

    # Plot the feature importances of the forest
    plt.figure(figsize=(18, 16))
    plt.title('Feature importances')
    plt.bar(range((features_num)), importances[indices], color='r', align='center')

    plt.xticks(range(features_num), labels, rotation = 45, ha='right')
    plt.xlim([-1, features_num])
    plt.tight_layout()
    plt.show()


def atmos_condition(x, atmos, cols):
    condition = (x.datetime >= atmos.dt_start) &\
                (x.datetime <= atmos.dt_end) &\
                (x.station == atmos.station)
    result = atmos[condition]
    if result.shape[0] > 0:
        return result.iloc[0][cols]
    else:
        return pd.DataFrame({x: [np.nan] for x in cols}).iloc[0]


def process(input, output, *, need_drop=True):
    # load
    train = pd.read_pickle(input)
    meteo = pd.read_pickle('meteo.pickle')
    atmos = pd.read_pickle('atmos.pickle')

    # prepare data
    if need_drop:
        train = train.dropna()
    meteo = meteo.dropna()
    meteo = meteo.rename(columns={'measure_dt': 'datetime'})
    meteo = meteo.sort_values('datetime')
    train = train.sort_values('datetime')

    meteo = meteo.drop(columns=['road_id', 'lat', 'lon'])
    atmos = atmos.drop(columns=['road_id', 'lat', 'lon'])

    train = pd.merge_asof(train, meteo, on='datetime', by='station')
    train[atmos_cols] = train.apply(lambda x: atmos_condition(x, atmos, atmos_cols), axis=1)
    if need_drop:
        train = train.dropna()

    train.to_pickle(output)

    return train


if __name__ == '__main__':
    if not Path(prepared_train).exists():
        print('--- Wait for process files ---')
        train = process('train.pickle', prepared_train)
        print('--- DONE ---')
    else:
        train = pd.read_pickle(prepared_train)

    x = train[d_features].values
    y = train.target.values

    # split
    X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.33, random_state=42)

    # train
    model_list = [
        ('LogisticRegression', LogisticRegression(solver='lbfgs', max_iter=2000).fit(X_train, y_train)),
        ('SVC', SVC().fit(X_train, y_train)),
    ]
    for name, model in model_list:
        print(f'--- {name} ---')
        # test
        result_train = f1_score(y_train, model.predict(X_train), average='macro')
        result_test = f1_score(y_test, model.predict(X_test), average='macro')
        print(f'f1_score_train = {result_train}')
        print(f' f1_score_test = {result_test}')

    print('--- CatBoost ---')
    # prepare
    cf_indices = [train[a_features].columns.get_loc(x) for x in c_features]
    x = train[a_features].values
    y = train.target.values

    # split
    X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.33, random_state=42)

    # train
    cf = CatBoostClassifier(iterations=100, auto_class_weights='Balanced', verbose=False)
    model = cf.fit(X_train, y_train, cat_features=cf_indices)

    # predict
    result_train = f1_score(y_train, model.predict(X_train), average='macro')
    result_test = f1_score(y_test, model.predict(X_test), average='macro')
    print(f'f1_score_train = {result_train}')
    print(f' f1_score_test = {result_test}')

    # features importance
    plot_feature_importance(X_train, model, a_features, len(a_features))
