from __future__ import division
import json
import codecs
from collections import Counter
import math
def assign_interest_to_press(vali_n=6000,vali_m=6):

    with codecs.open("t_author_press.json","r","utf-8") as fid:
        t_author_press = json.load(fid)

    with codecs.open("author_interest.json","r","utf-8") as fid:
        author_interest = json.load(fid)

    interest_count,length = count_interest_all(author_interest)
    press_interest = {}
    indx = 0
    author_seq = []
    for author,interest in author_interest.items():
        author_seq.append(author)
        if indx < vali_n:
            for press in t_author_press[author]:
                press_interest.setdefault(press,[]).extend(interest)
        indx += 1

    interest_idf = calculate_idf(press_interest)

    f_press_interest = {}
    for press,interest in press_interest.items():
        calculate_interest_value(f_press_interest,press,interest,interest_count,interest_idf)
    #with codecs.open("press_interest_count_value.json","w","utf-8") as fid:
    #    json.dump(f_press_interest,fid)

    return f_press_interest,author_seq

def count_interest_all(author_interest):
    all_interest = []
    for author,interest in author_interest.items():
        all_interest.extend(interest)
    length = len(all_interest)
    all_interest = Counter(all_interest)
    return all_interest,length

def calculate_idf(press_interest):
    interest = []
    for k,v in press_interest.items():
        interest.extend(v)
    interest = set(interest)

    d_length = len(press_interest)
    interest_idf = {}
    for v in interest:
        num = 0
        for p in press_interest.keys():
            if v in press_interest[p]:
                num += 1
        idf = math.log(d_length/num)
        interest_idf.setdefault(v,idf)

    return interest_idf

def calculate_interest_value(f_press_interest,press,interest,interest_count,interest_idf):
    c_interest = Counter(interest)
    len_interest = len(interest)
    for k,v in c_interest.items():
        num = (v/len_interest)#*(interest_idf[k])
        f_press_interest.setdefault(press,{}).setdefault(k,num)


def find_interest_by_count(press_interest,press_list):
    interest_score = {}
    count_press = Counter(press_list)
    for p in press_list:
        #weight = press_idf[p]*(count_press[p]/len(press_list))
        if p not in press_interest.keys():
            continue
        for k,v in press_interest[p].items():
            interest_score.setdefault(k,0)
            interest_score[k] += v
    result = sorted(interest_score.items(),key=lambda item:item[1],reverse=True)
    interest = []
    for i in result[:20]:
        interest.append(i[0])
    return interest

def calculate_press_tf(t_author_press):
    press_list = []
    for k,v in t_author_press.items():
        press_list.extend(v)
    press_count = Counter(press_list)
    return press_count

def predict_vali_interest():

    with codecs.open("author_interest.json","r","utf-8") as fid:
        author_interest = json.load(fid)

    with codecs.open("t_author_press.json","r","utf-8") as fid:
        t_author_press = json.load(fid)
    #with codecs.open("./press/press_interest_from_keyword.json","r","utf-8") as fid:
    #    press_interest = json.load(fid)
    for vali_m in range(1):
        press_interest,author_seq = assign_interest_to_press(5000,vali_m)
        #press_idf = calculate_idf(t_author_press)
        print (len(press_interest.keys()))
        accuracy = 0
        p_author_interest = {}
        for author in author_seq[-1000:]:
            p_interest = find_interest_by_count(press_interest,t_author_press[author])
            p_author_interest.setdefault(author,p_interest)
            accuracy += len(set(author_interest[author])&set(p_interest))/3
        print (accuracy/1000)

        with codecs.open("./data_merge/vali_predict_author_interest.json","w","utf-8") as fid:
            json.dump(p_author_interest,fid,ensure_ascii=False)


def predict_test_interest():

    #with codecs.open("author_interest.json","r","utf-8") as fid:
    #    author_interest = json.load(fid)

    with codecs.open("p_author_press.json","r","utf-8") as fid:
        p_author_press = json.load(fid)
    for vali_m in range(1):
        press_interest,author_seq = assign_interest_to_press(6000,6)
        #press_idf = calculate_idf(t_author_press)
        print (len(press_interest.keys()))
        #accuracy = 0
        p_author_interest = {}
        for author in p_author_press.keys():
            p_interest = find_interest_by_count(press_interest,p_author_press[author])
            p_author_interest.setdefault(author,p_interest)
            #accuracy += len(set(author_interest[author])&set(p_interest))/3
        #print (accuracy/1000)

        with codecs.open("./data_merge/p_predict_author_interest.json","w","utf-8") as fid:
            json.dump(p_author_interest,fid,ensure_ascii=False)


def predict_test_interest_old():

    with codecs.open("p_author_press.json","r","utf-8") as fid:
        p_author_press = json.load(fid)
    press_interest,author_seq = assign_interest_to_press(6000,4)
    author_interest = {}
    for author in p_author_press.keys():
        p_interest = []
        for pr in p_author_press[author]:
            if pr in press_interest.keys():
                p_interest.extend(press_interest[pr])
        p_interest = choose_n_interest(p_interest,10)
        author_interest.setdefault(author,p_interest)

    with codecs.open("p_interest_from_press.json","w","utf-8") as fid:
        json.dump(author_interest,fid)

def choose_n_interest(interest,n):
    r_interest = []
    c_interest = Counter(interest).most_common(n)
    #print (len(set(interest)))
    #print (len(interest)-len(set(interest)))
    for i in range(min(len(c_interest),n)):
        r_interest.append(c_interest[i][0])
    return r_interest


def predict_from_neighbor():
    with codecs.open("author_cooperators.json","r","utf-8") as fid:
        author_cooperators = json.load(fid)

    with codecs.open("author_interest.json","r","utf-8") as fid:
        author_interest = json.load(fid)

        accuracy = 0
        flag = 0
    for author in list(author_interest.keys())[-1000:]:
        print(flag)
        flag += 1
        p_interest = []
        for pr in author_cooperators[author]:
            if pr in author_interest.keys():
                p_interest.extend(author_interest[pr])
        #print (len(p_interest))
        p_interest = choose_n_interest(p_interest,10)
        accuracy += len(set(author_interest[author])&set(p_interest))/3
    print (accuracy/1000)
if __name__ == '__main__':
    #predict_test_interest()
    predict_vali_interest()
    #predict_from_neighbor()
    #assign_interest_to_press()
