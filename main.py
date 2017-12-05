import logging
from flask import request

from flask import Flask, render_template, jsonify
import pymongo
from bson.json_util import dumps
import json
from pymongo import MongoClient
import math
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

    # tempdict = {}
    d = request.get_json()
    username = d['Username']
    password = d['Password']
    
    cursor = hail.find({"Username":username})

    for doc in cursor:
        tempdict = doc

    if tempdict["Password"] == password:

        return dumps(True)
    else:
        return dumps(False)
    

# When adding a job, send a json object with "Username" and "Job", capitalized
# {"Username": "new",
# "Description": "Piano",
# "Size": "Medium",
# "From": [0, 0],
# "To": [100, 100]
# }
@app.route('/createjob', methods = ['POST'])

def addjob():

    global n

    d = request.get_json()
    username = d['Username']
    j = d['Description']
    size = d['Size']
    f = d['From']
    t = d['To']

    hail.update_one(
        {"Username":username},
        {
            '$push': {'jobID': n}
        }
    )

    job.insert_one(
        {
            "jobID":n,
            "jobcontent":j,
            "trucksize": size,
            "from": f,
            "to": t
        }
    )
    n += 1

    closest = findclosest(f, username)
    
    return dumps(closest)


def findclosest(f, username):

    cursor = drive.find()
    tempdict = {}

    for doc in cursor:
        
        tempdict[doc['Name']] = []
        tempdict[doc['Name']].append(doc['Location'])

    for val in tempdict.values():
        val.append(caldist(val[0],f))
    
    l = sorted(tempdict, key=lambda k: tempdict[k][1])
    

    # Before Adding the 4 drivers, add the user pic first

    cursor_user = hail.find({"Username":username})
    p = {}
    for profile in cursor_user:
        p = profile


    result = []
    result.append(p['Pic'])

    for i in range(4):
        tempdrive = drive.find({"Name":l[i]})
        result.append(tempdrive)

    return result


def caldist(driverloc, jobloc):
    
    return math.sqrt(((driverloc[0] - jobloc[0]) ** 2) + ((driverloc[1] - jobloc[1]) ** 2))


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
