from __future__ import division
import codecs
import json
import author_similarity
import lsi_model
import press_model
import lsi_author
#import lsi_press
#import lsi_model_2
import numpy as np
import math
#import interest_press_kl

def split_dataset(author_list):
    print("split dataset ...")

    with codecs.open("./raw_data/t_author_paper.json","r","utf-8") as fid:
        t_author_paper = json.load(fid)

    author_train = author_list[:6000]
    author_vali = author_list[-1000:]

    return (list(author_train),list(author_vali))

#def combine_press_author(p_interest_interest,p_press_interest,p_author_interest,c):
#    interest_score = {}
#    #print (p_press_interest)
#    #print (p_author_interest)
#
#    for k,v in p_interest_interest.items():
#        interest_score.setdefault(k,0)
#        interest_score[k] += v*c
#
#    for k,v in p_author_interest.items():
#        interest_score.setdefault(k,0)
#        interest_score[k] += v*(1-c)*20
#
#    for k,v in p_press_interest.items():
#        interest_score.setdefault(k,0)
#        interest_score[k] += v*0.01
#    result = sorted(interest_score.items(),key=lambda x:x[1],reverse=True)
#    interest = []
#    for v in result[:5]:
#        interest.append(v[0])
#    return interest
#
#def combine_test_result(vali_author,p_author_interest_score_interest,p_author_interest_score_author,p_author_interest_score_press,author_interest):
#    print ("combine result ...")
#
#    fid_result = codecs.open("./task2_out/9_28_3.txt","w","utf-8")
#
#    for c in np.arange(0.8,0.9,0.1):
#        #c = 1/c
#        accuracy = 0
#        with codecs.open("./raw_data/validation.txt","r","utf-8") as fid:
#            for line in fid:
#                if line == '\n':
#                    continue
#                author = line.strip()
#                interest = combine_press_author(p_author_interest_score_interest[author],p_author_interest_score_author[author],p_author_interest_score_press[author],c)
#                interest = interest[:5]
#                interest.extend([""]*(5-len(interest)))
#                fid_result.write(author + '\t' + '\t'.join(interest)+'\n')

#def combine_result(vali_author,p_author_interest_score_interest,p_author_interest_score_author,p_author_interest_score_press,author_interest):
#    print ("combine result ...")
#    for c in np.arange(0,1,0.1):
#        #c = 1/c
#        accuracy = 0
#        for author in vali_author:
#            interest = combine_press_author(p_author_interest_score_interest[author],p_author_interest_score_author[author],p_author_interest_score_press[author],c)
#            #break
#            accuracy += len(set(author_interest[author])&set(interest))/3
#        #break
#        print ("c : " + str(c) + "\tcombine_result : " + str(accuracy/1000))

def task2_main(flag_test_vali ):

    with codecs.open("./raw_data/t_author_paper.json","r","utf-8") as fid:
        t_author_paper = json.load(fid)

    with codecs.open("./raw_data/author_interest.json","r","utf-8") as fid:
        author_interest = json.load(fid)

    with codecs.open("./raw_data/p_author_paper_final.json","r","utf-8") as fid:
        p_author_paper = json.load(fid)

    #author_vali = []
    #with codecs.open("./raw_data/exclude_author.txt","r","utf-8") as fid:
    #    for line in fid:
    #        #print line
    #        author_vali = line.strip().split('\t')
    #        break

    #author_train = list(set(t_author_paper.keys())-set(author_vali))
    #print len(author_train)
    author_test = p_author_paper.keys()
    (author_train,author_vali) = split_dataset(t_author_paper.keys())


    p_author_interest_score_press = press_model.press_main(author_train,author_vali,author_test,author_interest,flag_test_vali)
    with codecs.open("./task2_out/p_author_interest_score_press.json" + flag_test_vali,"w","utf-8") as fid:
        json.dump(p_author_interest_score_press,fid,ensure_ascii=False)

    p_author_interest_score_interest = lsi_model_average(t_author_paper,author_interest,p_author_paper,author_train,author_vali,author_test,flag_test_vali)
    with codecs.open("./task2_out/p_author_interest_score_interest.json" + flag_test_vali,"w","utf-8") as fid:
        json.dump(p_author_interest_score_interest,fid,ensure_ascii=False)

    p_author_interest_score_author = lsi_author.author_main(author_train,author_vali,t_author_paper,author_interest,flag_test_vali)
    with codecs.open("./task2_out/p_author_interest_score_author.json" + flag_test_vali,"w","utf-8") as fid:
        json.dump(p_author_interest_score_author,fid,ensure_ascii=False)

    p_author_interest_score_indx_similarity  = author_similarity.similarity_by_indx(author_train,author_vali,author_test,author_interest,flag_test_vali)
    with codecs.open("./task2_out/p_author_interest_score_indx_similarity.json" + flag_test_vali,"w","utf-8") as fid:
        json.dump(p_author_interest_score_indx_similarity,fid,ensure_ascii=False)

    #p_author_interest_score_press_similarity  = author_similarity.similarity_by_press(author_train,author_vali,author_test,author_interest,flag_test_vali)
    #p_author_interest_score_press_similarity  = author_similarity.similarity_by_press(author_train,author_vali,author_interest)
    #with codecs.open("./task2_out/p_author_interest_score_press_similarity.json" + flag_test_vali,"w","utf-8") as fid:
    #    json.dump(p_author_interest_score_press_similarity,fid,ensure_ascii=False)

    #p_author_interest_score_pressf_similarity  = interest_press_kl.similarity_by_interest_press(author_train,author_vali,author_test,author_interest,'vali')
    #with codecs.open("./task2_out/p_author_interest_score_pressf_similarity.json" + flag_test_vali,"w","utf-8") as fid:
    #    json.dump(p_author_interest_score_pressf_similarity,fid,ensure_ascii=False)


