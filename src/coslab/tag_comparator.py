from sklearn.metrics.pairwise import cosine_similarity
from gensim.models.word2vec import Word2Vec
from scipy import spatial
from transformers import BertTokenizer, BertModel
from gensim.models import KeyedVectors
import gensim.downloader as gensimdl
from itertools import permutations
import collections
import sqlite3

import numpy as np

# Comparator template


def identity_comparator(tag1, tag2):
    return float(tag1 == tag2)

# Glove comparator

# choose more models from https://github.com/RaRe-Technologies/gensim-data
glove_model = gensimdl.load("glove-wiki-gigaword-50")

def glove_comparator(tag1, tag2):
    try:
        return glove_model.similarity(tag1, tag2)
    except KeyError:
        return -1 

# Word2Vec comparator

w2v_model = gensimdl.load("word2vec-google-news-300")

def w2v_comparator(tag1, tag2):
    try:
        return w2v_model.similarity(tag1, tag2)
    except KeyError:
        return -1

# # Bert comparator


# ## todo: why this pretrained model
# bert_tokenizer = BertTokenizer.from_pretrained(
#     'sentence-transformers/paraphrase-MiniLM-L6-v2')
# bert_model = BertModel.from_pretrained(
#     'sentence-transformers/paraphrase-MiniLM-L6-v2')


# def bert_comparator(tag1, tag2):

#     outputs = bert_model(**bert_tokenizer(tag1, return_tensors="pt"))
#     word_vect1 = outputs.pooler_output.detach().numpy()

#     outputs = bert_model(**bert_tokenizer(tag2, return_tensors="pt"))
#     word_vect2 = outputs.pooler_output.detach().numpy()

#     return float(cosine_similarity(word_vect1, word_vect2))

## Common comparing functionalities


def compare_data(data, comparator=identity_comparator):
    images = data.labels

    services = list(list(images.values())[0].keys())
    crosses = permutations(services, 2)

    results = {}

    for services in crosses:
        results[services] = compare_tags(
            data, services[0], services[1], comparator)

    return results


def compare_tags(results, service1, service2, comparator=identity_comparator):

    images = results.labels  # dict of dicts

    similarities = collections.defaultdict(list)

    for name, image in images.items():

        tags1 = image[service1]
        tags2 = image[service2]

        for tag1 in tags1:
            tag1 = tag1['label'].lower()
            tag_similarities = [-1]  # set a default value to make life easier
            for tag2 in tags2:
                tag2 = tag2['label'].lower()
                similarity = comparator( tag1, tag2 )
                tag_similarities.append( similarity )
            similarities[tag1].append( max( tag_similarities ) )

    return similarities

def compare_image_tags(results, image, label, service2, comparator=identity_comparator):

    image = results.labels[ image ]

    tags = image[service2]

    tag_similarities = [-1]  # set a default value to make life easier
    for tag2 in tags:
        tag2 = tag2['label'].lower()
        similarity = comparator( label, tag2 )
        tag_similarities.append( similarity )
    
    return max( tag_similarities )