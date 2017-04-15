import hashlib
import getpass
import glob

# Additions for assignment 4
INVINDEX_PATH = './assignment4/invindex_jobs/'
IDF_JOBS_PATH = './assignment4/idf_jobs/'
DOCS_JOBS_PATH = './assignment4/docs_jobs/'

FILES_INVINDEX = glob.glob(INVINDEX_PATH + '*.out')
FILES_IDF_JOBS = glob.glob(IDF_JOBS_PATH + '*.out')
FILES_DOCS_JOBS = glob.glob(DOCS_JOBS_PATH + '*.out')


# Set to True for running the Indexer
RUN_INDEXER = False

# Debugging On Flag
DEBUG = False

QUERY_LIMIT = 10

# weights for Title token and weight token
TITLE_WEIGHT = 5
TEXT_WEIGHT = 1

localhost = "http://localhost:"

# Frontend port and address
MAX_PORT = 49152
MIN_PORT = 10000
BASE_PORT = int(hashlib.md5(getpass.getuser().encode()).hexdigest()[:8], 16) % (MAX_PORT - MIN_PORT) + MIN_PORT
FE_PORT = BASE_PORT+100
FE_ADDRESS = localhost + str(FE_PORT)

index_ports = []
doc_ports = []

port_count = 1

for i in range(len(FILES_INVINDEX)):
    index_ports.append(FE_PORT + port_count)
    port_count += 1

for i in range(len(FILES_DOCS_JOBS)):
    doc_ports.append(FE_PORT + port_count)
    port_count += 1

"""
index_ports = [BASE_PORT + 1, BASE_PORT + 2, BASE_PORT + 3]
doc_ports = [BASE_PORT + 4, BASE_PORT + 5, BASE_PORT + 6]
"""
INDEX_PARTITIONS = len(index_ports)
DOC_PARTITIONS = len(doc_ports)

index_servers = []
doc_servers = []

for i in range(len(index_ports)):
    index_servers.append(localhost + str(index_ports[i]))

for i in range(len(doc_ports)):
    doc_servers.append(localhost + str(doc_ports[i]))

"""
index_servers = [localhost + str(index_ports[0]),
                 localhost + str(index_ports[1]),
                 localhost + str(index_ports[2])]

doc_servers = [localhost + str(doc_ports[0]),
               localhost + str(doc_ports[1]),
               localhost + str(doc_ports[2])]
"""

index_maps = {}
doc_maps = {}

ind = 0
for port in index_ports:
    index_maps[port] = str(ind)
    ind += 1

ind = 0
for port in doc_ports:
    doc_maps[port] = str(ind)
    ind += 1

# indexer.py constants
# XML file name
NAME_XML = 'input/info_ret.xml'

# Document Server saved pickled datastructure- Dictionary{DocID: DocumentInfo} - See Below for DocumentInfo
DOCUMENTS_DIRECTORY = 'document_servers'
DOC_FILE = DOCUMENTS_DIRECTORY + '/document_server_'  # .p added in the code

# Index Server saved pickled datastructure
INDEXER_DIRECTORY = 'index_servers'
INDEX_FILE = INDEXER_DIRECTORY + '/index_server_'  # .p added in the code
DOC_FREQ_FILE = INDEXER_DIRECTORY + '/doc_freq.p'

TAG_PAGE = '{http://www.mediawiki.org/xml/export-0.10/}page'
TAG_TITLE = '{http://www.mediawiki.org/xml/export-0.10/}title'
TAG_ID = '{http://www.mediawiki.org/xml/export-0.10/}id'
TAG_TEXT = '{http://www.mediawiki.org/xml/export-0.10/}text'
TAG_REV = '{http://www.mediawiki.org/xml/export-0.10/}revision'

WIKI_URL = 'http://en.wikipedia.org/wiki/'

# DocumentInfo = {DOC_ID: ID, DOC_TITLE: Title, DOC_TEXT: text}
DOC_ID = 'doc_Id'
DOC_TITLE = 'title'
DOC_TEXT = 'text'
DOC_URL = 'url'
DOC_SNIPPET = 'snippet'

RESULTS = 'results'
