#!/usr/bin/env python
import os, sys
import ConfigParser as cnfparse
import time
import json
import xmltodict
import requests as r
from extensions import stats, utils
from flask import Flask, Response, request, url_for, g, jsonify

app = Flask(__name__)

# PARSE CONFIGURATION FILE AS SPECIFED BY --CONFIG
cfg=cnfparse.ConfigParser()
cfg.read('./config.py')

# SET CONFIGURABLE VARS
PROTO = cfg.get('flask', 'proto')
HOST = cfg.get('flask', 'host')
PORT = cfg.get('flask', 'port')
THREAD = cfg.get('flask', 'thread')

BE_PROTO = cfg.get('nextbus', 'proto')
BE_HOST = cfg.get('nextbus', 'host')
BE_PATH = cfg.get('nextbus', 'path')
BEURI = BE_PROTO + BE_HOST + BE_PATH

def proxy_pass(**kwargs):
    qs=utils.qs_encode(kwargs['params'])
    url= BEURI + "?" + qs
    return r.get(url)

@app.after_request
def inject_x_rate_header(response):
    limit = getattr(g, '_view_rate_limit', None) # limit = g._view_rate_limit()
    if limit and limit.send_x_headers:
        h = response.headers
        h.add('X-RateLimit-Remaining', str(limit.remaining))
        h.add('X-RateLimit-Limit', str(limit.limit))
        h.add('X-RateLimit-Reset', str(limit.reset))
    return response

@app.route('/routes')
@stats.ratelimit()
@utils.gzipped
def routes_list():
    """Returns a list of all available routes in the sf-muni agency."""
    params = utils.qs_params(command='routeList',data=request.args)
    resp=proxy_pass(params=params)
    jdata=xmltodict.parse(resp.content, dict_constructor=dict)
    stats.put_stats(response=resp, request=request)
    return jsonify(jdata)

@app.route('/routes/<routeTag>')
@stats.ratelimit()
@utils.gzipped
def routes_config(routeTag):
    """Returns details about a given routeTag."""
    params = utils.qs_params(   command='routeConfig',
                                data=request.args,
                                r=routeTag  )
    resp=proxy_pass(params=params)
    jdata=xmltodict.parse(resp.content, dict_constructor=dict)
    stats.put_stats(response=resp, request=request)
    return jsonify(jdata)


@app.route('/stops/<stopId>/predictions')
@stats.ratelimit()
@utils.gzipped
def predictions_stopId(stopId):
    """Show prediction by route with stopId only - least specific"""
    params = utils.qs_params(   command='predictions',
                                data=request.args,
                                stopId=stopId  )
    resp=proxy_pass(params=params)
    jdata=xmltodict.parse(resp.content, dict_constructor=dict)
    stats.put_stats(response=resp, request=request)
    return jsonify(jdata)

@app.route('/stops/<stopId>/routes/<routeTag>/predictions')
@stats.ratelimit()
@utils.gzipped
def predictions_stopId_and_route(stopId,routeTag):
    """Show prediction by route with stopId and routeTag - mid specific """
    params = utils.qs_params(   command='predictions',
                                data=request.args,
                                stopId=stopId,
                                r=routeTag  )
    resp=proxy_pass(params=params)
    jdata=xmltodict.parse(resp.content, dict_constructor=dict)
    stats.put_stats(response=resp, request=request)
    return jsonify(jdata)

@app.route('/routes/<routeTag>/stops/<stopTag>/predictions')
@stats.ratelimit()
@utils.gzipped
def predictions_stopTag_and_route(routeTag,stopTag):
    """Show prediction by routes with routeTag and stopId - most specific"""
    params = utils.qs_params(   command='predictions',
                                data=request.args,
                                r=routeTag,
                                s=stopTag   )
    resp=proxy_pass(params=params)
    jdata=xmltodict.parse(resp.content, dict_constructor=dict)
    stats.put_stats(response=resp, request=request)
    return jsonify(jdata)

