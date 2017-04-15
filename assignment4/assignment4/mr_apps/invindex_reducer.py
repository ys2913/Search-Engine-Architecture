#!/usr/bin/env python
import sys
import pickle
postings = {}

input = pickle.load(sys.stdin.buffer)
data = input['data']

for lists in data:
    for val in lists:
        docid = val[0]
        term = val[1][0]
        count = val[1][1]

        if term in postings.keys():
            postings[term].append([docid, count])
        else:
            postings[term] = [[docid, count]]


pickle.dump(postings, sys.stdout.buffer)