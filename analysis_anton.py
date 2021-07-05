from typing import Counter
from nltk.internals import ElementWrapper
import numpy as np
import math
import re
from nltk.corpus import stopwords
import pandas as pd
from pandas.io.sql import read_sql
import scipy
from scipy import spatial
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer
from scipy.spatial import distance
import sqlite3
from sqlite3 import Error
import collections
import itertools

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

conn = sqlite3.connect("run.db")
conn.row_factory = dict_factory
db = conn.cursor()

image_ids = collections.defaultdict(list)

for result in db.execute("select * from results"):
    image_ids[result["image"]].append(result["id"])
# print(len(image_ids.keys()))

labels_per_service = collections.defaultdict(list)
labels_per_image_service = collections.defaultdict(
    lambda: collections.defaultdict(list)
)

for image, ids in image_ids.items():
    # print(", ".join(map(str, ids)))
    for result in db.execute(
        "SELECT (SELECT service FROM results where id==label) as service, * FROM results WHERE id in (%s)"
        % (", ".join(map(str, ids)))
    ):
        labels_per_service[result["service"]].append(result["label"])
        labels_per_image_service[image][result["service"]].append(result["label"])

# print(labels_per_image_service.keys())


###########################Word2Vec for tags######################################################
def word2vec(tag):
    # count the characters in tag
    cw = Counter(tag)
    # precomputes a set of the different characters
    sw = set(cw)
    # precomputes the "length" of the word vector
    lw = math.sqrt(sum(c*c for c in cw.values()))
    return cw, sw, lw #returns a tuple

def cosdis(v1, v2):
    common = v1[1].intersection(v2[1])
    return sum(v1[0][ch]*v2[0][ch] for ch in common)/v1[2]/v2[2]

a_azure = labels_per_service.get("azure_vision")
b_google = labels_per_service.get("google_vision")
c_amazon = labels_per_service.get("aws")

best_similarities = []
for tag1 in a_azure:
    for tag2 in b_google:
        similarities = []
        try:
            similarities.append(cosdis(word2vec(tag1), word2vec(tag2)))
            cos = cosdis(word2vec(tag1), word2vec(tag2))
            print("The cosine similarity between : {} and : {} is: {}".format(tag1, tag2, cos*100))
            
        except IndexError:
            pass
        best_similarities.append(max(similarities))

print(best_similarities)
           

###################Glove Embedding####################

# gloveFile = "trained_vectordata/glove.twitter.27B/glove.twitter.27B.50d.txt"


# def loadGloveModel(gloveFile):
#     print("Loading Glove Model")
#     with open(gloveFile, encoding="utf8") as f:
#         content = f.readlines()
#     model = {}
#     for line in content:
#         splitLine = line.split()
#         word = splitLine[0]
#         embedding = np.array([float(val) for val in splitLine[1:]])
#         model[word] = embedding
#     print("Done.", len(model), " words loaded!")
#     return model


# def preprocess(raw_text):
#     # keep only words
#     letters_only_text = re.sub("[^a-zA-Z]", " ", raw_text)

#     # convert to lower case and split
#     words = letters_only_text.lower().split()

#     # remove stopwords
#     stopword_set = set(stopwords.words("english"))
#     cleaned_words = list(set([w for w in words if w not in stopword_set]))

#     return cleaned_words


# def cosine_distance_between_two_words(word1, word2):
#     return 1 - scipy.spatial.distance.cosine(model[word1], model[word2])


# def calculate_heat_matrix_for_two_sentences(s1, s2):
#     s1 = preprocess(s1)
#     s2 = preprocess(s2)
#     result_list = [
#         [cosine_distance_between_two_words(word1, word2) for word2 in s2]
#         for word1 in s1
#     ]
#     result_df = pd.DataFrame(result_list)
#     result_df.columns = s2
#     result_df.index = s1
#     return result_df


# def cosine_distance_wordembedding_method(s1, s2):
#     vector_1 = np.mean([model[word] for word in preprocess(s1)], axis=0)
#     vector_2 = np.mean([model[word] for word in preprocess(s2)], axis=0)
#     cosine = scipy.spatial.distance.cosine(vector_1, vector_2)
#     print(
#         "Word Embedding method with a cosine distance asses that our two sentences are similar to",
#         round((1 - cosine) * 100, 2),
#         "%",
#     )


# def heat_map_matrix_between_two_sentences(s1, s2):
#     df = calculate_heat_matrix_for_two_sentences(s1, s2)

#     fig, ax = plt.subplots(figsize=(5, 5))
#     ax_blue = sns.heatmap(df, cmap="YlGnBu")
#     # ax_red = sns.heatmap(df)
#     print(cosine_distance_wordembedding_method(s1, s2))
#     return ax_blue


# ss1 = "Matti speaks at Think Corner, Helsinki"
# ss2 = "Matti speaks to some random media at Helsinki"

# model = loadGloveModel(gloveFile)
# heat_map_matrix_between_two_sentences(ss1, ss2)
