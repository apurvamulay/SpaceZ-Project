import sys
import requests
import apscheduler
from apscheduler.schedulers.background import BackgroundScheduler
import argparse
import time
import subprocess
import json

# Configure parser and arguments required
parser = argparse.ArgumentParser()
parser.add_argument('--name', '-n', help="name of payload", type= str)
parser.add_argument('--type', '-t', help="type of payload", type= str)

# Parse the arguments recieved from LaunchVehicle Program
args = parser.parse_args()

# Function to Send Telemetry to DSN
def send_telemetry_to_dsn(data=''):
    # Telemetry Data
    telemetry_data = {"altitude": 400, "longitude": -45.34, "latitude": -28.34, "temperature": 340}
    resp = requests.get('http://{0}:{1}/{2}'.format('localhost', '5344',
                                                    '/payload/capture-telemetry?name='+args.name+'&data=' + json.dumps(
                                                        telemetry_data)))

# Function to Send Payload Data to DSN
def send_data_to_dsn(data=''):
    payload_data = {}

    # Payload Data
    if args.type == 'Scientific':
        payload_data = {"solar-flares-per-second": 100}
    elif args.type == 'Communication':
        payload_data = {"uplink-data-rate": 5, "downlink-data-rate": 10}
    elif args.type == 'Spy':
        payload_data = {"image": "space.jpg"}
    else:
        raise Exception('Unknown Payload type encountered....Allowed Payload types are Scientific, Communication and Spy...')

    resp = requests.get('http://{0}:{1}/{2}'.format('localhost', '5344',
                                                    '/payload/capture-payload-data?name='+args.name+'&data=' + json.dumps(payload_data)))

# Accept command from DSN
data = sys.stdin.readline()

# Schedule a Background Scheduler to send data to DSN periodically at an interval
scheduler = BackgroundScheduler()
job = scheduler.add_job(send_telemetry_to_dsn, 'interval', args=[args.name], seconds=3)

# Schedule a Background Scheduler to send data to DSN periodically at an interval
data_scheduler = BackgroundScheduler()
data_job = None

if args.type == 'Scientific':
    data_job = data_scheduler.add_job(send_data_to_dsn, 'interval', args=[args.name], seconds=3)
elif args.type == 'Communication':
    data_job = data_scheduler.add_job(send_data_to_dsn, 'interval', args=[args.name], seconds=5)
elif args.type == 'Spy':
    data_job = data_scheduler.add_job(send_data_to_dsn, 'interval', args=[args.name], seconds=10)
else:
    raise Exception('Unknown Payload type encountered....Allowed Payload types are Scientific, Communication and Spy...')

while data.strip() != 'Decommission':
    if data.strip() == 'StartTelemetry':
        try:
            scheduler.start()
        except:
            scheduler.resume()

    if data.strip() == 'StopTelemetry':
        scheduler.pause()

    if data.strip() == 'StartData':
        try:
            data_scheduler.start()
        except:
            data_scheduler.resume()

    if data.strip() == 'StopData':
        data_scheduler.pause()

    data = sys.stdin.readline()
