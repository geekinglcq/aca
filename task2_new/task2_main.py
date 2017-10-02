from __future__ import division
import codecs
import json
import author_similarity
import lsi_model
import press_model
import lsi_author
import numpy as np

def split_dataset(author_list):
    print("split dataset ...")
    author_train = author_list[:5000]
    author_vali = author_list[-1000:]

    return (list(author_train),list(author_vali))

def combine_press_author(p_interest_interest,p_press_interest,p_author_interest,c):
    interest_score = {}
    #print (p_press_interest)
    #print (p_author_interest)

    for k,v in p_interest_interest.items():
        interest_score.setdefault(k,0)
        interest_score[k] += v*c

    for k,v in p_author_interest.items():
        interest_score.setdefault(k,0)
        interest_score[k] += v*(1-c)*20

    for k,v in p_press_interest.items():
        interest_score.setdefault(k,0)
        interest_score[k] += v*0.01
    result = sorted(interest_score.items(),key=lambda x:x[1],reverse=True)
    interest = []
    for v in result[:5]:
        interest.append(v[0])
    return interest

def combine_test_result(vali_author,p_author_interest_score_interest,p_author_interest_score_author,p_author_interest_score_press,author_interest):
    print ("combine result ...")

    fid_result = codecs.open("./task2_out/9_28_3.txt","w","utf-8")

    for c in np.arange(0.8,0.9,0.1):
        #c = 1/c
        accuracy = 0
        with codecs.open("./raw_data/validation.txt","r","utf-8") as fid:
            for line in fid:
                if line == '\n':
                    continue
                author = line.strip()
                interest = combine_press_author(p_author_interest_score_interest[author],p_author_interest_score_author[author],p_author_interest_score_press[author],c)
                interest = interest[:5]
                interest.extend([""]*(5-len(interest)))
                fid_result.write(author + '\t' + '\t'.join(interest)+'\n')

def combine_result(vali_author,p_author_interest_score_interest,p_author_interest_score_author,p_author_interest_score_press,author_interest):
    print ("combine result ...")
    for c in np.arange(0,1,0.1):
        #c = 1/c
        accuracy = 0
        for author in vali_author:
            interest = combine_press_author(p_author_interest_score_interest[author],p_author_interest_score_author[author],p_author_interest_score_press[author],c)
            #break
            accuracy += len(set(author_interest[author])&set(interest))/3
        #break
        print ("c : " + str(c) + "\tcombine_result : " + str(accuracy/1000))

def task2_main():

    with codecs.open("./raw_data/t_author_paper.json","r","utf-8") as fid:
        t_author_paper = json.load(fid)

    with codecs.open("./raw_data/author_interest.json","r","utf-8") as fid:
        author_interest = json.load(fid)

    with codecs.open("./raw_data/p_author_paper.json","r","utf-8") as fid:
        p_author_paper = json.load(fid)

    author_test = p_author_paper.keys()
    (author_train,author_vali) = split_dataset(t_author_paper.keys())

    #combine_result_file(author_vali)
    p_author_interest_score_press = press_model.press_main(author_train,author_vali,author_test,author_interest,'vali')
    with codecs.open("./task2_out/p_author_interest_score_press.json","w","utf-8") as fid:
        json.dump(p_author_interest_score_press,fid,ensure_ascii=False)

    p_author_interest_score_interest = lsi_model_average(t_author_paper,author_interest,p_author_paper,author_train,author_vali,'vali')
    with codecs.open("./task2_out/p_author_interest_score_interest.json","w","utf-8") as fid:
        json.dump(p_author_interest_score_interest,fid,ensure_ascii=False)

    p_author_interest_score_author = lsi_author.author_main(author_train,author_vali,t_author_paper,author_interest,'vali')
    with codecs.open("./task2_out/p_author_interest_score_author.json","w","utf-8") as fid:
        json.dump(p_author_interest_score_author,fid,ensure_ascii=False)
    #combine_test_result(author_vali,p_author_interest_score_interest,p_author_interest_score_author,p_author_interest_score_press,author_interest)
    p_author_interest_score_indx_similarity  = author_similarity.similarity_by_indx(author_train,author_vali,author_interest)
    #p_author_interest_score_press_similarity  = author_similarity.similarity_by_press(author_train,author_vali,author_interest)
    with codecs.open("./task2_out/p_author_interest_score_indx_similarity.json","w","utf-8") as fid:
        json.dump(p_author_interest_score_indx_similarity,fid,ensure_ascii=False)

