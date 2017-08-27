#-*-coding:utf-8-*-

from __future__ import division
from gensim import corpora,models,similarities
from collections import Counter,defaultdict
import codecs
import json

#interest_paper_path = 'interest_paper_from_neighbors.json'
def extract_paper_for_interest():

    with codecs.open("t_author_paper.json","r","utf-8") as fid:
        t_author_paper = json.load(fid)

    with codecs.open("author_interest.json","r","utf-8") as fid:
        author_interest = json.load(fid)

    interest_paper = {}
    for author,interest_list in author_interest.items():
        for interest in interest_list:
            for paper in t_author_paper[author]:
                interest_paper.setdefault(interest,[]).append(paper)

    with codecs.open("interest_paper.json","w","utf-8") as fid:
        json.dump(interest_paper,fid,ensure_ascii=False)


def create_dictionary():

    print ("create dictionary ...")
    with codecs.open("interest_paper.json","r","utf-8") as fid:
        interest_paper = json.load(fid)

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

def remove_once_appearance(text_list,n):
    frequency = defaultdict(int)
    for text in text_list:
        for token in text:
            frequency[token] += 1
    text_list = [[token for token in text if frequency[token] > n] for text in text_list]
    return text_list

def clean_data(text):

    stop_list = set()#set('a is are on from for and not to that') #this there these those have has been were I you me they can could be do . , : ! ? '.split())
    text = [word for word in text.lower().split() if word not in stop_list]
    return text



def create_lsi_model(num_topics,dictionary,corpus):

    print ("create lsi model ...")
    tfidf_model = models.TfidfModel(corpus)
    corpus_tfidf = tfidf_model[corpus]
    lsi_model = models.LsiModel(corpus_tfidf,id2word=dictionary,num_topics = num_topics)
    corpus_lsi = lsi_model[corpus_tfidf]
    corpus_simi_matrix = similarities.MatrixSimilarity(corpus_lsi)

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

def predict_n_interest(author_paper,interest_seq,dictionary,corpus,tfidf_model,lsi_model,corpus_simi_matrix):

    print ("predict interest ...")
    predict_author_interest = {}
    for author,paper in author_paper.items():
        interest = []
        test_text = clean_data(' '.join(paper))
        test_bow = dictionary.doc2bow(test_text)
        test_tfidf = tfidf_model[test_bow]
        test_lsi = lsi_model[test_tfidf]
        test_simi = corpus_simi_matrix[test_lsi]

        result = list(enumerate(test_simi))
        result.sort(key=lambda x:x[1])

        for v in result[-10:]:
            interest.append(interest_seq[v[0]])
        interest.extend(['']*(5-len(interest)))
        predict_author_interest.setdefault(author,interest)

    with codecs.open("p_author_interest_lsi_10.json","w","utf-8") as fid:
        json.dump(predict_author_interest,fid,ensure_ascii=False)

    return predict_author_interest

def print_validation_result(predict_author_interest,author_list,author_interest,num_topics):

    print (len(author_interest.keys()))
    print (len(predict_author_interest.keys()))

    with codecs.open("result_predict_by_interest_p.txt","a","utf-8") as fid:
        accuracy = 0
        for author in author_list:
            accuracy = accuracy + (len(set(predict_author_interest[author])&set(author_interest[author])))/3
            #fid.write(author+'\t'+str(len(set(predict_author_interest[author])&set(author_interest[author])))+'\n')
        fid.write(str(num_topics)+'\t'+str(accuracy/6000)+'\n')

def print_final_result(predict_author_interest,author_list,author_interest,num_topics):


    fid_result = codecs.open("interst_from_interest_800.txt","w","utf-8")

    with codecs.open("validation.txt","r","utf-8") as fid:
        for line in fid:
            if line == '\n':
                continue
            author = line.strip()
            fid_result.write(author + '\t' + '\t'.join(predict_author_interest[author])+'\n')



if __name__ == '__main__':
    #extract_paper_for_interest()
    with codecs.open("author_interest.json","r","utf-8") as fid:
        author_interest = json.load(fid)

    author_list = list(author_interest.keys())

    vali_data = read_test_data("t_author_paper.json")
    test_data = read_test_data("p_author_paper.json")
    (interest_seq,dictionary,corpus) = create_dictionary()

    for num_topics in range(800,860,60):
        (tfidf_model,lsi_model,corpus_simi_matrix) = create_lsi_model(num_topics,dictionary,corpus)
        predict_author_interest = predict_n_interest(test_data,interest_seq,dictionary,corpus,tfidf_model,lsi_model,corpus_simi_matrix)
        print_final_result(predict_author_interest,author_list,author_interest,num_topics)
