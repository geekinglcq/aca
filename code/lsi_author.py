#-*-coding:utf-8-*-

from __future__ import division
from gensim import corpora,models,similarities
from collections import Counter,defaultdict
import codecs
import json
import numpy as np
import nltk
#import smalltool_clustering
from nltk.stem.snowball import SnowballStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import LSHForest
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import gensim
from gensim.models import Doc2Vec
import random
import math
stemmer = SnowballStemmer("english")

def split_dataset(vali_num=5000):
    print("split dataset ...")
    with codecs.open("./raw_data/t_author_paper.json","r","utf-8") as fid:
        t_author_paper = json.load(fid)

    with codecs.open("./raw_data/t_author_seq_v.txt","r","utf-8") as fid:
        for line in fid:
            author_list = line.split("\t")

    #author_train = random.sample(t_author_paper.keys(),vali_num)
    #author_vali = set(t_author_paper.keys()) - set(author_train)
    with codecs.open("./raw_data/t_author_seq_v.txt","r","utf-8") as fid:
        for line in fid:
            line.strip()
            author_list = line.split("\t")

    author_train = author_list[:5000]
    author_vali = author_list[-1000:]

    return (list(author_train),list(author_vali),t_author_paper)

def shuffle_list(paper_list,number):
    random.shuffle(paper_list)
    return paper_list[:number]

def create_dictionary(author_train,t_author_paper,su):
    print ("create dictionary ...")
    author_seq = []
    paper_seq = []

    for author in author_train:
        author_seq.append(author)
        text = ' '.join(t_author_paper[author])
        #text = ' '.join(shuffle_list(t_author_paper[author],su))
        text = clean_data(text)
        paper_seq.append(text)

    dictionary = corpora.Dictionary(paper_seq)
    corpus = [dictionary.doc2bow(text) for text in paper_seq]

    return (author_seq,dictionary,corpus)


def create_lsi_model(num_topics,dictionary,corpus):
    print ("create lsi model ...")

    tfidf_model = models.TfidfModel(corpus)
    corpus_tfidf = tfidf_model[corpus]
    lsi_model = models.LsiModel(corpus_tfidf,id2word=dictionary,num_topics = num_topics)
    corpus_lsi = lsi_model[corpus_tfidf]
    corpus_simi_matrix = similarities.MatrixSimilarity(corpus_lsi)
    return (tfidf_model,lsi_model,corpus_simi_matrix)


def predict_n_interest(p_author_paper,author_seq,author_interest,dictionary,corpus,tfidf_model,lsi_model,corpus_simi_matrix,vali_n,su):
    print ("predict interest ...")

    with codecs.open("./raw_data/t_author_paper_ex_cite.json","r","utf-8") as fid:
        cite_author_paper = json.load(fid)
    predict_author_interest = {}
    with codecs.open("./raw_data/t_author_paper_ex_coop.json","r","utf-8") as fid:
        coop_author_paper = json.load(fid)
    flag = 0
    predict_author_interest_score = {}
    interest_score = count_interest(author_seq,author_interest)
    for author,paper in p_author_paper.items():

        #if len(paper) > 10:
        #    flag += 1
        #    predict_author_interest.setdefault(author,[])
        #    continue

        #paper.extend(shuffle_list(cite_author_paper[author],20))
        #paper.extend(shuffle_list(coop_author_paper[author],20))

        interest = []
        test_text = clean_data(' '.join(paper))
        #test_text = clean_data(' '.join(shuffle_list(paper,su)))
        test_bow = dictionary.doc2bow(test_text)
        test_tfidf = tfidf_model[test_bow]
        test_lsi = lsi_model[test_tfidf]
        test_simi = corpus_simi_matrix[test_lsi]
        result = list(enumerate(test_simi))
        result.sort(key=lambda x:x[1],reverse=True)

        interest_s = {}
        for v in result[:vali_n]:
            for inst in author_interest[author_seq[v[0]]]:
                interest_s.setdefault(inst,0)
                #interest_s[inst] += interest_score[inst]*math.exp(v[1])
                ##interest_s[inst] += interest_score[inst]*v[1]
                interest_s[inst] += v[1]

        predict_author_interest_score.setdefault(author,interest_s)
        interest_s = sorted(interest_s.items(),key=lambda x:x[1],reverse=True)
        interest = []
        for v in interest_s[:5]:
            interest.append(v[0])

        #interest = choose_n_interest(interest,20)
        predict_author_interest.setdefault(author,interest)


    return predict_author_interest,predict_author_interest_score,flag


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



