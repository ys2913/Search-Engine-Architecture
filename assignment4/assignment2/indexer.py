import os
import math
import pickle
import assignment2.inventory as inv
from nltk import word_tokenize
import xml.etree.ElementTree as ET

documentID = 1


def init_docservers():
    servers = []
    for i in range(0, inv.DOC_PARTITIONS):
        servers.append({})
    return servers


def init_postingsList():
    postings = []
    for i in range(0, inv.INDEX_PARTITIONS):
        postings.append({})
    return postings


def addTokens(sentence, postingList, score, doc_freq):
    tokens = word_tokenize(sentence)
    doc_tokens = {}

    for token in tokens:
        if token in postingList.keys():
            postingList[token] += score
        else:
            postingList[token] = score

    for token in postingList.keys():
        if token in doc_freq.keys():
            doc_freq[token] += 1
        else:
            doc_freq[token] = 1
    return


def getdocpostings(doc, doc_freq):
    postingList = {}
    addTokens(doc[inv.DOC_TITLE], postingList, inv.TITLE_WEIGHT, doc_freq)
    addTokens(doc[inv.DOC_TEXT], postingList, inv.TEXT_WEIGHT, doc_freq)
    return postingList


def mergePostingList(global_posting, doc_posting_list, docID):
    for key in doc_posting_list.keys():
        value = doc_posting_list[key]
        documentinfo = [docID, value]
        if key in global_posting.keys():
            glist = global_posting[key]
            ind = 0

            while ind < len(glist) and glist[ind][1] < documentinfo[1]:
                ind += 1

            glist.insert(ind, documentinfo)
        else:
            global_posting[key] = [documentinfo]
    return


def fillpostingsList(postings, doc, doc_freq):
    docID = inv.DOC_ID
    ind_index = doc[docID] % inv.INDEX_PARTITIONS
    doc_posting_list = getdocpostings(doc, doc_freq)
    mergePostingList(postings[ind_index], doc_posting_list, doc[docID])
    return


def addPage(documents, page, postings, doc_freq, documentID):
    docID = int(page.find(inv.TAG_ID).text)
    title = page.find(inv.TAG_TITLE).text
    rev = page.find(inv.TAG_REV)
    text = rev.find(inv.TAG_TEXT).text

    doc_index = docID % inv.DOC_PARTITIONS

    doc = {}
    doc[inv.DOC_ID] = docID
    doc[inv.DOC_TITLE] = title
    doc[inv.DOC_TEXT] = text
    doc[inv.DOC_URL] = inv.WIKI_URL + title
    documents[doc_index][docID] = doc

    fillpostingsList(postings, doc, doc_freq)
    return


def fillDocuments(documents, postings, doc_freq):
    tree = ET.parse(inv.NAME_XML)
    root = tree.getroot()
    pages = root.findall(inv.TAG_PAGE)
    docSize = len(pages)
    documentID = 1
    for page in pages:
        addPage(documents, page, postings, doc_freq, documentID)
        documentID += 1

    return docSize


def savetofile(documents, file, multiple_files):
    if multiple_files:
        for i in range(0, len(documents)):
            doc = documents[i]
            filename = file + str(i) + ".p"
            pickle.dump(doc, open(filename, "wb"))
    else:
        pickle.dump(documents, open(file, "wb"))
    return


def check_output_dir():
    if not os.path.isdir(inv.DOCUMENTS_DIRECTORY):
        os.mkdir(inv.DOCUMENTS_DIRECTORY)

    if not os.path.isdir(inv.INDEXER_DIRECTORY):
        os.mkdir(inv.INDEXER_DIRECTORY)
    return


def computeidf(doc_freq, size):
    for key in doc_freq.keys():
        df = doc_freq[key]
        doc_freq[key] = math.log(size / df)
    return


def init_indexer():
    # initializing document servers and postings list
    documents = init_docservers()
    postings = init_postingsList()
    doc_freq = {}
    docSize = 0

    docSize = fillDocuments(documents, postings, doc_freq)

    computeidf(doc_freq, docSize)
    check_output_dir()
    savetofile(documents, inv.DOC_FILE, True)
    savetofile(postings, inv.INDEX_FILE, True)
    savetofile(doc_freq, inv.DOC_FREQ_FILE, False)

    return

    # init_indexer()
