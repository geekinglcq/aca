# -*- coding: utf-8 -*-
import json
import pandas as pd
import codecs
import numpy as np

from collections import OrderedDict

train_path = './task1/training.txt'
validataion_path = './task1/validation.txt'

variable_map = OrderedDict({
    ("id", 0),
    ("name", 1),
    ("org", 2),
    ("search_results_page", 3),
    ("homepage", 4),
    ("pic", 5),
    ("email", 6),   
    ("gender", 7),
    ("position", 8),
    ("location", 9)
})
variable = ["id", "name", "org", "search_results_page", "homepage", "pic",\
    "email", "gender", "position", "location"]

def handle_one_scientist(lines):
    """
    Decode the info of one scientist in TASK 1.
    return 
    """
    sample = ['' for i in range(10)]
    for line in lines:
        k, v = line[1:].strip().split(':', 1)
        sample[variable_map[k]] = v
    return sample

def read_task1(file):
    """
    Read the data of task1.
    Return tha DataFrame of scientists' info. 
    """
    temp = []
    data = []
    for line in codecs.open(file, 'r', encoding='utf-8'):
        if not(line.strip() == ''):
            temp.append(line)
        else:
            sample = handle_one_scientist(temp)
            data.append(sample)
            temp = []
    data = pd.DataFrame(data, columns=variable)
    return data
    
def read_former_task1_ans(file):
    """
    Read former task1 ans 
    """
    ans = pd.read_csv(file, sep='\t', skiprows=[0], error_bad_lines=False, skipfooter=1)
    ans = ans.fillna('')
    ans.columns = ['id', 'homepage', 'gender', 'position', 'pic', 'email', 'location']
    data = read_task1(validataion_path)[["id", "name", "org", "search_results_page"]]
    ans = pd.merge(ans, data, how='outer', on='id')
    return ans

def load_search_res(labeled=True):
    """
    Return a dict contains the search results. 
    Key is scientist's id.
    """
    if labeled:
        with open('./data/train_search_info.json') as f:
            data = json.load(f)
    else:
        with open('./data/validation_search_info.json') as f:
            data = json.load(f)
    return data
