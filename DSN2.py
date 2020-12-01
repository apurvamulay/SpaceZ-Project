from flask import Flask, Blueprint, request, abort, make_response, jsonify, redirect, render_template
from flask_cors import CORS, cross_origin
import os, sys

import subprocess
import json
import psutil
from werkzeug.utils import secure_filename

LV_STATE_CREATED = 'created'
LV_STATE_FLYING = 'flying'
LV_STATE_IN_ORBIT = 'in-orbit'
LV_STATE_DE_ORBITED = 'deorbited'

PAYLOAD_STATE_CREATED = 'created'
PAYLOAD_STATE_DEPLOYED = 'deployed'
PAYLOAD_STATE_DECOMMISSIONED = 'decommissioned'

# Define blueprint for the SpaceZ DSN
bp = Blueprint('deep-space-network-service', __name__)

#################################### LAUNCH VEHICLE APIS ###################################

# The master set of launch vehicle names and objects will be stored here
launch_vehicles_map = {}

# The master set of payload names and objects will be stored here
payloads_map = {}

@bp.route("/")
def index():
    return render_template("index.html")


# Function to send command to launch vehicle
def send_command_to_launch_vehicle(launch_vehicle_name, command):
    if (command == 'DeployPayload') and (launch_vehicles_map[launch_vehicle_name][1] == LV_STATE_FLYING):
        print('Launch Vehicle has still not reach orbit. Please wait...')
        return {'error': 'Launch Vehicle has still not reach orbit. Please wait...'}

    if launch_vehicles_map[launch_vehicle_name][1] == LV_STATE_DE_ORBITED:
        print('Launch Vehicle is already de-orbited...Not possible to send commands...')
        return {'error': 'Launch Vehicle is already de-orbited...Not possible to send commands...'}

    print('Sending command {0} to Launch Vehicle {1}'.format(command, launch_vehicle_name))

    launch_vehicle_object = launch_vehicles_map[launch_vehicle_name][0]

    launch_vehicle_object.stdin.write("{0}\n".format(command).encode('utf-8'))
    launch_vehicle_object.stdin.flush()

    return {}

# API Call to Deploy a Launch Vehicle using the given configuration
@bp.route('/launch-vehicle/deploy', methods=['GET'])
@cross_origin()
def deploy_launch_vehicle():
    results = {}

    f = open(request.args.get('config-file'))
    launch_vehicle_config = json.load(f)

    launch_vehicle_1 = subprocess.Popen(['python', 'LaunchVehicle.py', '--name', launch_vehicle_config['Name'], '--orbit',
                                         str(launch_vehicle_config['Orbit']),
                                         '--payload-config', launch_vehicle_config['PayloadConfig']],
                                        shell=True, stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE)
    launch_vehicles_map[launch_vehicle_config['Name']] = [launch_vehicle_1, LV_STATE_FLYING, '']

    return results

# API Call to Launch Vehicle to Start Telemetry
@bp.route('/launch-vehicle/start-telemetry', methods=['GET'])
@cross_origin()
def start_telemetry():
    results = {}
    send_command_to_launch_vehicle(request.args.get('name'), 'StartTelemetry')
    return results

# API Call to Launch Vehicle to Start Telemetry
@bp.route('/launch-vehicle/stop-telemetry', methods=['GET'])
@cross_origin()
def stop_telemetry():
    results = {}
    send_command_to_launch_vehicle(request.args.get('name'), 'StopTelemetry')
    return results

# API Call to De-orbit Launch Vehicle
@bp.route('/launch-vehicle/deorbit', methods=['GET'])
@cross_origin()
def deorbit():
    results = {}
    send_command_to_launch_vehicle(request.args.get('name'), 'Deorbit')
    launch_vehicles_map[request.args.get('name')][1] = LV_STATE_DE_ORBITED

    return results

# API Call to accept update from Launch Vehicle that it has reached orbit
@bp.route('/launch-vehicle/update-status', methods=['GET'])
@cross_origin()
def update_from_launch_vehicle():
    results = {}

    launch_vehicles_map[request.args.get('name')][1] = LV_STATE_IN_ORBIT
    print('Launch Vehicle reached orbit now...')

    return results

# API Call to Capture telemetry data of Launch Vehicle
@bp.route('/launch-vehicle/capture-telemetry', methods=['GET'])
@cross_origin()
def capture_launch_vehicle_telemetry():
    results = {}
    data = request.args.get('data').strip()
    print(data.strip())

    launch_vehicles_map[request.args.get('name')][2] = data

    return results

@bp.route('/launch-vehicle/deploy-payload', methods=['GET'])
@cross_origin()
def deploy_payload():
    results = send_command_to_launch_vehicle(request.args.get('name'), 'DeployPayload')

    return results

@bp.route('/launch-vehicle/create-payload', methods=['GET'])
@cross_origin()
def create_payload():
    results = {}

    name = request.args.get('name')
    type = request.args.get('type')

    payload_object = subprocess.Popen(
        ['python', 'Payload.py', '--name', name, '--type', type], shell=True, stdin=subprocess.PIPE,
        stdout=subprocess.PIPE)
    payloads_map[name] = [payload_object, PAYLOAD_STATE_DEPLOYED, '', '', type]

    return results

