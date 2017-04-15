import argparse
import xml.etree.ElementTree as ET

import assignment4.constants as inv

parser = argparse.ArgumentParser(description='Coordinator')
parser.add_argument('xmlinput', action='store', default='input/info_ret.xml',
                    help='Mapper path')
parser.add_argument('--job_path', action='store', default='idf_jobs',
                    help='Mapper path')
parser.add_argument('--num_partitions', type=int, default=5, metavar='N',
                    help='Number of reducers required')
args = parser.parse_args()

print(args)


def init_docs(partitions):
    docs = []
    for i in range(0, partitions):
        docs.append([])
    return docs


def addPage(docs, page, doc_ID, index):
    docID = doc_ID  # int(page.find(inv.TAG_ID).text)
    title = page.find(inv.TAG_TITLE).text
    rev = page.find(inv.TAG_REV)
    text = rev.find(inv.TAG_TEXT).text

    doc_index = index

    doc = {}
    doc[inv.DOC_ID] = docID
    doc[inv.DOC_TITLE] = title
    doc[inv.DOC_TEXT] = text
    doc[inv.DOC_URL] = inv.WIKI_URL + title
    docs[doc_index].append(doc)
    return


def fillDocuments(file, docs, partitions):
    tree = ET.parse(file)
    root = tree.getroot()
    pages = root.findall(inv.TAG_PAGE)
    len_pages = len(pages)

    for i in range(len_pages):
        addPage(docs, pages[i], i + 1, i % partitions)
    return


def writetofile(f, pages):
    for page in pages:
        f.write(inv.XML_DOC_ID)
        f.write(str(page[inv.DOC_ID]))
        f.write("\n")
        f.write(inv.XML_DOC_TITLE)
        f.write("\n")
        f.write(page[inv.DOC_TITLE])
        f.write("\n")
        f.write(inv.XML_DOC_TEXT)
        f.write("\n")
        f.write(page[inv.DOC_TEXT])
        f.write("\n")


def savefiles(docs, path):
    for i in range(len(docs)):
        filename = path + '/info_ret_' + str(i + 1) + '.in'
        f = open(filename, 'w')
        writetofile(f, docs[i])
        # pickle.dump(docs[i], open( filename, "wb" ))
        f.close()
    return


if __name__ == "__main__":
    docs = init_docs(args.num_partitions)
    fillDocuments(args.xmlinput, docs, args.num_partitions)
    savefiles(docs, args.job_path)
