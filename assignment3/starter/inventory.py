import hashlib
import getpass


WORKERS_COUNT = 3
localhost = "http://localhost:"

MAX_PORT = 49152
MIN_PORT = 10000
BASE_PORT = int(hashlib.md5(getpass.getuser().encode()).hexdigest()[:8], 16) % (MAX_PORT - MIN_PORT) + MIN_PORT

WORKER_PORTS = [BASE_PORT + 1, BASE_PORT + 2, BASE_PORT + 3]
WORKERS = []

for port in WORKER_PORTS:
    WORKERS.append(localhost + str(port))
