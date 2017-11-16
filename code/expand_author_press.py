import codecs
import json
import random

def shuffle_list(paper_list,number):
    random.shuffle(paper_list)
    return paper_list[:number]
def expand_by_coop(flag):
    with codecs.open("./raw_data/author_press.json","r","utf-8") as fid:
        author_press = json.load(fid)

    with codecs.open("./raw_data/author_cooperators.json","r","utf-8") as fid:
        author_cooperators = json.load(fid)

    with codecs.open("./raw_data/p_author_press_final.json","r","utf-8") as fid:
        p_author_press = json.load(fid)

    with codecs.open("./raw_data/t_author_press.json","r","utf-8") as fid:
        t_author_press = json.load(fid)


    if flag == 'training':
        author_list = t_author_press.keys()
        file_name = "./raw_data/t_author_press_ex_coop.json"
        f_author_press = t_author_press

    if flag == 'test':
        author_list = p_author_press.keys()
        file_name = "./raw_data/p_author_press_ex_coop.json"
        f_author_press = p_author_press

    t_author_press_ex = {}
    for author in author_list:
        press = author_press[author]
        if len(f_author_press[author]) < 20:
            coop = []
            coop.extend(author_cooperators[author])
            for v in coop:
                press.extend(shuffle_list(author_press[author],20))
        t_author_press_ex.setdefault(author,press)

    with codecs.open(file_name,"w","utf-8") as fid:
        json.dump(t_author_press_ex,fid,ensure_ascii=False)

def expand_by_cite(flag):
    with codecs.open("./raw_data/author_indx_citeindx.json","r","utf-8") as fid:
        author_indx_citeindx = json.load(fid)

    with codecs.open("./raw_data/indx_press.json","r","utf-8") as fid:
        indx_press = json.load(fid)

    with codecs.open("./raw_data/p_author_press_final.json","r","utf-8") as fid:
        p_author_press = json.load(fid)

    with codecs.open("./raw_data/t_author_press.json","r","utf-8") as fid:
        t_author_press = json.load(fid)


    if flag == 'training':
        author_list = t_author_press.keys()
        file_name = "./raw_data/t_author_press_ex_cite.json"
        f_author_press = t_author_press

    if flag == 'test':
        author_list = p_author_press.keys()
        file_name = "./raw_data/p_author_press_ex_cite.json"
        f_author_press = p_author_press

    t_author_press_ex = {}

    for author in author_list:
        press = f_author_press[author]
        if len(f_author_press[author]) < 20:
            cite = []
            for indx in author_indx_citeindx[author].keys():
                cite.extend(author_indx_citeindx[author][indx])
            for v in cite:
                press.extend(indx_press[str(v)])
        t_author_press_ex.setdefault(author,press)

    with codecs.open(file_name,"w","utf-8") as fid:
        json.dump(t_author_press_ex,fid,ensure_ascii=False)


def read_paper():
    indx_press = {}

    with codecs.open("./raw_data/papers.txt","r","utf-8") as fid:
        for eachLine in fid:
            if eachLine.startswith('#index'):
                i = int(eachLine[6:])
                indx_press.setdefault(str(i),[])
            elif eachLine.startswith("#c"):
                press = eachLine[2:-1].strip()
                indx_press[str(i)].append(press)
            else:
                pass
    with codecs.open("./raw_data/indx_press.json","w",'utf-8') as fid_json:
        json.dump(indx_press,fid_json,ensure_ascii=False)

if __name__ == "__main__":
    read_paper()
    expand_by_cite('training')
    expand_by_coop('training')
    expand_by_cite('test')
    expand_by_coop('test')
