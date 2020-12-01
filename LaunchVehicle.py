import sys
import requests
import apscheduler
from apscheduler.schedulers.background import BackgroundScheduler
import argparse
import time
import subprocess
from threading import Thread
from time import sleep
import json

# Configure parser and arguments required
parser = argparse.ArgumentParser()
parser.add_argument('--name', '-n', help="name of launch vehicle", type= str)
parser.add_argument('--orbit', '-o', help="radius of orbit (in kms)", type= int, default= 0)
parser.add_argument('--payload-config', '-p', help="payload config file", type= str)

# Parse the arguments recieved from DSN
args = parser.parse_args()

# Time To Orbit
global time_to_orbit
time_to_orbit = (args.orbit/3600) + 10

def timer():
    global time_to_orbit
    while time_to_orbit > 0:
        time_to_orbit = time_to_orbit - 1
        sleep(1)
    update_dsn('')

# Function to Send Telemetry to DSN
def send_telemetry_to_dsn(data=''):
    global time_to_orbit

    # Telemetry Data
    telemetry_data = {"altitude": 400, "longitude": -45.34, "latitude": -28.34, "temperature": 340, "timeToOrbit": time_to_orbit}
    resp = requests.get('http://{0}:{1}/{2}'.format('localhost', '5344', '/launch-vehicle/capture-telemetry?name='+args.name+'&data='+json.dumps(telemetry_data)))

def countdown_timer():
    global time_to_orbit
    time_to_orbit = time_to_orbit - 1

# Function to send update to DSN that it has reached orbit
def update_dsn(data=''):
    resp = requests.get('http://{0}:{1}/{2}'.format('localhost', '5344', '/launch-vehicle/update-status?name='+args.name+'&data=' + str(data)))

def create_payload(name, type):
    resp = requests.get('http://{0}:{1}/{2}'.format('localhost', '5344', '/launch-vehicle/create-payload?name=' + name + '&type=' + type))

t1 = Thread(target=timer)
t1.start()

# Accept command from DSN
data = sys.stdin.readline()

# Schedule a Background Scheduler to send data to DSN periodically at an interval
scheduler = BackgroundScheduler()
job = scheduler.add_job(send_telemetry_to_dsn, 'interval', args=[args.name], seconds=1)

#timer = BackgroundScheduler()
#timer_job = timer.add_job(countdown_timer, 'interval', seconds=1)
#timer.start()

while data.strip() != 'DEORBIT':
    if data.strip() == 'StartTelemetry':
        if scheduler.state == 1:
            scheduler.resume()
        else:
            try:
                scheduler.start()
            except:
                scheduler.resume()
    if data.strip() == 'StopTelemetry':
        scheduler.pause()

    if data.strip() == 'DeployPayload':
        import json
        f = open(args.payload_config)
        payload_config = json.load(f)
        create_payload(payload_config['Name'], payload_config['Type'])

    data = sys.stdin.readline()