def lsi_model_average(t_author_paper,author_interest,p_author_paper,author_train,author_vali,author_test,flag):
    lsi_result = []
    num = 10
    for i in range(num):
        lsi_result.append(lsi_model.lsi_main(t_author_paper,author_interest,p_author_paper,author_train,author_vali,author_test,flag))

    if flag == 'vali':
        author_list = author_vali
    if flag == 'test':
        author_list = author_test
    author_interest_score = {}
    for author in author_list:
        interest_s = {}
        for i in range(num):
            for k,v in lsi_result[i][author].items():
                interest_s.setdefault(k,0)
                interest_s[k] += v
        for k in interest_s.keys():
            interest_s[k] = interest_s[k]/num
        author_interest_score.setdefault(author,interest_s)
    return author_interest_score
def combine_result_file(flag):

    with codecs.open("./task2_out/p_author_interest_score_press.json" + flag,"r","utf-8") as fid:
        p_author_interest_score_press = json.load(fid)

    with codecs.open("./task2_out/p_author_interest_score_interest.json"+ flag,"r","utf-8") as fid:
        p_author_interest_score_interest = json.load(fid)

    with codecs.open("./task2_out/p_author_interest_score_author.json"+ flag,"r","utf-8") as fid:
        p_author_interest_score_author = json.load(fid)

    with codecs.open("./task2_out/p_author_interest_score_indx_similarity.json"+ flag,"r","utf-8") as fid:
        p_author_interest_score_indx_similarity = json.load(fid)

    #with codecs.open("./task2_out/p_author_interest_score_pressf_similarity.json"+ flag,"r","utf-8") as fid:
    #    p_author_interest_score_pressf_similarity = json.load(fid)

    with codecs.open("./raw_data/author_interest.json","r","utf-8") as fid:
        author_interest = json.load(fid)

    print (len(p_author_interest_score_press.keys() ))
    print (len(p_author_interest_score_interest.keys() ))
    print (len(p_author_interest_score_author.keys() ))
    print (len(p_author_interest_score_indx_similarity.keys() ))
    #print (len(p_author_interest_score_press_similarity.keys()))

    for c in np.arange(2.0,2.01,0.1):
        p_author_interest = {}
        for author in p_author_interest_score_press.keys():
            #interest = combine_final(p_author_interest_score_interest[author],p_author_interest_score_press[author],p_author_interest_score_author[author],p_author_interest_score_indx_similarity[author],c)
            interest = combine_5(p_author_interest_score_interest[author],p_author_interest_score_press[author],p_author_interest_score_author[author],p_author_interest_score_indx_similarity[author],c)
            p_author_interest.setdefault(author,interest)

        print ("c : " + str(c))
        #print_validation_result(p_author_interest,author_interest)
    return p_author_interest

def print_test_result(predict_author_interest):
    fid_result = codecs.open("./task2_out/10_08_4_2.0.txt","w","utf-8")
    fid_result.write("<task2>"+'\n')
    fid_result.write("authorname\tinterest1\tinterest2\tinterest3\tinterest4\tinterest5"+'\n')
    with codecs.open("./raw_data/task2_test_final.txt","r","utf-8") as fid:
        for line in fid:
            if line == '\n':
                continue
            author = line.strip()
            #interest = combine_press_author(p_author_interest_score_interest[author],p_author_interest_score_author[author],p_author_interest_score_press[author],c)
            interest = predict_author_interest[author][:5]
            interest.extend([""]*(5-len(interest)))
            fid_result.write(author + '\t' + '\t'.join(interest)+'\n')
    fid_result.write("</task2>"+'\n')
    fid.close()

