# -*- coding: utf-8 -*-
import pandas
import codecs
import numpy as np

import data_io
import urllib
import requests
from urllib.request import urlopen
from bs4 import BeautifulSoup as bs 

def get_search_page(search_url):
    """
    Return the search results of the given searching url.
    Including the info of results title, url, detail and if or not have fl(bool)
    """
    try:
        html = urlopen(search_url, timeout=5)
        bsObj = bs(html.read())
        res = bsObj.findAll("div", {"class": "rc"})
        ans = []
        for i in res:
            sample = []
            sample.append(i.h3.a.text)
            temp = get_true_url(i.h3.a["href"]):
            if temp == None:
                sample.append(i.h3.a["href"])
            else:
                sample.append(temp)
            sample.append(i.find("span", {"class": "st"}).text)
            if i.div.div.find("div", {"class": "slp f"}) == None:
                sample.append(1)
            else:
                sample.append(0)
            ans.append(sample)
        return ans

    except Exception as e:
      print(e)
      return None

def get_true_url(url):
    """
    Get the true url after redirecting. 
    """
    try:

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'}
        dlurl = requests.get(url, headers=headers, timeout=5)
        return dlurl.url
    except Exception as e:
        return None
