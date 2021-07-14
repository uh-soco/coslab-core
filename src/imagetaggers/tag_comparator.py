import gensim.downloader as api
from gensim.models.word2vec import Word2Vec
from gensim.models import KeyedVectors
import sqlite3
import collections
import numpy as np
from scipy import spatial

#Load in models

#################GLOVE####################
model = api.load("glove-wiki-gigaword-50") #choose more models from https://github.com/RaRe-Technologies/gensim-data

# #################Word2Vec###################
filename = 'trained_vectordata/GoogleNews-vectors-negative300.bin'
w2v_model = KeyedVectors.load_word2vec_format(filename, binary=True)

#################Bert######################
from sentence_transformers import SentenceTransformer, util
bert_model = SentenceTransformer('paraphrase-MiniLM-L12-v2')

#Some functions for Glove

def preprocess(s):
    return [i.lower() for i in s.split()]

def get_vector(s):
    return np.sum(np.array([model[i] for i in preprocess(s)]), axis=0)

def cosine(t1, t2):
    return 1 - spatial.distance.cosine(t1, t2)

#Comparator template
def identity_comparator( tag1, tag2 ):
    if tag1 == tag2:
        return 1
    else:
        return 0

def glove_comparator( tag1, tag2 ):
    #vectorize tags
    v1 = get_vector(tag1)
    v2 = get_vector(tag2)

    if tag1 == tag2:
        return 1
    else:
        return cosine(v1,v2)


def w2v_comparator( tag1, tag2 ):
    if tag1 == tag2:
        return 1
    else:
        return w2v_model.similarity(tag1, tag2)

def bert_comparator( tag1, tag2 ):
    embedding1 = bert_model.encode(tag1, convert_to_tensor=True)
    embedding2 = bert_model.encode(tag2, convert_to_tensor=True)
    cosine_scores = util.pytorch_cos_sim(embedding1,embedding2)

    if tag1 == tag2:
        return 1
    else:
        return cosine_scores

def compare_tags( results, service1, service2, comparator = identity_comparator ):

    images = results.labels ## dict of dicts

    for image in images:
        tags1 = image[ service1 ]
        tags2 = image[ service2 ]

        best_similarities = {}
        for tag1 in tags1:
            similarities = []
            for tag2 in tags2:
                similarity = comparator( tag1, tag2 )
                similarities.append( similarity )
            best_similarities[ tag1 ] = max( similarities )
            
    return best_similarities
