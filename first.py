# -*- coding: utf-8 -*-
import re
import os
import json
import pandas 
import codecs
import pickle
import random
import crawler
import utility


import data_io as dio
import xgboost as xgb

from utility import homepage_neg
from utility import homepage_pos
from pypinyin import lazy_pinyin
from scipy.sparse import csr_matrix
from bs4 import BeautifulSoup as bs
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


def photo_url(html, url, filter='head'):
    pic_url = crawler.get_pic_url(html, url)
    if filter == 'head':
        pic_url = utility.head_phote_filter(pic_url)
    if filter == 'email':
        pic_url = utility.email_pic_filter(pic_url)
    # return pic_url
    if len(pic_url) == 0:
        return []
    else:
        return pic_url

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

def one_sample_homepage_features(data, search_res, labeled=True):
    """
    Input: data - the row of dataframe. search_res - the list of search results info
    Ouput: features
    """
    features = []
    p = re.compile(r'University|university|大学|Institute|School|school|College')
    pos_p = re.compile('|'.join(homepage_pos))
    neg_p = re.compile('|'.join(homepage_neg))
    name = data['name'].replace('?', '')
    name_p = re.compile(r'|'.join(name.lower().split(' ')))
    
    if p.match(data["org"]):
        in_school = 1 # 0 
    else:
        in_school = 0
    if search_res == None:
        return []
    for i in range(len(search_res)):
        rank = i # 1
        title = ' '.join(lazy_pinyin(search_res[i][0]))
        url = search_res[i][1]
        content = search_res[i][2]
        is_cited = search_res[i][3] # 2
        pos_words_num = len(pos_p.findall(url)) # 3
        neg_words_num = len(neg_p.findall(url)) # 4
        edu = 1 if 'edu' in url else 0 # 5
        org = 1 if 'org' in url else 0 # 6
        gov = 1 if 'gov' in url else 0 # 7
        name_in = 1 if len(name_p.findall(title.lower())) != 0 else 0 # 8
        linkedin = 1 if 'linkedin' in url else 0 # 9
        title_len = len(title) # 10
        content_len = len(content) # 11

        if labeled:
            if url == data.homepage:
                label = 1
            else:
                # subsample
                if random.random() < 0.2:
                    label = 0
                else:
                    continue
        else:
            label = url
        features.append([label, in_school, rank, is_cited, pos_words_num, neg_words_num, edu, org, gov,\
        name_in, linkedin, title_len, content_len])

    return features

def extract_homepage_features(labeled=True, full_data=False):
    
    features = []
    if labeled:
        if full_data:
            raw_data = dio.read_former_task1_ans('./full_data/full_data_ans.txt', raw='./full_data/full_data.tsv', skiprows=False)
            search_info = json.load(open('./full_data/all_search_info.json'))
        else:
            raw_data = dio.read_task1('./task1/training.txt')
            search_info = dio.load_search_res(labeled)
    else:
        raw_data = dio.read_task1('./task1/validation.txt')
        search_info = dio.load_search_res(labeled)
    for i, r in raw_data.iterrows():
        samples = one_sample_homepage_features(r, search_info[r["id"]], labeled)
        if samples != []:
            features.extend(samples)
    if full_data:
        labeled = 'all'
    with open('./data/%s_features.svm.txt'%(labeled), 'w') as f:
        for feature in features:
            line = str(feature[0]) + ' '
            line = line + ' '.join([str(i) + ':' + str(feature[i]) for i in range(1, len(feature))]) + '\n'
            f.write(line)

def homepage_xgb_model(model_path, training_set='True'):
    training_set = './data/%s_features.svm.txt'%(training_set)
    model = xgb.XGBClassifier()
    X, y = load_svmlight_file(training_set)
    model.fit(X,y)
    pickle.dump(model, open(model_path, 'wb'))
    return model

def load_homepage_model(model_path):
    model = pickle.load(open(model_path, 'rb'))
    return model

