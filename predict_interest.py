# -*- coding: utf-8 -*-
import json
import codecs
from collections import Counter

def titleInterest():
    
    with codecs.open("author_interest.json","r",'utf-8') as fid:
        author_interest = json.load(fid)

    with codecs.open("author_cooperators.json","r",'utf-8') as fid:
        author_cooperators = json.load(fid)
    
    title_interest = {}
    for key,value in title_authors.items():
        interest = []
        for tmp in value:
            if tmp in author_interest.keys():
                interest.extend(author_interest[tmp])
        interest_count = Counter(interest).most_common(5)

        for i in range(len(interest_count)):
            interest_values = interest_count[i][0]
        if len(interest) > 0 :
            title_interest.setdefault(key,interest_values)

    with codecs.open("title_interests.json","w",'utf-8') as fid:
        json.dump(title_interest,fid)

def predict_interest():
    with codecs.open("author_interest.json","r",'utf-8') as fid:
        author_interest = json.load(fid)

    with codecs.open("author_cooperators.json","r",'utf-8') as fid:
        author_cooperators = json.load(fid)
    
    fid_predict = codecs.open("interest_predict.txt","a",'utf-8')
    fid_predict.write("<task2>\n")

    inter_predict = {}
    for key,value in author_cooperators.items():
        # print(key)
        interest = []
        if key in author_interest.keys():
            interest = author_interest[key]
        else:
            interest = []
        for tmp in value:
            # print(tmp)
            if tmp in author_interest.keys():
                interest.extend(author_interest[tmp])
        interest_count = Counter(interest).most_common(5)

        for i in range(len(interest_count)):
            interest_values = interest_count[i][0]
        if len(interest) > 0 :
            inter_predict.setdefault(key,[]).append(interest_values)

    with codecs.open("validation.txt","r",'utf-8') as fid:
        for line in fid:
            if line == "\n":
                continue
            line = line.strip()
            fid_predict.write(line)
            if line in inter_predict.keys():
                for tmp in inter_predict[line]:
                    fid_predict.write("\t%s" %tmp.strip())
                for tmp in range(5 - len(inter_predict[line])):
                    fid_predict.write("\t''")
            else:
                for tmp in range(5):
                    fid_predict.write("\t''")
            fid_predict.write('\n')

    fid_predict.write("</task2>\n")
    fid_predict.close()