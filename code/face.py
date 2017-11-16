#   import facenet libraires
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import re
import cv2
from scipy import misc
import tensorflow as tf
from align import detect_face


#   setup facenet parameters
minsize = 50 # minimum size of face
threshold = [ 0.6, 0.7, 0.7 ]  # three steps's threshold
factor = 0.709 # scale factor

#   fetch images
image_dir = './'

#   create a list of your images
images = ['./head/7.jpg']

class face_tool():

    def __init__(self):
        with tf.Graph().as_default():
            sess = tf.Session()
            with sess.as_default():
                self.pnet, self.rnet, self.onet = detect_face.create_mtcnn(
                sess, None)
    
    def detect(self, img_path):
        try:
            img = misc.imread(os.path.expanduser(img_path))
            bounding_boxes, _ = detect_face.detect_face(
                    img, minsize, self.pnet,
                    self.rnet, self.onet, threshold, factor)
            
            return len(bounding_boxes)
        except Exception as e:
            print(e)
            return 0

        #   for each box
        # for (x1, y1, x2, y2, acc) in bounding_boxes:
        #     w = x2-x1
        #     h = y2-y1
        #     #   plot the box using cv2
        #     cv2.rectangle(img,(int(x1),int(y1)),(int(x1+w),
        #         int(y1+h)),(255,0,0),2)
        #     print ('Accuracy score', acc)
        # #   show the boxed face
        # cv2.imshow('facenet is cool', img)
        # print('Press any key to advance to the next image')
        # cv2.waitKey(0)


def filter_pic(succ):
    """
    Filter pic
    Input: succ - dict of {'id':[[pic_path, pic_url], ... , [pic_path, pic_url]]}
    Output: ans - dict of pic_url that have at least one face {'id': [(pic_url, face_num), (pic_url, face_num)]}
    """
    model = face_tool()
    ans = {}
    for index, pid in enumerate(succ):
        if index % 100 == 0:
            print(index)
        ans[pid] = []
        for pic in succ[pid]:
            path, url = pic
            face_num = model.detect(path + '.jpg')
            if face_num > 0 :
                ans[pid].append((url, face_num))
    return ans

def check_name_in_url(name, url):
    """
    Sample: for the name of "Bai Li", \
    www.xx.com/li.jpg get 0.5
    www.xx.org/bai_li.jpg get 1
    www.xx.org.avatar.jpg get 0
    """
    score = 0
    for i in re.split(r'[ -]', name):
        if i.lower() in url.lower():
            score += 1
    return score / len(name.split(' '))
def neg_word_filter(ans):
    """
    ans -list of (pic_url, face_num)
    """
    p = re.compile(r'logo|banner')
    return list(filter(lambda x: p.findall(x[0].lower()) == 0, ans))

def face_num_filter(ans):
    """
    ans -list of (pic_url, face_num)
    """
    return list(filter(lambda x: x[1] == 1, ans))

def try_to_select(ans, name):
    """
    ans -list of (pic_url, face_num)
    """
    num = len(ans)
    filter_word = neg_word_filter(ans)
    if len(filter_word) == 1:
        return filter_word[0][0]
    filter_num = face_num_filter(ans)
    if len(filter_num) == 1:
        return filter_num[0][0]
    enhanced_filter = list(set(filter_num) & set(filter_word))
    if len(enhanced_filter) == 0:
        return ans[0][0]
    max = -1
    for i in enhanced_filter:
        score = check_name_in_url(name, i[0])
        if score > max:
            max = score
            res = i[0]
    return res

def predict_pic(data, ans):
    """
    Determine the pic that chosen to be as predict
    Input:
        data - standard DataFrame 
        ans - dict of pic_url that have at least one face {'id': [(pic_url, face_num), (pic_url, face_num)]}
    Ouput:
        the DataFrame after modify
    """
    for i, r in data.iterrows():
        head = ans[r['id']]
        if len(head) == 0:
            data.set_value(i, 'pic', '')
        elif len(head) == 1:
            data.set_value(i, 'pic', head[0][0])
        else:
            pic = try_to_select(head, r['name'])
            data.set_value(i, 'pic', pic)
    