# -*- coding: utf-8 -*-
import json
import codecs

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.svm import SVR
from sklearn.datasets import load_svmlight_file
training_data = './task3/train.feature.txt'
validation_data = './task3/validation.feature.txt'

def train_model(data_path=training_data):
    X, y = load_svmlight_file(data_path)
    model = SVR()
    model.fit(X, y)

    return model
def get_score(y, y_pred):
    score = 0
    for i in range(len(y)):
        if y[i] ==  y_pred[i] and y[i] == 0:
            continue
        score += abs(y[i] - y_pred[i]) / max(y[i], y_pred[i])
    return 1 - score / len(y)

def xgb_model(data_path=training_data):
    X, y = load_svmlight_file(data_path)
    X_train = X[0:600000]
    y_train = y[0:600000]
    x_test = X[600000:]
    y_test = y[600000:]
    model = xgb.XGBRegressor()
    model.fit(X_train, y_train)
    y_pred = model.predict(X)
    print(get_score(y, y_pred))
    y_test_pred = model.predict(x_test)
    print(get_score(y_test_pred, y_test))

    return model

def generate_t3(y):
    data = pd.read_csv('./task3/validation.csv')
    with codecs.open('./third_ans.txt', 'w', 'utf-8') as f:
        f.write('<task3>\nauthorname\tcitation\n')
        for i, author in enumerate(data.AUTHOR):
            f.write(str(author) + '\t' + str(y[i]) + '\n')
        f.write('</task3>\n')


