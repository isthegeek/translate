import logging
import argparse
import base64
import json
import os
import subprocess

from flask import Flask, render_template, request
from werkzeug import secure_filename
from googleapiclient import discovery
import httplib2
from oauth2client.client import GoogleCredentials

DISCOVERY_URL = ('https://{api}.googleapis.com/$discovery/rest?'
                 'version={apiVersion}')
app = Flask(__name__)

# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = 'uploads/'
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['wav'])

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('main_input_form.html')

@app.route('/test', methods=['POST'])
def test():
    print request.form['language']

@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500


if __name__ == "__main__":
    app.run(port=5002)
