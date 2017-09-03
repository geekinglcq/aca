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
    if len(data[0]) == 4:
        data = pd.DataFrame(data, columns=variable[0:3])
    else:
        data = pd.DataFrame(data, columns=variable)
    return data
    

def read_former_task1_ans(file, raw=validataion_path, skiprows=True):
    """
    Read former task1 ans 
    """
    if skiprows:
        skiprows = [0]
    else:
        skiprows = None
    ans = pd.read_csv(file, sep='\t', skiprows=skiprows, error_bad_lines=False)
    ans = ans.fillna('')
    if skiprows == [0]:
        ans = ans.drop(ans.shape[0] - 1)
    ans.columns = ['id', 'homepage', 'gender', 'position', 'pic', 'email', 'location']
    # print(ans.head())
    data = read_task1(raw)[["id", "name", "org", "search_results_page"]]
    # print(data.head())
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
