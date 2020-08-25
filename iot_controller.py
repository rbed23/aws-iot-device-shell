from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient

from datetime import datetime
import json
import os
from time import sleep

from device_manager import *


def customMssgCallback(client, userdata, message):
    print("Received a new message:")
    print(message.payload.decode('utf-8'))
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")


def customShadowCallback_Get(payload, responseStatus, token):
    if responseStatus == "timeout":
        print("Get request " + token + " time out!")
        devShadow.shadowGet(customShadowCallback_Get, 10)
    if responseStatus == "accepted":
        payloadDict = json.loads(payload)
        print("~~~~~~~~~~~~~~~~~~~~~~~")
        print("Get request with token: " + token + " accepted!")
        get_device_state()
    if responseStatus == "rejected":
        print("Get request " + token + " rejected!")
        print(json.loads(payload)['message'])
        devShadow.shadowUpdate(
            json.dumps(tmp['default_shadow']),
            customShadowCallback_Update, 5)


def customShadowCallback_Update(payload, responseStatus, token):
    # payload is a JSON string ready to be parsed using json.loads(...)
    # in both Py2.x and Py3.x
    if responseStatus == "timeout":
        print("Update request " + token + " time out!")
    if responseStatus == "accepted":
        payloadDict = json.loads(payload)
        print("~~~~~~~~~~~~~~~~~~~~~~~")
        print("Update request with token: " + token + " accepted!")
        if [x for x in payloadDict['state'].keys()][0] == 'reported':
            print("Reported state: " + str(payloadDict["state"]["reported"]))
        else:
            print("Desired state: " + str(payloadDict["state"]["desired"]))
        print("~~~~~~~~~~~~~~~~~~~~~~~\n\n")
    if responseStatus == "rejected":
        print("Update request " + token + " rejected!")
        print(json.loads(payload)['message'])


def customShadowCallback_Delta(payload, responseStatus, token):
    # payload is a JSON string ready to be parsed using json.loads(...)
    # in both Py2.x and Py3.x
    payloadDict = json.loads(payload)
    print("++++++++DELTA++++++++++")
    delta_payload = payloadDict['state']
    print(f"Delta state: {delta_payload}")
    print(f"Version: {payloadDict['version']}")
    print("+++++++++++++++++++++++\n\n")

    delta_handler(delta_payload)


def customShadowCallback_Delete(payload, responseStatus, token):
    if responseStatus == "timeout":
        print("Delete request " + token + " time out!")
    if responseStatus == "accepted":
        print("~~~~~~~~~~~~~~~~~~~~~~~")
        print("Delete request with token: " + token + " accepted!")
        print("~~~~~~~~~~~~~~~~~~~~~~~\n\n")
    if responseStatus == "rejected":
        print("Delete request " + token + " rejected!")
        print(json.loads(payload)['message'])


def get_device_state():
    print('getting device state...')
    pass


def delta_handler(delta_state):
    aar = {}

    for k, v in delta_state.items():

        '''
        if k == 'something':
            ### DO SOMETHING ###
            aar['something'] = something_handler(v)
        else:
            print('Invalid input')
        '''
        pass

        aar = delta_state
    
    devShadow.shadowUpdate(
        json.dumps({'state': {'reported': aar}}),
        customShadowCallback_Update, 5)


# -----------------------------------
# IOT DEVICE CONFIGURATION
# -----------------------------------


def get_myShadowClient():
    # Get device configuration details
    with open('config.json', 'r') as cfg:
        device = json.load(cfg)
    thing_uid = device['thing_uid']

    # Get keyfile paths
    key_dir = f'{os.getcwd()}/keys/'

    if os.path.exists(key_dir):
        try:
            with open(f'{key_dir}{thing_uid}.crt', 'r') as r:        
                root_file = f'{key_dir}RootCA.pem'
                key_file = f'{key_dir}{thing_uid}.private.key'
                crt_file = f'{key_dir}{thing_uid}.crt'
        except FileNotFoundError as err:
            print(f'Issue with filenames in <{key_dir}>')
            print(str(err))
    else:
        print(f'Path <{key_dir} does not exist; verify working directory')

    # Certificate based connection
    myShadowClient = AWSIoTMQTTShadowClient(thing_uid)
    print(f'Shadow Client: {myShadowClient}')
    print(f'Shadow Client ID: {thing_uid}')

    # Configuration for TLS mutual authentication
    myShadowClient.configureEndpoint(
        device['endpt'], int(device['prt']))
    myShadowClient.configureCredentials(
        root_file,
        key_file,
        crt_file)

    myShadowClient.configureAutoReconnectBackoffTime(1, 32, 20)
    myShadowClient.configureConnectDisconnectTimeout(10)  # 10 sec
    myShadowClient.configureMQTTOperationTimeout(5)  # 5 sec

    print('shadow client configured')

    myShadowClient.connect()

    print('shadow client connected')
    return myShadowClient, thing_uid


def get_devShadow(myShadowClient, uid):
    # Create a device shadow instance using persistent subscriptions
    devShadow = myShadowClient.createShadowHandlerWithName(uid, True)

    # Shadow operations
    #devShadow.shadowGet(customShadowCallback_Get, 5)
    #devShadow.shadowUpdate(shadow_doc, customShadowCallback_Update, 5)
    #devShadow.shadowDelete(customShadowCallback_Delete, 5)
    devShadow.shadowRegisterDeltaCallback(customShadowCallback_Delta)
    #devShadow.shadowUnregisterDeltaCallback()

    print('shadow handler configured')

    return devShadow


def get_myMQTTClient(myShadowClient):
    # Create a device mqtt client instance
    myMQTTClient = myShadowClient.getMQTTConnection()

    print('mqtt client connection active')

    return myMQTTClient


def init_device_shadow(devShadow, shadow):
    devShadow.shadowGet(customShadowCallback_Get, 5)
    sleep(5)

def init_device_mqtt(devMQTT, payload):
    devMQTT.subscribe('myTopic', 1, customMssgCallback)
    sleep(0.1)
    devMQTT.publish("myTopic", json.dumps(payload), 0)


myShadowClient, uid = get_myShadowClient()
devShadow = get_devShadow(myShadowClient, uid)
devMQTTClient = get_myMQTTClient(myShadowClient)


with open('default_payloads.json', 'r') as defaults:
    tmp = json.load(defaults)

dev_shadow = tmp['default_shadow']
dev_payload = tmp['default_payload']

init = {
    'ping': 0,
    'action': 'pinging',
    'time': f'{datetime.now()}'
}
dev_shadow['state']['reported'].update(init)
dev_payload['uid'] = uid
dev_payload.update(init)

init_device_shadow(devShadow, dev_shadow)
init_device_mqtt(devMQTTClient, dev_payload)  
