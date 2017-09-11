#-*-coding:utf-8-*-

from __future__ import division
from gensim import corpora,models,similarities
from collections import Counter,defaultdict
import codecs
import json
import numpy as np
import nltk
import smalltool_clustering
from nltk.stem.snowball import SnowballStemmer
#interest_paper_path = 'interest_paper_from_neighbors.json'

from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import gensim
from gensim.models import Doc2Vec
import random

stemmer = SnowballStemmer("english")

def extract_paper_for_interest(vali_n):

    with codecs.open("t_author_paper.json","r","utf-8") as fid:
        t_author_paper = json.load(fid)

    with codecs.open("author_interest.json","r","utf-8") as fid:
        author_interest = json.load(fid)

    interest_paper = {}
    indx = 0
    author_seq =[]
    for author,interest_list in author_interest.items():
        if indx < 1000*(vali_n-1):
            author_seq.append(author)
            for interest in interest_list:
                for paper in t_author_paper[author]:
                    interest_paper.setdefault(interest,[]).append(paper)
        elif indx < 1000*vali_n:
            author_seq.append(author)
        else:
            author_seq.append(author)
            for interest in interest_list:
                for paper in t_author_paper[author]:
                    interest_paper.setdefault(interest,[]).append(paper)
        #else:
        #    author_seq.append(author)

        indx += 1
    #interest_paper = expand_interest_paper(interest_paper)
    with codecs.open("interest_paper_merge_validation.json","w","utf-8") as fid:
        json.dump(interest_paper,fid,ensure_ascii=False)
    with codecs.open("t_author_seq_v.txt","w","utf-8") as fid:
        fid.write('\t'.join(author_seq))

def load_train():
    print ("load training data ...")

    with codecs.open("./precise_interest/interest_paper_stem_n_2.json","r","utf-8") as  fid:
        interest_paper = json.load(fid)
    return interest_paper


def predict_n_interest_vec(model,author_paper,interest_paper,author_interest):

    print ("predict interest ...")
    predict_author_interest = {}

    interest_seq = []
    paper_seq = []
    for interest,paper in interest_paper.items():
        interest_seq.append(interest)
        paper_seq.append(' '.join(paper))
        #paper_vec.extend(model.docvecs)

    print len(paper_seq)
    indx = 0
    for author,paper in author_paper.items():
        print (indx)
        indx += 1
        interest = []
        result = []
        test_text = clean_data(' '.join(paper))
        flag = 0
        for p in paper_seq:
            #print ("")
            #dis = model.n_similarity(' '.join(paper),' '.join(p))
            dis = model.wmdistance(' '.join(test_text).lower().split(),p.lower().split())
            result.append((flag,dis))
            flag += 1
        #test_bow = dictionary.doc2bow(test_text)
        #test_tfidf = tfidf_model[test_bow]
        #test_lsi = lsi_model[test_tfidf]
        #test_simi = corpus_simi_matrix[test_lsi]

        #result = list(enumerate(test_simi))
        result.sort(key=lambda x:x[1])

        for v in result[:5]:
            interest.append(interest_seq[v[0]])
        print len(set(interest)&set(author_interest[author]))
        interest.extend(['']*(5-len(interest)))
        predict_author_interest.setdefault(author,interest)


    #with codecs.open("p_interest_from_lsi_p_10.json","w","utf-8") as fid:
    #    json.dump(predict_author_interest,fid,ensure_ascii=False)

    #predict_author_interest = times_s_matrix(predict_author_interest)
    return predict_author_interest
