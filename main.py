import logging
from flask import request

from flask import Flask, render_template, jsonify
import pymongo
from bson.json_util import dumps
import json
from pymongo import MongoClient
# from flask_pymongo import PyMongo


# This defines a Flask application
app = Flask(__name__)
MONGODB_URI = 'mongodb://test:test@ds119446.mlab.com:19446/joesecretcloset'
client = MongoClient(MONGODB_URI, connectTimeoutMS=30000)
db = client.joesecretcloset
hail = db.Hailers

    # Magical annotations define URL routing via the Flask application

@app.route('/')
def home_page():
        # online_users = mongo.db.user.find({'Name': 'Joe'})
        # docs = list(online_users)
    temp = []
    for data in hail.find():
        temp.append(data)
    
        
    output = hail.find({"Name" : "Joe"})
        
    return dumps(temp)

# @app.route('/add/<phone>', methods = ['POST'])
# def check_num_exist(phone):
	# names.append(username)
	# return '{} added'.format(username)

@app.route('/phone', methods = ['POST'])
def checknum():
    
    num = request.form['num']

    return dumps(num)
    # if num == '12345':
    #     return dumps('true')

    # else:
    #     return dumps('false')


@app.route('/add', methods = ['POST'])
def addrec():

    d = request.get_json()
    hail.insert_one(d)
    
    return dumps(0)


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


# This allows you to run locally.
# When run in GCP, Gunicorn is used instead (see entrypoint in app.yaml) to
# Access the Flack app via WSGI
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
