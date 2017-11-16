import codecs
import json
from collections import Counter

def expand_by_cite(flag):
    with codecs.open("./raw_data/p_author_paper_final.json","r","utf-8") as fid:
        p_author_paper = json.load(fid)

    with codecs.open("./raw_data/t_author_paper.json","r","utf-8") as fid:
        t_author_paper = json.load(fid)

    with codecs.open("./raw_data/author_indx_citeindx.json","r","utf-8") as fid:
        author_indx_citeindx = json.load(fid)

    with codecs.open("./raw_data/indx_paper_author.json","r","utf-8") as fid:
        indx_paper_author = json.load(fid)

    #print len(author_indx_citeindx)



    if flag == 'training':
        #author_list = t_author_press.keys()
        file_name = "./raw_data/t_author_paper_ex_cite.json"
        f_author_paper = t_author_paper

    if flag == 'test':
        #author_list = p_author_press.keys()
        file_name = "./raw_data/p_author_paper_ex_cite.json"
        f_author_paper = p_author_paper

    t_author_paper_ex = {}
    for author in f_author_paper.keys():
        paper = []
        for indx in author_indx_citeindx[author].keys():
            paper.append(str(indx))
            paper.extend(author_indx_citeindx[author][indx])
        paper = [indx_paper_author[str(indx)][1] for indx in paper ]
        t_author_paper_ex.setdefault(author,paper)


    with codecs.open(file_name,"w","utf-8") as fid:
        json.dump(t_author_paper_ex,fid,ensure_ascii=False)


def expand_by_author(flag):
    with codecs.open("./raw_data/p_author_paper_final.json","r","utf-8") as fid:
        p_author_paper = json.load(fid)

    with codecs.open("./raw_data/t_author_paper.json","r","utf-8") as fid:
        t_author_paper = json.load(fid)

    with codecs.open("./raw_data/author_indx_citeindx.json","r","utf-8") as fid:
        author_indx_citeindx = json.load(fid)

    with codecs.open("./raw_data/author_cooperators.json","r","utf-8") as fid:
        author_cooperators = json.load(fid)

    with codecs.open("./raw_data/indx_paper_author.json","r","utf-8") as fid:
        indx_paper_author = json.load(fid)
    print len(author_indx_citeindx)



    if flag == 'training':
        #author_list = t_author_press.keys()
        file_name = "./raw_data/t_author_paper_ex_coop.json"
        f_author_paper = t_author_paper

    if flag == 'test':
        #author_list = p_author_press.keys()
        file_name = "./raw_data/p_author_paper_ex_coop.json"
        f_author_paper = p_author_paper



    t_author_paper_ex = {}
    for author in f_author_paper.keys():
        paper = []
        for cop in author_cooperators[author]:
            #paper.append(str(indx))
            paper.extend(choose_n_interest(author_indx_citeindx[cop].keys(),20))
        #paper = choose_n_interest(paper,20)
        paper = [indx_paper_author[str(indx)][1] for indx in paper ]
        t_author_paper_ex.setdefault(author,paper)


    with codecs.open(file_name,"w","utf-8") as fid:
        json.dump(t_author_paper_ex,fid,ensure_ascii=False)

def choose_n_interest(interest,n):
    r_interest = []
    c_interest = Counter(interest).most_common(n)
    for i in range(min(len(c_interest),n)):
        r_interest.append(c_interest[i][0])
    return r_interest

if __name__ == '__main__':
    expand_by_cite('training')
    expand_by_author('training')
    expand_by_cite('test')
    expand_by_author('test')