@app.route('/tuples/predictions')
@stats.ratelimit()
@utils.gzipped
def predictions_for_multi_stops():
    """Show time predictions for multiple stops specified by an array of 
    stop/route tags. Use the 'r' parameter suffixed with empty brackets as the key (r[]),
    and seperate route tags from stop tags with a vertical pipe delimited with commas (routeTag|stopTag)."""
    params = utils.qs_params(   command='predictionForMultiStops',
                                data=request.args   )
    resp=proxy_pass(params=params)
    jdata=xmltodict.parse(resp.content, dict_constructor=dict)
    stats.put_stats(response=resp, request=request)
    return jsonify(jdata)

@app.route('/routes/<routeTag>/schedule')
@stats.ratelimit()
@utils.gzipped
def routes_schedule(routeTag):
    """Return predictions for """
    params = utils.qs_params(   command='schedule',
                                data=request.args,
                                r=routeTag  )
    resp=proxy_pass(params=params)
    jdata=xmltodict.parse(resp.content, dict_constructor=dict)
    stats.put_stats(response=resp, request=request)
    return jsonify(jdata)

@app.route('/routes/messages')
@stats.ratelimit()
@utils.gzipped
def routes_messages():
    """Returns currently active messages and notifications for routes specified by parameter 'r'. 
    If you want to specify multiple routes, use the 'r[]' key in the query string. If no routes are
    specified, all active messages will be returned."""
    params = utils.qs_params(   command='messages',
                                data=request.args   )
    resp=proxy_pass(params=params)
    jdata=xmltodict.parse(resp.content, dict_constructor=dict)
    stats.put_stats(response=resp, request=request)
    return jsonify(jdata)

@app.route('/routes/<routeTag>/vehicles')
@stats.ratelimit()
@utils.gzipped
# TODO: timeparser
def vehicle_locations_route(routeTag):
    """Returns currently acitve vehicles for specified routeTag."""
    params = utils.qs_params(   command='vehicleLocations',
                                data=request.args,
                                r=routeTag              )
    resp=proxy_pass(params=params)
    jdata=xmltodict.parse(resp.content, dict_constructor=dict)
    stats.put_stats(response=resp, request=request)
    return jsonify(jdata)

@app.route('/routes/offhours/<timewindow>')
@stats.ratelimit()
@utils.gzipped
# TODO: timeparser
def routes_off_hours(timewindow):
    """Returns all routes that are not running during the specified time frame. 
    Under construnction :( """
    params = utils.qs_params(   command='vehicleLocations',
                                data=request.args,
                                r=routeTag              )
    resp=proxy_pass(params=params)
    jdata=xmltodict.parse(resp.content, dict_constructor=dict)
    stats.put_stats(response=resp, request=request)
    return jsonify(jdata)

@app.route('/endpoints')
@stats.ratelimit(limit=200, per=10)
@utils.gzipped
def endpoints_list():
    """Return all endpoints and the corresponding paths exposed in this api."""
    func_list = {}
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            endpoint_key = app.view_functions[rule.endpoint].__name__
            func_list[endpoint_key] = {}
            func_list[endpoint_key]['rule'] = rule.rule
            func_list[endpoint_key]['description'] = app.view_functions[rule.endpoint].__doc__
    return jsonify(func_list)

@app.route('/endpoints/stats/<endpoint>')
@stats.ratelimit(limit=200, per=10)
@utils.gzipped
# TODO: timeparser
def endpoints_stats(endpoint):
    """Returns a stats object which lists the total bytes and total hits of each endpoint\
    beginning from the last time application was started."""
    return jsonify(stats.get_counts(endpoint))

@app.route('/endpoints/stats/slow')
@stats.ratelimit(limit=200, per=10)
@utils.gzipped
def stats_slowqueries():
    """Returns most recent queries which exceeded the 'slow_threshold'\n
    parameter. Parameter can be adjusted in the config.py file. 
    The default number of queries returned is 30, use row_limit parameter to adjust."""
    if request.args and request.args['row_limit']:
        row_limit = int(request.args['row_limit'])
    else:
        row_limit = 30
    return jsonify(stats.get_slow_queries(row_limit=row_limit))

if __name__ == '__main__':
    app.run(host=HOST, port=int(PORT))

