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


class K8sEventHandlerService:
    """ Service to handle K8s events and trigger DB updates. """

    name = "K8sEventHandlerService"
    CONFIG = {'AMQP_URI' : "amqp://guest:guest@localhost:5672"}

    def __init__(self):
        print("K8sEventHandlerService object created")

    #@rpc
    @event_handler("NatsEventSubscriberService", "Event_K8SEvent")
    def processEvent(self, payload):
        'Do Something'
        #print("Reached K8s event handler")
        sys.stdout.flush()
        events = payload
        for event in events:
            """----Add code to put Kubernetes events in Graph Database ------------"""
            res = post_request('events', json.dumps(event))
            logger.info("Recd. SM-Item --> id[%s],[resource:%s],[name:%s]",
                            event["id"],
                            event["resource"],
                            event["name"])


    #@rpc
    @event_handler("NatsEventSubscriberService", "Event_K8SAlarm")
    def processAlarm(self, payload):
        'Do Something'
        try:
            alarms = payload
            if(len(alarms) < 1):
                print("Alarm list empty")
            for alarm in alarms:
                someObjName = alarm.get("objectName")
                alarmClass = alarm.get("criticality")
                alarmText = alarm.get("alarmDescription")
                alarmState = "ACTIVE"
                GphDB.updateAlarmForObject(someObjName, alarmClass, alarmText, alarmState)
                post_request('alarms',  json.dumps(alarm))
                print("Alarm : %s :: %s" %(someObjName, alarmText))
        except Exception as e: 
            sys.stdout.flush()




    def __objectCreated(self, payload):
        'Do Something'

    def __objectDeleted(self, payload):
        'Do Something'

    def __objectUpdated(self, payload):
        'Do Something'

    def __raiseAlarm(self, payload):
        'Do Something'

    def __cancelAlarm(self, payload):
        'Do Something'

from nameko.containers import ServiceContainer
container = ServiceContainer(K8sEventHandlerService, config=K8sEventHandlerService.CONFIG)
service_extensions = list(container.extensions)
container.start()


