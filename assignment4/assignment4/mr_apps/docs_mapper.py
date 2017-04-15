#!/usr/bin/env python
import sys
import pickle

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


def fillvalues(values, istitle, line):
    if istitle:
        values[0] += line.replace('\n', '')
    else:
        values[1] += line.replace('\n', '')
    return


def initval():
    val = list()
    val.append("")
    val.append("")
    return val


values = initval()
isstart = True

for line in sys.stdin:
    if line.find(XML_DOC_ID) != -1:
        docIds_count += 1
        if not isstart:
            output.append([int(docID), values])
        values = initval()
        isstart = False
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
        fillvalues(values, istitle, line)

out_values = {'data': output, 'count': docIds_count}

pickle.dump(out_values, sys.stdout.buffer)
