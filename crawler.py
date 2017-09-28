# -*- coding: utf-8 -*-
import re
import os
import math
import json
import shutil
import pandas
import codecs
import numpy as np
import data_io
import urllib
import hashlib
import requests
import threading
import multiprocessing
from PIL import Image
from random import randint
from threading import Thread
from selenium import webdriver
from urllib.request import urlopen
from bs4 import BeautifulSoup as bs 

phantomjs_path = r'D:\DevTools\phantomjs-2.1.1-windows\bin\phantomjs.exe'

user_agents = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',\
               'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063',\
               'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv,2.0.1) Gecko/20100101 Firefox/4.0.1',\
               'Mozilla/5.0 (Windows NT 6.1; rv,2.0.1) Gecko/20100101 Firefox/4.0.1',\
               'Mozilla/5.0 (Windows NT 6.1; rv,2.0.1) Gecko/20100101 Firefox/4.0.1']
ss_proxies = {"http": "127.0.0.1:1080", "https": "127.0.0.1:1080"}

def get_search_page(search_url, use_proxy=False):

    """
    Return the search results of the given searching url.
    Including the info of results title, url, detail and if or not have fl(bool)
    """
    try:
        if use_proxy:
            proxies = ss_proxies
        else:
            proxies = None
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'}
        search_url = search_url.replace('ifang.ml', '166.111.7.106')
        html = requests.get(search_url, headers=headers, timeout=20, proxies=proxies)
        
        bsObj = bs(html.text)
        res = bsObj.findAll("div", {"class": "rc"})
        ans = []
        for i in res:
            sample = []
            sample.append(i.h3.a.text) 
            temp = get_true_url(i.h3.a["href"])
            if temp == '':
                sample.append(i.h3.a["href"])
            else:
                sample.append(temp)
            if (i.find("span", {"class", "st"}) != None):
                sample.append(i.find("span", {"class": "st"}).text)
            else:
                sample.append('Nothing')
            temp = i.div.div.find("div", {"class": "slp f"})
            if temp == None:
                sample.append(1)
            elif temp.find("a", {"class": "fl"}) == None:
                sample.append(1) 
            else:
                sample.append(0)
            ans.append(sample)
        return ans

    except Exception as e:
      print(e)
      return []
def single_thread_get_search_page(data, search_info):
    """
    Data - [[id, url], [id, url]]
    """
    c = 0
    for i in data:
        if (c % 50) == 0:
            print(c)
        search_info[i[0]] = get_search_page(i[1])
        c += 1

def multi_thread_get_search_page(data, threads_num=10):
    """
    Data - stdandard dataframe
    """
    search_info = []
    for i in range(threads_num):
        search_info.append(dict())
    threads = []
    num = len(data)
    chunk = math.ceil(num / threads_num)
    splited_data = [[] for i in range(threads_num)]
    for i, r in data.iterrows():
        splited_data[i % threads_num].append([r['id'], r['search_results_page']])
    print('Data split done')
    
    for i in range(threads_num):
        t = threading.Thread(target=single_thread_get_search_page, args=(splited_data[i], search_info[i]))
        threads.append(t)
    for i in threads:
        print('Start')
        i.start()
    for i in threads:
        i.join()
    info_sum = {}
    for i in search_info:
        info_sum.update(i)
    return info_sum
    


def get_true_url(url, use_proxy=True, re_try=False):
    """
    Get the true url and title after redirecting. 
    """
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063',\
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',\
                    'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',\
                    'Accept-Encoding': 'gzip, deflate',\
                    'Referer': 'https://www.google.com/'}
    try:
        if re_try:
            verify = False
        else:
            verify = True
        dlurl = requests.get(url, headers=headers, timeout=10, verify=verify)
        return dlurl.url
    except Exception as e:  
        if use_proxy:
            proxies = ss_proxies
            try:
                dlurl = requests.get(url, headers=headers, timeout=20, proxies=proxies)
                return dlurl.url
            except Exception as e:
                print(e)
                return ''
        else:
            print(e)
            return ''
    
