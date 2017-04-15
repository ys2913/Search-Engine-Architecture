#!/usr/bin/env python
import sys
import pickle
import math
postings = {}

input = pickle.load(sys.stdin.buffer)

docIds = set()
document_count = {}
idfs = {}

total_document_count = input['count']
data = input['data']

for lists in data:
    for val in lists:
        docid = val[1]
        term = val[0]
        docIds.add(docid)
        if term in document_count.keys():
            document_count[term] += 1
        else:
            document_count[term] = 1

for key in document_count.keys():
    idfs[key] = math.log((1.0*len(docIds)) / document_count[key])

pickle.dump(idfs, sys.stdout.buffer)