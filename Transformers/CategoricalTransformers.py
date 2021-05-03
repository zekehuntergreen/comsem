# Primary work on implementing Transformers for ComSem was by Nate Kirsch
# Original code and dataset comes from Thomas McKenzie's repo
# https://github.com/tmckenzie2/ComsemNeuralNetwork/tree/9b1fd4db829b35bc6a3404f679d790306a1204e0/error-detection-neural-nets-master
#
# The code from Thomas's gihub was modified to try and use BERT, or in this case DistilBERT for Categorical analysis
# with this article being the primary guide:
# https://towardsdatascience.com/text-classification-with-hugging-face-transformers-in-tensorflow-2-without-tears-ee50e4f3e7ed
# 
# Additional potentially useful links:
# Why Turn into a Pickle
# https://towardsdatascience.com/why-turn-into-a-pickle-b45163007dac
# 
# HuggingFace Transformers docs
# https://huggingface.co/transformers/model_doc/bert.html
# https://huggingface.co/transformers/model_doc/distilbert.html#tfdistilbertforsequenceclassification
#
# Additional reading on Transformers model
# https://www.analyticsvidhya.com/blog/2019/09/demystifying-bert-groundbreaking-nlp-framework/
# https://analyticsindiamag.com/how-to-use-bert-transformer-for-grammar-checking/
# 

import csv
import matplotlib.pyplot as plt
import tensorflow as tf
import numpy as np

from scipy.spatial.distance import cdist
from keras.models import Sequential
from keras.layers import Dense, GRU, Embedding, Flatten
from keras.optimizers import Adam

from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras import backend as K

import ktrain
from ktrain import text
from transformers import BertModel, BertConfig


tf.compat.v1.disable_eager_execution()

# categories:
#   0 - correct
#   1 - sv agreement
#   2 - np error
#   3 - tense
categories = ['0', '1', '2', '3']

x_train_text = []
y_train_targ = []
x_test_text = []
y_test_targ = []

with open("combinetrainset.csv") as csvfile:
    readCSV = csv.reader(csvfile, delimiter=",")
    for row in readCSV:
        x_train_text.append(row[0])
        y_train_targ.append(row[3])

with open("combinetestset.csv") as csvfile:
    readCSV = csv.reader(csvfile, delimiter=",")
    for row in readCSV:
        x_test_text.append(row[0])
        y_test_targ.append(row[3])

MODEL_NAME = 'distilbert-base-uncased'

t = text.Transformer(MODEL_NAME, maxlen=500, class_names=categories)

trn = t.preprocess_train(x_train_text, y_train_targ)
val = t.preprocess_test(x_test_text, y_test_targ)

model = t.get_classifier()
learner = ktrain.get_learner(model, train_data=trn, val_data=val, batch_size=6)
# Everything up to this point works, meaning the data correctly gets pre-processed
# Below, the data fails to properly get processed due to "logits" and "labels"
# Not sure what about the data is causing it to fault.
learner.fit_onecycle(5e-5, 4)
learner.validate(class_names=t.get_classes())

# learner.lr_find(show_plot=True, max_epochs=1)

