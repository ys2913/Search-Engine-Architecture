#!/usr/bin/env python
import sys
import pickle

DOC_ID = 'doc_Id'
DOC_TITLE = 'title'
DOC_TEXT = 'text'
DOC_URL = 'url'
WIKI_URL = 'http://en.wikipedia.org/wiki/'
postings = {}

input = pickle.load(sys.stdin.buffer)

data = input['data']


def filldoc(docid, values):
    doc = {}
    doc[DOC_ID] = docid
    doc[DOC_TITLE] = values[0]
    doc[DOC_TEXT] = values[1]
    doc[DOC_URL] = WIKI_URL + values[0]
    return doc


for lists in data:
    for val in lists:
        docid = val[0]
        doc = filldoc(docid, val[1])
        postings[docid] = doc

pickle.dump(postings, sys.stdout.buffer)
