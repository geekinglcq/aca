# -*- coding: utf-8 -*-
import re
import json
import codecs
import http.client
import requests
import urllib
import base64
import readability
from bs4 import BeautifulSoup as bs
homepage_pos = [u'edu',u'faculty', u'id', u'staff',  u'detail', u'person', u'about', u'academic', u'teacher', u'list', \
                u'lish', u'homepages', u'researcher', u'team', u'teachers', u'member']
homepage_neg = [u'books', u'google', u'pdf', u'esc', u'scholar', u'netprofile', u'linkedin', u'researchgate', u'news',\
                u'article', u'[^n]wikipedia', u'gov', u'showrating', u'youtube', u'blots', u'citation']
stop_words = ['', 'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', "aren't", 'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', "can't", 'cannot', 'could', "couldn't", 'did', "didn't", 'do', 'does', "doesn't", 'doing', "don't", 'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had', "hadn't", 'has', "hasn't", 'have', "haven't", 'having', 'he', "he'd", "he'll", "he's", 'her', 'here', "here's", 'hers', 'herself', 'him', 'himself', 'his', 'how', "how's", 'i', "i'd", "i'll", "i'm", "i've", 'if', 'in', 'into', 'is', "isn't", 'it', "it's", 'its', 'itself', "let's", 'me', 'more', 'most', "mustn't", 'my', 'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', "shan't", 'she', "she'd", "she'll", "she's", 'should', "shouldn't", 'so', 'some', 'such', 'than', 'that', "that's", 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', "there's", 'these', 'they', "they'd", "they'll", "they're", "they've", 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', "wasn't", 'we', "we'd", "we'll", "we're", "we've", 'were', "weren't", 'what', "what's", 'when', "when's", 'where', "where's", 'which', 'while', 'who', "who's", 'whom', 'why', "why's", 'with', "won't", 'would', "wouldn't", 'you', "you'd", "you'll", "you're", "you've", 'your', 'yours', 'yourself', 'yourselves']

def load_title_tf():
    with codecs.open('./data/title_tf.json', 'r' ,'utf-8') as f:
        tf = json.load(f)
    return tf
def load_title_idf():
    with codecs.open('./data/title_idf.json', 'r' ,'utf-8') as f:
        idf = json.load(f)
    return idf
def load_content_idf():
    with codecs.open('./data/content_idf.json', 'r' ,'utf-8') as f:
        idf = json.load(f)
    return idf
def load_content_tf():
    with codecs.open('./data/content_tf.json', 'r' ,'utf-8') as f:
        tf = json.load(f)
    return tf

def check_email_validation(email):
    
    if len(email) >= 60:
        return False
    if email.endswith('.pdf') or email.endswith('.htm') or email.endswith('.jpg') \
    or email.endswith('.css') or email.endswith('Try') or email.endswith('.png'):
        return False
    if 'info' in email or 'communication' in email or 'example' in email or 'mathews'in email\
    or 'physics' in email or 'support' in email or 'engineering' in email or 'help' in email:
        return False
    return True

def select_email(email):
    pass

def email_getter(text):
    """
    Email format: xx@xx , xx SYMBOL_AT xx DOT xx DOT xx, xx [at] xx [dot] xx [dot] xx, xx at xx, xx (at) xx, xx AT xx, xx（AT）xx, xx[at]xx, xx (dot) xx (at) xx,
    xx<dot>xx<punkt><at><point>xx<dot>xx,  xxx_xx_xx (replace underscores by @ and .), xx [a] xx [d] xx, sunmeng x math [dot] pku [dot] edu [dot] cn [@/x],
    loris (at) cs (dot) wisc (another dot) edu, username=bdavie domain=mit.edu, 
    """
    #dot_p = r' ?[\[<\{\(](?:(?:[Dd][Oo][Tt])|(?:\.)|(?:another dot)|(?:d))[\]>\}\)] ?|[\[<\{\(](?:(?:[Dd][Oo][Tt])|(?:\.)|(?:another dot)|(?:d))[\]>\}\)]'
    dot_p = r'\.| dot | tod | \[dot\] | DOT | \(dot\) | \[-dot-\] | \(another dot\) |<dot>| \[d\] | \(DOT\) |\[dot\]|\(\.\)|\[.\]|\{dot\}| \. |\(dot\)| \{dot\} | \[dot\]| \[or\] |_DOT_| “dot” |DOT|_DOT_| -dot- '
    #'([-+\w]+(?:\.| dot [-+\w]+)*(@| AT | at | \[at\] |\[at\]| SYMBOL_AT |（AT）|<punkt><at><point>| \[a\] |\[at\]| \(at\) |\(at\)| @ )(?:[-\w]+\.| dot )+[a-zA-Z]{2,7})'
    at_p = r'@|\(@|&nbsp;\[at\]&nbsp;|&#64;|&#0064;| AT | at | \[-at-\] | ta | AT SPAMFREE | \[at\] |\[at\]| SYMBOL_AT | \[@\] |（AT）|<punkt><at><point>| \[a\] |\[at\]| \(at\) |\(at\)| @ | At | … | \'at\' |@nospam@|\[AT\]| \_at\_ | a t m a r k |<at>|_at_| \[AT\] | \(you can make the \"at\"\) |\(aτ\)| \/at\/ |\{at\}|AT|\.at\.|_AT_| \{at\} |_\(on\)_| \(a\) |<at> |--at--|\(a-t\)| “at” | \(here at\) |\[arrowbase\]| - at - | \"at\" | \(a\) |\(AT\)|@\.| -at- '
    #'([-+\w]+(?:(\.| dot | \[dot\] | DOT | \(dot\) | \(another dot\) |<dot>| \[d\] |)[-+\w]+)*(@| AT | at | \[at\] |\[at\]| SYMBOL_AT |（AT）|<punkt><at><point>| \[a\]|\[at\]| \(at\) |\(at\))(?:[-\w]+\.| dot | \[dot\] | DOT | \(dot\) | \(another dot\) |<dot>| \[d\] |)+[a-zA-Z]{2,7})'
    simple_p = re.compile(r'((?:\[)?[-+\w]+(?:(?:%s)[-+\w]+)*(?:\])?(?:%s)(?:\[)?(?:[-\w]+(?:%s))+[a-zA-Z]{2,7}(?:\])?)'%(dot_p, at_p, dot_p))
    p2 = re.compile(r'([-+\w]+(?: [dot] [-+\w]+)* [at] (?:[-\w]+ [dot] )+[a-zA-Z]{2,7})')
    email = simple_p.findall(text)
    email = list(filter(lambda x: check_email_validation(x), email))
    # email = list(filter(lambda x: not(x.endswith('.pdf') or x.endswith('.htm') or)))
    return email
    # if len(email) == 1:
    #     return email[0]
    # elif len(email) == 0:
    #     return ''
    # else:
    #     return select_email(email)

def get_clean_text(html):
    """
    generate clean text for given html
    """
    doc = readability.Document(html)
    try:
        doc._html()
        clean = doc.get_clean_html()
    except Exception as e:
        print(e)
        clean = html
    bsObj = bs(clean)
    return bsObj.get_text()

def head_phote_filter(pic_list):
    p = re.compile(r'mail|logo|facebook|twitter|banner|arrow|icon')
    return list(filter(lambda x : len(p.findall(x.lower())) == 0, pic_list))

def email_pic_filter(pic_list):
    p = re.compile(r'mail|address|contact|text')
    p2 = re.compile(r'cn_text|thu_text|footer|ico|logo|button|media_sharing')
    return list(filter(lambda x : (len(p.findall(x.lower())) != 0) and (len(p2.findall(x.lower())) == 0), pic_list))


def check_name_in_text(name, text):
    """
    Sample: for the name of "Bai Li", \
    # www.xx.com/li.jpg get 0.5
    www.xx.org/bai_li.jpg get 1
    www.xx.org.avatar.jpg get 0
    """
    score = 0
    short = ''
    for i in re.split(r'[ -]', name):
        short = i.lower().strip()[0] + short
        if i.lower() in text.lower():
            score += 1
    if short in text.lower() or short[::-1] in text.lower():
        score += 0.2
    print(short)
    return score / len(re.split(r'[ -]', name))
