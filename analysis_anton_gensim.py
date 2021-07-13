import gensim.downloader as api
from gensim.models.word2vec import Word2Vec
from gensim.models import KeyedVectors
import sqlite3
import collections
import numpy as np
from scipy import spatial 

# Lets read in our data
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

#################GLOVE####################
model = api.load("glove-wiki-gigaword-50") #choose more models from https://github.com/RaRe-Technologies/gensim-data

def preprocess(s):
    return [i.lower() for i in s.split()]

def get_vector(s):
    return np.sum(np.array([model[i] for i in preprocess(s)]), axis=0)

def cosine(t1, t2):
    return 1 - spatial.distance.cosine(t1, t2)


services = labels_per_service.keys()

best_similarities_glove = []
for image, d in labels_per_image_service.items(): 
    for service1 in services:
        for service2 in services:
            for tag1 in d[service1]:
                similarities_glove = []
                for tag2 in d[service2]:
                    try:
                        v1 = get_vector(tag1)
                        v2 = get_vector(tag2)
                        # print(v1,v2)
                        # print('azure tag:{} vs google tag:{} ->'.format(tag1,tag2),cosine(get_vector(tag1), get_vector(tag2)))
                        similarities_glove.append(cosine(v1,v2))
                        best_similarities_glove.append(max(similarities_glove))
                    except KeyError:
                        pass
                    
print("Glove: ", similarities_glove)
print()
print()

#################Word2Vec###################
filename = 'trained_vectordata/GoogleNews-vectors-negative300.bin'
w2v_model = KeyedVectors.load_word2vec_format(filename, binary=True)

best_similarities_w2v = []
for image, d in labels_per_image_service.items(): 
    for service1 in services:
        for service2 in services:
            for tag1 in d[service1]:
                similarities_w2v = []
                for tag2 in d[service2]:
                    try:
                        sim = w2v_model.similarity(tag1, tag2)
                        similarities_w2v.append(sim)
                        best_similarities_w2v.append(max(similarities_w2v))
                    except KeyError:
                        pass

print("Word2Vec: ", similarities_w2v)


#################Bert######################

# from sentence_transformers import SentenceTransformer, util
# model = SentenceTransformer('paraphrase-MiniLM-L12-v2')

# services = labels_per_service.keys()

# tags1 = []
# tags2 = []
# for image, d in labels_per_image_service.items():
#     for service1 in services:
#         for service2 in services:
#             for tag1 in d[service1]:
#                 for tag2 in d[service2]:
#                     tags1.append(tag1)
#                     tags2.append(tag2)

# #Compute embedding for both lists
# embeddings1 = model.encode(tags1, convert_to_tensor=True)
# embeddings2 = model.encode(tags2, convert_to_tensor=True)
# #Compute cosine-similarits
# cosine_scores = util.pytorch_cos_sim(embeddings1, embeddings2)
# #Output the pairs with their score
# for i in range(len(tags1)):
#     print("{} \t\t {} \t\t Score: {:.4f}".format(tags1[i], tags2[i], cosine_scores[i][i]))



