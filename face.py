#   import facenet libraires
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from scipy import misc
import tensorflow as tf
import os
from facenet.align import detect_face

#  import other libraries
import cv2

#   setup facenet parameters
gpu_memory_fraction = 1.0
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
    
    def judge(self, img_path):
        try:
            img = misc.imread(os.path.expanduser(img_path))
            bounding_boxes, _ = detect_face.detect_face(
                    img, minsize, self.pnet,
                    self.rnet, self.onet, threshold, factor)
            # print(bounding_boxes)
            # print(_)
            return len(bounding_boxes)
        except Exception as e:
            print(e)
            return 0
        # if len(bounding_boxes) != 0:
        #     return True

        # #   for each box
        # for (x1, y1, x2, y2, acc) in bounding_boxes:
        #     w = x2-x1
        #     h = y2-y1
        #     #   plot the box using cv2
        #     cv2.rectangle(img,(int(x1),int(y1)),(int(x1+w),
        #         int(y1+h)),(255,0,0),2)
        #     print ('Accuracy score', acc)
        # #   save a new file with the boxed face
        # cv2.imwrite('faceBoxed'+i, img)
        # #   show the boxed face
        # cv2.imshow('facenet is cool', img)
        # print('Press any key to advance to the next image')
        # cv2.waitKey(0)