import codecs
import json


#def create_author_paper():
#
#    dict_result = {}
#    with codecs.open('./raw_data/papers.txt',"r",'utf-8') as f:
#        for eachLine in f:
#            if eachLine.startswith('#index'):
#                i = int(eachLine[6:])
#                #dict_result.setdefault(i,[])
#            elif eachLine.startswith("#@"):
#                Author = eachLine[2:-1].strip().split(',')
#                for j in range(len(Author)):
#                    Author[j] = Author[j].strip()
#                    dict_result.setdefault(Author[j],[])
#            elif eachLine.startswith("#*"):
#                press = eachLine[2:-1].strip()
#                for v in Author:
#                    dict_result.setdefault(v,[]).append(press)
#            else:
#                pass
#
#    with codecs.open("author_paper.json","w",'utf-8') as fid_json:
#        json.dump(dict_result,fid_json,ensure_ascii=False)
#

def create_author_interest():

    fid = codecs.open('./raw_data/training.txt','r','utf-8')
    lines = fid.readlines()

    dict_name_interest = {}
    for i in range(0,len(lines),3):
        name = lines[i].strip()
        interest = lines[i+1].strip().split(',')
        for j in range(len(interest)):
            interest[j] = interest[j].strip()
        dict_name_interest.setdefault(name,interest)

    with codecs.open("./raw_data/author_interest.json","w",'utf-8') as fid_json:
        json.dump(dict_name_interest,fid_json,ensure_ascii=False)


def create_author_press():

    dict_result = {}
    with codecs.open('./raw_data/papers.txt',"r",'utf-8') as f:
        for eachLine in f:
            if eachLine.startswith('#index'):
                i = int(eachLine[6:])
                #dict_result.setdefault(i,[])
            elif eachLine.startswith("#@"):
                Author = eachLine[2:-1].strip().split(',')
                for j in range(len(Author)):
                    Author[j] = Author[j].strip()
                    dict_result.setdefault(Author[j],[])
            elif eachLine.startswith("#c"):
                press = eachLine[2:-1].strip()
                for v in Author:
                    dict_result.setdefault(v,[]).append(press)
            else:
                pass

    with codecs.open("./raw_data/author_press.json","w",'utf-8') as fid_json:
        json.dump(dict_result,fid_json,ensure_ascii=False)


def create_author_indx_citeindx():

    author_indx_citeindx = {}
    with codecs.open('./raw_data/papers.txt',"r",'utf-8') as f:
        for eachLine in f:
            if eachLine.startswith('#index'):
                i = int(eachLine[6:])
                i = str(i)
                #dict_result.setdefault(i,[])
            elif eachLine.startswith("#@"):
                Author = eachLine[2:-1].strip().split(',')
                for j in range(len(Author)):
                    Author[j] = Author[j].strip()
                    author_indx_citeindx.setdefault(Author[j],{}).setdefault(i,[])
            elif eachLine.startswith("#%"):
                cite = eachLine[2:-1].strip()
                for v in Author:
                    author_indx_citeindx[v][i].append(cite)
            else:
                pass

    with codecs.open("./raw_data/author_indx_citeindx.json","w",'utf-8') as fid_json:
        json.dump(author_indx_citeindx,fid_json,ensure_ascii=False)


def create_indx_paper_author():
    indx_paper_author = {}

    with codecs.open('./raw_data/papers.txt',"r",'utf-8') as f:
        for eachLine in f:
            if eachLine.startswith('#index'):
                i = int(eachLine[6:])
                indx_paper_author.setdefault(i,[])
            elif eachLine.startswith("#@"):
                Author = eachLine[2:-1].strip().split(',')
                indx_paper_author[i].append(Author)
            elif eachLine.startswith("#*"):
                paper = eachLine[2:-1].strip()
                indx_paper_author[i].append(paper)
            else:
                pass

    with codecs.open("./raw_data/indx_paper_author.json","w",'utf-8') as fid_json:
        json.dump(indx_paper_author,fid_json,ensure_ascii=False)



