import hashlib
import json
import pickle
import subprocess
import urllib
import uuid
from operator import itemgetter
import tornado.httpclient
import tornado.ioloop
import tornado.web
from tornado import gen, process
import assignment3.inventory as c

tasks = {}


# work on mapper for hashing words into list
class RetrieveMap(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self):
        servername = self.request.host
        reducer_ix = int(self.get_arguments('reducer_ix')[0])
        map_task_id = self.get_arguments('map_task_id')[0]

        task_data = tasks[map_task_id]['data'][reducer_ix]

        output = {'data': task_data, 'count': tasks[map_task_id]['count']}
        encoded_list = json.dumps(output)
        self.finish(encoded_list)
        return


class Map(tornado.web.RequestHandler):
    def init_tokenlist(self, num_reducers):
        tokens = []
        for i in range(0, num_reducers):
            tokens.append([])
        return tokens

    # @gen.coroutine
    def getmapper(self, mapper_path, input_file, num_reducers):
        #   reading input file
        file = open(input_file, 'r')
        data = file.read()

        p = subprocess.Popen(mapper_path, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        (out, _) = p.communicate(data.encode())
        file.close()

        tokens = pickle.loads(out)
        tokenlist = self.init_tokenlist(num_reducers)

        tokendata = tokens['data']
        for i in range(0, len(tokendata)):
            token = tokendata[i]
            index = int(hashlib.sha1(str(token[0]).encode()).hexdigest(), 16) % num_reducers
            tokenlist[index].append(token)

        taskID = uuid.uuid4().hex

        for i in range(0, num_reducers):
            tokenlist[i].sort(key=itemgetter(0))

        taskdict = {'data': tokenlist, 'count': tokens['count']}
        tasks[taskID] = taskdict
        if c.DEBUG:
            print("Task ID added: ",taskID)
        return taskID

    def get(self):
        mapper_path = self.get_arguments('mapper_path')
        input_file = self.get_arguments('input_file')
        num_reducers = self.get_arguments('num_reducers')
        taskID = self.getmapper(mapper_path[0], input_file[0], int(num_reducers[0]))
        output = {'status': 'success', 'map_task_id': taskID}
        self.finish(json.dumps(output))
        return


class Reducer(tornado.web.RequestHandler):
    @gen.coroutine
    def getreducer(self, reducer_ix, reducer_path, map_task_ids, job_path):
        mapper_count = len(map_task_ids)
        http_client = tornado.httpclient.AsyncHTTPClient()
        servers = c.WORKERS
        lenservers = len(servers)
        urls = []

        for i in range(mapper_count):
            server = servers[i % lenservers]
            params = urllib.parse.urlencode({'reducer_ix': reducer_ix,
                                             'map_task_id': map_task_ids[i]})
            url = "%s/retrieve_map_output?%s" % (server, params)
            urls.append(url)

        responses = yield [http_client.fetch(url) for url in urls]

        print("Responses: ", len(responses))

        mapper_outs = []
        document_count = 0
        for i in range(mapper_count):
            try:
                response = responses[i]
                response.rethrow()
                keys_list = json.loads(response.body.decode())
                mapper_outs.append(keys_list['data'])
                document_count += keys_list['count']
            except Exception as e:
                print('Exception: %s %s' % (e, urls[i]))

        reducer_input = {'data': mapper_outs, 'count': document_count}
        print("Doc Count: ",document_count)
        filename = job_path + '/' + str(reducer_ix) + '.out'
        en_map_outs = pickle.dumps(reducer_input)
        p = subprocess.Popen(reducer_path, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        (out, _) = p.communicate(en_map_outs)
        fobj = pickle.loads(out)
        pickle.dump(fobj, open(filename, "wb"))
        return

    def get(self):
        reducer_ix = self.get_arguments('reducer_ix')
        reducer_path = self.get_arguments('reducer_path')
        map_task_ids = self.get_arguments('map_task_ids')
        job_path = self.get_arguments('job_path')

        self.getreducer(reducer_ix[0], reducer_path[0], map_task_ids[0].split(','), job_path[0])
        self.finish({"status": "success"})
        return


def make_workerserver():
    return tornado.web.Application([
        (r"/reduce", Reducer),
        (r"/map", Map),
        (r"/retrieve_map_output", RetrieveMap)
    ])


def init_worker():
    task_id = process.fork_processes(c.WORKERS_COUNT, max_restarts=0)
    port = c.WORKER_PORTS[task_id]
    worker = make_workerserver()
    worker.listen(port)
    print("Worker initialized at %d" % port)
    tornado.ioloop.IOLoop.current().start()
    return


init_worker()
