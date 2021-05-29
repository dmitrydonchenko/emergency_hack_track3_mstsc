from regression import *
import pickle


def save_model(model, output):
    with open(output, 'wb') as f:
        pickle.dump(model, f)


if __name__ == '__main__':
    train = pd.read_pickle(prepared_train)

    x = train[d_features].values
    y = train.target.values

    m1 = LogisticRegression(solver='lbfgs', max_iter=2000).fit(x, y)
    m2 = SVC(max_iter=2000).fit(x, y)

    save_model(m1, 'LogisticRegression.pickle')
    save_model(m2, 'SVC.pickle')

    c_features = [x for x in c_features if '_q' not in x]
    a_features = d_features + c_features
    cf_indices = [train[a_features].columns.get_loc(x) for x in c_features]
    x = train[a_features].values
    y = train.target.values

    m3 = CatBoostClassifier(iterations=2000, auto_class_weights='Balanced', verbose=False)\
            .fit(x, y, cat_features=cf_indices)

    save_model(m3, 'CatBoostClassifier.pickle')

    for model in [m1, m2, m3]:
        result = f1_score(y, model.predict(x), average='macro')
        print(f'f1_score = {result}')
