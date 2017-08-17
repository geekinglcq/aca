# -*- coding: utf-8 -*-
import re
import json
import http.client
import requests
import urllib
import base64

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
    pattern = re.compile(u'[\W]|https|http|www|_')
    url = pattern.sub('', url)
    words = word_extract(url)
    return words
