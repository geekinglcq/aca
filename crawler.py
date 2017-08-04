# -*- coding: utf-8 -*-
import pandas
import codecs
import numpy as np

import data_io
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

