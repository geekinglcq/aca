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


def extract_training_paper_for_interest(train_author,t_author_paper,author_interest):

    print ("extract training paper for interest ... 20")
    interest_paper = {}
    for author in train_author:
        interest_list = author_interest[author]
        for interest in interest_list:
            for paper in shuffle_list(t_author_paper[author],20):
                interest_paper.setdefault(interest,[]).append(paper)
    return interest_paper


def create_dictionary(interest_paper):

    print ("create dictionary ...")

    interest_seq = []
    paper_seq = []
    for interest,paper in interest_paper.items():
        interest_seq.append(interest)
        text = ' '.join(paper)
        text = clean_data(text)
        paper_seq.append(text)
    #paper_seq = remove_once_appearance(paper_seq,2)

    dictionary = corpora.Dictionary(paper_seq)
    corpus = [dictionary.doc2bow(text) for text in paper_seq]
    return (interest_seq,dictionary,corpus)

def clean_data( text):

    n_text = []
    text = text.strip()
    p_set = '. , ! : ? ` ` '.split()
    for i in range(len(text)):
        if text[i] not in p_set:
            n_text.append(text[i])
    text = ''.join(n_text)

    stop_list =set('a is are on from for and not to'.split())
    #stop_list =set('a is are on from for and not to that this there these \
    #               those have has been were I you me they can could be do . , : ! ? '.split())
    text = [word for word in text.lower().split() if word not in stop_list]
    #text = [stemmer.stem(t) for t in text]
    return text

def create_lsi_model(num_topics,dictionary,corpus):

    print ("create lsi model ...")
    tfidf_model = models.TfidfModel(corpus)
    corpus_tfidf = tfidf_model[corpus]
    lsi_model = models.LsiModel(corpus_tfidf,id2word=dictionary,num_topics = num_topics)
    #lsi_model = models.LsiModel(corpus,id2word=dictionary,num_topics = num_topics)
    corpus_lsi = lsi_model[corpus_tfidf]
    #corpus_lsi = lsi_model[corpus]
    corpus_simi_matrix = similarities.MatrixSimilarity(corpus_lsi)
    #corpus_simi_matrix = similarities.MatrixSimilarity(corpus_tfidf)
    return (tfidf_model,lsi_model,corpus_simi_matrix)


def predict_n_interest_by_score(interest_score,author_paper,interest_seq,dictionary,corpus,tfidf_model,lsi_model,corpus_simi_matrix):

    print ("predict interest by score ...")
    predict_author_interest = {}
    predict_author_interest_score = {}
    for author,paper in author_paper.items():
        interest = []
        test_text = clean_data(' '.join(paper))
        test_bow = dictionary.doc2bow(test_text)
        test_tfidf = tfidf_model[test_bow]
        test_lsi = lsi_model[test_tfidf]
        test_simi = corpus_simi_matrix[test_lsi]

        result = list(enumerate(test_simi))
        result.sort(key=lambda x:x[1],reverse=True)

        interest_s ={}
        for v in result[:10]:
            interest_s.setdefault(interest_seq[v[0]],interest_score[interest_seq[v[0]]]*v[1])

        predict_author_interest_score.setdefault(author,interest_s)

        interest_s = sorted(interest_s.items(),key=lambda x:x[1],reverse=True)

        interest = []
        for v in interest_s[:5]:
            interest.append(v[0])
        predict_author_interest.setdefault(author,interest)

    #with codecs.open("./lsi_dataset/"+str(vali_n) +"_t_author_interest_20.json","w","utf-8") as fid:
    #    json.dump(predict_author_interest,fid,ensure_ascii=False)
    return predict_author_interest,predict_author_interest_score

def choose_n_interest(interest,n):
    r_interest = []
    c_interest = Counter(interest).most_common(n)
    for i in range(min(len(c_interest),n)):
        r_interest.append(c_interest[i][0])
    return r_interest

