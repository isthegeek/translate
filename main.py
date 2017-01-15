import logging
import argparse
import base64
import json
import os
import subprocess
import datetime
import time
import requests

from flask import Flask, render_template, request, jsonify
from flask.ext.pymongo import PyMongo
from werkzeug import secure_filename
from googleapiclient import discovery
import httplib2
from oauth2client.client import GoogleCredentials
import xml.etree.ElementTree as etree
from dicttoxml import dicttoxml

app = Flask(__name__)

# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = 'uploads/'
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_MIMETYPE'] = set(['audio/wav'])

#Initialise Pymongo connection to MLAB
app.config['MONGO3_HOST'] = 'ds145848.mlab.com'
app.config['MONGO3_PORT'] = 45848
app.config['MONGO3_DBNAME'] = 'plivo-translate'
app.config['MONGO3_USERNAME'] = 'isthegeek'
app.config['MONGO3_PASSWORD'] = 'isthegeek'
mongo = PyMongo(app, config_prefix='MONGO3')

@app.route('/')
def index():
    return render_template('main_input_form.html')

@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file_to_convert']
    file_language = request.form['language']
    if file and file.content_type in app.config['ALLOWED_MIMETYPE']:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename + '.wav'))
        files = {'file_to_convert': open('uploads/'+filename + '.wav', 'rb')}
        r = requests.post('http://localhost:5000/upload', files = files, data = {'language':file_language})
        json_data = json.loads(r.text)
        return jsonify(text=json_data['text'], translated_text=json_data['translated_text'])

@app.route('/insert', methods=['POST'])
def insert():
    increase_id = mongo.db.counters.insert({'seq' : mongo.db.counters.count()+1})
    document_count = mongo.db.counters.count()
    ts = time.time()
    timenow = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    data = {
        'id' : document_count,
        'translated_text': request.form['translated_text'],
        'text' : request.form['text'],
        'timestamp' : timenow
    }
    query = mongo.db.users.insert(data)
    return 'OK'

# Route to access all the data of db.
@app.route('/history', methods=['GET'])
def retrieve():
    data = list(mongo.db.users.find({},{'_id': False}))
    xmldata = dicttoxml(data, custom_root='plivo-translate', attr_type=False)
    parsedData = []
    root = etree.fromstring(xmldata)

    for item in root.findall('item'):
        parsedData.append([ item.find('id').text,item.find('text').text,item.find('translated_text').text, item.find('timestamp').text])
    return render_template('history.html', xmldata=xmldata, parsedData=parsedData)

if __name__ == "__main__":
    app.run(port=5004)
