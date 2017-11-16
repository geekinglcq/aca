from __future__ import division
import json
import codecs
from collections import Counter
import math

def count_interest(author_seq,author_interest):
    print ("exp(1-1/count)")
    interest_list = []
    for author in author_seq:
        interest_list.extend(author_interest[author])
    c_interest = Counter(interest_list)
    interest_score = {}
    for interest,count in c_interest.items():
        #interest_score.setdefault(interest,math.exp(1-1/count))
        interest_score.setdefault(interest,math.exp(1-1/math.sqrt(count)))
    return interest_score



def find_similar_author(author_train_indx,indx_list):
    author_score = {}
    for author in author_train_indx.keys():
        num =calculate_similarity(author_train_indx[author],indx_list)
        author_score.setdefault(author,num)
    return author_score

def calculate_similarity(list_1,list_2):
    num = 0
    #for v in list_2:
    #    if v in list_1:
    #        num += 1
    #num = num/(len(list_2)+len(list_1))
    num = (len(set(list_1)&set(list_2))/len(set(list_2)|set(list_1)))#*math.exp(1/len(list_1)**4)
    return num

def predict_by_indx_similarity(author_train,author_vali,author_indx_citeindx,indx_neighbors,author_interest):
    author_train_indx = {}
    author_vali_indx = {}
    for author in author_train:
        indx_list = []
        for indx in author_indx_citeindx[author].keys():
            indx_list.append(str(indx))
            #indx_list.extend(map(str,cit))
            #for v in indx_neighbors[str(indx)]:
            #    indx_list.append(v)
            indx_list.extend(indx_neighbors[str(indx)])
        author_train_indx.setdefault(author,indx_list)

    interest_score = count_interest(author_train,author_interest)

    predict_author_interest = {}
    predict_author_interest_score = {}
    flag = 0
    for author in author_vali:
        print (flag)
        flag += 1

        indx_list = []
        for indx in author_indx_citeindx[author].keys():
            indx_list.append(str(indx))
            #for k,v in indx_neighbors[str(indx)].items():
            indx_list.extend(indx_neighbors[str(indx)])
        result = find_similar_author(author_train_indx,indx_list)
        interest_s = {}
        for author_r,score in result.items():
            for inst in author_interest[author_r]:
                interest_s.setdefault(inst,0)
                interest_s[inst] += interest_score[inst]*score
                #interest_s[inst] += score
        predict_author_interest_score.setdefault(author,interest_s)

        interest_s = sorted(interest_s.items(),key=lambda x:x[1],reverse=True)
        interest = []
        for v in interest_s[:5]:
            interest.append(v[0])
        predict_author_interest.setdefault(author,interest)

    return predict_author_interest,predict_author_interest_score

def print_validation_result(predict_author_interest,author_interest):

    accuracy = 0
    print (predict_author_interest)
    print (len(predict_author_interest.keys()))
    for author in predict_author_interest.keys():
        accuracy = accuracy + (len(set(predict_author_interest[author])&set(author_interest[author])))/3
    print ("result by indx_similarity : "+ str(accuracy/1000))

def similarity_by_indx(author_train,author_vali,author_test,author_interest,flag):
    with codecs.open("./raw_data/author_indx_citeindx.json","r","utf-8") as fid:
        author_indx_citeindx = json.load(fid)

    with codecs.open("./raw_data/indx_neighbors.json","r","utf-8") as fid:
        indx_neighbors = json.load(fid)
    if flag == 'vali':
        predict_author_interest,predict_author_interest_score = predict_by_indx_similarity(author_train,author_vali,author_indx_citeindx,indx_neighbors,author_interest)
        print_validation_result(predict_author_interest,author_interest)
    if flag == 'test':
        predict_author_interest,predict_author_interest_score = predict_by_indx_similarity(author_train,author_test,author_indx_citeindx,indx_neighbors,author_interest)

    return predict_author_interest_score

def similarity_by_press(author_train,author_vali,author_test,author_interest,flag):

    with codecs.open("./raw_data/t_author_press.json","r","utf-8") as fid:
        t_author_press = json.load(fid)

    with codecs.open("./raw_data/p_author_press.json","r","utf-8") as fid:
        p_author_press = json.load(fid)
    if flag == 'vali':
        predict_author_interest,predict_author_interest_score =  predict_by_press_similarity(author_train,author_vali,t_author_press,p_author_press,author_interest)
        print_validation_result(predict_author_interest,author_interest)
    if flag == 'test':
        predict_author_interest,predict_author_interest_score =  predict_by_press_similarity(author_train,author_test,t_author_press,p_author_press,author_interest)

    return predict_author_interest_score


def predict_by_press_similarity(author_train,author_vali,t_author_press,p_author_press,author_interest):
    author_train_press = {}
    author_vali_press = {}
    for author in author_train:
        press_list = []
        press_list.extend(t_author_press[author])
        author_train_press.setdefault(author,press_list)

    interest_score = count_interest(author_train,author_interest)

    predict_author_interest = {}
    predict_author_interest_score = {}
    flag = 0
    for author in author_vali:
        print (flag)
        flag += 1
        press_list = []
        press_list.extend(t_author_press[author])
        result = find_similar_author(author_train_press,press_list)
        interest_s = {}
        for author_s,score in result.items():
            for inst in author_interest[author_s]:
                interest_s.setdefault(inst,0)
                interest_s[inst] += score# interest_score[inst]*score
        predict_author_interest_score.setdefault(author,interest_s)

        interest_s = sorted(interest_s.items(),key=lambda x:x[1],reverse=True)
        interest = []
        for v in interest_s[:5]:
            interest.append(v[0])
        predict_author_interest.setdefault(author,interest)

    return predict_author_interest,predict_author_interest_score

def similarity_by_interest_press(author_train,author_vali,author_test,author_interest,flag):

    with codecs.open("./raw_data/t_author_press.json","r","utf-8") as fid:
        t_author_press = json.load(fid)

    with codecs.open("./raw_data/p_author_press.json","r","utf-8") as fid:
        p_author_press = json.load(fid)
    if flag == 'vali':
        predict_author_interest,predict_author_interest_score =  predict_by_interest_press_similarity(author_train,author_vali,t_author_press,p_author_press,author_interest)
        print_validation_result(predict_author_interest,author_interest)
    if flag == 'test':
        predict_author_interest,predict_author_interest_score =  predict_by_interest_press_similarity(author_train,author_test,t_author_press,p_author_press,author_interest)

    return predict_author_interest_score

def predict_by_interest_press_similarity(author_train,author_vali,t_author_press,p_author_press,author_interest):
    interest_train_press = {}
    author_vali_press = {}

    for author in author_train:
        for interest in author_interest[author]:
            interest_train_press.setdefault(interest,[]).extend(t_author_press[author])

    interest_score = count_interest(author_train,author_interest)

    predict_author_interest = {}
    predict_author_interest_score = {}
    flag = 0
    for author in author_vali:
        print (flag)
        flag += 1
        press_list = []
        press_list.extend(t_author_press[author])
        result = find_similar_author(interest_train_press,press_list)
        predict_author_interest_score.setdefault(author,result)

        result = sorted(result.items(),key=lambda x:x[1],reverse=True)
        interest = []
        for v in result[:5]:
            interest.append(v[0])
        predict_author_interest.setdefault(author,interest)

    return predict_author_interest,predict_author_interest_score

