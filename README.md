# NextBus RESTful API

### Installation 

To run as a docker container cd into the directory which you pulled the repo into and:
```sh
$ docker-compose build 
$ docker-compose -d up 
```

To run as a native application without docker, cd into the project directory
```sh
$ export PYTHON_PATH=./extenstions/
$ pip install -r requirements.txt
```
To initialize the server 
```sh
$ python server.py
```
Or using gunicorn you for concurrency (adjusting -w parameter)
```sh
$ gunicorn server:app -k gevent -w 4
```

### Configuration
```
/config.py
```
flask - change the host, port, proto and threading mode of flask web application
nextbus - contains all the nextbus xml feel url components (dont need to change)
rate-limiter - decrease / increase the ratelimiting parameters on all of the non-internal endpoints. Current default is set at 1 request / 30 seconds / endpoint-params
gzip - adjust the compression ratio of gzip module (lowest=1, highest=9)
slow_queries - adjust the time (ms) threshold that defines a slow_query, if a given query exceeds this value, it will be logged into the redis SLOW_QUERIES hash and accessible via the /stats/slow endpoint
redis - adjust the redis hostname and listening ports
logging - adjust the output directory and path

### Endpoints
Endpoints and brief descriptions can be listed via the /endpoints endpoint
```sh
$ curl http://localhost:8889/endpoints
```
Each object contains the actual endpoint name, endpoint rule (url structure), and description.

