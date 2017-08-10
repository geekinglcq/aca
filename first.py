# -*- coding: utf-8 -*-

import pandas 
import codecs
import crawler
import json
import data_io as dio


def generate_one_row(row):
    """
    Input: one row data of pandas.series
    Output: the answer string 
    """
    ans = '\t'.join([row.id, row.homepage, row.gender, row.position, row.pic, row.email, row.location])
    return ans + '\n'

def generat_ans_file(data):
    with codecs.open('first_task_ans.txt', 'w', encoding='utf-8') as f:
        f.write('<task1>\n')
        f.write('expert_id\thomepage_url\tgender\tposition\tperson_photo\temail\tlocation\n')
        for index, row in  data.iterrows():
            f.write(generate_one_row(row))
        f.write('</task1>\n')

def extract_search_info():
    data = dio.read_task1('./task1/training.txt')
    print(data.shape)
    train_set_info = {}
    for index, row in data.iterrows():
        if (index < 5000):
            continue
        print(index)
        train_set_info[row.id] = crawler.get_search_page(row.search_results_page)
        if (index % 100) == 0:
            with open('train_search_info_5.json', 'w') as f:
                json.dump(train_set_info, f)
        # if (index >= 6000):
        #     break
    with open('train_search_info_5.json', 'w') as f:
        json.dump(train_set_info, f)
    #data = dio.read_task1('./task1/validation.txt')
    #test_set_info = {}
    #for index, row in data.iterrows():
    #    print(index)
    #    test_set_info[row.id] = crawler.get_search_page(row.search_results_page)
    #with open('train_search_info.json', 'w') as f:
    #    json.dump(test_set_info, f)