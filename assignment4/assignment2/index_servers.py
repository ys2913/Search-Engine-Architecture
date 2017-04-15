import json
import operator
import pickle
import glob
from tornado import process
import tornado.httpclient
import tornado.ioloop
import tornado.web

import assignment2.inventory as inv
from assignment2.frontend import Frontend
from assignment2.doc_servers import DocServer


class IndexServer(tornado.web.RequestHandler):
    def initialize(self, database):
        self.__data = database

    def getscore(self, queries):
        scores = []
        term_idfs = self.__data[0]

        for term in queries:
            if term in term_idfs.keys():
                scores.append(term_idfs[term])
            else:
                scores.append(0)
        return scores

    def getfilename(self):
        port = self.request.host.split(":")[1]
        filename = inv.INDEX_FILE + inv.index_maps[int(port)] + '.p'
        return filename

    def score(self, lis1, lis2):
        score = 0
        for ind in range(0, len(lis1)):
            score += lis1[ind] * lis2[ind]
        return score

    def calculateScore(self, qscore, doc_scores):
        scores = {}
        for key in doc_scores.keys():
            if inv.DEBUG:
                print(key)
                print(doc_scores[key])
            scores[key] = self.score(qscore, doc_scores[key])
        return scores

    def getnewVal(self, qlength):
        temp = []
        for i in range(0, qlength):
            temp.append(0)
        return temp

    def getdocscores(self, queries, query_score):
        doc_scores = {}
        postings = []
        # filename = self.getfilename()
        postingList = self.__data[1]  # pickle.load(open(filename, "rb"))

        for i in range(0, len(queries)):
            term = queries[i]
            if term in postingList.keys():
                if inv.DEBUG:
                    print("Term: " + term)
                    print(postingList[term])
                for doc in postingList[term]:
                    if doc[0] in doc_scores.keys():
                        doc_scores[doc[0]][1] = doc[1]
                    else:
                        doc_scores[doc[0]] = self.getnewVal(len(queries))
                        doc_scores[doc[0]][i] = doc[1]

        scores = self.calculateScore(query_score, doc_scores)

        sortedlist = sorted(scores.items(), key=operator.itemgetter(1))
        length = len(sortedlist)

        for ind in range(length - 1, -1, -1):
            val = []
            val.append(sortedlist[ind][0])
            val.append(sortedlist[ind][1])
            postings.append(val)

        return postings

    def getList(self, queries):
        query_score = self.getscore(queries)
        doc_scores = self.getdocscores(queries, query_score)
        if inv.DEBUG:
            print(doc_scores)
        docIDs = {"postings": doc_scores}
        if inv.DEBUG:
            print(docIDs)
        return json.dumps(docIDs)

    def get(self):
        servername = self.request.host
        query = self.get_arguments("q")[0]
        queries = query.split(" ")
        print("Query = " + query + " received at: " + servername)
        result = self.getList(queries)
        self.finish(result)
        return


def loadidfs():
    idfs = {}
    files = glob.glob(inv.IDF_JOBS_PATH + '*.out')

    for filename in files:
        dic = pickle.load(open(filename, 'rb'))
        idfs.update(dic)

    return idfs


def make_indexserver(data):
    return tornado.web.Application([
        (r"/index", IndexServer, dict(database=data))
    ])


def make_docserver(data):
    return tornado.web.Application([
        (r"/doc", DocServer, dict(database=data))
    ])


def make_frontend():
    return tornado.web.Application([
        (r"/search", Frontend)
    ])


def init_servers():
    totalprocesses = len(inv.doc_ports) + len(inv.index_servers) + 1
    task_id = process.fork_processes(totalprocesses, max_restarts=0)

    if task_id == 0:
        frontend = make_frontend()
        frontend.listen(inv.FE_PORT)
        print("Front end-Started at: ", inv.FE_PORT)

    elif task_id <= len(inv.index_ports):
        idfs = loadidfs()
        tid = task_id - 1
        data = []
        pList = pickle.load(open(inv.INVINDEX_PATH + str(tid) + '.out', 'rb'))
        data.append(idfs)
        data.append(pList)
        indexserver = make_indexserver(data)
        indexport = inv.index_ports[tid]
        indexserver.listen(indexport)
        print("Index Server Started at port: " + str(indexport))

    else:
        tid = task_id - len(inv.index_ports) - 1
        doc = pickle.load(open(inv.DOCS_JOBS_PATH + str(tid) + '.out', 'rb'))
        data = []
        data.append(doc)

        docserver = make_docserver(data)
        docport = inv.doc_ports[tid]

        docserver.listen(docport)
        print("Document Server Started at port: " + str(docport))

    tornado.ioloop.IOLoop.current().start()
