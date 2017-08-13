#-*- coding=utf-8 -*-

import json
import codecs
import random
from collections import Counter
def find_key_word():

    interest_list = []
    with codecs.open("labels.txt","r","utf-8") as fid:
        for line in fid:
            if line == '\n':
                continue
            line = line.strip()
            interest_list.append(line)

    with codecs.open("p_author_paper.json","r","utf-8") as fid:
        p_author_paper = json.load(fid)

    fid_result = codecs.open("p_author_keyword.txt","w","utf-8")
    for key,value in p_author_paper.items():
        keyword = []
        fid_result.write(key+'\t')
        text = ' '.join(value)
        for v in interest_list:
            time = count_find_str(v,text)
            if  0 < time:
                keyword.extend([v]*time)
        fid_result.write('\t'.join(keyword)+'\n')
    fid_result.close()


def count_find_str(str2find,text):
    pos = text.find(str2find)
    time = 0
    while pos != -1:
        time = time+1
        pos = pos+len(str2find)
        pos = text.find(str2find,pos)
    return time


def merge_result():

    interest_from_neighbor = {}
    interest_from_title = {}
    with codecs.open("predict3.txt","r","utf-8") as fid:
        for line in fid:
            if line == '\n':
                continue
            line = line.strip()
            line = line.split('\t')
            interest_from_neighbor.setdefault(line[0],line[1:])

    with codecs.open("p_author_count_keyword.txt","r","utf-8") as fid:
        for line in fid:
            if line == '\n':
                continue
            line = line.strip()
            line = line.split('\t')
            interest_from_title.setdefault(line[0],line[1:])
    
    fid_result = codecs.open("neighbor_title.txt","w","utf-8")
    with codecs.open("validation.txt","r","utf-8") as fid:
        for line in fid:
            if line == '\n':
                continue
            line = line.strip()
            fid_result.write(line+'\t')
            interest = []
            interest_title = return_n_interest(interest_from_title[line],2)
            interest_neighbor = interest_from_neighbor[line]
            if len(interest_title) < 2:
                if len(interest_title) == 1:
                    interest.extend(interest_neighbor[:4])
                    interest.extend(interest_title)
                else:
                    interest.extend(interest_neighbor)
            else:
                interest.extend(interest_neighbor[:3])
                interest.extend(interest_title[:2])

            #intersection_set = set(interest_from_neighbor[line]) & set(interest_from_title[line])
#            union_set = (set(interest_from_neighbor[line]) | set(interest_from_title[line]))- \
#            intersection_set

#            interest = []
#            interest.extend(list(intersection_set))
#            interest.extend(random.sample(list(union_set),min(5-len(intersection_set),len(union_set))))
#            interest.extend(['']*(5-len(interest)))
            fid_result.write('\t'.join(interest)+'\n')
#            fid_result.write('\n')
    fid_result.close()




def return_n_interest(interest,n):
    tmp = Counter(interest).most_common(n)
    r_interest = []
    for v in tmp:
        r_interest.append(v[0])
    r_interest.extend(['']*(n-len(r_interest)))
    return r_interest

if __name__ == '__main__':
    #find_key_word()
    merge_result()
