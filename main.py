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
drive = db.Drivers
job = db.Jobs



if job.count() == 0:
    n = 0

else:
    cur = job.find_one(sort=[("jobID", -1)])
    n = cur['jobID'] + 1

    # Magical annotations define URL routing via the Flask application

@app.route('/')
def home_page():

    temp = []
    cursor = hail.find()
    for doc in cursor:
        temp.append(doc)
        
    return dumps(temp)


@app.route('/phone', methods = ['POST'])
def checknum():
    
    num = request.form['num']

    return dumps(num)


@app.route('/add', methods = ['POST'])

def addrec():

    d = request.get_json()
    d['jobID'] = []
    hail.insert_one(d)

    
    return dumps(0)


@app.route('/checkpasswd', methods = ['POST'])

def auth():

    tempdict = {}
    d = request.get_json()
    username = d['Username']
    password = d['Password']
    
    cursor = hail.find({"Username":username})

    for doc in cursor:
        tempdict = doc
    if tempdict["password"] == password:

        return dumps(True)
    else:
        return dumps(False)
    

# When adding a job, send a json object with "Username" and "Job", capitalized
@app.route('/createjob', methods = ['POST'])

def addjob():

    global n

    d = request.get_json()
    username = d['Username']
    j = d['Job']

    hail.update_one(
        {"Username":username},
        {
            '$push': {'jobID': n}
        }
    )

    job.insert_one(
        {
            "jobID":n,
            "jobcontent":j
        }
    )
    
    n += 1
    return dumps(j)



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
