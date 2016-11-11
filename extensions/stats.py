#!/usr/bin/env python
import time
import urllib
import json
import ConfigParser as cnfparse
from functools import update_wrapper
from flask import Response, request, g, jsonify

# PARSE CONFIGURATION FILE AS SPECIFED BY --CONFIG
cfg=cnfparse.ConfigParser()
cfg.read('./config.py')

# PARSE STATS CONFIGURATION VARIABLES
REDIS_HOST = cfg.get('redis','host')
REDIS_PORT = cfg.get('redis','port')
QUERY_HOST = cfg.get('slow_queries','hostname')
QUERY_THRESHOLD = cfg.get('slow_queries','threshold')
RLIMIT_TIME = int(cfg.get('rate-limiter','time'))
RLIMIT_LIMIT = int(cfg.get('rate-limiter','limit'))

from redis import Redis
redis = Redis(host=REDIS_HOST, port=REDIS_PORT)

def cache_key(prefix, delim, suffix=None):
    if suffix:
        return prefix + delim + urllib.urlencode([(k, v) for k in sorted(suffix) for v in sorted(suffix.getlist(k))])
    else:
        return prefix

class RateLimit(object):
    expiration_window = 10

    def __init__(self, key_prefix, limit, per, send_x_headers):
        self.reset = (int(time.time()) // per) * per + per
        self.key = key_prefix + '_' + str(self.reset)
        self.limit = limit
        self.per = per
        self.send_x_headers = send_x_headers
        p = redis.pipeline()
        p.incr(self.key)
        p.expireat(self.key, self.reset + self.expiration_window)
        self.current = min(p.execute()[0], limit)

    remaining = property(lambda x: x.limit - x.current)
    over_limit = property(lambda x: x.current >= x.limit)

def get_view_rate_limit():
    return getattr(g, '_view_rate_limit', None)

def on_over_limit(limit):
    return jsonify({'status': 429, 'message': 'Too Many Requests: You have exceeded global rate limit please wait.'}), 429

def ratelimit(limit=RLIMIT_LIMIT, per=RLIMIT_TIME, send_x_headers=True, over_limit=on_over_limit):
    def decorator(f):
        def rate_limited(*args, **kwargs):
            key = 'RLIMIT:%s' % ( cache_key(request.path, '?', request.args) )
            rlimit = RateLimit(key, limit+1, per, send_x_headers)
            g._view_rate_limit = rlimit
            if over_limit is not None and rlimit.over_limit:
                return over_limit(rlimit)
            return f(*args, **kwargs)
        return update_wrapper(rate_limited, f)
    return decorator

def put_stats(threshold=.1, **kwargs):
    # initiate redis pipe
    pipe = redis.pipeline()
    req = kwargs['request']  # request argument comes from flask
    res = kwargs['response'] # response argument comes from nextbus
    length = int(res.headers.get('Content-Length', 0))
    
    # increment the hits and bytes COUNT hashes
    pipe.hincrby( 'COUNT:%s' % (req.endpoint), 'hits', 1)
    pipe.hincrby( 'COUNT:%s' % (req.endpoint), 'bytes', length)
    
    # update the slow queries log 
    if res.elapsed.total_seconds() >= QUERY_THRESHOLD:
        kv = {}
        kv['host'] = QUERY_HOST
        kv['status'] = str(res.status_code)
        kv['endpoint'] = req.endpoint
        kv['path'] = req.path
        kv['query_string'] = json.dumps(req.args)
        kv['size'] = int(res.headers.get('Content-Length', 0))
        kv['datetime'] = res.headers.get('Date', '0000-00-00')
        kv['unixtime'] = str(int(time.time()*100))
        kv['latency'] = res.elapsed.total_seconds()
        kv['ip'] = req.remote_addr
        pipe.lpush('SLOW_QUERIES', json.dumps(kv))
    #commit the redis pipe of commands
    pipe.execute()
    return

def get_slow_queries(**kwargs):
    """Simple function to construct and pass the args 
    for a redis LRANGE query on the slow_queries log."""
    pipe = redis.pipeline()
    resp = {}
    hash_key='SLOW_QUERIES'
    # minus 1 from the actual integer passed for row limit 
    pipe.lrange(hash_key, 0, kwargs['row_limit']-1)
    data=pipe.execute()[0]
    resp['slow_queries'] = [json.loads(d) for d in data]
    return resp

def get_counts(*args):
    """Another simple function to construct the hash_key and args
    for a redis HGETALL query on the COUNT incrementers log."""
    pipe = redis.pipeline()
    resp = {}
    hash_key='COUNT:%s' % (args[0])
    pipe.hgetall(hash_key)
    data=pipe.execute()[0]
    resp['endpoint'] = args[0]
    resp['stats'] = data
    return resp