def extract_precise_training_paper_for_interest(vali_n):

    with codecs.open("author_indx_citeindx.json","r","utf-8") as fid:
        author_indx_citeindx = json.load(fid)

    with codecs.open("author_interest.json","r","utf-8") as fid:
        author_interest = json.load(fid)

    with codecs.open("indx_interest_from_author_all_keyword.json","r","utf-8") as fid:
        indx_interest = json.load(fid)

    with codecs.open("indx_paper_author.json","r","utf-8") as fid:
        indx_paper_author = json.load(fid)

    interest_paper = {}
    flag = 0
    author_seq =[]
    for author in author_interest.keys():
        print(flag)
        if flag < 1000*(vali_n-1):
            author_seq.append(author)
            for indx in author_indx_citeindx[author].keys():
                if str(indx) in indx_interest.keys():
                    for v in indx_interest[str(indx)]:
                        interest_paper.setdefault(v,[]).append(indx_paper_author[str(indx)][1])
        elif flag < 1000*vali_n:
            author_seq.append(author)
        elif flag < 5000:
            author_seq.append(author)
            for indx in author_indx_citeindx[author].keys():
                if str(indx) in indx_interest.keys():
                    for v in indx_interest[str(indx)]:
                        interest_paper.setdefault(v,[]).append(indx_paper_author[str(indx)][1])
            #for interest in interest_list:
            #    for paper in t_author_paper[author]:
            #        interest_paper.setdefault(interest,[]).append(paper)
        else:
            author_seq.append(author)

        flag += 1

    with codecs.open("interest_paper_validation.json","w","utf-8") as fid:
        json.dump(interest_paper,fid,ensure_ascii=False)
    with codecs.open("t_author_seq_v.txt","w","utf-8") as fid:
        fid.write('\t'.join(author_seq))


def shuffle_list(paper_list,number):
    random.shuffle(paper_list)
    return paper_list[:number]


def extract_precise_training_all_paper_for_interest(vali_n):

    with codecs.open("author_indx_citeindx.json","r","utf-8") as fid:
        author_indx_citeindx = json.load(fid)

    with codecs.open("author_interest.json","r","utf-8") as fid:
        author_interest = json.load(fid)

    with codecs.open("indx_interest_from_author_keyword_all.json","r","utf-8") as fid:
        indx_interest = json.load(fid)

    with codecs.open("indx_paper_author.json","r","utf-8") as fid:
        indx_paper_author = json.load(fid)

    interest_paper = {}
    flag = 0
    author_seq =[]
    for author in author_interest.keys():
        print(flag)
        if flag < 1000*(vali_n-1):
            author_seq.append(author)
            for indx in indx_interest.keys():
                #if str(indx) in indx_interest.keys():
                for v in indx_interest[str(indx)]:
                    interest_paper.setdefault(v,[]).append(indx_paper_author[str(indx)][1])
        elif flag < 1000*vali_n:
            author_seq.append(author)
        elif flag < 5000:
            author_seq.append(author)
            for indx in indx_interest.keys():
                #if str(indx) in indx_interest.keys():
                for v in indx_interest[str(indx)]:
                    interest_paper.setdefault(v,[]).append(indx_paper_author[str(indx)][1])
            #for interest in interest_list:
            #    for paper in t_author_paper[author]:
            #        interest_paper.setdefault(interest,[]).append(paper)
        else:
            author_seq.append(author)

        flag += 1

    with codecs.open("interest_paper_validation.json","w","utf-8") as fid:
        json.dump(interest_paper,fid,ensure_ascii=False)
    with codecs.open("t_author_seq_v.txt","w","utf-8") as fid:
        fid.write('\t'.join(author_seq))

def extract_training_paper_for_interest(vali_n,vali_many):

    with codecs.open("t_author_paper.json","r","utf-8") as fid:
        t_author_paper = json.load(fid)

    with codecs.open("author_interest.json","r","utf-8") as fid:
        author_interest = json.load(fid)

    interest_paper = {}
    indx = 0
    author_seq =[]
    for author,interest_list in author_interest.items():
        if indx < 1000*(vali_n-1):
            author_seq.append(author)
            for interest in interest_list:
                for paper in shuffle_list(t_author_paper[author],20):
                    interest_paper.setdefault(interest,[]).append(paper)
        elif indx < 1000*vali_n:
            author_seq.append(author)
        elif indx < 5000:
            author_seq.append(author)
            for interest in interest_list:
                for paper in shuffle_list(t_author_paper[author],20):
                    interest_paper.setdefault(interest,[]).append(paper)
        else:
            author_seq.append(author)

        indx += 1

    #interest_paper = expand_interest_paper(interest_paper)
    with codecs.open("interest_paper_validation.json","w","utf-8") as fid:
        json.dump(interest_paper,fid,ensure_ascii=False)
    with codecs.open("t_author_seq_v.txt","w","utf-8") as fid:
        fid.write('\t'.join(author_seq))

