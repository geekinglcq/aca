from sklearn.feature_extraction.text import TfidfVectorizer
from numpy import linalg as la
from gensim import corpora,models,similarities
from sklearn.cluster import KMeans
import json
import codecs
from sklearn.externals import joblib
from scipy.sparse import csr_matrix
import numpy as np
import nltk
from nltk.stem.snowball import SnowballStemmer
from scipy.cluster.hierarchy import ward, dendrogram,linkage,fcluster
from sklearn.metrics.pairwise import cosine_similarity
stemmer = SnowballStemmer("english")
def tokenize_and_stem(text):
    tokens = [word for word in text.lower().split()]
    filtered_tokens = []
    stems = [stemmer.stem(t) for t in tokens]
    return stems

def assign_paper_for_interest(paper_list,interest_list,interest_paper):
    tfidf_vectorizer = TfidfVectorizer(max_df=0.9, max_features=2000,\
                        min_df=0.05, stop_words='english',\
                        use_idf=True, tokenizer=tokenize_and_stem, ngram_range=(1,3))


    if len(paper_list) <=2 :
        for p in paper_list:
            interest = return_interest(interest_list,p)
            if len(interest) > 0:
                for v in set(interest):
                    interest_paper.setdefault(v,[]).append(p)
            else:
                for v in interest_list:
                    interest_paper.setdefault(v,[]).append(p)
        return interest_paper

    tfidf_matrix = tfidf_vectorizer.fit_transform(paper_list)

    tfidf_new = tfidf_matrix.toarray()
    if (tfidf_new.shape[0]) > 0:
        u,s,v = la.svd(tfidf_new,full_matrices=False)
        #print(u[:,:6].shape)
        #print(s[:6].shape)
        #print(v[:6,:].shape)
        tfidf_new = np.dot(u[:,:16],np.dot(np.diag(s[:16]),v[:16,:]))

    dist = cosine_similarity(tfidf_new)
    result = kmeans_clustering(dist)
    i_paper =group_paper(result,paper_list)
    for i,value in i_paper.items():
        interest = return_interest(interest_list,' '.join(value))
        if len(interest) > 0:
            for inst in interest:
                for p in value:
                    interest_paper.setdefault(inst,[]).append(p)
        else:
            for inst in interest_list:
                for p in value:
                    interest_paper.setdefault(inst,[]).append(p)
    return interest_paper

def ward_clustering(matrix):
    linkage_matrix = ward(matrix)
    result = fcluster(linkage_matrix, 3, criterion='maxclust')
    #print (result)
    return result

def group_paper_for_test(paper_list):

    tfidf_vectorizer = TfidfVectorizer(max_df=0.9, max_features=2000,\
                        min_df=0.05, stop_words='english',\
                        use_idf=True, tokenizer=tokenize_and_stem, ngram_range=(1,3))

    tfidf_matrix = tfidf_vectorizer.fit_transform(paper_list)
    tfidf_new = tfidf_matrix.toarray()
    if (tfidf_new.shape[0]) > 0:
        u,s,v = la.svd(tfidf_new,full_matrices=False)
        #print(u[:,:6].shape)
        #print(s[:6].shape)
        #print(v[:6,:].shape)
        tfidf_new = np.dot(u[:,:16],np.dot(np.diag(s[:16]),v[:16,:]))

    dist =  cosine_similarity(tfidf_new)
    result = ward_clustering(dist)
    i_paper =group_paper(result,paper_list)
    return i_paper

def kmeans_clustering(tfidf_matrix):
    num_clusters = min(tfidf_matrix.shape[0],3)
    km = KMeans(n_clusters=num_clusters)
    km.fit(tfidf_matrix)
    clusters = km.labels_.tolist()

    #print (clusters)
    return clusters

def main():
    with codecs.open("../t_author_paper.json","r","utf-8") as fid:
        t_author_paper = json.load(fid)

    with codecs.open("../author_interest.json","r","utf-8") as fid:
        author_interest = json.load(fid)

    interest_paper = {}
    flag = 0
    for author,paper_list in t_author_paper.items():
        if flag == 16:
            print (author)
            print (author_interest[author])
            i = 0
            for p in paper_list:
                print (str(i) + " : " + p)
                i += 1
            assign_paper_for_interest(paper_list,author_interest[author],interest_paper)
            break
        flag += 1

def group_paper(label_list,paper_list):
    class_paper = {}
    for i in range(len(label_list)):
        class_paper.setdefault(label_list[i],[]).append(paper_list[i])
    return class_paper


def return_interest(interest_list,paper_text):

        interest_stem = {}
        for v in interest_list:
            interest_stem.setdefault(v,v.split()).extend(tokenize_and_stem(v))
        interest_token = []
        for k,v in interest_stem.items():
            interest_token.extend(v)

        set_token = set(tokenize_and_stem(paper_text))&set(interest_token)
        result = []
        for v in set_token:
            result.extend([ k for k,value in interest_stem.items() if v in value ])
        return result


#if __name__ == "__main__":
#    main()
