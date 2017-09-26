# -*- coding: utf-8 -*-
import re
import os
import json
import pandas 
import codecs
import pickle
import random
import crawler
import hashlib

import data_io as dio
import pagehome as ph
from utility import email_getter
from utility import homepage_neg
from utility import homepage_pos
from utility import head_phote_filter
from utility import email_pic_filter
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
        pic_url = head_phote_filter(pic_url)
    if filter == 'email':
        pic_url = email_pic_filter(pic_url)
    # return pic_url
    if len(pic_url) == 0:
        return []
    else:
        return pic_url

def data_pic_url(data, html):
    """
    Input: data - standard DataFrame
           html - dict of {'id': html content}
    """
    pics = {}
    for i, r in data.iterrows():
        pics[r['id']] = crawler.get_pic_url(html[r['id']], r['homepage'])
    return pics

def generat_ans_file(data, flag=True, path='first_task_ans.txt'):
    with codecs.open(path, 'w', encoding='utf-8') as f:
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

def get_email(name, email):
    """
    Return a list of email address for given html
    """
    # if html == '':
    #     return []
    # # text = get_clean_text(html)
    # text = html
    # email = []
    # for i in text.split('\\n'):
    #     t = email_getter(i)
    #     if t != '':
    #         email.extend(t)
    # return list(set(email))
    max_score = -1
    if len(email) == 0:
        return ''
    for i in email:
        score = ph.check_name_in_text(name, i)
        if score >= max_score:
            if score == max_score:
                # To handle to suiation of ['chaomin.shen@asu.edu', 'cmshen {at} cs.ecnu.edu.cn']
                if len(i.split(' ')) <= len(ans.split(' ')):
                    continue
            max_score = score
            ans = i
        
    return ans

def predict_email(data, html):
    emails = {}
    for i, r in data.iterrows():
        email = get_email(r['name'], html[r['id']])
        emails[r['id']] = (r['name'], r['homepage'], email)
        # data.set_value(i, 'email', email)
    return emails

def get_homepage_html(data, prefix='./webpage/'):
    """
    Return homepage html text
    Input: data - standard DataFrame
    Ouput: html - dict of {'id': html content}
    """
    html = {}
    for i, r in data.iterrows():
        one_html = crawler.get_local_html(r['homepage'], prefix=prefix)
        html[r['id']] = one_html
    return html


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