def print_validation_result(predict_author_interest,author_interest):
    accuracy = 0
    for author in predict_author_interest.keys():
        accuracy = accuracy + (len(set(predict_author_interest[author])&set(author_interest[author])))/3
    print ("accuracy : " + str(accuracy/len(predict_author_interest.keys())))


def combine_final(p_interest_interest,p_press_interest,p_author_interest,p_indx_similarity_interest,c):
    interest_score = {}

    for k,v in p_interest_interest.items():
        interest_score.setdefault(k,0)
        interest_score[k] += v*c

    for k,v in p_author_interest.items():
        interest_score.setdefault(k,0)
        interest_score[k] += v*0.009

    for k,v in p_press_interest.items():
        interest_score.setdefault(k,0)
        interest_score[k] += v*10

    for k,v in p_indx_similarity_interest.items():
        interest_score.setdefault(k,0)
        interest_score[k] += v*0.06

    result = sorted(interest_score.items(),key=lambda x:x[1],reverse=True)
    interest = []
    for v in result[:5]:
        interest.append(v[0])
    return interest

def combine_5(p_interest_interest,p_press_interest,p_author_interest,p_indx_similarity_interest,c):
    interest_score = {}

    for k,v in p_interest_interest.items():
        interest_score.setdefault(k,0)
        #interest_score[k] += math.exp((1+v))*c
        interest_score[k] += v*c

    for k,v in p_author_interest.items():
        interest_score.setdefault(k,0)
        #interest_score[k] += math.exp((1+v))*0.0
        interest_score[k] += v*0.008

    for k,v in p_press_interest.items():
        interest_score.setdefault(k,0)
        #interest_score[k] += math.exp((1+v))*0.0
        interest_score[k] += v*10

    for k,v in p_indx_similarity_interest.items():
        interest_score.setdefault(k,0)
        #interest_score[k] += math.exp((1+v))*0.05
        interest_score[k] += v*0.06

    #for k,v in p_press_similarity_interest.items():
    #    interest_score.setdefault(k,0)
        #interest_score[k] += math.exp((1+v))*0.0
    #    interest_score[k] += v*0.0

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

    with codecs.open("./raw_data/t_author_press.json","r","utf-8") as fid:
        t_author_press = json.load(fid)

    with codecs.open("./raw_data/p_author_press.json","r","utf-8") as fid:
        p_author_press = json.load(fid)

    author_vali = []
    with codecs.open("./raw_data/exclude_author.txt","r","utf-8") as fid:
        for line in fid:
            author_vali = line.strip().split('\t')
    author_test = p_author_press.keys()
    (author_train,author_vali) = split_dataset(t_author_press.keys())
    author_train = list(set(t_author_press.keys())-set(author_vali))

    #p_author_interest_score_author = lsi_author.author_main(author_train,author_vali,t_author_paper,author_interest,'vali')
    #lsi_press.lsi_main(t_author_press,author_interest,p_author_press,author_train,author_vali,author_test,'vali')
    #p_author_interest_score_press = press_model.press_main(author_train,author_vali,author_test,author_interest,'vali')
    #p_author_interest_score_indx_similarity  = author_similarity.similarity_by_indx(author_train,author_vali,author_test,author_interest,'vali')
    #p_author_interest_score_indx_similarity  = author_similarity.similarity_by_interest_press(author_train,author_vali,author_test,author_interest,'vali')
    #p_author_interest_score_indx_similarity  = interest_press_kl.similarity_by_interest_press(author_train,author_vali,author_test,author_interest,'vali')
    lsi_model_2.lsi_main(t_author_paper,author_interest,p_author_paper,author_train,author_vali,author_test,'vali')



if __name__ == "__main__":

    with codecs.open("./raw_data/author_interest.json","r","utf-8") as fid:
        author_interest = json.load(fid)

    flag = 'test'

    #single_test()
    if flag == 'vali':
        #task2_main(flag)
        p_author_interest = combine_result_file(flag)
        print_validation_result(p_author_interest,author_interest)
    if flag == 'test':
        task2_main(flag)
        p_author_interest = combine_result_file(flag)
        print_test_result(p_author_interest)

    #single_test()