def predict_one_homepage(model, data):
    """
    Input: model - the trained xgb model. data - features generated by `one_sample_homepage_features`
    Output: the predict url of homepage
    """
    features = csr_matrix([x[1:] for x in data ])
    urls = [i[0] for i in data]
    # return urls[0]
    pred = model.predict_proba(features)[: ,1]
    # print(pred)
    url = urls[pred.argmax()]
    if pred.max() < 0.5:
        url = urls[0]
    return url

def check_homepage_validity(name, res):
    """
    Check if the homepage is simtisfied basic rules.
    Input: name-name of expert res-homepage info list
    """
    title, url, detail, cited = res
    if url.endswith('pdf') or url.endswith('doc') or 'linkedin' in url.lower() or 'researchgate' in url.lower() or 'citations' in url.lower():
        return False
    # to check if the title or detail contains the name
    
    
    title = ' '.join(lazy_pinyin(title))
    name = name.replace('?', '')
    p = re.compile(r'|'.join(name.lower().split(' ')))
    if len(p.findall(title.lower())) == 0:
        return False
    
    #if 'wikipedia' in title.lower():
     #   return False
    return True

def simple_guess_homepage(data, res):
    """
    Use simple rules to guess homepage
    res - homepage search results 
    """
    for i in res:
        if check_homepage_validity(data['name'], i):
            return i[1]
    return res[0][1]

def get_email(html):
    """
    Return a list of email address for given html
    """
    if html == '':
        return []
    # text = utility.get_clean_text(html)
    text = html
    email = []
    for i in text.split('\\n'):
        t = utility.email_getter(i)
        if t != '':
            email.append(t)
    return email


def predcit_homepage_simple(data, res):
    """
    Assign homepage values using simple rules
    """
    for index, row in data.iterrows():
        homepage = simple_guess_homepage(row, res[row['id']])
        data.set_value(index, 'homepage', homepage)
    return data
def score_homepage_simple(data, res):
    """
    Score homepage generated by simple rules
    """
    score = 0
    for index, row in data.iterrows():
        homepage = simple_guess_homepage(row, res[row['id']])
        if homepage == row['homepage']:
            score += 1
    return score / data.shape[0]

def predict_homepage(model, data, res):
    """
    Assign homepage value to input data, using the input model.
    """
    for index, row in data.iterrows():
        features = one_sample_homepage_features(row, res[row['id']], labeled=False)
        homepage = predict_one_homepage(model, features)
        data.set_value(index, 'homepage', homepage)

    return data

def score_homepage(model, data, res):
    """
    To get the score of homepage result to input data, using the input model.
    """
    score = 0
    for index, row in data.iterrows():
        features = one_sample_homepage_features(row, res[row['id']], labeled=False)
        homepage = predict_one_homepage(model, features)
        if homepage == row['homepage']:
            score += 1
    print(score)
    return score / data.shape[0]

def get_homepage_html(data, prefix='./webpage/'):
    """
    Return homepage html text
    Input: data - [id, url]
    """
    if not os.path.isfile(prefix + data[0]):
        html_text = crawler.get_html_text(data[1])
        if html_text == '':
            return ''
        else:
            with codecs.open(prefix + data[0], 'w', 'utf-8') as f:
                f.write(html_text)
            return html_text
    else:
        with codecs.open(prefix + data[0], 'r', 'utf-8') as f:
            return f.read()


def score_to(ans, keys):
    """
    Return score the ans get.
    Ans and keys are key-value dict.
    key - expert id
    values - [homepage,gender,position,pic,email,location]
    """
    num = len(ans)
    goals = 0
    for i in ans:
        goal = 0
        x = ans[i]
        y = keys[i]
        for j in range(len(x)):
            if j != 2:
                if x[j] == y[j]:
                    goal += 1
            else:
                pos_x = set(x[j].split(';'))
                pos_y = set(y[j].split(';'))
                goal += len(pos_x & pos_y) / len(pos_x | pos_y)
        goals += goal
    goals = goals / (num * 6)
    return goals