#!/usr/bin/env python
import json
import gzip
import functools 
from datetime import datetime
from flask import after_this_request, request
from cStringIO import StringIO as IO

def qs_params(command, data, **kwargs):
    """allowed kwargs are [r,s,stopId,t]"""
    param = {}
    param['command'] = command
    param['a'] = 'sf-muni'
    # iterate through query string params from client
    for k,v in data.iteritems():
        # identify if the key is array
        if k.endswith('[]') is True:
            param[k] = v.split(',')
        else:
            param[k]=v
    # add all url parameters to the params from fe_app
    for k,v in kwargs.iteritems():
        param[k] = v
    # return param as json - passed as data to be_app
    return param
    
def qs_encode(data, **kwargs):
    # parses fe_app data object into encoded querystring
    qs_list = [] 
    # parameters should always be in same order so using sorted(lists)
    for key in sorted(list(data)): 
        # check if key contains a list (array)
        if key.endswith('[]') is True:
            key_str=key.replace('[]','')
            sub_qs_str = '&'.join([ "%s=%s" % (key.replace('[]',''),item) for item in sorted(data[key])])
            qs_list.append(sub_qs_str)
        # if its not a list, will be string
        else:
            qs_list.append("%s=%s" % (key,data[key]))
    # convert into one large querystring
    qs_string = '&'.join(sorted(qs_list))
    return qs_string

def gzipped(f):
    @functools.wraps(f)
    def view_func(*args, **kwargs):
        @after_this_request
        def zipper(response):
            accept_encoding = request.headers.get('Accept-Encoding', '')

            if 'gzip' not in accept_encoding.lower():
                return response

            response.direct_passthrough = False

            if (response.status_code < 200 or
                response.status_code >= 300 or
                'Content-Encoding' in response.headers):
                return response
            gzip_buffer = IO()
            gzip_file = gzip.GzipFile(mode='wb', 
                                      fileobj=gzip_buffer,
                                      compresslevel=9)
            gzip_file.write(response.data)
            gzip_file.close()

            response.data = gzip_buffer.getvalue()
            response.headers['Content-Encoding'] = 'gzip'
            response.headers['Vary'] = 'Accept-Encoding'
            response.headers['Content-Length'] = len(response.data)

            return response

        return f(*args, **kwargs)

    return view_func