def extract_training_paper_for_interest_plus_clustering(vali_n):

    with codecs.open("./multi-label/t_author_paper_p.json","r","utf-8") as fid:
        t_author_paper = json.load(fid)

    with codecs.open("author_interest.json","r","utf-8") as fid:
        author_interest = json.load(fid)

    interest_paper = {}
    indx = 0
    author_seq =[]
    flag =0
    for author,interest_list in author_interest.items():
        #print (flag)
        flag += 1
        if indx < 1000*(vali_n-1):
            author_seq.append(author)
            smalltool_clustering.assign_paper_for_interest(t_author_paper[author],author_interest[author],interest_paper)
        elif indx < 1000*vali_n:
            author_seq.append(author)
        elif indx < 5000:
            author_seq.append(author)
            smalltool_clustering.assign_paper_for_interest(t_author_paper[author],author_interest[author],interest_paper)
        else:
            author_seq.append(author)

        indx += 1

    #interest_paper = expand_interest_paper(interest_paper)
    with codecs.open("interest_paper_validation.json","w","utf-8") as fid:
        json.dump(interest_paper,fid,ensure_ascii=False)
    with codecs.open("t_author_seq_v.txt","w","utf-8") as fid:
        fid.write('\t'.join(author_seq))

def create_s_matrix():

    label_seq = []
    with codecs.open("labels.txt","r","utf-8") as fid:
        for line in fid:
            if line == '\n':
                continue
            label_seq.append(line.strip())

    s_matrix = np.zeros((len(label_seq,),len(label_seq)))
    with codecs.open("author_interest.json","r","utf-8") as fid:
        author_interest = json.load(fid)

    for author,interest in author_interest.items():
        for v in interest:
            indx_v = label_seq.index(v)
            for p in interest:
                indx_p = label_seq.index(p)
                s_matrix[indx_v][indx_p] += 1
                s_matrix[indx_p][indx_v] += 1
    return (label_seq,np.mat(s_matrix))

def create_dictionary(vali_many):

    print ("create dictionary ...")
    with codecs.open("interest_paper_validation.json","r","utf-8") as fid:
        interest_paper = json.load(fid)
    #interest_paper = expand_interest_paper(interest_paper)

    interest_seq = []
    paper_seq = []

    for interest,paper in interest_paper.items():
        interest_seq.append(interest)
        #paper = choose_n_interest(paper,vali_many)
        text = ' '.join(paper)
        text = clean_data(text)
        paper_seq.append(text)
    #paper_seq = remove_once_appearance(paper_seq,2)

    dictionary = corpora.Dictionary(paper_seq)
    corpus = [dictionary.doc2bow(text) for text in paper_seq]
    return (interest_seq,dictionary,corpus)

def remove_once_appearance(text_list,n):
    frequency = defaultdict(int)
    for text in text_list:
        for token in text:
            frequency[token] += 1
    text_list = [[token for token in text if frequency[token] > n] for text in text_list]
    return text_list

def clean_data( text):

    stop_list = set()#set('a is are on from for and not to that') #this there these those have has been were I you me they can could be do . , : ! ? '.split())
    text = [word for word in text.lower().split() if word not in stop_list]
    #text = [stemmer.stem(t) for t in text]
    return text



def create_lsi_model(num_topics,dictionary,corpus):

    print ("create lsi model ...")
    tfidf_model = models.TfidfModel(corpus)
    corpus_tfidf = tfidf_model[corpus]
    lsi_model = models.LsiModel(corpus_tfidf,id2word=dictionary,num_topics = num_topics)
    corpus_lsi = lsi_model[corpus_tfidf]
    corpus_simi_matrix = similarities.MatrixSimilarity(corpus_lsi)
    #corpus_simi_matrix = similarities.MatrixSimilarity(corpus_tfidf)
    #record_papers_tfidf(corpus_tfidf)
    return (tfidf_model,lsi_model,corpus_simi_matrix)


def record_papers_tfidf(corpus_tfidf):
    print("record papers' tfidf ...")
    fid_result = codecs.open("corpus_tfidf_papers","w","utf-8")
    for token in corpus_tfidf:
        tfidf_list = []
        for v in token:
            tfidf_list.append(str(v[0])+":"+str(v[1]))
        fid_result.write('\t'.join(tfidf_list)+'\n')
    fid_result.close()


