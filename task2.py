# -*- coding: utf-8 -*-
import codecs
import json

def readTraining(file_str):
    # read data from training.txt
    # record to json file {key=name,value=[interest1,]}

    fid = codecs.open(file_str,'r','utf-8')
    lines = fid.readlines()

    dict_name_interest = {}
    # read three lines at one time 
    for i in range(0,len(lines),3):
        name = lines[i].strip()
        interest = lines[i+1].strip().split(',')
        for j in range(len(interest)):
            interest[j] = interest[j].strip()
        dict_name_interest.setdefault(name,interest)

    with codecs.open("author_interest.json","w",'utf-8') as fid_json:
        json.dump(dict_name_interest,fid_json,ensure_ascii=False)

def readPaper(file_str):
    # read data from papres.txt
    # output three json files

    # indx_author_paper.json
    # author_cooperators.json
    # title_authors.json

    dict_indx = {}
    dict_author = {}
    dict_title = {}
    with codecs.open(file_str,"r",'utf-8') as f:
        for eachLine in f:
            if eachLine.startswith('#index'):
                i = int(eachLine[6:])
                dict_indx.setdefault(i,[])
            elif eachLine.startswith("#@"):
                Author = eachLine[2:-1].strip().split(',')
                for j in range(len(Author)):
                    Author[j] = Author[j].strip()
                # for indx_author_paper
                dict_indx[i].append(Author)
                
                # for author_cooperator    
                for j in range(len(Author)):
                    dict_author.setdefault(Author[j],[])
                    for k in range(len(Author)):
                        if k != j:
                            dict_author[Author[j]].append(Author[k])
            elif eachLine.startswith("#*"):
                Title = eachLine[2:-1]
                # for indx_author_paper
                dict_indx[i].append(Title)
                # for title_author
                dict_title.setdefault(Title,[]).append(Author)
            else:
                pass
    


    with codecs.open("indx_author_paper.json","w",'utf-8') as fid_json:
        json.dump(dict_indx,fid_json,ensure_ascii=False)

    with codecs.open("author_cooperators.json","w",'utf-8') as fid_json:
        json.dump(dict_author,fid_json,ensure_ascii=False)
    
    with codecs.open("title_authors.json","w",'utf-8') as fid_json:
        json.dump(dict_title,fid_json,ensure_ascii=False)
    

# def findCooperator(file_str):
    
#     # find author's cooperators

#     dict_result = {}
#     dict_title = {}
#     with codecs.open(file_str,"r",'utf-8') as f:
#         for eachLine in f:
#             if eachLine.startswith("#@"):
#                 Author = eachLine[2:-1].strip().split(',')
#                 for j in range(len(Author)):
#                     Author[j] = Author[j].strip()                
#                 for j in range(len(Author)):
#                     dict_result.setdefault(Author[j],[])
#                     for k in range(len(Author)):
#                         if k != j:
#                             dict_result[Author[j]].append(Author[k])
#             elif eachLine.startswith("#*"):
#                 Titile =  eachLine[2:-1].strip()
#                 dict_title.setdefault(Titile,[]).append(Author)
#             else:
#                 pass
#     with codecs.open("author_cooperators.json","w",'utf-8') as fid_json:
#         json.dump(dict_result,fid_json,ensure_ascii=False)
    
#     with codecs.open("title_authors.json","w",'utf-8') as fid_json:
#         json.dump(dict_title,fid_json,ensure_ascii=False)
    