def create_author_paper_final():
    test_author = []
    with codecs.open("./raw_data/task2_test_final.txt","r","utf-8") as fid:
        for line in fid:
            if line == '\n':
                continue
            line = line.strip()
            test_author.append(line)

    with codecs.open("./raw_data/author_indx_citeindx.json","r","utf-8") as fid:
        author_indx_citeindx = json.load(fid)

    with codecs.open("./raw_data/indx_paper_author.json","r","utf-8") as fid:
        indx_paper_author = json.load(fid)

    author_paper = {}
    for author in test_author:
        paper = []
        paper.extend(author_indx_citeindx[author].keys())
        paper = [indx_paper_author[str(indx)][1] for indx in paper]
        author_paper.setdefault(author,paper)

    with codecs.open("./raw_data/p_author_paper_final.json","w","utf-8") as fid:
        json.dump(author_paper,fid,ensure_ascii=False)

def create_author_paper_training():
    test_author = []
    with codecs.open("./raw_data/author_interest.json","r","utf-8") as fid:
        author_interest = json.load(fid)
    test_author = author_interest.keys()

    with codecs.open("./raw_data/author_indx_citeindx.json","r","utf-8") as fid:
        author_indx_citeindx = json.load(fid)

    with codecs.open("./raw_data/indx_paper_author.json","r","utf-8") as fid:
        indx_paper_author = json.load(fid)

    author_paper = {}
    for author in test_author:
        paper = []
        paper.extend(author_indx_citeindx[author].keys())
        paper = [indx_paper_author[str(indx)][1] for indx in paper]
        author_paper.setdefault(author,paper)

    with codecs.open("./raw_data/t_author_paper.json","w","utf-8") as fid:
        json.dump(author_paper,fid,ensure_ascii=False)


def create_author_press_final():
    test_author = []
    with codecs.open("./raw_data/task2_test_final.txt","r","utf-8") as fid:
        for line in fid:
            if line == '\n':
                continue
            line = line.strip()
            test_author.append(line)

    #with codecs.open("./raw_data/author_indx_citeindx.json","r","utf-8") as fid:
    #    author_indx_citeindx = json.load(fid)

    with codecs.open("./raw_data/author_press.json","r","utf-8") as fid:
        author_press = json.load(fid)

    p_author_press = {}
    for author in test_author:
        press = author_press[author]
        #paper = [indx_paper_author[str(indx)][1] for indx in paper]
        p_author_press.setdefault(author,press)

    with codecs.open("./raw_data/p_author_press_final.json","w","utf-8") as fid:
        json.dump(p_author_press,fid,ensure_ascii=False)

def create_author_press_training():
    test_author = []
    with codecs.open("./raw_data/author_interest.json","r","utf-8") as fid:
        author_interest = json.load(fid)
    test_author = author_interest.keys()

    #with codecs.open("./raw_data/author_indx_citeindx.json","r","utf-8") as fid:
    #    author_indx_citeindx = json.load(fid)

    with codecs.open("./raw_data/author_press.json","r","utf-8") as fid:
        author_press = json.load(fid)

    t_author_press = {}
    for author in test_author:
        press = author_press[author]
        #paper.extend(author_indx_citeindx[author].keys())
        #paper = [indx_paper_author[str(indx)][1] for indx in paper]
        t_author_press.setdefault(author,press)

    with codecs.open("./raw_data/t_author_press.json","w","utf-8") as fid:
        json.dump(t_author_press,fid,ensure_ascii=False)



def findCooperator():

    # find author's cooperators

    dict_result = {}
    dict_title = {}
    with codecs.open('./raw_data/papers.txt',"r",'utf-8') as f:

        # author_for_title = []
        for eachLine in f:
            if eachLine.startswith("#@"):
                Author = eachLine[2:-1].strip().split(',')
                for j in range(len(Author)):
                    Author[j] = Author[j].strip()
                # author_for_title = Author.copy()
                for j in range(len(Author)):
                    dict_result.setdefault(Author[j],[])
                    for k in range(len(Author)):
                        if k != j:
                            dict_result[Author[j]].append(Author[k])
            elif eachLine.startswith("#*"):
                Titile =  eachLine[2:-1].strip()
                dict_title.setdefault(Titile,Author)
            else:
                pass
    with codecs.open("./raw_data/author_cooperators.json","w",'utf-8') as fid_json:
        json.dump(dict_result,fid_json,ensure_ascii=False)

    #with codecs.open("./raw_data/title_authors.json","w",'utf-8') as fid_json:
    #    json.dump(dict_title,fid_json,ensure_ascii=False)


if __name__ == '__main__':
    create_indx_paper_author()
    findCooperator()
    create_author_indx_citeindx()
    create_author_press()
    create_author_interest()
    create_author_paper_training()
    create_author_paper_final()
    create_author_press_training()
    create_author_press_final()
