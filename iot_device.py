from datetime import datetime
import json
import threading
from time import sleep, time

import schedule

from iot_controller import *


alive_counter = 0


def ping_state():
    global alive_counter
    alive_counter += 1


def event_state(client, payload, shadow, report, event_type=""):
    if event_type == 'ping':
        ping_state()
        payload['action'] = 'pinging'
        report['action'] = 'pinging'

    global alive_counter

    time = f'{datetime.now()}'

    payload['time'] = time
    payload['ping'] = alive_counter
    client.publish('myTopic', json.dumps(payload), 0)

    report['state']['reported']['time'] = time
    report['state']['reported']['ping'] = alive_counter
    shadow.shadowUpdate(
        json.dumps(report), 
        customShadowCallback_Update, 5)


def run_tgsn():

    # Schedule Reporting Service(s)
    schedule.every(10).seconds.do(event_state, devMQTTClient, dev_payload, devShadow, dev_shadow, 'ping')


    while True:

        # Run Scheduler(s)
        schedule.run_pending()

        # Event 1
        '''
        event_state(devClient, devPayload, devShadow, shadow_report)
        '''

        # Event 2
        '''
        event_state(devClient, devPayload, devShadow, shadow_report)
        '''
        
        # Sleep
        sleep(0.1)


if __name__ == "__main__":

    run_tgsn()
