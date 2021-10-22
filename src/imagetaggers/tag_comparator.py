import gensim.downloader as api
from gensim.models.word2vec import Word2Vec
from gensim.models import KeyedVectors
import sqlite3
import collections
import numpy as np
from scipy import spatial


# load models

glove_model = api.load("glove-wiki-gigaword-50") #choose more models from https://github.com/RaRe-Technologies/gensim-data

## TODO: make this right and working with real package structure as well
import os
datapath = os.path.dirname(os.path.realpath(__file__)) + '/../../trained_vectordata/'

filename = 'GoogleNews-vectors-negative300.bin'

w2v_model = KeyedVectors.load_word2vec_format( datapath + filename, binary=True)

#################Bert######################
#from sentence_transformers import SentenceTransformer, util
#bert_model = SentenceTransformer('paraphrase-MiniLM-L12-v2')

# Comparator template
def identity_comparator( tag1, tag2 ):
    return float( tag1 == tag2 )

# Glove comparator

def _preprocess(s):
    return [i.lower() for i in s.split()]

def _get_vector(s):
    return np.sum(np.array([glove_model[i] for i in _preprocess(s)]), axis=0)

def glove_comparator( tag1, tag2 ):
    #vectorize tags
    v1 = _get_vector(tag1)
    v2 = _get_vector(tag2)

    return 1 - spatial.distance.cosine(v1, v2)

# Word2Vec comparator

def w2v_comparator( tag1, tag2 ):
    return w2v_model.similarity(tag1, tag2)

# Bert comparator

def bert_comparator( tag1, tag2 ):
    embedding1 = bert_model.encode(tag1, convert_to_tensor=True)
    embedding2 = bert_model.encode(tag2, convert_to_tensor=True)
    cosine_scores = util.pytorch_cos_sim(embedding1,embedding2)

    return cosine_scores

## Common comparing functionalities

def compare_tags( results, service1, service2, comparator = identity_comparator ):

    images = results.labels ## dict of dicts

    for name, image in images.items():
        tags1 = image[ service1 ]
        tags2 = image[ service2 ]

        best_similarities = {}
        for tag1 in tags1:
            tag1 = tag1['label']
            similarities = [ -1 ] ## set a default value to make life easier
            for tag2 in tags2:
                tag2 = tag2['label']
                similarity = comparator( tag1, tag2 )
                similarities.append( similarity )
            best_similarities[ tag1 ] = max( similarities )

    return best_similarities
