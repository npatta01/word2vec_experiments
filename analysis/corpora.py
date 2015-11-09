from __future__ import print_function
import sys

import gensim
from gensim.models import Phrases
import helper
from model import BibleDatabase, BibleIterMode
import logging


class BibleIterator(object):
    def __init__(self, db_path, bible_iter_mode):
        self.db_path = db_path
        self.iter_mode = bible_iter_mode

    def __iter__(self):
        last_verse_seen = None
        last_chapter_seen = None
        last_book_seen = None

        verses = []
        bible_db = BibleDatabase(self.db_path)
        for bible_verse in bible_db:
            transition_occurred = False
            verses.append(bible_verse)

            if self.iter_mode == BibleIterMode.VERSE:
                if bible_verse.verse_id != last_verse_seen:
                    transition_occurred = True
            if self.iter_mode == BibleIterMode.CHAPTER:
                if bible_verse.chapter_id != last_chapter_seen:
                    transition_occurred = True
            if self.iter_mode == BibleIterMode.BOOK:
                if bible_verse.book_id != last_book_seen:
                    transition_occurred = True

            last_book_seen = bible_verse.book_id
            last_chapter_seen = bible_verse.chapter_id
            last_verse_seen = bible_verse.verse_id

            if transition_occurred:
                yield verses
                verses = []
        yield verses


class BibleSqliteCorpus(object):
    def __init__(self, db_path, normalizer=None, iter_mode=BibleIterMode.VERSE):

        self.db_path = db_path
        self.iter_mode = iter_mode

        self.documents_parsed = 0
        self.normalizer = normalizer

        self.dictionary = gensim.corpora.Dictionary()
        self.__learn_collocations__()
        self.__update_dictionary()

        logging.debug("Created Dictionary")

    @property
    def iterator(self):
        return BibleIterator(self.db_path, self.iter_mode)

    def ___collocated_iterator__(self):
        for tokens in self.__collection_iterator_():
            yield tokens
            # yield self.trigram[tokens]

    def __collection_iterator_(self):
        docs_seen = 0

        for bible_verses in self.iterator:

            doc_contents = [item.text for item in bible_verses]

            doc_content = " ".join(doc_contents)
            tokens = self.normalizer.process(doc_content)
            docs_seen += 1

            if docs_seen % 1000 == 0:
                print("\r--- Completed {0} {1}s".format(docs_seen, self.iter_mode), end=' ')
                sys.stdout.flush()

            yield tokens

        print("\r--- Completed {0} {1}s".format(docs_seen, self.iter_mode), end=' ')
        sys.stdout.flush()

        print()

    def __update_dictionary(self):
        for doc_tokens in self.__collection_iterator_():
            self.dictionary.doc2bow(doc_tokens, allow_update=True)
            self.documents_parsed += 1

    def __learn_collocations__(self):
        bigram = Phrases(self.__collection_iterator_())
        self.trigram = Phrases(bigram[self.__collection_iterator_()])

    def __iter__(self):
        for sentences in self.___collocated_iterator__():
            yield sentences
            # yield self.dictionary.doc2bow(doc_tokens)

    def __len__(self):
        return self.documents_parsed

    def finalize_dictionary(self, no_below=5, no_above=0.8):
        self.dictionary.filter_extremes(no_below, no_above)
        self.dictionary.compactify()
