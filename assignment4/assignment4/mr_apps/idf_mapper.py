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

docID = 0
istitle = False

output = []
docIds_count = 0

def fillfreq(line):
    tokens = word_tokenize(line)
    for token in tokens:
        output.append([token, docID])
    return


for line in sys.stdin:
    line = line.replace('\n', '')
    if line.find(XML_DOC_ID) != -1:
        docIds_count += 1
        freq = {}
        val = line.split(':')
        docID = int(val[1].replace('\n', ''))
        continue
    elif line.find(XML_DOC_TITLE) != -1:
        continue
    elif line.find(XML_DOC_TEXT) != -1:
        continue
    else:
        fillfreq(line)

out_values = {'data': output, 'count': docIds_count}

pickle.dump(out_values, sys.stdout.buffer)