def read_test_data(json_name):

    with codecs.open(json_name,"r","utf-8") as fid:
        author_paper = json.load(fid)

    return author_paper

def predict_n_interest(author_paper,interest_seq,dictionary,corpus,tfidf_model,lsi_model,corpus_simi_matrix,vali_n):

    print ("predict interest ...")
    predict_author_interest = {}
    flag = 0
    for author,paper in author_paper.items():
        interest = []
        test_text = clean_data(' '.join(paper))
        test_bow = dictionary.doc2bow(test_text)
        test_tfidf = tfidf_model[test_bow]
        test_lsi = lsi_model[test_tfidf]
        test_simi = corpus_simi_matrix[test_lsi]

        result = list(enumerate(test_simi))
        result.sort(key=lambda x:x[1])

        for v in result[-5:]:
            interest.append(interest_seq[v[0]])
        #r_interest = interest
        #r_interest = smalltool_clustering.return_interest(r_interest,' '.join(paper))
        #if len(r_interest) < 5:
        #    flag +=1
            #r_interest.extend(clean_interest_data(interest,r_interest)[len(r_interest)-5:])
        #interest = r_interest
        #interest.extend(['']*(5-len(interest)))
        #interest = interest[:5]
        predict_author_interest.setdefault(author,interest)
    print (flag)

    with codecs.open("./data_merge/p_interest_lsi_5.json","w","utf-8") as fid:
        json.dump(predict_author_interest,fid,ensure_ascii=False)

    #predict_author_interest = times_s_matrix(predict_author_interest)
    return predict_author_interest


def clean_interest_data(interest,set_r):
    for v in interest:
        if v in set_r:
            interest.remove(v)
    return interest

def predict_n_interest_plus_clustering(author_paper,interest_seq,dictionary,corpus,tfidf_model,lsi_model,corpus_simi_matrix,vali_n,vali_many):

    with codecs.open("t_author_seq_v.txt","r","utf-8") as fid:
        for line in fid:
            author_list = line.strip().split('\t')

    print ("predict interest ...")
    predict_author_interest = {}

    flag = 0
    for author in author_list:
        paper = author_paper[author]
        if len(paper) < 2:
            test_text = clean_data(' '.join(paper))
            test_bow = dictionary.doc2bow(test_text)
            test_tfidf = tfidf_model[test_bow]
            test_lsi = lsi_model[test_tfidf]
            test_simi = corpus_simi_matrix[test_lsi]
            result = list(enumerate(test_simi))
            result.sort(key=lambda x:x[1])

            for v in result[-5:]:
                interest.append(interest_seq[v[0]])
            interest.extend(['']*(5-len(interest)))
            predict_author_interest.setdefault(author,interest)
            continue

        i_paper = smalltool_clustering.group_paper_for_test(paper)
        interest = []
        for i , g_paper in i_paper.items():
            test_text = clean_data(' '.join(g_paper))
            test_bow = dictionary.doc2bow(test_text)
            test_tfidf = tfidf_model[test_bow]
            test_lsi = lsi_model[test_tfidf]
            test_simi = corpus_simi_matrix[test_lsi]

            result = list(enumerate(test_simi))
            result.sort(key=lambda x:x[1])

            for v in result[-4:]:
                interest.append(interest_seq[v[0]])
        if len(interest) < 0:
            f_interest = []
            test_text = clean_data(' '.join(paper))
            test_bow = dictionary.doc2bow(test_text)
            test_tfidf = tfidf_model[test_bow]
            test_lsi = lsi_model[test_tfidf]
            test_simi = corpus_simi_matrix[test_lsi]

            result = list(enumerate(test_simi))
            result.sort(key=lambda x:x[1])
            for v in result[-5:]:
                f_interest.append(interest_seq[v[0]])
            interest.extend(f_interest)
        #interest = f_interest
        interest = choose_n_interest(interest,5)
        #interest = list (set(interest)&set(f_interest))

        if len(interest)>5:
            flag += 1
        interest.extend(['']*(5-len(interest)))
        predict_author_interest.setdefault(author,interest)
    print ("flag : " + str(flag))


    #with codecs.open("t_author_interest_for_s.json","w","utf-8") as fid:
    #    json.dump(predict_author_interest,fid,ensure_ascii=False)

    #predict_author_interest = times_s_matrix(predict_author_interest)
    return predict_author_interest
