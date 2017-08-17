# -*- coding: utf-8 -*-
import re
import json
import pandas 
import codecs
import pickle
import random
import crawler
import data_io as dio

import xgboost as xgb


from utility import homepage_neg
from utility import homepage_pos
from scipy.sparse import csr_matrix
from sklearn.metrics import accuracy_score
from sklearn.datasets import load_svmlight_file
from sklearn.model_selection import train_test_split

def generate_one_row(row, flag=True):
    """
    Input: one row data of pandas.series
    Output: the answer string 
    """
    if flag:
        ans = '\t'.join([row.id, row.homepage, row.gender, row.position, row.pic, row.email, row.location])
    else:
        ans = '\t'.join([row.expert_id, row.homepage_url, row.gender, row.position, row.person_photo, row.email, row.location])
    return ans + '\n'

def photo_url(url):
    pic_url = crawler.get_pic_url(url)
    if len(pic_url) == 0:
        return ''
    else:
        return pic_url[random.randint(0, len(pic_url) - 1)]

def generat_ans_file(data, flag=True):
    with codecs.open('first_task_ans.txt', 'w', encoding='utf-8') as f:
        f.write('<task1>\n')
        f.write('expert_id\thomepage_url\tgender\tposition\tperson_photo\temail\tlocation\n')
        for index, row in  data.iterrows():
            f.write(generate_one_row(row, flag))
        f.write('</task1>\n')

def extract_search_info():
    data = dio.read_task1('./task1/training.txt')
    print(data.shape)
    train_set_info = {}
    for index, row in data.iterrows():
        if (index < 5000):
            continue
        print(index)
        train_set_info[row.id] = crawler.get_search_page(row.search_results_page)
        if (index % 100) == 0:
            with open('train_search_info_5.json', 'w') as f:
                json.dump(train_set_info, f)
        # if (index >= 6000):
        #     break
    with open('train_search_info_5.json', 'w') as f:
        json.dump(train_set_info, f)
    #data = dio.read_task1('./task1/validation.txt')
    #test_set_info = {}
    #for index, row in data.iterrows():
    #    print(index)
    #    test_set_info[row.id] = crawler.get_search_page(row.search_results_page)
    #with open('train_search_info.json', 'w') as f:
    #    json.dump(test_set_info, f)

def one_sample_homepage_features(data, search_res, labeled):
    features = []
    p = re.compile(r'University|university|大学|Institute|School|school|College')
    pos_p = re.compile('|'.join(homepage_pos))
    neg_p = re.compile('|'.join(homepage_neg))
    if p.match(data["org"]):
        in_school = 1 # 1
    else:
        in_school = 0
    if search_res == None:
        return []
    for i in range(len(search_res)):
        rank = i # 2
        title = search_res[i][0]
        url = search_res[i][1]
        content = search_res[i][2]
        is_cited = search_res[i][3] # 3
        pos_words_num = len(pos_p.findall(url)) # 4
        neg_words_num = len(neg_p.findall(url)) # 5
        if labeled:
            if url == data.homepage:
                label = 1
            else:
                label = 0
        else:
            label = url
        features.append([label, in_school, rank, is_cited, pos_words_num, neg_words_num])

    return features

def extract_homepage_features(labeled=True):
    
    features = []
    if labeled:
        raw_data = dio.read_task1('./task1/training.txt')
        search_info = dio.load_search_res(labeled)
    else:
        raw_data = dio.read_task1('./task1/validation.txt')
        search_info = dio.load_search_res(labeled)
    for i, r in raw_data.iterrows():
        samples = one_sample_homepage_features(r, search_info[r["id"]], labeled)
        if samples != []:
            features.extend(samples)

    with open('./data/%s_features.svm.txt'%(labeled), 'w') as f:
        for feature in features:
            line = str(feature[0]) + ' '
            line = line + ' '.join([str(i) + ':' + str(feature[i]) for i in range(1, len(feature))]) + '\n'
            f.write(line)

def homepage_xgb_model(model_path):
    model = xgb.XGBClassifier()
    X, y = load_svmlight_file('./data/True_features.svm.txt')
    model.fit(X,y)
    pickle.dump(model, open(model_path, 'wb'))
    return model

def load_homepage_model(model_path):
    model = pickle.load(open(model_path, 'rb'))
    return model

def predict_one_homepage(model, data):
    features = csr_matrix([x[1:] for x in data ])
    urls = [i[0] for i in data]
    pred = model.predict_proba(features)[: ,1]
    return pred
    url = urls[pred.argmax()]
    if pred.max() < 0.9:
        url = urls[0]
    return url