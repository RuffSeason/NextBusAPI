import os 
import sys 
import time
import json
import xmltodict
import requests as r
from extensions import stats, utils
from flask import Flask, Response, request, url_for, g, jsonify

app = Flask(__name__)

def proxy_pass(**kwargs):
    BEURL='http://127.0.0.1:8888/xmlproxy'
    proto = "http://"
    host = "webservices.nextbus.com"
    path = "/service/publicXMLFeed"
    qs=utils.qs_encode(kwargs['params'])
    url=proto + host + path + "?" + qs
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
    """Configuration Route - Fetches a list of all route and their information
    available in given agency using the nextbus API service"""
    params = utils.qs_params(command='routeList',data=request.args)
    resp=proxy_pass(params=params)
    jdata=xmltodict.parse(resp.content, dict_constructor=dict)
    #jbody=json.dumps(jdata,indent=1)
    stats.put_stats(response=resp, request=request)
    return Response(jbody, mimetype='application/json')

@app.route('/routes/<routeTag>')
@stats.ratelimit()
@utils.gzipped
def routes_config(routeTag):
    """ Grabs a list of all r"""
    params = utils.qs_params(   command='routeConfig',
                                data=request.args,
                                r=routeTag  )
    resp=proxy_pass(params=params)
    jdata=xmltodict.parse(resp.content, dict_constructor=dict)
    jbody=json.dumps(jdata,indent=1)
    stats.put_stats(response=resp, request=request)
    return Response(jbody, mimetype='application/json')

@app.route('/stops/<stopId>/predictions')
@stats.ratelimit()
@utils.gzipped
def predictions_stopId(stopId):
    """Show prediction by route of stopId (non-unique)
    stop identifier - least specific"""
    params = utils.qs_params(   command='predictions',
                                data=request.args,
                                stopId=stopId  )
    resp=proxy_pass(params=params)
    jdata=xmltodict.parse(resp.content, dict_constructor=dict)
    jbody=json.dumps(jdata,indent=1)
    stats.put_stats(response=resp, request=request)
    return Response(jbody, mimetype='application/json')

@app.route('/stops/<stopId>/routes/<routeTag>/predictions')
@stats.ratelimit()
@utils.gzipped
def predictions_stopId_and_route(stopId,routeTag):
    """ Show prediction by route of stopId (non-unique) and 
        unique route tag - mid specific """
    params = utils.qs_params(   command='predictions',
                                data=request.args,
                                stopId=stopId,
                                r=routeTag  )
    resp=proxy_pass(params=params)
    jdata=xmltodict.parse(resp.content, dict_constructor=dict)
    jbody=json.dumps(jdata,indent=1)
    stats.put_stats(response=resp, request=request)
    return Response(jbody, mimetype='application/json')

@app.route('/routes/<routeTag>/stops/<stopTag>/predictions')
@stats.ratelimit()
@utils.gzipped
def predictions_stopTag_and_route(routeTag,stopTag):
    """ Show prediction by route of stopId (non-unique) and 
        unique route tag - most specific    """
    params = utils.qs_params(   command='predictions',
                                data=request.args,
                                r=routeTag,
                                s=stopTag   )
    resp=proxy_pass(params=params)
    jdata=xmltodict.parse(resp.content, dict_constructor=dict)
    jbody=json.dumps(jdata,indent=1)
    stats.put_stats(response=resp, request=request)
    return Response(jbody, mimetype='application/json')

@app.route('/tuples/predictions')
@stats.ratelimit()
@utils.gzipped
def predictions_for_multi_stops():
    """Show prediction of an array of stop/route tags in a 
    stops array. This is contained in the params payload."""
    params = utils.qs_params(   command='predictionForMultiStops',
                                data=request.args   )
    resp=proxy_pass(params=params)
    jdata=xmltodict.parse(resp.content, dict_constructor=dict)
    jbody=json.dumps(jdata,indent=1)
    stats.put_stats(response=resp, request=request)
    return Response(jbody, mimetype='application/json')

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
    jbody=json.dumps(jdata,indent=1)
    stats.put_stats(response=resp, request=request)
    return Response(jbody, mimetype='application/json')

@app.route('/routes/messages')
@stats.ratelimit()
@utils.gzipped
def routes_messages():
    """  """
    params = utils.qs_params(   command='messages',
                                data=request.args   )
    resp=proxy_pass(params=params)
    jdata=xmltodict.parse(resp.content, dict_constructor=dict)
    jbody=json.dumps(jdata,indent=1)
    stats.put_stats(response=resp, request=request)
    return Response(jbody, mimetype='application/json')

@app.route('/routes/<routeTag>/vehicles')
@stats.ratelimit()
@utils.gzipped
# TODO: timeparser
def vehicle_locations_route(routeTag):
    """   """
    params = utils.qs_params(   command='vehicleLocations',
                                data=request.args,
                                r=routeTag              )
    resp=proxy_pass(params=params)
    jdata=xmltodict.parse(resp.content, dict_constructor=dict)
    jbody=json.dumps(jdata,indent=1)
    stats.put_stats(response=resp, request=request)
    return Response(jbody, mimetype='application/json')

@app.route('/routes/offhours/<timewindow>')
@stats.ratelimit()
@utils.gzipped
# TODO: timeparser
def routes_off_hours(timewindow):
    """   """
    params = utils.qs_params(   command='vehicleLocations',
                                data=request.args,
                                r=routeTag              )
    resp=proxy_pass(params=params)
    jdata=xmltodict.parse(resp.content, dict_constructor=dict)
    jbody=json.dumps(jdata,indent=1)
    stats.put_stats(response=resp, request=request)
    return Response(jbody, mimetype='application/json')

@app.route('/endpoints')
@stats.ratelimit(limit=200, per=10)
@utils.gzipped
def endpoints_list():
    """Return all endpoints/mapped_functions available to this api."""
    func_list = {}
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            endpoint_key = app.view_functions[rule.endpoint].__name__
            func_list[endpoint_key] = {}
            func_list[endpoint_key]['rule'] = rule.rule
            func_list[endpoint_key]['description'] = app.view_functions[rule.endpoint].__doc__
    return Response(json.dumps(func_list), mimetype='application/json')

@app.route('/endpoints/stats')
@stats.ratelimit(limit=200, per=10)
@utils.gzipped
# TODO: timeparser
def stats_endpoints(timewindow):
    """Returns a stats object which lists the total bytes and total hits of each endpoint
    beginning from the last time application was started."""
    #stats.put_stats(response=resp, request=request)
    return jsonify({"stats":None})

@app.route('/endpoints/stats/slow')
@stats.ratelimit(limit=200, per=10)
@utils.gzipped
def stats_slowqueries(row_limit=30):
    """Returns most recent queries which exceeded the 'slow_threshold'
    parameter. The parameter can be adjusted in the sfmuni.conf file. 
    More rows can be returned by increasing the row_limit parameter."""
    #stats.put_stats(response=resp, request=request)
    return jsonify({"stats":None})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(8889), threaded=True)