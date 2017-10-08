from __future__ import division
import json
import codecs
from collections import Counter
import math


def count_interest_all(author_interest):
    all_interest = []
    for author,interest in author_interest.items():
        all_interest.extend(interest)
    length = len(all_interest)
    all_interest = Counter(all_interest)
    return all_interest,length

def assign_interest_to_press(author_train,author_interest):

    with codecs.open("./raw_data/t_author_press.json","r","utf-8") as fid:
        t_author_press = json.load(fid)

    interest_count,length = count_interest_all(author_interest)
    press_interest = {}
    indx = 0
    author_seq = []
    for author in author_train:
        interest = author_interest[author]
        for press in t_author_press[author]:
            press_interest.setdefault(press,[]).extend(interest)
    interest_score = calculate_interest_score(interest_count,length)

    f_press_interest = {}
    for press,interest in press_interest.items():
        calculate_interest_value(f_press_interest,press,interest,interest_count,interest_score)
    return f_press_interest
    #with codecs.open("press_interest_count_value.json","w","utf-8") as fid:
    #    json.dump(f_press_interest,fid)

def calculate_interest_score(interest_count,length):

    interest_idf = {}
    for k,v in interest_count.items():
        idf = math.exp(1/v-1)
        interest_idf.setdefault(k,idf)
    return interest_idf

def calculate_interest_value(f_press_interest,press,interest,interest_count,interest_score):
    c_interest = Counter(interest)
    len_interest = len(interest)
    for k,v in c_interest.items():
        num = (v/len_interest)#*(interest_score[k])
        f_press_interest.setdefault(press,{}).setdefault(k,num)
    return f_press_interest

def calculate_press_score(t_author_press):
    press_list = []
    for k,v in t_author_press.items():
        press_list.extend(v)

    c_press = Counter(press_list)
    #len_interest = len(interest)
    press_score = {}
    for k,v in c_press.items():
        num = math.exp(1/v-1)
        press_score.setdefault(k,num)
    return press_score,c_press

def predict_test_interest(author_test,author_interest,press_interest,t_author_press,p_author_press):

    press_score,all_press_count = calculate_press_score(t_author_press)
    for vali_m in range(1):
        #accuracy = 0
        #p_author_interest = {}
        p_author_interest_score = {}
        for author in author_test:
            p_interest,p_interest_score = find_interest_by_count(press_interest,p_author_press[author],press_score,all_press_count)
            #p_author_interest.setdefault(author,p_interest)
            p_author_interest_score.setdefault(author,p_interest_score)
            #accuracy += len(set(author_interest[author])&set(p_interest))/3
        #print (accuracy/1000)
    return p_author_interest_score

def predict_vali_interest(author_vali,author_interest,press_interest,t_author_press):

    press_score,all_press_count = calculate_press_score(t_author_press)
    for vali_m in range(1):
        accuracy = 0
        p_author_interest = {}
        p_author_interest_score = {}
        for author in author_vali:
            p_interest,p_interest_score = find_interest_by_count(press_interest,t_author_press[author],press_score,all_press_count)
            p_author_interest.setdefault(author,p_interest)
            p_author_interest_score.setdefault(author,p_interest_score)
            accuracy += len(set(author_interest[author])&set(p_interest))/3
        print (accuracy/1000)
    return p_author_interest_score

def find_interest_by_count(press_interest,press_list,press_score,all_press_count):
    interest_score = {}
    count_press = Counter(press_list)
    for p,w in count_press.items():
        if p not in press_interest.keys():
            continue
        for k,v in press_interest[p].items():
            interest_score.setdefault(k,0)
            #interest_score[k] += v*math.exp(w/all_press_count[p]-1)#*math.exp(w/len(press_list))#*press_score[p]
            interest_score[k] += v*(w/len(press_list))*press_score[p]
    result = sorted(interest_score.items(),key=lambda item:item[1],reverse=True)
    interest = []
    for i in result[:5]:
        interest.append(i[0])
    return interest,interest_score

def press_main(author_train,author_vali,author_test,author_interest,flag):

    with codecs.open("./raw_data/t_author_press.json","r","utf-8") as fid:
        t_author_press = json.load(fid)
    with codecs.open("./raw_data/p_author_press.json","r","utf-8") as fid:
        p_author_press = json.load(fid)
    press_interest = assign_interest_to_press(author_train,author_interest)
    if flag == 'vali':
        p_author_interest_score = predict_vali_interest(author_vali,author_interest,press_interest,t_author_press)
    if flag == 'test':
        p_author_interest_score = predict_test_interest(author_test,author_interest,press_interest,t_author_press,p_author_press)
    return p_author_interest_score

