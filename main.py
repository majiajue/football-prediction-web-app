from flask import Flask, render_template, url_for, request, redirect, session
from flask_apscheduler import APScheduler

from datetime import datetime
import string
import time
import datetime
import os

from update import updatePredictions
from aws import downloadFileAWS

# AWS access
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
BUCKET_NAME = os.environ.get('S3_BUCKET')
fpath = "static/predicted.txt"

downloadFileAWS(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, BUCKET_NAME, fpath)

app = Flask(__name__)
scheduler = APScheduler()

firstSeason = 0
firstSeasonTest = 19
lastSeason = 19

def updatePredictionsRef(): 
    updatePredictions(
        download=True, 
        preprocess=True, 
        predictYN=True, 
        leagues=leagues,
        firstSeason=firstSeason, 
        firstSeasonTest=firstSeasonTest, 
        lastSeason=lastSeason, 
        train=False
    )

leagues = {
    'E0': 5,
    'D1': 6,
    'I1': 5,
    'SP1': 5,
    'F1': 5,
    'E1': 5,
    'P1': 17,
    'N1': 17
}

@app.route('/', methods=['POST','GET'])
def index():
    return render_template('index.html')

# hidden feature for emergency data refresh, /refreshData after URL. If you see this, please don't abuse this link :) Thanks!
@app.route('/refreshData', methods=['POST','GET'])
def indexRefresh():
    updatePredictionsRef()
    return redirect('/')

app.secret_key = 'SECRET KEY'

if __name__ == "__main__":

    scheduler.add_job(
        id='dataRefresh_main',
        func = updatePredictionsRef, trigger='cron', hour='19', minute='00'
    )
    scheduler.start()

    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True,use_reloader=False)