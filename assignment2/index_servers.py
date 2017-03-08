import tornado.httpclient
import tornado.ioloop
import tornado.web
import socket
import hashlib
import getpass
import pickle
import json
import operator
from tornado import gen
import inventory as inv


class IndexServer(tornado.web.RequestHandler):
	def getscore(self, queries):
		scores = []
		term_idfs = pickle.load(open(inv.DOC_FREQ_FILE, "rb"))
		
		for term in queries:
			if term in term_idfs.keys():
				scores.append(term_idfs[term])
			else:
				scores.append(0)
		return scores

	def getfilename(self):
		port = self.request.host.split(":")[1]
		filename = inv.INDEX_FILE + inv.index_maps[int(port)] + '.p'
		return	filename

	def score(self, lis1, lis2):
		score = 0
		for ind in range(0,len(lis1)):
			score += lis1[ind]*lis2[ind]
		return score

	def calculateScore(self, qscore,doc_scores):
		scores = {}
		for key in doc_scores.keys():
			if inv.DEBUG:
				print(key)
				print(doc_scores[key])
			scores[key] = self.score(qscore, doc_scores[key])
		return scores

	def getnewVal(self,qlength):
		temp = []
		for i in range(0,qlength):
			temp.append(0)
		return temp
	
	def getdocscores(self, queries, query_score):
		doc_scores = {}
		postings = []
		filename = self.getfilename()
		postingList = pickle.load(open(filename,"rb"))

		for i in range(0, len(queries)):
			term = queries[i]
			if term in postingList.keys():
				if inv.DEBUG:
					print("Term: "+term)
					print(postingList[term])
				for doc in postingList[term]:
					if doc[0] in doc_scores.keys():
						doc_scores[doc[0]][1] = doc[1] 
					else:
						doc_scores[doc[0]] = self.getnewVal(len(queries))
						doc_scores[doc[0]][i] = doc[1]

		scores = self.calculateScore(query_score,doc_scores)

		sortedlist = sorted(scores.items(), key = operator.itemgetter(1))
		length = len(sortedlist)

		for ind in range(length-1,-1,-1):
			val = []
			val.append(sortedlist[ind][0])
			val.append(sortedlist[ind][1])
			postings.append(val)

		return postings

	def getList(self, queries):
		query_score = self.getscore(queries)
		doc_scores = self.getdocscores(queries,query_score)
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

def make_indexserver():
    return tornado.web.Application([
        (r"/index", IndexServer)
    ])

def init_index_servers():
	indexserver = make_indexserver()
	indexports = inv.index_ports

	for port in indexports:
		indexserver.listen(port)
		print("Index Server Started at port: " + str(port))

	return