import tornado.httpclient
import tornado.ioloop
import tornado.web
import socket
import hashlib
import getpass
from tornado import gen


#sock = socket.getsockname()
socks = []
MAX_PORT = 49152
MIN_PORT = 10000
hostinfo = socket.gethostname()

class BackServerHandler(tornado.web.RequestHandler):
    def get(self):
    	hostname = socket.gethostname()
    	self.write(self.request.host)

def make_backserver():
    return tornado.web.Application([
        (r"/", BackServerHandler),
    ])

class LoadHandler(tornado.web.RequestHandler):
    var=0
    @gen.coroutine
    def get(self):
        http_client = tornado.httpclient.AsyncHTTPClient()
        address="http://"+hostinfo+":"+str(socks[LoadHandler.var])
        response = yield http_client.fetch(address)
        self.write(response.body)
        LoadHandler.var=(LoadHandler.var+1)%3
        self.finish()

def make_loadbalancer():
    return tornado.web.Application([
        (r"/", LoadHandler),
    ])

if __name__ == "__main__":
    backendserver = make_backserver()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    BASE_PORT = int(hashlib.md5(getpass.getuser().encode()).hexdigest()[:8], 16) % (MAX_PORT - MIN_PORT) + MIN_PORT
    for x in range(0,3):
    	BASE_PORT = BASE_PORT+x
    	socks.append(BASE_PORT)
    	backendserver.listen(BASE_PORT)
    	print("Backend Server Started at port: "+str(BASE_PORT))


    loadbalancer = make_loadbalancer()
    BASE_PORT = BASE_PORT + 1
    loadbalancer.listen(BASE_PORT)
    print("Load balancer started at port: "+str(BASE_PORT))

    tornado.ioloop.IOLoop.current().start()