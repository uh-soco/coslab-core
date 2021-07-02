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
print(len(image_ids.keys()))

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


#####################Accuracy metrics#########################
services = labels_per_service.keys()

similarity = collections.defaultdict(int)
max_change = collections.defaultdict(int)

for image, d in labels_per_image_service.items():
    for service1 in services:
        for service2 in services:
            ## compare services 1 and 2

            d1 = set(d[service1])
            d2 = set(d[service2])

            ## similarity
            sim = len(d1.intersection(d2))
            # print(sim)

            max_change[service1, service2] += min(len(d1), len(d2))
            similarity[service1, service2] += sim

for service1 in services:
    for service2 in services:

        accuracy = similarity[service1, service2] / max_change[service1, service2]

        print(service1, service2, accuracy)


# ###############Count Vectorizer method (Implementation for tags) ##############
# services = labels_per_service.keys()
# similarity = collections.defaultdict(int)
# vectorizer = CountVectorizer()

# for image, d in labels_per_image_service.items():
#     for service1 in services:
#         for service2 in services:
#             ## compare services 1 and 2
#             # print(image, d)
#             d1 = set(d[service1])
#             d2 = set(d[service2])

#             x = []
#             x2 = []
#             for tag in d1:
#                 x.append(str.lower(tag))
#             for tag in d2:
#                 x2.append(str.lower(tag))

#             x_str = ' '.join([str(elem) for elem in x])
#             x2_str = ' '.join([str(elem) for elem in x2])

#             alltags = [x_str, x2_str]
#             # print(alltags)
#             all_tags_to_vector = vectorizer.fit_transform(alltags)
#             # print(all_tags_to_vector)
#             tag_to_vector_v1 = all_tags_to_vector.toarray()[0].tolist()
#             tag_to_vector_v2 = all_tags_to_vector.toarray()[1].tolist()

#             ## distance of similarity
#             cosine = distance.cosine(tag_to_vector_v1, tag_to_vector_v2)
#             print("Similarity of three tags are equal to ", round((1 - cosine) * 100, 2), "%")


##########################Count vectorized for sentences#######################################3

ss1 = "Matti speaks at Think Corner, Helsinki"
ss2 = "Matti speaks to some random media at Helsinki"

def cosine_distance_countvectorizer_method(s1, s2):
    # tags to list
    alltags = [s1,s2]

    # text to vector
    vectorizer = CountVectorizer()
    all_tags_to_vector = vectorizer.fit_transform(alltags)
    tag_to_vector_v1 = all_tags_to_vector.toarray()[0].tolist()
    tag_to_vector_v2 = all_tags_to_vector.toarray()[1].tolist()

    # distance of similarity
    cosine = distance.cosine(tag_to_vector_v1, tag_to_vector_v2)
    print(
        "Similarity of three tags are equal to ", round((1 - cosine) * 100, 2), "%"
    )
    return cosine


cosine_distance_countvectorizer_method(ss1, ss2)


###########################Word2Vec for tags######################################################

list_azure = labels_per_service.get("azure_vision")
list_google = labels_per_service.get("google_vision")

def word2vec(tag):
    # count the characters in tag
    cw = Counter(tag)
    # precomputes a set of the different characters
    sw = set(cw)
    # precomputes the "length" of the word vector
    lw = math.sqrt(sum(c*c for c in cw.values()))

    return cw, sw, lw #retursn a tuple

def cosdis(v1, v2):
    common = v1[1].intersection(v2[1])
    return sum(v1[0][ch]*v2[0][ch] for ch in common)/v1[2]/v2[2]


threshold = 0.80     # if needed
for key in list_azure:
    for tag in list_google:
        try:
            # print(key)
            # print(word)
            res = cosdis(word2vec(tag), word2vec(key))
            # print(res)
            print("The cosine similarity between : {} and : {} is: {}".format(tag, key, res*100))
            # if res > threshold:
            #     print("Found a word with cosine distance > 80 : {} with original word: {}".format(word, key))
        except IndexError:
            pass


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
