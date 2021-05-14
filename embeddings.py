import datetime
import numpy as np
import os
import gensim
from gensim.test.utils import datapath, get_tmpfile
from gensim.scripts.glove2word2vec import glove2word2vec

print("gensim Version: %s" % (gensim.__version__))


class WordEmbedding:
    def __init__(self, verbose=0):
        self.verbose = verbose
        self.model = {}

    def convert(self, source, ipnut_file_path, output_file_path):
        if source == "glove":
            input_file = datapath(ipnut_file_path)
            output_file = get_tmpfile(output_file_path)
            glove2word2vec(input_file, output_file)
        elif source == "word2vec":
            pass
        else:
            raise ValueError("Possible value of source are glove or word2vec")

    def load(self, source, file_path):
        print(datetime.datetime.now(), "start: loading", source)
        if source == "glove":
            self.model[source] = gensim.models.KeyedVectors.load_word2vec_format(
                file_path
            )
        elif source == "word2vec":
            self.model[source] = gensim.models.KeyedVectors.load_word2vec_format(
                file_path, binary=True
            )
        else:
            raise ValueError("Possible value of source are glove or word2vec")

        print(datetime.datetime.now(), "end: loading", source)

        return self

    def get_model(self, source):
        if source not in ["glove", "word2vec"]:
            raise ValueError("Possible value of source are glove or word2vec")

        return self.model[source]

    def get_words(self, source, size=None):
        if source not in ["glove", "word2vec"]:
            raise ValueError("Possible value of source are glove or word2vec")

        if source in ["glove", "word2vec"]:
            if size is None:
                return [w for w in self.get_model(source=source).vocab]
            elif size is None:
                return [w for w in self.get_model(source=source).vocab]
            else:
                results = []
                for i, word in enumerate(self.get_model(source=source).vocab):
                    if i >= size:
                        break

                    results.append(word)
                return results

        return Exception("Unexpected flow")

    def get_dimension(self, source):
        if source not in ["glove", "word2vec"]:
            raise ValueError("Possible value of source are glove or word2vec")

        if source in ["glove", "word2vec"]:
            return self.get_model(source=source).vectors[0].shape[0]

    def get_vectors(self, source, words=None):
        if source not in ["glove", "word2vec"]:
            raise ValueError("Possible value of source are glove or word2vec")

        if source in ["glove", "word2vec"]:
            if words is None:
                words = self.get_words(source=source)

            embedding = np.empty(
                (len(words), self.get_dimension(source=source)), dtype=np.float32
            )
            for i, word in enumerate(words):
                embedding[i] = self.get_vector(source=source, word=word)

            return embedding

        return Exception("Unexpected flow")

    def get_vector(self, source, word, oov=None):
        if source not in ["glove", "word2vec"]:
            raise ValueError("Possible value of source are glove or word2vec")

        if source not in self.model:
            raise ValueError("Did not load %s model yet" % source)

        try:
            return self.model[source][word]
        except KeyError as e:
            raise

    def get_synonym(self, source, word, oov=None):
        if source not in ["glove", "word2vec"]:
            raise ValueError("Possible value of source are glove or word2vec")

        if source not in self.model:
            raise ValueError("Did not load %s model yet" % source)

        try:
            return self.model[source].most_similar(positive=word, topn=5)
        except KeyError as e:
            raise

    def which_distance_between_two_words(self, source, word1, word2, oov=None):
        if source not in ["glove", "word2vec"]:
            raise ValueError("Possible value of source are glove or word2vec")

        if source not in self.model:
            raise ValueError("Did not load %s model yet" % source)

        try:
            return self.model[source].similarity(word1, word2)
        except KeyError as e:
            raise


# We may need to convert text file (downloaed from GloVe website) to vector format


downloaded_glove_file_path = (
    "/media/antonberg/Origenes/Datasets/glove.twitter.27B/glove.twitter.27B.100d.txt"
)

glove_file_path = (
    "/media/antonberg/Origenes/Datasets/glove.twitter.27B/glove.twitter.27B.100d.vec"
)
word2vec_file_path = (
    "/media/antonberg/Origenes/Datasets/GoogleNews-vectors-negative300.bin"
)

word_embedding = WordEmbedding()

word_embedding.convert(
    source="glove",
    ipnut_file_path=downloaded_glove_file_path,
    output_file_path=glove_file_path,
)

word_embedding.load(source="word2vec", file_path=word2vec_file_path)
word_embedding.load(source="glove", file_path=glove_file_path)


# Get vectors
for source in ["glove", "word2vec"]:
    print("Source: %s" % (source))
    print(word_embedding.get_vector(source=source, word="fail"))
    print(len(word_embedding.get_vector(source=source, word="fail")))

# Get most similar words
for source in ["glove", "word2vec"]:
    print("Source: %s" % (source))
    print(word_embedding.get_synonym(source=source, word="fail"))

# Get distance
w1 = "king"
w2 = "queen"

for source in ["glove", "word2vec"]:
    print("Source: %s" % (source))
    print(
        word_embedding.which_distance_between_two_words(
            source=source, word1=w1, word2=w2
        )
    )
