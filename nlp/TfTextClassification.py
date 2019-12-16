# coding=utf-8
# from https://tensorflow.google.cn/tutorials/keras/text_classification
from __future__ import absolute_import, division, print_function, unicode_literals

import tensorflow as tf
from tensorflow import keras

import numpy as np

print(tf.__version__)

imdb = keras.datasets.imdb

(train_data, train_labels), (test_data, test_labels) = imdb.load_data(num_words=1000)

print("Training entries: {}, labels: {}".format(len(train_data), len(train_labels)))