def get_html_text(url, use_proxy=False, re_try=False):
    """
    Get the html text for given url
    """
    try:
        if use_proxy:
            proxies = ss_proxies
            timeout = 40
        else:
            proxies = None
            timeout = 10
        if re_try:
            verify = False
        else:
            verify = './data/certs.pem'
        user_agent = user_agents[randint(0, len(user_agents) - 1)]
        headers = {'User-Agent': user_agent,\
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',\
                    'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',\
                    'Accept-Encoding': 'gzip, deflate',\
                    'Referer': 'https://www.google.com/'}
        html = requests.get(url, headers=headers, timeout=timeout, proxies=proxies, verify=verify)
        return html.text
    except requests.exceptions.SSLError:
        if not re_try:
            return get_html_text(url, use_proxy=True, re_try=True)
        else:
            return ''
    except Exception as e:  
        print(e)
        print(type(e))
        if not use_proxy:
            return get_html_text(url, use_proxy=True)
        return ''
def get_local_html(url, prefix='./webpage/'):
    try:
        filename = hashlib.md5(url.encode('utf-8')).hexdigest()
        if not os.path.isfile(prefix + filename):
            html_text = get_html_text(url)
            if html_text == '':
                return ''
            else:
                with codecs.open(prefix + filename, 'w', 'utf-8') as f:
                    f.write(html_text)
                return html_text
        else:
            with codecs.open(prefix + filename, 'r', 'utf-8') as f:
                return f.read()
    except Exception as e:
        return ''

def store_html_text(data, prefix='./webpage/'):
    """
    Store the html text. Check if there is a html file in disk, if not get html text and store it.
    Input:  data - list of [id, url]
    """
    filename = hashlib.md5(data[1].encode('utf-8')).hexdigest()
    # if not os.path.isfile(prefix + filename):
    if True:
        html_text = get_html_text(data[1])
        if html_text == '':
            return False
        else:
            with codecs.open(prefix + filename, 'w', 'utf-8') as f:
                f.write(html_text)
            return True
def store_d_html_text_single(data, prefix='./webpage/'):
    """
    Get the dynamical html text for given urls and store them.
    Input: data - list of [id, url]
    """
    service_args=[]
    service_args.append('--load-images=no')  ##关闭图片加载
    service_args.append('--disk-cache=yes')  ##开启缓存
    driver = webdriver.PhantomJS(executable_path=phantomjs_path, service_args=service_args)
    driver.set_page_load_timeout(30)
    for pid, url in data:
        try:
            driver.get(url)
            filename = hashlib.md5(url.encode('utf-8')).hexdigest()
            with codecs.open(prefix + filename, 'w', 'utf-8') as f:
                f.write(driver.page_source)
            driver.get("about:blank")
        except Exception as e:  
            pass


def store_d_html_text_multi(data, prefix='./webpage/', threads_num=10):
    """
    Input: data- standard dataframe
    """
    chunk = math.ceil(data.shape[0] / threads_num)
    threads = []
    id_url = [[] for i in range(threads_num)]
    for i, r in data.iterrows():
        id_url[i % threads_num].append((r['id'], r['homepage']))
    for i in id_url:
        t = threading.Thread(target=store_d_html_text_single,
        args=(i, prefix))
        threads.append(t)
    for i in threads:
        i.start()
    for i in threads:
        i.join()
    
def store_html_single_thread(data, prefix='./webpage/'):
    for i in data:
        store_html_text(i, prefix=prefix)

def store_multi_thread(data, threads=10, prefix='./webpage/'):
    """
    Execute task using threadings
    Data - standard DataFrame
    """
    num = len(data)
    chunk = math.ceil(num / threads)
    splited_data = [[] for i in range(threads)]
    for i, r in data.iterrows():
        splited_data[i % threads].append([r['id'], r['homepage']])
        
    print('Data split done')
    # multi thread
    threads = []
    for i in splited_data:
        t = threading.Thread(target=store_html_single_thread,
        args=(i, prefix))
        threads.append(t)
    for i in threads:
        i.start()
    for i in threads:
        i.join()
    


def get_pic_url(html, url):
    """
    Return the url of pics of given page text
    """
    try:
        pattern = re.compile(r'(?:src|SRC)(?: ?= ?)"([^<> \t\r\n]+?\.(jpg|png|gif)(?:\?[^<> \t\r\n]+)?)"')
        img_list = pattern.findall(html)
        root_url_p = re.compile(r'http[s]?:\/\/[^/]*\/')
        root_url = root_url_p.findall(url)
        img_list = list(set(list([i[0] for i in img_list])))
        # print(img_list)
        for i in range(len(img_list)):
            if not img_list[i].startswith('http'):        
                img_list[i] = urllib.parse.urljoin(url, img_list[i])
                
        return list(set(img_list))
    except Exception as e:
        print(e)
        return []

def get_pic_url2(html, url):
    try:
        root_url_p = re.compile(r'http[s]?:\/\/[^/]*\/')
        root_url = root_url_p.findall(url)
        bsObj = bs(html)
        img_list = set(list(filter(lambda x: x!= '', [i.get('src', '') for i in bsObj.findAll('img')])))
        temp = list(filter(lambda x: x!= '', [i.get('data-src', '') for i in bsObj.findAll('img')]))
        img_list = img_list | set(temp)
        temp = list(filter(lambda x: x!= '', [i.get('SRC', '') for i in bsObj.findAll('img')]))
        img_list = list(img_list | set(temp))
        for i in range(len(img_list)):
            if not img_list[i].startswith('http'):
                img_list[i] = urllib.parse.urljoin(url, img_list[i])
        return img_list
    except Exception as e:
        print(e.__traceback__())
        return []

    
def get_gender_name_single_page(url, use_proxy=True):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'}
    try:
        if use_proxy:
            proxies = ss_proxies
        else:
            proxies = None
        html = requests.get(url, headers=headers, timeout=5, proxies=proxies)
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

def check_request_validation(url, use_proxy=True):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'}
    try:
        if use_proxy:
            proxies = ss_proxies
        else:
            proxies = None
        res = requests.get(url, headers=headers, proxies=proxies)
        
        if res.status_code == 200:
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False

def download_image(url, path, use_proxy=False):
    """
    Download the image based on url to given path. 
    Output: True save successfully, False save unsuccessfully
    If the formate is not jpg, swith it to jpg then store it.
    """
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'}
    if use_proxy:
        proxies = ss_proxies
    else:
        proxies = None
    try:
        r = requests.get(url, headers=headers, stream=True, proxies=proxies, timeout=80)
        postfix = '.jpg'
        if r.status_code == 200:
            with open(path + postfix, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
            img = Image.open(path + postfix)
            if img.format != 'jpg':
                if img.mode in ['P', 'LA', 'I','RGBA']:
                    img = img.convert('RGB')
                img.save(path + postfix, 'JPEG')
            img.close()
            return True
        return False
    except Exception as e:
        print(e)
        if use_proxy:
            return False
        else:
            return download_image(url, path, use_proxy=True)

def single_thread_download_image(pics, succ, index):
    flag = 0
    succ = {}
    for i in pics:
        flag = 0
        succ[i] = []
        urls = pics[i]
        for url in urls:
            path = './head/%s-%s'%(i, flag)
            if download_image(url, path):
                flag += 1
                succ[i].append([path, url])
        if len(succ) % 10 ==0:
            with codecs.open('./temp/%s_succ.json'%(index), 'w', 'utf-8') as f:
                json.dump(succ, f)
            with open('./temp/%s_num.txt'%(index), 'a') as f:
                f.write(str(len(succ)))
    return succ


def multi_thread_download_image(pics, threads_num=10):
    """
    Pics - dict of {'id':[urls]}
    Output: save all possible images and return the list of images that stored successfully
    """
    num = len(pics)
    chunk = math.ceil(num / threads_num)
    threads = []
    ids = list(pics.keys())
    split_data = [{} for i in range(threads_num)]
    succ_sub = [{} for i in range(threads_num)]
    for i, pid in enumerate(ids):
        split_data[i % threads_num][pid] = pics[pid]
    for i in range(threads_num):
        t = my_thread(split_data[i], i)
        # t =  threading.Thread(target=single_thread_download_image, args=(split_data[i], succ_sub[i], i))
        threads.append(t)
    for i in threads:
        i.start()
    for i in threads:
        i.join()
    succ = {}
    for i in threads:
        succ.update(i.get_result())
    return succ

class my_thread(Thread):
    def __init__(self, data, i):
        Thread.__init__(self)
        self.data = data
        self.index = i
        

    def run(self):
        self.result = single_thread_download_image(self.data, {}, self.index)
        
    def get_result(self):
        return self.result
