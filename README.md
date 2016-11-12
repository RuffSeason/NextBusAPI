# NextBus RESTful API

### Installation

To run as a docker container cd into the directory which you pulled the repo into and:
```sh
$ docker-compose build
$ docker-compose up -d
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

## Configuration
```
/config.py
```
- **flask** - change the host, port, proto and threading mode of flask web application
- **nextbus** - contains all the nextbus xml feel url components (dont need to change)
- **rate-limiter** - decrease / increase the ratelimiting parameters on all of the non-internal endpoints. Current default is set at 1 request / 30 seconds / endpoint-params
- **gzip** - adjust the compression ratio of gzip module (lowest=1, highest=9)
- **slow_queries** - adjust the time (ms) threshold that defines a slow_query (default .5), if a given query exceeds this value, it will be logged into the redis SLOW_QUERIES hash and accessible via the /stats/slow endpoint
- **redis** - adjust the redis hostname and listening ports
- **logging** - adjust the output directory and path

## SF-Muni NextBus Endpoints
Endpoints and brief descriptions can be listed via the /endpoints endpoint
```sh
$ curl http://localhost:8889/endpoints
```
Each object contains the actual endpoint name, endpoint rule (url structure), and description.

#### routes_list  
`/routes` : Provides a list off all the NextBus routes by name and tag.
- verbose = true,false
- terse = true,false

#### routes_config 
`/routes/<routeTag>`: Provides more detailed configuration info for a given routeTag, including stopId, stopTag, 
- verbose = true,false
- terse = true,false

#### routes_messages
`/routes` : Provides a list off all the NextBus routes by name and tag, use `r` key in query string to specify route tag.
- `r` = for one routeTag: `r=N_OWL`
- `r[]` = for multiple routeTags, seperated by a comma: `r[]=N_OWL,45,61`
```sh
$ curl "http://127.0.0.1:8889/routes/messages?r\[\]=T_OWL,61"
```
- `verbose` = true,false
- `terse` = true,false


#### routes_schedule
`/routes/<routeTag>/schedule` : Returns the routes' timetable, grouped into direction, and schedule class groups. 
- verbose = true,false
- terse = true,false

#### predictions_stopId
`/stops/<stopId>/predictions` : Show prediction by route with stopId only - least specific
- verbose = true,false
- terse = true,false 

#### predictions_stopId_and_route
`/stops/<stopId>/routes/<routeTag>/predictions` : Show prediction by route with stopId and routeTag - mid specific . 
- verbose = true,false
- terse = true,false

#### predictions_stopTag_and_route
`/routes/<routeTag>/stops/<stopTag>/predictions` : Show prediction by routes with routeTag and stopId - most specific.
- verbose = true,false
- terse = true,false

#### vehicle_locations_route
`/routes/<routeTag>/vehicles` : Returns currently acitve vehicles for specified routeTag. 
- verbose = true,false
- terse = true,false

## Stats-API Endpoints
#### endpoints_stats
`/endpoints/stats/<endpoint>` : Returns a stats object which lists the total bytes and total hits of each endpoint beginning from the last time application was started. 
- verbose = true,false
- terse = true,false

#### stats_slowqueries
`stats_slowqueries` : Returns most recent queries which exceeded the 'slow_threshold' parameter. Parameter can be adjusted in the config.py file. The default number of queries returned is 30, use row_limit parameter to adjust.
- row_limit = used to change the number of rows returned sorted in descending order by time of query: `row_limit=40`
- verbose = true,false
- terse = true,false
