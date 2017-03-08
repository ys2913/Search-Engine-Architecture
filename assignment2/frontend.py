import socket
import hashlib
import getpass
import json
import tornado.web
import tornado.ioloop
import urllib
from tornado import gen
import inventory as inv
import tornado.httpclient
import index_servers as inds
import doc_servers as docs

class Frontend(tornado.web.RequestHandler):
    # extracting list from the response
    def extractvals(self, data):
        res = []
        jdata = json.loads(data)
        postings = jdata['postings']
        return postings

    # merging the response results from the index servers
    def mergeresults(self, res, data):
        results = []
        i, j, k = 0, 0, -1
        while(i < len(res) and j < len(data)):
            if k == -1:
                k+=1
                if res[i][0] == data[j][0]:
                    results.append(res[i])
                    i+=1
                    j+=1
                elif res[i][1] > data[j][1]:
                    results.append(res[i])
                    i+=1
                else:
                    results.append(data[j])
                    j+=1
            else:
                if res[i][0] == data[j][0]:
                    if res[i][0] != results[k]:
                        k+=1
                        results.append(res[i])
                    i+=1
                    j+=1
                elif res[i][1] > data[j][1]:
                    if res[i][0] != results[k]:
                        k+=1
                        results.append(res[i])
                    i+=1
                else:
                    if data[j][0] != results[k]:
                        k+=1
                        results.append(data[j])
                    j+=1

        if i == len(res):
            while(j < len(data)):
                if k == -1 or data[j][0] != results[k]:
                    k+=1
                    results.append(data[j])
                j+=1

        if j == len(data):
            while(i < len(res)):
                if k == -1 or res[i][0] != results[k]:
                    k+=1
                    results.append(res[i])
                i+=1
        return results

    # returns the document server corresponding to the document ID
    def getDocServer(self, docId):
        size = inv.DOC_PARTITIONS
        docServers = inv.doc_servers
        serverId = docId % size
        return docServers[serverId]

    # merging the document server output
    def mergedocs(self, docs):
        lis = []
        for doc in docs:
            jdata = json.loads(doc)
            result = jdata[inv.RESULTS]
            lis.append(result)
        res = {'num_results':len(lis),'results':lis}
        return res

    @gen.coroutine
    def get(self):
        doc_infos = []
        documents = []
        query = self.get_arguments("q")[0]
        query.replace("%20",":")

        if inv.DEBUG:
            print("Query received at frontend = " + query)
        servers = inv.index_servers

        addresses = []
        for server in servers:
            address = server + "/index?" + urllib.parse.urlencode({'q':query})
            addresses.append(address)


        http_client = tornado.httpclient.AsyncHTTPClient()
        responses = yield [http_client.fetch(url) for url in addresses]

        for i in range(0,len(addresses)):
            try:
                response = responses[i]
                response.rethrow()
                data = self.extractvals(response.body.decode("utf-8"))
                doc_infos = self.mergeresults(doc_infos, data)
            except Exception as e:
                print('Exception: %s %s' % (e,addresses[i]))
            
        qsize = min(inv.QUERY_LIMIT, len(doc_infos))
        if inv.DEBUG:
            print("Query Size: " + str(qsize))

        doc_addresses = []

        for i in range(0,qsize):
            doc = doc_infos[i]
            docId = doc[0]
            server = self.getDocServer(docId)
            address = server + "/doc?" + urllib.parse.urlencode({'q':query, 'id':docId})
            doc_addresses.append(address)

        responses = yield [http_client.fetch(url) for url in doc_addresses]

        for i in range(0,qsize):
            try:
                response = responses[i]
                response.rethrow()
                data = documents.append(response.body.decode("utf-8"))
            except Exception as e:
                print('Exception: %s %s' % (e,doc_addresses[i]))
                continue

        documents = self.mergedocs(documents)
        self.finish(json.dumps(documents))
        return


def make_frontend():
    return tornado.web.Application([
        (r"/search", Frontend)
    ])

def init_frontend():
    frontend = make_frontend()
    frontend.listen(inv.FE_PORT)
    print("Frontend started at: "+ str(inv.FE_PORT))
    return