def choose_n_interest(interest,n):
    r_interest = []
    c_interest = Counter(interest).most_common(n)
    #print (len(set(interest)))
    #print (len(interest)-len(set(interest)))
    for i in range(min(len(c_interest),n)):
        r_interest.append(c_interest[i][0])
    return r_interest

def print_validation_result(predict_author_interest,author_seq,author_interest,num_topics,flag):
    print ("validation result ...")

    print (len(author_interest.keys()))
    print (len(predict_author_interest.keys()))

    accuracy = 0
    for author in predict_author_interest.keys():
        accuracy = accuracy + (len(set(predict_author_interest[author])&set(author_interest[author])))/3
    print (accuracy/(1000-flag))

def clean_data( text):
    n_text = []
    text = text.strip()
    p_set = '. , ! : ? ` ` '.split()
    for i in range(len(text)):
        if text[i] not in p_set:
            n_text.append(text[i])
    text = ''.join(n_text)
    stop_list =set('a is are on from for and not to that this there these those \
                   have has been were I you me they can could be do . , : ! ? '.split())
    text = [word for word in text.lower().split() if word not in stop_list]
    #text = [stemmer.stem(t) for t in text]
    return text

def read_train_data(author_train,author_vali,t_author_paper):
    train_author_paper = {}
    vali_author_paper = {}
    for author in author_train:
        train_author_paper.setdefault(author,t_author_paper[author])

    for author in author_vali:
        vali_author_paper.setdefault(author,t_author_paper[author])

    return (train_author_paper,vali_author_paper)



#if __name__ =="__main__":
def author_main(author_train,author_vali,t_author_paper,author_interest,flag):
    #with codecs.open("./raw_data/author_interest.json","r","utf-8") as fid:
    #    author_interest = json.load(fid)

    with codecs.open("./raw_data/p_author_paper_final.json","r","utf-8") as fid:
        p_author_paper = json.load(fid)

    #(author_train,author_vali,t_author_paper) = split_dataset()
    train_author_paper,vali_author_paper = read_train_data(author_train,author_vali,t_author_paper)
    for su in range(150,160,20):
        (author_seq,dictionary,corpus) = create_dictionary(author_train,t_author_paper,su)
        for vali_n in range(40,45,5):
            for num_topics in range(200,250,50):
                print (vali_n,num_topics)
                (tfidf_model,lsi_model,corpus_simi_matrix)=create_lsi_model(num_topics,dictionary,corpus)
                if flag == 'vali':
                    predict_author_interest,predict_author_interest_score,flag = predict_n_interest(vali_author_paper,author_train,author_interest,dictionary,corpus,tfidf_model,lsi_model,corpus_simi_matrix,vali_n,su)
                    #predict_author_interest,predict_author_interest_score = predict_n_interest(p_author_paper,author_train,author_interest,dictionary,corpus,tfidf_model,lsi_model,corpus_simi_matrix,vali_n,su)
                    #predict_author_interest = predict_n_interest(p_author_paper,author_train,author_interest,dictionary,corpus,tfidf_model,lsi_model,corpus_simi_matrix,vali_n,su)
                    print_validation_result(predict_author_interest,author_seq,author_interest,vali_n,flag)
                if flag == 'test':
                    predict_author_interest,predict_author_interest_score,flag = predict_n_interest(p_author_paper,author_train,author_interest,dictionary,corpus,tfidf_model,lsi_model,corpus_simi_matrix,vali_n,su)
    return predict_author_interest_score
