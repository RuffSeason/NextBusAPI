#!/usr/bin/env bash
#    _ __     ___  __  __ | |_   
#   | '_ \   / _ \ \ \/ / | __|  
#   | | | | |  __/  >  <  | |_   
#   |_| |_|  \___| /_/\_\  \__|  
#   | |__    _   _   ___   / _|  
#   | '_ \  | | | | / __| | |_   
#   | |_) | | |_| | \__ \ |  _|  
#   |_.__/   \__,_| |___/ |_|    
#  

## FLASK
export FLASK_PROTO=http://
export FLASK_HOST=localhost
export FLASK_PORT=8000
export FLASK_THRD=False

## NEXTBUS
export BE_PROTO=http://
export BE_HOST=webservices.nextbus.com
export BE_PATH=/service/publicXMLFeed
export BE_AGENCY=sf-muni

## RATE-LIMITER
export RLIMIT_COUNT=1
export RLIMIT_PER=30

## GZIP
export COMPRESSION=3

## SLOW_QUERIES
export SQ_THRESHOLD=.5

## LOGGING
export LOG_PATH=/var/log
export LOG_NAME=nextbus.log