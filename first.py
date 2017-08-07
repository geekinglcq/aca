# -*- coding: utf-8 -*-

import pandas 
import codecs

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
        f.write('</task1>')

  
