# RedisProxyServer

RedisProxyServer is a Redis proxy application built on Flask in Python. The application allows for creation of key/value pairs that can be stored on Redis and on a local cache (Memcache). 

The application works as follows.
* GET Request - A specified key is checked against the local cache to see if it exists there. It is fetched if it does. If it does not, the key is then checked in the Redis store to see if it exists there. If it does exist there, the associated value is fetched back and the key/value pair is added to the local cache. Subsequent queries for the same key will return the value for the key from the local cache.
* POST Request - A POST indicates a Setting of specified key/value pair. The key is checked against the local and redis caches and the key/value pair is inserted. A check is performed to see if the key does exist in the local and redis stores and an appropriate message is displayed indicating the value is being overwritten.

###Configurable Options
A global expiration time of 300s is set in the constants.py for the local cache. As I am using memcache, the threshold
 (capacity) is not configurable, If I switch that to SimpleCache (for single process environments), I will be
  able to provide a configurable option for the threshold.
The expiration time for each Redis key is set to 3000 in the constants.py file
Memcached, Redis host and port configuration is also configurable as they are in the constants.py file.

I have also included a way to set/get the key value pairs using a web form. Once Flask starts, the form can be accessible at http://<configured_host>:8000
 
## Installation

* Clone github repo (or use archive containing project)
* Install dependencies using pip (requirements.txt included)


### Dependencies
- python 3.7.4 (May be usable with lower 3.x versions. Tested with 3.7.4)
- requests==2.23.0
- redis==3.4.1
- python-memcached==1.59
- Flask==1.1.1
- Flask-Caching==1.8.0
- Flask-Ext==0.1
- gunicorn==20.0.4
- Werkzeug==0.15.4

### Files
Main app - RedisProxyServer/app.py. This file contains the get/set functions that are called by the GET/POST calls respectively.

Helper functions - RedisProxyServer/module/helper.py. This file contains the helper methods that are created to mitigate the repetitive tasks performed by the form GET/SET and the explicit GET/SET calls.

Template files for web forms (results.html and index2.html)

```

## Start Flask using Gunicorn

cd to RedisProxyServer directory

``` Run gunicorn -w 3 -b 127.0.0.1:8000 app:app
    (or FLASK_APP=app python app.py)

Launch browser session for updating and retrieving key/value pairs at
 http://127.0.0.1:8000
(see screenshots folder)

Examples using Curl. GET is performed at the root '/' endpoint. POST is performed at '/set' endpoint.$ curl -X GET http://localhost:8000?key=doom

{
  "message": "<br>Key not found in local cache<br>Key not found in redis cache"
}
$ curl -X POST http://localhost:8000/set -d '{"doom": "Dr Vaughn"}' -H 'Content-Type: application/json'
{
  "Key": "doom", 
  "Value": "Dr Vaughn", 
  "message": "<br>Key not found in local cache<br>Setting key in local cache<br>Key not found in redis cache<br>Setting key in redis cache", 
  "status": "successful"
}
$ curl -X GET http://localhost:8000?key=doom{
  "Key": "doom", 
  "Value": "Dr Vaughn", 
  "message": "<br><b>Key found in local cache</b>", 
  "status": "successful"
}
$ curl -X GET http://localhost:8000?key=shazia
{
  "Key": "shazia", 
  "Value": "sana", 
  "message": "<br>Key not found in local cache<br><b>Key found in redis cache</b>", 
  "status": "successful"
}
$ curl -X GET http://localhost:8000?key=shazia
{
  "Key": "shazia", 
  "Value": "sana", 
  "message": "<br><b>Key found in local cache</b>", 
  "status": "successful"
}
```