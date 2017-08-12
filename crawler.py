# -*- coding: utf-8 -*-
import re
import pandas
import codecs
import numpy as np

import data_io
import urllib
import requests
import multiprocessing
from urllib.request import urlopen
from bs4 import BeautifulSoup as bs 

def get_search_page(search_url):
    """
    Return the search results of the given searching url.
    Including the info of results title, url, detail and if or not have fl(bool)
    """
    try:
        html = urlopen(search_url, timeout=10)
        bsObj = bs(html.read())
        res = bsObj.findAll("div", {"class": "rc"})
        ans = []
        for i in res:
            sample = []
            sample.append(i.h3.a.text)
            temp = get_true_url(i.h3.a["href"])
            if temp == None:
                sample.append(i.h3.a["href"])
            else:
                sample.append(temp)
            if (i.find("span", {"class", "st"}) != None):
                sample.append(i.find("span", {"class": "st"}).text)
            else:
                sample.append('Nothing')
            if i.div.div.find("div", {"class": "slp f"}) == None:
                sample.append(1)
            else:
                sample.append(0)
            ans.append(sample)
        return ans

    except Exception as e:
      print(e)
      return []

def get_true_url(url):
    """
    Get the true url after redirecting. 
    """
    try:

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'}
        dlurl = requests.get(url, headers=headers, timeout=5)
        return dlurl.url
    except Exception as e:  
        return ''

def get_pic_url(html):
    """
    Return the url of pics of given page text
    """
    try:
        pattern = re.compile(r'src="(.+?\.jpg)"')
        # headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'}
        # html = requests.get(url, headers=headers, timeout=5)
        img_list = pattern.findall(html.text)
        return img_list
        for i in range(len(img_list)):
            if not img_list[i].startswith('http'):
                root_url_p = re.compile(r'http[s]?:\/\/[^/]*\/')
                root_url = root_url_p.findall(html.url)
                if len(root_url) > 0:
                    img_list[i] = root_url[0][:-1] + img_list[i]
        return img_list
    except Exception as e:
        print(e)
        return []

def get_gender_name_single_page(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'}
    try:
        html = requests.get(url, headers=headers, timeout=5)
        bsObj = bs(html.text)
        name_list = [i.text for i in bsObj.findAll("span", {"class": "result-name"})]
        return name_list
    except Exception as e:
        print(e)
        return []
def get_gender_name():
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'}
        boy_url = 'http://www.babynames.net/boy?page='
        girl_url = 'http://www.babynames.net/girl?page='
        boys_name = set()
        girls_name = set()
        for i in range(1, 462):
            boys_name.update(get_gender_name_single_page(boy_url + str(i)))
        for i in range(1, 316):
            girls_name.update(get_gender_name_single_page(girl_url + str(i)))
        neuter_name = boys_name & girls_name
        boys_name = boys_name - neuter_name
        girls_name = girls_name - neuter_name
        return boys_name, girls_name
    except Exception as e:
        print(e)
        return [['Error'], ['Error']]