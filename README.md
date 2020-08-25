# AWS IoT Device Shell #

Ready to use AWS IoT device that is setup to connect via MQTT client 'pubsub' and AWS IoT Device Shadow methods

Requires:

* AWS Account
* AWS IoT Endpoint Setup
* AWS IoT Device Thing
* AWS IoT Device Certificate and Keyfiles

Python Imports:
* AWSIoTPythonSDK
* schedule

## Procedure ##

1. move to working directory
   1. `cd path/to/working/directory`
2. run Pipenv installer
   1. `pipenv install`
3. create "keys/" folder in working directory
   1. `mkdir keys`
4. move keyfiles into working directory under "keys/" folder
   1. path/to/working/directory/**keys**
5. rename keyfiles like:
   1. RootCA.pem
   2. "AWS IOT Thing Name".crt
   3. "AWS IOT Thing Name".private.key
   4. "AWS IOT Thing Name".public.key
6. run `python iot_device.py`

With AWSIoTPythonSDK properly installed, and keyfiles properly renamed and moved to the **keys/** folder, you should have a device up and running with the following activity:

#### Shadow Doc ####
    {
        "state": {
            "reported":{
                "last_event": "",
                "ping": "",
                "action": "",
                "time": ""
            }
        }
    }

#### PubSub Messaging ####

subscribed to the topic "myTopic"

    {
        "action": "",
        "ping": "",
        "time": "",
        "uid": ""
    }