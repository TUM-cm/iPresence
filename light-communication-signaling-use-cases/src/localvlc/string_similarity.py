import numpy
import jellyfish
from difflib import SequenceMatcher

# https://github.com/jamesturk/jellyfish
# http://blog.christianperone.com/2013/09/machine-learning-cosine-similarity-for-vector-space-models-part-iii/
#from sklearn.feature_extraction.text import TfidfVectorizer
#from sklearn.metrics.pairwise import cosine_similarity

def levenshtein_distance(query, template):
    return jellyfish.levenshtein_distance(query, template)

def damerau_levenshtein_distance(query, template):
    return jellyfish.damerau_levenshtein_distance(query, template)

def hamming_distance(query, template):
    return jellyfish.hamming_distance(query, template)

def jaro_similarity(query, template):
    return 1.0 - jellyfish.jaro_distance(query, template)

def jaro_winkler_similarity(query, template):
    return 1.0 - jellyfish.jaro_winkler(query, template)

def match_rating(query, template):
    return jellyfish.match_rating_comparison(query, template)

def sequence_matcher_similarity(query, template):
    return 1.0 - SequenceMatcher(None, query, template).ratio()

# def cosine_matrix(query, template):
#     query = [x[0] for x in query] # flatten
#     data = [template] + query
#     tfidf_vectorizer = TfidfVectorizer() 
#     tfidf_matrix = tfidf_vectorizer.fit_transform(data)
#     return cosine_similarity(tfidf_matrix[0], tfidf_matrix[1:])[0]
# 
# def cosine(query, template):
#     data = [query] + [template]
#     tfidf_vectorizer = TfidfVectorizer()
#     tfidf_matrix = tfidf_vectorizer.fit_transform(data)
#     return cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])
# 
# def test_cosine(query, template):
#     result = numpy.empty(len(query))
#     for i, entry in enumerate(query):
#         result[i] = cosine(entry[0], template)
#     print len(result)
#     print result
#     result = cosine_matrix(query, template)
#     print len(result)
#     print result

def test_string_similarity(query, template):
    func = [levenshtein_distance, damerau_levenshtein_distance,
            hamming_distance, jaro_similarity, jaro_winkler_similarity,
            sequence_matcher_similarity]
    query = [x[0] for x in query] # flatten
    for f in func:
        print(f.__name__)
        result = numpy.empty(len(query))
        for i, entry in enumerate(query):
            result[i] = f(entry, template)
        idx = numpy.where(result>0)
        print(result[idx])
        print(numpy.array(query)[idx])
    