def predict_n_interest(author_paper,interest_seq,dictionary,corpus,tfidf_model,lsi_model,corpus_simi_matrix,author_vali):

    print ("predict interest ...")
    predict_author_interest = {}
    predict_author_interest_score = {}

    flag = 0

    with codecs.open("./raw_data/p_author_paper_ex_cite.json","r","utf-8") as fid:
        cite_author_paper = json.load(fid)
    with codecs.open("./raw_data/p_author_paper_ex_coop.json","r","utf-8") as fid:
        coop_author_paper = json.load(fid)

    for author,paper in author_paper.items():
    #exclude_author = []
    #for author in author_vali:
        paper = author_paper[author]
        #if  len(paper) < 5 or len(paper) > 10:
            #exclude_author.append(author)
            #paper.extend(achoose_n_interest(e_author_paper[author],10))
            #if author in author_vali:
            #    paper = e_author_paper[author]
            #    print (len(paper))
                #if len(paper) < 40:
        #    flag += 1
        #    predict_author_interest.setdefault(author,[])
        #    predict_author_interest_score.setdefault(author,{})
        #    continue
        if len(paper) <= 10:
            paper.extend(shuffle_list(cite_author_paper[author],40))
            #paper.extend(shuffle_list(coop_author_paper[author],0))
        #print len(paper)
        #paper = paper
        interest = []
        test_text = clean_data(' '.join(paper))
        test_bow = dictionary.doc2bow(test_text)
        test_tfidf = tfidf_model[test_bow]
        test_lsi = lsi_model[test_tfidf]
        #test_lsi = lsi_model[test_bow]
        test_simi = corpus_simi_matrix[test_lsi]

        result = list(enumerate(test_simi))
        result.sort(key=lambda x:x[1],reverse=True)

        interest_score = {}
        for v in result:
            #interest_score.setdefault(interest_seq[v[0]],math.exp(v[1]))
            interest_score.setdefault(interest_seq[v[0]],v[1])
        predict_author_interest_score.setdefault(author,interest_score)

        for v in result[:5]:
            interest.append(interest_seq[v[0]])
        predict_author_interest.setdefault(author,interest)

    #with codecs.open("./raw_data/exclude_author.txt","w","utf-8") as fid:
    #    fid.write("\t".join(exclude_author))
    print 1000-flag
    return predict_author_interest,predict_author_interest_score,flag


def print_validation_result(predict_author_interest,author_list,author_interest,flag):

    print ("lsi validation result accuracy ...")
    #predict_author_interest = find_similar_author(predict_author_interest,author_list,author_interest)

    with codecs.open("result_predict_by_interest_valimany.txt","a","utf-8") as fid:
        accuracy = 0
        for author in author_list:
            #print  (len(set(predict_author_interest[author])&set(author_interest[author])))
            accuracy = accuracy + (len(set(predict_author_interest[author])&set(author_interest[author])))/3
            #fid.write(author+'\t'+str(len(set(predict_author_interest[author])&set(author_interest[author])))+'\n')
        fid.write(str(accuracy/1000)+'\n')
        print ("50 lsi model accuracy : " + str(accuracy/(1000-flag)))

def compute_interest_score(author_interest):
    print ("compute interest score ...")
    interest_list = []
    for author,interest in author_interest.items():
        interest_list.extend(interest)
    c_interest = Counter(interest_list)
    interest_score = {}
    for interest,count in c_interest.items():
        #interest_score.setdefault(interest,math.exp(1-1/count))
        interest_score.setdefault(interest,math.exp(1/math.sqrt(count)-1))
    return interest_score

def shuffle_list(paper_list,number):
    random.shuffle(paper_list)
    return paper_list[:number]

def extract_vali_data(author_vali,t_author_paper):
    author_paper = {}
    for author in author_vali:
        author_paper.setdefault(author,t_author_paper[author])

    return author_paper

def lsi_main(t_author_paper,author_interest,p_author_paper,train_author,vali_author,author_test,flag):

    print ("lsi main ...")
    interest_score = compute_interest_score(author_interest)
    vali_data = extract_vali_data(vali_author,t_author_paper)
    interest_paper = extract_training_paper_for_interest(train_author,t_author_paper,author_interest)
    (interest_seq,dictionary,corpus) =  create_dictionary(interest_paper)
    (tfidf_model,lsi_model,corpus_simi_matrix) = create_lsi_model(800,dictionary,corpus)
    if flag == 'vali':
        #predict_author_interest,predict_author_interest_score = predict_n_interest_by_score(interest_score,vali_data,interest_seq,dictionary,corpus,tfidf_model,lsi_model,corpus_simi_matrix)
        predict_author_interest,predict_author_interest_score,flag = predict_n_interest(t_author_paper,interest_seq,dictionary,corpus,tfidf_model,lsi_model,corpus_simi_matrix,vali_author)
        print_validation_result(predict_author_interest,vali_author,author_interest,flag)
    if flag == 'test':
        predict_author_interest,predict_author_interest_score,flag = predict_n_interest(p_author_paper,interest_seq,dictionary,corpus,tfidf_model,lsi_model,corpus_simi_matrix,vali_author)
    return predict_author_interest_score
