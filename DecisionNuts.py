import sys
from subprocess import call
import numpy as np
import tensorflow as tf
import cv2
import tensorflow.python.platform
from types import *

class DecisionTest:

    IMAGE_SIZE = 56
    NUM_CLASSES = 3
    
    def inference(self, images_placeholder, keep_prob):

        NEURONS_NUM = 14
        
        def weight_variable(shape):
          initial = tf.truncated_normal(shape, stddev=0.1)
          return tf.Variable(initial)

        def bias_variable(shape):
          initial = tf.constant(0.1, shape=shape)
          return tf.Variable(initial)

        def conv2d(x, W):
          return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')

        def max_pool_2x2(x):
          return tf.nn.max_pool(x, ksize=[1, 2, 2, 1],
                                strides=[1, 2, 2, 1], padding='SAME')

        x_image = tf.reshape(images_placeholder, [-1, self.IMAGE_SIZE, self.IMAGE_SIZE, 3])

        with tf.name_scope('conv1') as scope:
            W_conv1 = weight_variable([5, 5, 3, 32])
            b_conv1 = bias_variable([32])
            h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)
        
        with tf.name_scope('pool1') as scope:
            h_pool1 = max_pool_2x2(h_conv1)

        with tf.name_scope('conv2') as scope:
            W_conv2 = weight_variable([5, 5, 32, 64])
            b_conv2 = bias_variable([64])
            h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)

        with tf.name_scope('pool2') as scope:
            h_pool2 = max_pool_2x2(h_conv2)

        with tf.name_scope('fc1') as scope:
            W_fc1 = weight_variable([NEURONS_NUM * NEURONS_NUM * 64, 1024])
            b_fc1 = bias_variable([1024])
            h_pool2_flat = tf.reshape(h_pool2, [-1, NEURONS_NUM * NEURONS_NUM * 64])
            h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)
            h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)

        with tf.name_scope('fc2') as scope:
            W_fc2 = weight_variable([1024, self.NUM_CLASSES])
            b_fc2 = bias_variable([self.NUM_CLASSES])

        with tf.name_scope('softmax') as scope:
            y_conv=tf.nn.softmax(tf.matmul(h_fc1_drop, W_fc2) + b_fc2)

        return y_conv    

    def GetTypeOfNuts(self, img, logits, images_placeholder, keep_prob, sess):

        test_image = []
       
        img = cv2.resize(img, (self.IMAGE_SIZE, self.IMAGE_SIZE))
        test_image.append(img.flatten().astype(np.float32)/255.0)

        test_image = np.asarray(test_image)

        print(len(test_image))
        for i in range(len(test_image)):
            pr = logits.eval(feed_dict={ 
                images_placeholder: [test_image[i]],
                keep_prob: 1.0 })[0]
            pred = np.argmax(pr)
            answer = "almond"
            if int(pred) is 1: answer = "peanut"
            if int(pred) is 2: answer = "kurumi"
            print (answer)
        
if __name__ == '__main__':
    
    cls = DecisionTest()
    IMAGE_SIZE = 56
    IMAGE_PIXELS = IMAGE_SIZE*IMAGE_SIZE*3
    NUM_CLASSES = 3
    
    images_placeholder = tf.placeholder("float", shape=(None, IMAGE_PIXELS))
    labels_placeholder = tf.placeholder("float", shape=(None, NUM_CLASSES))
    keep_prob = tf.placeholder("float")
    logits = cls.inference(images_placeholder, keep_prob)

    sess = tf.InteractiveSession()
    sess.run(tf.global_variables_initializer())
    
    saver = tf.train.Saver()
    saver.restore(sess, "./models/model.ckpt")
        
    print(logits)
    print(images_placeholder)
    print(keep_prob)
    
    imgPath = "/home/pi/robot/pic/t_1001.jpg"
    cls.GetTypeOfNuts(imgPath, logits,images_placeholder, keep_prob)
    
    imgPath = "/home/pi/robot/pic/t_1002.jpg"
    cls.GetTypeOfNuts(imgPath, logits, images_placeholder, keep_prob)
    
   
