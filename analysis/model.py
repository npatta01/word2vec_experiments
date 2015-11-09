from __future__ import print_function

import sqlite3

from enum import Enum


class BibleIterMode(Enum):
    VERSE = 1
    CHAPTER = 2
    BOOK = 3


class BibleVerse(object):
    def __init__(self, book_id=None, chapter_id=None, verse_id=None, text=None):
        self.book_id = book_id
        self.chapter_id = chapter_id
        self.verse_id = verse_id
        self.text = text

    @property
    def id(self):
        return '{0:02d}{1:03d}{2:03d}'.format(self.book_id, self.chapter_id, self.verse_id)

    def __repr__(self):
        return str(self.__dict__)


class BibleDatabase(object):
    def __init__(self, db):
        self.db = db

    def __iter__(self):
        with sqlite3.connect(self.db) as conn:
            cursor = conn.cursor()

            for row in cursor.execute('''
            SELECT id,b,c,v,t
            FROM t_asv

            '''):
                bs = self._parse_row(row)
                yield bs

    def get_bible_verses(self, start_id, end_id=None):
        if end_id is None:
            end_id = start_id
        rows = None
        with sqlite3.connect(self.db) as conn:
            cursor = conn.cursor()

            rows = list(
                cursor.execute('''
                  SELECT id,b,c,v,t
                  FROM t_asv
                  WHERE Id BETWEEN ? AND ?''', (start_id, end_id)))

            rows = [self._parse_row(r) for r in rows]

        return rows

    def _parse_row(self, row):
        bs = BibleVerse(
            book_id=row[1]
            , chapter_id=row[2]
            , verse_id=row[3]
            , text=row[4]

        )

        return bs
