import re
import logging
import sqlite3

import nltk
from nltk.stem.snowball import SnowballStemmer
from textblob import TextBlob
import json
from model import BibleVerse
from nltk.stem import WordNetLemmatizer


def tokenize_and_stem(text, stemmer=SnowballStemmer("english")):
    """
    tokenize and stem the passed text
    :param text:
    :return:
    """
    # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
    tokens = [word.strip() for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
    filtered_tokens = []
    # filter out any tokens not containing letters (e.g., numeric tokens, raw punctuation)
    for token in tokens:
        if re.search('[a-zA-Z]', token):
            filtered_tokens.append(token)

    if stemmer is not None:
        #stems = [stemmer.stem(t) for t in filtered_tokens]
        stems = [stemmer.lemmatize(t) for t in filtered_tokens]
        return stems
    else:
        return filtered_tokens


def remove_stopwords(tokenized_text, stopwords=[]):
    """
    For every word in sentence, lower and reduce 
    """
    return [word for word in tokenized_text if word.lower() not in stopwords]


def filter_parts_of_speech(sentence, part_of_speech_to_keep=None):
    if part_of_speech_to_keep is None:
        return sentence
    else:
        sentence_blob = TextBlob(sentence)
        result = " ".join([res[0] for res in sentence_blob.tags if res[1] in part_of_speech_to_keep])

        return result


def save_to_json(value_dict, path):
    with open(path, 'w') as fp:
        json.dump(value_dict, fp)


class Normalizer(object):
    def __init__(self, stem=False, stop_words=None,
                 filter_parts_of_speech=False, min_word_length=1
                 , lower_case=False
                 ):
        self.stem = stem

        self.filter_parts_of_speech = filter_parts_of_speech
        self.min_word_length = min_word_length

        self.lower_case = lower_case

        # valid_pos= ["FW","NN","NNS","NNP","NNPS","VB","VBZ","VBP","VBD","VBN","VBG"]

        valid_pos = ["FW", "NN", "NNS", "NNP", "NNPS"]

        with open(stop_words) as temp_file:
            self.stopwords = [line.rstrip('\n') for line in temp_file]
            self.stopwords = set(self.stopwords)

        valid_pos_set = set(valid_pos)

        if self.stem:
            #self.stemmer = SnowballStemmer("english")
            self.stemmer=WordNetLemmatizer()
        else:
            self.stemmer = None

        if filter_parts_of_speech:
            self.valid_pos_set = valid_pos_set
        else:
            self.valid_pos_set = None

    def process(self, document):

        if self.valid_pos_set:
            document = filter_parts_of_speech(document)

        document = tokenize_and_stem(document, stemmer=self.stemmer)

        if self.lower_case:
            document = [word.lower() for word in document]

        document = remove_stopwords(document, self.stopwords)

        document = [word for word in document if len(word) > self.min_word_length]

        document = [word for word in document if word[0] != "'"]

        return document


