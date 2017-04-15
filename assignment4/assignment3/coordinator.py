import glob
import json
import urllib
import tornado.httpclient
import tornado.ioloop
import tornado.web
from tornado import gen
import assignment3.inventory as inv
from assignment3.opts import Parser


# parser = Parser()
# args = parser.getargs()

@gen.coroutine
def coordinator(mapper_path, reducer_path, job_path):
    filename = job_path + '/*.in'
    files = glob.glob(filename)
    num_map = len(files)

    tornado.httpclient.AsyncHTTPClient.configure(None, defaults={'connect_timeout': 300, 'request_timeout': 300})
    http_client = tornado.httpclient.AsyncHTTPClient()

    map_urls = []
    for i in range(0, num_map):
        url = inv.WORKERS[i % inv.WORKERS_COUNT] + '/map?' \
              + urllib.parse.urlencode({'mapper_path': mapper_path, \
                                        'num_reducers': num_map, \
                                        'input_file': files[i]})
        map_urls.append(url)

    if inv.DEBUG:
        for url in map_urls:
            print(url)
    responses = yield [http_client.fetch(url) for url in map_urls]

    map_task_ids = ""
    for i in range(0, len(map_urls)):
        try:
            response = responses[i]
            response.rethrow()
            data = json.loads(response.body.decode())
            if map_task_ids == "":
                map_task_ids = data['map_task_id']
            else:
                map_task_ids += ',' + data['map_task_id']
        except Exception as e:
            print('Exception: %s %s' % (e, map_urls[i]))

    red_urls = []
    for i in range(0, num_map):
        url = inv.WORKERS[i % inv.WORKERS_COUNT] + '/reduce?' \
              + urllib.parse.urlencode({'reducer_ix': i % num_map, \
                                        'reducer_path': reducer_path, \
                                        'map_task_ids': map_task_ids, \
                                        'job_path': job_path})
        red_urls.append(url)

    if inv.DEBUG:
        for url in red_urls:
            print(url)
    responses = yield [http_client.fetch(url) for url in red_urls]

    for i in range(0, len(red_urls)):
        try:
            response = responses[i]
            response.rethrow()
            data = response.body.decode("utf-8")
        except Exception as e:
            print('Exception: %s %s' % (e, red_urls[i]))

    print('Coordinator Finished')
    return


def run(mapper_path, reducer_path, job_path):
    tornado.ioloop.IOLoop.current().run_sync(lambda :coordinator(mapper_path, reducer_path, job_path))
