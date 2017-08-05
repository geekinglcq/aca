# -*- coding: utf-8 -*-
import pandas
import codecs
import numpy as np

import data_io
import urllib
from urllib.request import urlopen
from bs4 import BeautifulSoup as bs 

def get_search_page(search_url):
    """
    Return the search results of the given searching url.
    Including the info of results title and url
    """
    html = urlopen(search_url)
    bsObj = bs(html.read())
    res = bsObj.findAll("h3", {"class": "r"})
    res = [[x.a.text, x.a["href"]] for x in res]
    return res

def get_true_url(url):
    """
    Get the true url after redirecting. 
    """
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko')
        response = urllib.request.urlopen(req)
        dlurl = response.geturl()    
        return dlurl
    except Exception as e:
        return None