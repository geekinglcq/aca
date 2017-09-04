# -*- coding: utf-8 -*-
import re
import json
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


def face_cog(pic_url):

    # Replace the subscription_key string value with your valid subscription key.
    subscription_key_set = ['156af6858fca46f4a156e44250ed1c59','19913dc0e75b428899562253e892dc0b']
    # NOTE: Free trial subscription keys are generated in the westcentralus region, so if you are using
    # a free trial subscription key, you should not need to change this region.
    uri_base = 'https://westcentralus.api.cognitive.microsoft.com'
    # Request parameters.
    params = {
        'returnFaceId': 'true',
        'returnFaceLandmarks': 'false',
        # 'returnFaceAttributes': 'age,gender,headPose,smile,facialHair,glasses,emotion,hair,makeup,occlusion,accessories,blur,exposure,noise',
        'returnFaceAttributes': 'age,gender',
    }


    for indx in range(len(subscription_key_set)):
        isExist = 0
        gender  = 0
        subscription_key = subscription_key_set[indx]
        headers = {
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': subscription_key,
        }
        
        try:
            # The URL of a JPEG image to analyze.
            body = {'url': pic_url}
            # Execute the REST API call and get the response.
            response = requests.request('POST', uri_base + '/face/v1.0/detect', json=body, data=None, headers=headers, params=params)
            parsed = json.loads(response.text)
            # 'data' contains the JSON data. The following formats the JSON data for display.
            if len(parsed)>0:
                # print len(parsed)
                isExist = 1
                # age = parsed[0]["faceAttributes"]["age"]
                gender = 1 if parsed[0]["faceAttributes"]["gender"] == 'male' else 0
            
            return ([isExist,gender])
        except Exception as e:
            print("[Errno {0}] {1}".format(e.errno, e.strerror))
            
            return None



def word_extract(str_url):
        # Replace the subscription_key string value with your valid subscription key.
    subscription_key_set = ['8e33aa488f1f42a281188680c3eab177','3ea78262e0cc4538ae5b002f44e2a3f7']
   
    for indx in range(len(subscription_key_set)):
        
        headers = {
            # Request headers
            'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key': subscription_key_set[indx],
        }

        params = urllib.parse.urlencode({
            # Request parameters
            'model': 'title',
            'text': str_url,
            # 'order': '{number}',
            'maxNumOfCandidatesReturned': 1,
        })

        try:
            conn = http.client.HTTPSConnection('westus.api.cognitive.microsoft.com')
            conn.request("POST", "/text/weblm/v1.0/breakIntoWords?%s" % params, "{body}", headers)
            response = conn.getresponse()
            data = response.read()
            data = data.decode('utf-8')
            data = eval(data)
            if 'candidates' in data.keys():
                words = data["candidates"][0]['words']
            elif 'statusCode' in data.keys():
                print (data["message"])
                continue
            conn.close()
            return words
        except Exception as e:
            print("[Errno {0}] {1}".format(e.errno, e.strerror))

def url_segmentation(url):
    """
    For given url, return a segmentation of this url based on 
    Web Language Model
    """
    pattern = re.compile(r'[\W]|https|http|www|_')
    url = pattern.sub('', url)
    words = word_extract(url)
    return words

def email_getter(text):
    """
    Email format: xx@xx , xx SYMBOL_AT xx DOT xx DOT xx, xx [at] xx [dot] xx [dot] xx, xx at xx, xx (at) xx, xx AT xx, xx（AT）xx, xx[at]xx, xx (dot) xx (at) xx,
    xx<dot>xx<punkt><at><point>xx<dot>xx,  xxx_xx_xx (replace underscores by @ and .), xx [a] xx [d] xx, sunmeng x math [dot] pku [dot] edu [dot] cn [@/x],
    loris (at) cs (dot) wisc (another dot) edu, username=bdavie domain=mit.edu, 
    """
    #dot_p = r' ?[\[<\{\(](?:(?:[Dd][Oo][Tt])|(?:\.)|(?:another dot)|(?:d))[\]>\}\)] ?|[\[<\{\(](?:(?:[Dd][Oo][Tt])|(?:\.)|(?:another dot)|(?:d))[\]>\}\)]'
    dot_p = r'\.| dot | \[dot\] | DOT | \(dot\) | \(another dot\) |<dot>| \[d\] | \(DOT\) |\[dot\]|\(\.\)|\[.\]|\{dot\}| \. |\(dot\)| \{dot\} | \[dot\]| \[or\] |_DOT_| “dot” |DOT|_DOT_| -dot- '
    #'([-+\w]+(?:\.| dot [-+\w]+)*(@| AT | at | \[at\] |\[at\]| SYMBOL_AT |（AT）|<punkt><at><point>| \[a\] |\[at\]| \(at\) |\(at\)| @ )(?:[-\w]+\.| dot )+[a-zA-Z]{2,7})'
    at_p = r'@| AT | at | \[at\] |\[at\]| SYMBOL_AT |（AT）|<punkt><at><point>| \[a\] |\[at\]| \(at\) |\(at\)| @ | At | … | \'at\' |@nospam@|\[AT\]| \_at\_ | a t m a r k |<at>|_at_| \[AT\] | \(you can make the \"at\"\) |\(aτ\)| \/at\/ |\{at\}|AT|\.at\.|_AT_| \{at\} |_\(on\)_| \(a\) |<at> |--at--|\(a-t\)| “at” | \(here at\) |\[arrowbase\]| - at - | \"at\" | \(a\) |\(AT\)|@\.| -at- '
    #'([-+\w]+(?:(\.| dot | \[dot\] | DOT | \(dot\) | \(another dot\) |<dot>| \[d\] |)[-+\w]+)*(@| AT | at | \[at\] |\[at\]| SYMBOL_AT |（AT）|<punkt><at><point>| \[a\]|\[at\]| \(at\) |\(at\))(?:[-\w]+\.| dot | \[dot\] | DOT | \(dot\) | \(another dot\) |<dot>| \[d\] |)+[a-zA-Z]{2,7})'
    simple_p = re.compile(r'((?:\[)?[-+\w]+(?:(?:%s)[-+\w]+)*(?:\])?(%s)(?:\[)?(?:[-\w]+(?:%s))+[a-zA-Z]{2,7}(?:\])?)'%(dot_p, at_p, dot_p))
    p2 = re.compile(r'([-+\w]+(?: [dot] [-+\w]+)* [at] (?:[-\w]+ [dot] )+[a-zA-Z]{2,7})')
    email = simple_p.findall(text)
    if len(email) > 0:
        return email[0][0]
    else:
        return ''

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