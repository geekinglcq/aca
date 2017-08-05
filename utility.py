# -*- coding: utf-8 -*-
import json
import http.client
import requests
import urllib
import base64

###############################################
#### Input picture url, return (bool_isExist , bool_gender)(1:male) ###
###############################################

def face_cog(pic_url):

    # Replace the subscription_key string value with your valid subscription key.
    subscription_key_set = ['156af6858fca46f4a156e44250ed1c59','19913dc0e75b428899562253e892dc0b']

    # Replace or verify the region.
    #
    # You must use the same region in your REST API call as you used to obtain your subscription keys.
    # For example, if you obtained your subscription keys from the westus region, replace 
    # "westcentralus" in the URI below with "westus".
    #
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

        