def times_s_matrix(author_interest):


    #with codecs.open("t_author_interest_for_s.json","r","utf-8") as fid:
    #    author_interest = json.load(fid)

    label_seq,s_matrix = create_s_matrix()
    r_author_interest = {}
    for author,interest in author_interest.items():
        #interest_one = np.zeros((1,len(label_seq)))
        r_interest = []
        for v in interest:
            interest_one = np.array(s_matrix[label_seq.index(v)])[0]
            #print ((interest_one))
            for i in range(len(interest_one)):
                if interest_one[i] > 0:
                    r_interest.extend([label_seq[i]]*int(interest_one[i]))
        r_interest = choose_n_interest(r_interest,5)
        r_author_interest.setdefault(author,r_interest)
    return r_author_interest


def predict_n_interest_one(author_paper,interest_seq,dictionary,corpus,tfidf_model,lsi_model,corpus_simi_matrix,vali_n):

    print ("predict interest ...")



    with codecs.open("t_paper_neighbor.json","r","utf-8") as fid:
        t_paper_neighbors = json.load(fid)

    with codecs.open("t_author_seq_v.txt","r","utf-8") as fid:
        for line in fid:
            author_list = line.strip().split('\t')[-1000:]

    predict_author_interest = {}
    flag = 0
    for author in author_list:
        paper = author_paper[author]
        print ("flag: "+str(flag) + "paper len: "+str(len(paper)))
        flag += 1
        interest = []
        for p in paper:
            #test_text = clean_data(p)
            test_text = clean_data(t_paper_neighbors[p][0])
            #print (test_text)
            test_bow = dictionary.doc2bow(test_text)
            test_tfidf = tfidf_model[test_bow]
            test_lsi = lsi_model[test_tfidf]
            test_simi = corpus_simi_matrix[test_lsi]

            result = list(enumerate(test_simi))
            result.sort(key=lambda x:x[1])

            for v in result[-2:]:
                interest.append(interest_seq[v[0]])

        interest = choose_n_interest(interest,3)

        test_text = clean_data(' '.join(paper))
        #print (test_text)
        test_bow = dictionary.doc2bow(test_text)
        test_tfidf = tfidf_model[test_bow]
        test_lsi = lsi_model[test_tfidf]
        test_simi = corpus_simi_matrix[test_lsi]

        result = list(enumerate(test_simi))
        result.sort(key=lambda x:x[1])

        for v in result[-3:]:
            interest.append(interest_seq[v[0]])
        #print(len(set(interest)))
        #interest = choose_n_interest(interest,5)
        interest.extend(['']*(5-len(interest)))
        predict_author_interest.setdefault(author,interest)

    with codecs.open("t_author_interest_lsi_topics_"+ str(vali_n+18) + ".json","w","utf-8") as fid:
        json.dump(predict_author_interest,fid,ensure_ascii=False)

    return predict_author_interest



def choose_n_interest(interest,n):
    r_interest = []
    c_interest = Counter(interest).most_common(n)
    #print (len(set(interest)))
    #print (len(interest)-len(set(interest)))
    for i in range(min(len(c_interest),n)):
        r_interest.append(c_interest[i][0])
    return r_interest


def find_similar_author(predict_author_interest,author_list,author_interest):

    p_author_interest = {}
    for author in author_list[-1000:]:
        flag = 0
        result = []
        interest = []
        for v in author_list[:5000]:
            sims = len(set(predict_author_interest[author])&set(predict_author_interest[v]))
            result.append((flag,sims))
        result.sort(key=lambda x:x[1])
        for i in result[-3:]:
            interest.extend(author_interest[author_list[i[0]]])
        p_author_interest.setdefault(author,interest)

    return p_author_interest


def print_validation_result(predict_author_interest,author_list,author_interest,num_topics,vali_n,vali_many):

    print (len(author_interest.keys()))
    print (len(predict_author_interest.keys()))

    with codecs.open("t_author_seq_v.txt","r","utf-8") as fid:
        for line in fid:
            author_list = line.strip().split('\t')[-1000:]

    #predict_author_interest = find_similar_author(predict_author_interest,author_list,author_interest)

    with codecs.open("result_predict_by_interest_valimany.txt","a","utf-8") as fid:
        accuracy = 0
        for author in author_list:
            #print  (len(set(predict_author_interest[author])&set(author_interest[author])))
            accuracy = accuracy + (len(set(predict_author_interest[author])&set(author_interest[author])))/3
            #fid.write(author+'\t'+str(len(set(predict_author_interest[author])&set(author_interest[author])))+'\n')
        fid.write(str(vali_many)+'\t'+str(accuracy/1000)+'\n')
        print (accuracy)

