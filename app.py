# -*- coding: utf-8 -*-

"""
RedisProxyServer.app
~~~~~~~~~~~~~~~~~~~~

Server hosted using Flask for allowing GET/POST calls to set key value in an upstream Redis instance. If the key
does not exist on a local cache (memcache), it is set accordingly.
Aside from using REST GET/POST calls to manage the key value pairs, there is another mechanism provided to get and set
the values using a web form.
The Flask application can be started directly by running python 3 on this file (app.py)
i.e 'python app.py' (NOTE you may need to set the FLASK_APP=app.py environment variable prior to starting the server)
The application can also be started using gunicorn, i.e 'gunicorn -w 2 -b 127.0.0.1:8000 app:app'

"""
from config import constants
from module import helper

import argparse
from flask import Flask, request, render_template, jsonify

app = Flask(__name__)

# settings kept in config folder under project root
app.config.from_object('config.settings')

# bootstrapping for redis and memcache for use with python
c = helper.CacheInit()


@app.route('/set', methods=['POST'])
def set():
    """
    Method to set key/value pairs in Redis and local memcache.
    :rtype: json | flask response
    """

    if request.method == 'POST':
        # This is when we receive a POST request with a dictionary payload depicting the key/value pair
        kv_ds = request.get_json()
        if kv_ds:
            # Get the key of a dict with single key/value
            key = next(iter(kv_ds))
            value = kv_ds[key]
        else:
            # Here is where we may instead expect a key/value pair submitted using a webform
            key = request.form.get('key_to_save')
            value = request.form['retrieved_value']

        # Helper class
        ch = helper.CacheHelper()

        message = ""
        if not key or key is None:
            message = "<br>No key provided!"
        if not value or value is None:
            message += "<br>No Value provided!"
        if message != "":
            return render_template('results.html', key=key, value=value, message=message)

        # Get details and value for key. c.cache is the memcache object
        l_value, l_message = ch.check_key_in_local_cache(key, c.cache)
        # If value exists, appending the overriding string
        if l_value:
            l_message += " Overriding!"
        else:
            l_message += "<br>Setting key in local cache"

        # c.redis is the redis object
        r_value, r_message = ch.check_key_in_redis_cache(key, c.redis)
        if r_value:
            r_message += " Overriding!"
        else:
            r_message += "<br>Setting key in redis cache"
        # When running a POST, according to the requirements, we need to update both local and redis caches with the k/v
        # pairs
        c.cache.set(key, value)
        c.redis.set(key, value, ex=constants.REDIS_EXPIRE)
        message = message + l_message + r_message

        # If this is a POST request using curl or any other means, provide the response
        if kv_ds:
            data = {"status": "successful", "Key": key, "Value": value, "message": message}
            return jsonify(data)
        else:
            # Return response back to the Web form
            return render_template('results.html', key=key, value=value, message=message)
    return render_template('index2.html')


@app.route('/', methods=['GET', 'POST'])
def get():
    """
    GET method for retrieving the key value pairs.
    :return:
    """
    if request.method == 'POST':
        # Check if key is being Posted using the web form. Treat accordingly.
        key = request.form.get('get_key')
        if not key or key is None:
            return render_template('results.html', key=key, message="""<br>Key not found!""")

        # Helper function to obfuscate repeated logic for setting/getting the data
        value, message = helper.CacheHelper.get_key_logic(key, c.cache, c.redis)
        if value:
            return render_template('results.html', key=key, value=value, message=message)
        else:
            return render_template('results.html', key=key, message=message)
    # This is when we pass in a key in a GET request
    # i.e curl -X GET http://localhost:8000?key=mykey1
    api_key = request.args.get('key')
    if not api_key:
        return render_template('index2.html')
    else:
        key = api_key
        value, message = helper.CacheHelper.get_key_logic(key, c.cache, c.redis)
        if value:
            data = {"status": "successful", "Key": key, "Value": value, "message": message}
        else:
            data = {"message": message}
        return jsonify(data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    app.run(port=8000)