def lsi_model_average(t_author_paper,author_interest,p_author_paper,author_train,author_vali,flag):
    lsi_result = []
    num = 5
    for i in range(num):
        lsi_result.append(lsi_model.lsi_main(t_author_paper,author_interest,p_author_paper,author_train,author_vali,flag))

    author_interest_score = {}
    for author in author_vali:
        interest_s = {}
        for i in range(num):
            for k,v in lsi_result[i][author].items():
                interest_s.setdefault(k,0)
                interest_s[k] += v
        for k in interest_s.keys():
            interest_s[k] = interest_s[k]/num
        author_interest_score.setdefault(author,interest_s)
    return author_interest_score
def combine_result_file():

    with codecs.open("./task2_out/p_author_interest_score_press.json","r","utf-8") as fid:
        p_author_interest_score_press = json.load(fid)

    with codecs.open("./task2_out/p_author_interest_score_interest.json","r","utf-8") as fid:
        p_author_interest_score_interest = json.load(fid)

    with codecs.open("./task2_out/p_author_interest_score_author.json","r","utf-8") as fid:
        p_author_interest_score_author = json.load(fid)

    with codecs.open("./task2_out/p_author_interest_score_indx_similarity.json","r","utf-8") as fid:
        p_author_interest_score_indx_similarity = json.load(fid)

    with codecs.open("./raw_data/author_interest.json","r","utf-8") as fid:
        author_interest = json.load(fid)

    print (len(p_author_interest_score_press.keys() ))
    print (len(p_author_interest_score_interest.keys() ))
    print (len(p_author_interest_score_author.keys() ))
    print (len(p_author_interest_score_indx_similarity.keys() ))
    for c in np.arange(0,1,0.1):
        #c = 1/c
        accuracy = 0
        for author in p_author_interest_score_press.keys():
            #interest = combine_press_author(p_author_interest_score_interest[author],p_author_interest_score_author[author],p_author_interest_score_press[author],p_author_interest_score_indx_similarity[author],c)
            interest = combine_press_author(p_author_interest_score_interest[author],p_author_interest_score_press[author],p_author_interest_score_author[author],p_author_interest_score_indx_similarity[author],c)
            #break
            accuracy += len(set(author_interest[author])&set(interest))/3
        #break
        print ("c : " + str(c) + "\tcombine_result : " + str(accuracy/1000))

def combine_press_author(p_interest_interest,p_press_interest,p_author_interest,p_indx_similarity_interest,c):
    interest_score = {}

    for k,v in p_interest_interest.items():
        interest_score.setdefault(k,0)
        interest_score[k] += v*c

    for k,v in p_author_interest.items():
        interest_score.setdefault(k,0)
        interest_score[k] += v*0.009

    for k,v in p_press_interest.items():
        interest_score.setdefault(k,0)
        interest_score[k] += v*4

    for k,v in p_indx_similarity_interest.items():
        interest_score.setdefault(k,0)
        interest_score[k] += v*0.06

    result = sorted(interest_score.items(),key=lambda x:x[1],reverse=True)
    interest = []
    for v in result[:5]:
        interest.append(v[0])
    return interest

def single_test():

    with codecs.open("./raw_data/t_author_paper.json","r","utf-8") as fid:
        t_author_paper = json.load(fid)

    with codecs.open("./raw_data/author_interest.json","r","utf-8") as fid:
        author_interest = json.load(fid)

    with codecs.open("./raw_data/p_author_paper.json","r","utf-8") as fid:
        p_author_paper = json.load(fid)

    author_test = p_author_paper.keys()
    (author_train,author_vali) = split_dataset(t_author_paper.keys())

    p_author_interest_score_indx_similarity  = author_similarity.similarity_by_indx(author_train,author_vali,author_interest)
    p_author_interest_score_indx_similarity  = author_similarity.similarity_by_press(author_train,author_vali,author_interest)

if __name__ == "__main__":
    #combine_result_file()
    #task2_main()
    single_test()