def print_final_result(predict_author_interest,author_list,author_interest,num_topics):


    fid_result = codecs.open("interst_training_20.txt","w","utf-8")

    with codecs.open("validation.txt","r","utf-8") as fid:
        for line in fid:
            if line == '\n':
                continue
            author = line.strip()
            fid_result.write(author + '\t' + '\t'.join(predict_author_interest[author])+'\n')


def expand_traing_set(test_n):
    indx = 0

    with codecs.open("p_author_paper.json","r","utf-8") as fid:
        t_author_paper = json.load(fid)

    with codecs.open("p_author_interest.json","r","utf-8") as fid:
        author_interest = json.load(fid)

    interest_paper = {}
    indx = 0
    author_seq =[]
    for author,interest_list in author_interest.items():
        if indx < 1000*(vali_n-1):
            author_seq.append(author)
            for interest in interest_list:
                for paper in t_author_paper[author]:
                    interest_paper.setdefault(interest,[]).append(paper)
        elif indx < 1000*vali_n:
            author_seq.append(author)
        else:
            author_seq.append(author)
            for interest in interest_list:
                for paper in t_author_paper[author]:
                    interest_paper.setdefault(interest,[]).append(paper)
        #    author_seq.append(author)

        indx += 1

    with codecs.open("interest_paper_validation.json","w","utf-8") as fid:
        json.dump(interest_paper,fid,ensure_ascii=False)
    with codecs.open("t_author_seq_v.txt","w","utf-8") as fid:
        fid.write('\t'.join(author_seq))


def read_data():
    with codecs.open("./precise_interest/interest_paper_stem_n.json","r","utf-8") as fid:
        interest_paper1 = json.load(fid)
    return interest_paper1

def expand_interest_paper(interest_paper1):
    interest_paper2 = read_data()
    interest_paper = {}
    flag = 0
    for interest,paper in interest_paper1.items():
        if interest in interest_paper2.keys():
            paper.extend(interest_paper2[interest])
        interest_paper.setdefault(interest,paper)
    return interest_paper




if __name__ == '__main__':

    for vali_many in range(200,1000,100):
        vali_n = 1
        num_topics = 666
        print (vali_n)
        #extract_paper_for_interest(vali_n)
        #extract_training_paper_for_interest_plus_clustering(vali_n)
        #extract_precise_training_all_paper_for_interest(vali_n)
        extract_training_paper_for_interest(0,vali_many)
        with codecs.open("author_interest.json","r","utf-8") as fid:
            author_interest = json.load(fid)

        author_list = list(author_interest.keys())
        #model = Doc2Vec.load("./doc2vec/doc2vec.model")
        vali_data = read_test_data("t_author_paper.json")
        test_data = read_test_data("p_author_paper.json")
        (interest_seq,dictionary,corpus) = create_dictionary(vali_many)

        for num_topics in range(800,860,160):
            (tfidf_model,lsi_model,corpus_simi_matrix) = create_lsi_model(num_topics,dictionary,corpus)
            #predict_author_interest = predict_n_interest(test_data,interest_seq,dictionary,corpus,tfidf_model,lsi_model,corpus_simi_matrix,vali_n)
            #predict_author_interest = predict_n_interest_plus_clustering(vali_data,interest_seq,dictionary,corpus,tfidf_model,lsi_model,corpus_simi_matrix,vali_n,vali_many)
            predict_author_interest = predict_n_interest(vali_data,interest_seq,dictionary,corpus,tfidf_model,lsi_model,corpus_simi_matrix,vali_n)
            #print_final_result(predict_author_interest,author_list,author_interest,num_topics)
            #predict_author_interest = times_s_matrix()
            #interest_paper = load_train()
            #predict_author_interest = predict_n_interest_vec(model,vali_data,interest_paper,author_interest)
            print_validation_result(predict_author_interest,author_list,author_interest,num_topics,vali_n,vali_many)
