import tornado.httpclient
import tornado.ioloop
import tornado.web
import socket
import hashlib
import getpass
import json
import re
import pickle
from tornado import gen
import inventory as inv


class DocServer(tornado.web.RequestHandler):
	def getfilename(self, servername):
		port = servername.split(":")[1]
		filename = inv.DOC_FILE + inv.doc_maps[int(port)] + '.p'
		return	filename

	def getdocsnippet(self, text, query):
		snippet = ""
		tokens 	= query.split(" ")
		matches	= []
		text.replace(",",".").replace("\n",".").replace(";",".")
		body	= text.split(".")

		added	= False
		for i in range(0,len(body)):
			for token in tokens:
				if body[i].find(token) >= 0:
					if i > 0:
						snippet += body[i-1]
						added = True
					snippet += body[i].replace(token," <b> "+token+" </b> ")
					
					if not added and i < len(body)-1:
						snippet += body[i+1]
					break;
		return snippet

	def getdocumentinfo(self, doc, query):
		docinfo = {}

		docinfo[inv.DOC_TITLE]		= doc[inv.DOC_TITLE]
		docinfo[inv.DOC_URL]		= doc[inv.DOC_URL]
		docinfo[inv.DOC_ID]			= doc[inv.DOC_ID]
		docinfo[inv.DOC_SNIPPET]	= self.getdocsnippet(doc[inv.DOC_TEXT], query)

		output = {inv.RESULTS: docinfo}
		return output

	def getDocuments(self, docID, query, servername):
		filename = self.getfilename(servername)
		documents = pickle.load(open(filename,"rb"))
		docinfo = self.getdocumentinfo(documents[docID], query)
		return docinfo

	def get(self):
		servername = self.request.host
		query = self.get_arguments("q")[0]
		docID = self.get_arguments("id")[0]
		print("Doc ID = " + docID + ", Query = " + query + " received at: " + servername)
		result = self.getDocuments(int(docID),query,servername)
		self.finish(result)
		return

def make_docserver():
    return tornado.web.Application([
        (r"/doc", DocServer)
    ])

def init_doc_servers():
	docserver = make_docserver()
	docports = inv.doc_ports

	for port in docports:
		docserver.listen(port)
		print("Document Server Started at port: " + str(port))

	return