#!/usr/bin/env python
import sys
import pickle
from nltk import word_tokenize


DOC_ID = 'doc_Id'
DOC_TITLE = 'title'
DOC_TEXT = 'text'
XML_DOC_ID = "<=====" + DOC_ID + "=====>:"
XML_DOC_TITLE = "<=====" + DOC_TITLE + "=====>:"
XML_DOC_TEXT = "<=====" + DOC_TEXT + "=====>:"
freq = {}
docID = 0
istitle = False
output = []

docIds_count = 0

def printfreq(freq):
    if len(freq.keys()) > 0:
        for key in sorted(freq.keys()):
            output.append([int(docID), [key, freq[key]]])
            #print('%s\t%s:!:!:!%s' % (docID, key, freq[key]))
    return


def fillfreq(freq, istitle, line):
    tokens = word_tokenize(line)
    score = 1
    if istitle:
        score *= 3

    for token in tokens:
        if token in freq.keys():
            freq[token] += score
        else:
            freq[token] = score
    return


for line in sys.stdin:
    line = line.replace('\n', '')
    if line.find(XML_DOC_ID) != -1:
        docIds_count += 1
        printfreq(freq)
        freq = {}
        val = line.split(':')
        docID = val[1].replace('\n', '')
        continue
    elif line.find(XML_DOC_TITLE) != -1:
        istitle = True
        continue
    elif line.find(XML_DOC_TEXT) != -1:
        istitle = False
        continue
    else:
        fillfreq(freq, istitle, line)

out_values = {'data': output, 'count': docIds_count}

pickle.dump(out_values, sys.stdout.buffer)