@bp.route('/launch-vehicle/create', methods=['POST'])
@cross_origin()
def create_launch_vehicle():
    results = {}

    f = request.files['file']
    f.save(secure_filename(f.filename))

    f = open(f.filename)
    j = json.loads(f.read())
    launch_vehicles_map[j['Name']] = [None, LV_STATE_CREATED, '']

    results['name'] = j['Name']
    return results


#################################### PAYLOAD APIS ###################################

# Function to send command to Payload
def send_command_to_payload(payload_name, command):
    if payloads_map[payload_name][1] == PAYLOAD_STATE_DECOMMISSIONED:
        print('Payload is already decommissioned...Not possible to send commands...')
        return False

    print('Sending command {0} to Payload {1}'.format(command, payload_name))

    print("payloads_map", payloads_map[payload_name][0])
    payload_object = payloads_map[payload_name][0]

    payload_object.stdin.write("{0}\n".format(command).encode('utf-8'))
    payload_object.stdin.flush()

# API Call to Create a Launch Vehicle (Spacecraft) using the given configuration
@bp.route('/payload/create', methods=['POST'])
@cross_origin()
def upload_payload():
    results = {}

    f = request.files['file']
    f.save(secure_filename(f.filename))

    f = open(f.filename)
    j = json.loads(f.read())
    payloads_map[j['Name']] = [None, PAYLOAD_STATE_CREATED, '', '', '']

    results['Name'] = j['Name']
    results['type'] = j['Type']
    return results

# API Call to Capture telemetry data of Payload
@bp.route('/payload/capture-telemetry', methods=['GET'])
@cross_origin()
def capture_payload_telemetry():
    results = {}
    data = request.args.get('data').strip()
    print(data.strip())

    payloads_map[request.args.get('name')][2] = data

    return results

# API Call to Payload to Start Telemetry
@bp.route('/payload/start-telemetry', methods=['GET'])
@cross_origin()
def p_start_telemetry():
    results = {}
    send_command_to_payload(request.args.get('name'), 'StartTelemetry')
    return results

# API Call to Payload to Stop Telemetry
@bp.route('/payload/stop-telemetry', methods=['GET'])
@cross_origin()
def p_stop_telemetry():
    results = {}
    send_command_to_payload(request.args.get('name'), 'StopTelemetry')
    return results

# API Call to Payload to Start Data
@bp.route('/payload/start-data', methods=['GET'])
@cross_origin()
def p_start_data():
    results = {}

    print(request.args.get('name'))
    send_command_to_payload(request.args.get('name'), 'StartData')
    return results

# API Call to Payload to Stop Data
@bp.route('/payload/stop-data', methods=['GET'])
@cross_origin()
def p_stop_data():
    results = {}
    send_command_to_payload(request.args.get('name'), 'StopData')
    return results

# API Call to Capture payload data of Payload
@bp.route('/payload/capture-payload-data', methods=['GET'])
@cross_origin()
def capture_payload_data():
    results = {}
    data = request.args.get('data').strip()
    print(data.strip())

    payloads_map[request.args.get('name')][3] = data

    return results

# API Call to Capture payload data of Payload
@bp.route('/payload/get-data', methods=['GET'])
@cross_origin()
def get_payload_data():
    results = {}


    try:
        results['type'] = payloads_map[request.args.get('name')][4]
    except:
        results = {}

    return results

# API Call to Decommission Payload
@bp.route('/payload/decommission', methods=['GET'])
@cross_origin()
def decommission():
    results = {}
    send_command_to_payload(request.args.get('name'), 'Decommission')
    payloads_map[request.args.get('name')][1] = PAYLOAD_STATE_DECOMMISSIONED

    return results

################################### DASHBOARD APIs ####################################

@bp.route('/dashboard-metrics', methods=['GET'])
@cross_origin()
def get_overall_metrics():
    active_spacecrafts = 0
    waiting_to_launch_spacecrafts = 0

    for key in launch_vehicles_map:
        if (launch_vehicles_map[key][1] == LV_STATE_FLYING) or (launch_vehicles_map[key][1] == LV_STATE_IN_ORBIT):
            active_spacecrafts = active_spacecrafts + 1
        elif launch_vehicles_map[key][1] == LV_STATE_CREATED:
            waiting_to_launch_spacecrafts = waiting_to_launch_spacecrafts + 1

    results = {}
    results['active_spacecrafts'] = active_spacecrafts
    results['waiting_to_launch_spacecrafts'] = waiting_to_launch_spacecrafts

    return results

@bp.route('/get-all-payloads', methods=['GET'])
@cross_origin()
def get_all_payloads():
    results = {}

    for key in payloads_map:
        if payloads_map[key][1] != PAYLOAD_STATE_DECOMMISSIONED:
            results[key] = ""
    return results

################################### MAIN FLASK APPLICATION ############################

def config_app(app, conf=None):
    app.config.update(dict(DEBUG=True))
    app.config.update(conf or {})
    app.register_blueprint(bp)

    return app

flask_app = config_app(Flask(__name__))

cors = CORS(flask_app)
flask_app.config['CORS_HEADERS'] = 'Content-Type'

if __name__ == '__main__':
    flask_app.run(host='localhost', port=5344, use_reloader=False)