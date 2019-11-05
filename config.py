import os
NUM_WORKERS=4
NUM_THREADS=4
keepalive = 100
worker_class = 'gevent'
# workers = int(os.environ.get('GUNICORN_PROCESSES', NUM_WORKERS))
# threads = int(os.environ.get('GUNICORN_THREADS', NUM_THREADS))
timeout = 120
forwarded_allow_ips = '*'
secure_scheme_headers = { 'X-Forwarded-Proto': 'https' }
loglevel = 'debug'
