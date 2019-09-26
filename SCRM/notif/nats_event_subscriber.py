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
import sys
import logging
import asyncio
import traceback
from nats.aio.client import Client as NATS
from nats.aio.errors import ErrConnectionClosed, ErrTimeout, ErrNoServers

from nameko.events import EventDispatcher
from nameko.rpc import rpc, RpcProxy
import json
from nameko.standalone.rpc import ClusterRpcProxy

from notif.aws_eventhandler import AwsEventHandlerService
from notif.k8s_eventhandler import K8sEventHandlerService
import datetime

class NatsEventSubscriberService:
    """ Service to handle K8s events and trigger DB updates. """

    name = "NatsEventSubscriberService"
    CONFIG = {'AMQP_URI' : "amqp://guest:guest@localhost:5672"}
    dispatch = EventDispatcher(use_confirms=False, persistence="transient") 

    def __init__(self):
        self.__NATSserversList = ["nats://localhost:4222"]
        self.__natsClient = NATS()
        self.__subjects = ["k8s.events", "aws.events", "k8s.alarms", "aws.alarms"]
        self.__msgReaders = [self.__readEventMessage, 
                             self.__readEventMessage, 
                             self.__readAlarmMessage, 
                             self.__readAlarmMessage]
        self.__loop = asyncio.new_event_loop()
        print("Created a NatsEventSubscriberService")


    @rpc
    def processInternalAlarm(self, payload):
        print("In processInternalAlarm")
        self.dispatch("Event_K8SAlarm", payload)
        return "Success"

    @rpc
    def createNatsSubscriber(self):
        'Create a NATS Subscriber and run its event loop'
        self.__loop.run_until_complete(self.__natsReaderLoop(self.__loop))
        print("Completed run until complete loop")
        try:
            print("Starting event Loop")
            self.__loop.run_forever()
        finally:
            print("Closing event Loop")
            self.__loop.close()


    async def __readEventMessage(self, msg):
        'Read message, verify if JSON, call the right handler RPC'
        print("Received message on Topic: {subject} : Data {data}"
              .format(subject = msg.subject, data = msg.data.decode()))
        try:
           if msg.subject == "aws.events":
               msgJSON = json.loads(msg.data.decode())
               print("Prep. AWS Event Dispatch")
               self.dispatch("Event_AWSEvent", msgJSON)
               print("AWS Event Dispatched")
           elif msg.subject == "k8s.events":
               msgJSON = json.loads(msg.data.decode())
               print("Prep. K8s Event Dispatch")
               self.dispatch("Event_K8SEvent", msgJSON)
               print("K8s Event Dispatched")
           else:
               print("Message is not a handled Event")
        except Exception as e:
            print("Exception in processing message on Topic: {subject} : Data {data}, Exception : {ex}"
                  .format(subject = msg.subject, data = msg.data.decode(), ex = e ))


    async def __readAlarmMessage(self, msg):
        'Read message, verify if JSON, call the right handler RPC'
        print(" ---Received message on Topic: {subject} : Data {data}"
              .format(subject = msg.subject, data = msg.data.decode()))
        try:
           if msg.subject == "aws.alarms":
               msgJSON = json.loads(msg.data.decode())
               self.dispatch("Alarm_AWSAlarm", msgJSON)              
           elif msg.subject == "k8s.alarms":
               msgJSON = json.loads(msg.data.decode())
               self.dispatch("Event_K8SAlarm", msgJSON)
           else:
               print("Message is not a handled Event")
        except Exception as e:
            print("Exception in processing message on Topic: {subject} : Data {data}"
                  .format(subject = msg.subject, data = msg.data.decode()))


    def __natsReaderLoop(self, loop):
        try:
            print("Connecting to NATS server : ", str(self.__NATSserversList))
            yield from self.__natsClient.connect(servers=self.__NATSserversList, 
                                                 io_loop=self.__loop)
            print("Connected")
            for i in range(len(self.__subjects)):
                print("Subscribing to subject : ", self.__subjects[i],)
                yield from self.__natsClient.subscribe(self.__subjects[i], 
                                                       "nats-subscriber", 
                                                       self.__msgReaders[i])
                print("Subscribed")
            sys.stdout.flush()
        except Exception as e:
            print(e)
            sys.stdout.flush()
            sys.exit(1)

'''from nameko.containers import ServiceContainer
container = ServiceContainer(NatsEventSubscriberService, config=NatsEventSubscriberService.CONFIG)
service_extensions = list(container.extensions)
container.start()
with ClusterRpcProxy(NatsEventSubscriberService.CONFIG) as rpc:
    rpc.NatsEventSubscriberService.createNatsSubscriber() '''

if __name__ == '__main__':
    scrbr = NatsEventSubscriberService()

    scrbr.createNatsSubscriber()


    


