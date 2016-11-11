#!/usr/bin/env python
#    _ __     ___  __  __ | |_   
#   | '_ \   / _ \ \ \/ / | __|  
#   | | | | |  __/  >  <  | |_   
#   |_| |_|  \___| /_/\_\  \__|  
#   | |__    _   _   ___   / _|  
#   | '_ \  | | | | / __| | |_   
#   | |_) | | |_| | \__ \ |  _|  
#   |_.__/   \__,_| |___/ |_|    
#  
#	@adam.ossowski
#	http://flask.pocoo.org/docs/0.11/config/#builtin-configuration-values
[flask]
proto = http://
host = localhost
port = 8889
thread = False

[nextbus]
proto = http://
host = webservices.nextbus.com
path = /service/publicXMLFeed
agency = sf-muni

[rate-limiter]
time = 30
limit = 1

[gzip]
compression = 3

[slow_queries]
threshold = .5
hostname = macosx

[redis]
#host = redis
host = 0.0.0.0
port = 6379

[logging]
log_path = /var/log/
log_name = sfmuni.log
