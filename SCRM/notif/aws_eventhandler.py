# 
#  Copyright 2019 Altran. All rights reserved.
# 
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
# 
#      http://www.apache.org/licenses/LICENSE-2.0
# 
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
# 
# 
from nameko.events import EventDispatcher, event_handler, EventHandler
from nameko.rpc import rpc
import json
from nameko.standalone.rpc import ClusterRpcProxy

import sys, os
sys.path.insert(0, os.getcwd() + "../util/")

from util.elastic_search_client import get_request, post_request
from util.gphmodels import GphDB, Component, WorkLoad, Policy, Cluster, Alarm

class AwsEventHandlerService:
    """ Service to handle AWS events and trigger DB updates. """

    name = "AwsEventHandlerService"
    CONFIG = {'AMQP_URI' : "amqp://guest:guest@localhost:5672"}
    
    def __init__(self):
        print("AwsEventHandlerService object created")

    @event_handler("NatsEventSubscriberService", "Event_AWSEvent")
    def processEvent(self, payload):
        print("------------------------------AWS EVENT--------------------------")
        sys.stdout.flush()

        'Do Something'
        events = payload
        invalidCloud = False
        if(len(events) < 1):
            print("Invalid or Empty event-list recd.")
            sys.stdout.flush()
            return
        for event in events:
            cloudType = event.get("cloudType")
            if(cloudType == 'AWS' ):
                if event["action"] == "Item created":
                    self.__objectCreated(event)
                elif event["action"] == "Item deleted":
                    item_name = event["name"]
                    self.__objectDeleted(item_name)
                else:
                    'Create / Update Item in Graph-DB'

                res = post_request('events', json.dumps(event))
                print("Recd. SM-Item --> id[%s],[resource:%s],[name:%s]",
                          event["id"],
                          event["resource"],
                          event["name"])
            else:
                print("Unknown Cloud-type")
        sys.stdout.flush()
         
    @event_handler("NatsEventSubscriberService", "Alarm_AWSAlarm")
    def processAlarm(self, payload):
        print("Reached AWS Alarm handler")
        alarms = payload
        if(len(alarms) < 1):
            print("Alarm list empty")
        for alarm in alarms:
            someObjName = alarm.get("objectName")
            alarmClass = alarm.get("criticality")
            alarmText = alarm.get("alarmDescription")
            alarmState = "ACTIVE"
            GphDB.updateAlarmForObject(someObjName, alarmClass, alarmText, alarmState)
            post_request('alarms',json.dumps(alarm))
            print("Alarm added successfylly")
        sys.stdout.flush()
            

    def __objectCreated(self, payload):
        if payload["resource"] == "securitygroup":
            policy = Policy(name=payload["name"],
                            labels=str(payload["account"]
                                       + "," + payload["region"]))
            vpcName = payload["name"].split(' ')[3]
            raisedOn = GphDB.getGphObject(vpcName, Cluster)
            if not raisedOn:
                cluster = Cluster(name=vpcName,
                                  organization=payload["account"],
                                  zone=payload["region"])
                raisedOn =  GphDB.addGphObject(cluster)

            sys.stdout.flush()
            policy = GphDB.addGphObject(policy)
            policy.appliesToCluster.connect(raisedOn)
        else:
            return


    def __objectDeleted(self, payload):
        policy = GphDB.getGphObject(payload, Policy)
        if(policy != 'None'):
            delelteResponse = GphDB.delGphObject(policy)
        else:
            print("Payload : " + payload + " not found in Graph DB.")


    def __objectUpdated(self, payload):
        'Do Something'

    def __raiseAlarm(self, payload):
        'Do Something'

    def __cancelAlarm(self, payload):
        'Do Something'

from nameko.containers import ServiceContainer
container = ServiceContainer(AwsEventHandlerService, config=AwsEventHandlerService.CONFIG)
service_extensions = list(container.extensions)
container.start()
