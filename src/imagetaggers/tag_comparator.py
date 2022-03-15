from itertools import permutations
import collections
import sqlite3

import numpy as np


## TODO: make this right and working with real package structure as well

import os
datapath = os.path.dirname(os.path.realpath(__file__)) + '/../../trained_vectordata/'

# Comparator template

def identity_comparator( tag1, tag2 ):
    return float( tag1 == tag2 )

# Glove comparator

from scipy import spatial
import gensim.downloader as gensimdl

glove_model = gensimdl.load("glove-wiki-gigaword-50") #choose more models from https://github.com/RaRe-Technologies/gensim-data

def _preprocess(s):
    return [i.lower() for i in s.split()]

def _get_vector(s):
    return np.sum(np.array([glove_model[i] for i in _preprocess(s)]), axis=0)

def glove_comparator( tag1, tag2 ):
    #vectorize tags
    try:
        v1 = _get_vector(tag1)
        v2 = _get_vector(tag2)

        return 1 - spatial.distance.cosine(v1, v2)
    except KeyError:
        return -1

# Word2Vec comparator

from gensim.models.word2vec import Word2Vec
from gensim.models import KeyedVectors

w2v_model = KeyedVectors.load_word2vec_format( datapath + 'GoogleNews-vectors-negative300.bin', binary=True)

def w2v_comparator( tag1, tag2 ):
    try:
        return w2v_model.similarity(tag1, tag2)
    except KeyError:
        return -1

# Bert comparator

from sklearn.metrics.pairwise import cosine_similarity

from sentence_transformers import SentenceTransformer, util
bert_model = SentenceTransformer('paraphrase-MiniLM-L12-v2')

def bert_comparator( tag1, tag2 ):

    embeddings = bert_model.encode( [tag1, tag2] )
    cosine_scores = cosine_similarity( embeddings )

    return cosine_scores[0,1]

## Common comparing functionalities

def compare_data( data, comparator = identity_comparator ):
    images = data.labels

    services = list( list( images.values() )[0].keys() )
    crosses = permutations( services, 2 )

    results = {}

    for services in crosses:
        results[ services ] = compare_tags( data, services[0], services[1], comparator )

    return results


def compare_tags( results, service1, service2, comparator = identity_comparator ):

    images = results.labels ## dict of dicts

    best_similarities = {}

    for name, image in images.items():

        tags1 = image[ service1 ]
        tags2 = image[ service2 ]

        for tag1 in tags1:
            tag1 = tag1['label']
            similarities = [ -1 ] ## set a default value to make life easier
            for tag2 in tags2:
                tag2 = tag2['label']
                similarity = comparator( tag1, tag2 )
                similarities.append( similarity )
            best_similarities[ tag1 ] = max( similarities )

    return best_similarities
