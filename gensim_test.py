# -*- coding: utf-8 -*-
from gensim import corpora,models,similarities
from collections import defaultdict
from collections import Counter
import codecs
import json
import numpy as np

def make_dictionary():

    with codecs.open("t_author_paper.json","r","utf-8") as fid:
        t_author_paper = json.load(fid)

    author = []
    papers = []

    for k,v in t_author_paper.items():
        author.append(k)
        if len(v) <= 0:
            papers.append("NNNN")
        else:
            papers.append(" ".join(v))

    stoplist = set('for a of the and that to in on from is are there this these some more any very \
                   an , . : '.split())

    texts = [[word for word in paper.lower().split() if word not in stoplist] 
             for paper in papers]

    dictionary = corpora.Dictionary(texts)
    
    with codecs.open("t_seq.txt","w","utf-8") as fid:
        fid.writelines('\t'.join(author))
    # save dictionary
    print (len(author))
    print (len(papers))
    print("saving ...")
    dictionary.save('papers_dictionary_300.dict')
    corpus = [dictionary.doc2bow(text) for text in texts]
    corpora.MmCorpus.serialize('papers_dictionary_300.mm',corpus)

def create_model():

    with codecs.open("t_seq.txt","r","utf-8") as fid:
        for author in fid:
            authors = author.strip().split('\t')

    with codecs.open("p_author_paper.json","r","utf-8") as fid:
        p_author_paper = json.load(fid)

    dictionary = corpora.Dictionary.load('papers_dictionary_300.dict')
    corpus = corpora.MmCorpus('papers_dictionary_300.mm')
    tfidf_model = models.TfidfModel(corpus)
    corpus_tfidf = tfidf_model[corpus]
    lsi_model = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=300)

    print("save tfide_model")
    tfidf_model.save('tfidf_model_300')
    print("save lsi_model")
    lsi_model.save('lsi_model_300.lsi')
    #tfidf_mode = models.TfidfModel(corpus)
    #corpus_lsi = lsi_model[corpus_tfidf]
    #corpus_simi_matrix = similarities.MatrixSimilarity(corpus_lsi)
        #p_author_related.setdefault(key,author_related)

    #with codecs.open("p_author_related.json","w","utf-8") as fid:
     #   json.dump(p_author_related, fid, ensure_ascii=False)

    #return p_author_related

def calculate_similarity():
    lsi_model = models.LsiModel.load('lsi_model_300.lsi')
    tfidf_model = models.TfidfModel.load('tfidf_model_300')

    with codecs.open("t_seq.txt","r","utf-8") as fid:
        for author in fid:
            authors = author.strip().split('\t')

    with codecs.open("p_author_paper.json","r","utf-8") as fid:
        p_author_paper = json.load(fid)

    dictionary = corpora.Dictionary.load('papers_dictionary_300.dict')
    corpus = corpora.MmCorpus('papers_dictionary_300.mm')
    corpus_tfidf = tfidf_model[corpus]
    corpus_lsi = lsi_model[corpus_tfidf]
    corpus_simi_matrix = similarities.MatrixSimilarity(corpus_lsi)
    corpus_simi_matrix.save("corpus_simi_matrix_300")
    #corpus_simi_matrix = similarities.MatrixSimilarity.load('corpus_simi_matrix')

    p_author_related = {}
    author_related = []


    stoplist = set('for a of the and that to in on from is are there this these some more any very \
                   an , . : '.split())

    for key,value in p_author_paper.items():
        author_related = []
        test_text = (" ".join(value)).split()

        texts = [word for word in test_text if word not in stoplist]
        test_bow = dictionary.doc2bow(texts)
        test_tfidf = tfidf_model[test_bow]
        test_lsi = lsi_model[test_tfidf]
        test_simi = corpus_simi_matrix[test_lsi]

        result = list(enumerate(test_simi))
        result.sort(key=lambda x:x[1])
        for v in result[-4:]:
            author_related.append(authors[v[0]])
        #print (author_related)
        p_author_related.setdefault(key,author_related)
    
    with codecs.open("p_author_related.json","w","utf-8") as fid:
        json.dump(p_author_related, fid, ensure_ascii=False)

    return p_author_related


def predict_by_title(p_author_related):


    fid_result = codecs.open("predict_gensim_300.txt","w","utf-8")

    with codecs.open("author_interest.json","r","utf-8") as fid:
        author_interest = json.load(fid)

    with codecs.open("validation.txt","r","utf-8") as fid:
        for line in fid:
            if line == '\n':
                continue

            interest = []
            line = line.strip()
            fid_result.write(line+'\t')
            for v in p_author_related[line]:
                interest.extend(author_interest[v])

            interest = Counter(interest).most_common(5)
            final_interest = []
            for i in range(len(interest)):
                final_interest.append(interest[i][0])
            final_interest.extend([(5-len(final_interest))*""])
            fid_result.write('\t'.join(final_interest)+'\n')
    fid_result.close()

def author_paper():

    with codecs.open("indx_paper_author.json","r","utf-8") as fid:
        indx_paper_author = json.load(fid)

    with codecs.open("author_interest.json","r","utf-8") as fid:
        author_interest = json.load(fid)

    with codecs.open("p_author_cooperators.json","r","utf-8") as fid:
        p_author_cooperators = json.load(fid)

    t_author_paper = {}
    p_author_paper = {}
    for key,value in indx_paper_author.items():
        for v in value[0]:
            if v in author_interest.keys():
                t_author_paper.setdefault(v,[]).append(value[1])
            elif v in p_author_cooperators.keys():
                p_author_paper.setdefault(v,[]).append(value[1])

    with codecs.open("t_author_paper.json","w","utf-8") as fid:
        json.dump(t_author_paper, fid, ensure_ascii=False)

    with codecs.open("p_author_paper.json","w","utf-8") as fid:
        json.dump(p_author_paper, fid, ensure_ascii=False)



if __name__ == "__main__":
    print ('begin to make dictionary ...')
    make_dictionary()
    print ('begin to make models ...')
    create_model()
    print ('begin to calculate_similarity ...')
    p = calculate_similarity()
    print ('begin to predict ...')
    predict_by_title(p)

