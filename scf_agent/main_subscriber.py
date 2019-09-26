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
import asyncio
import yaml
import sys
import ast
import json
import requests
from nats.aio.client import Client as NATS
from nats.aio.errors import ErrConnectionClosed, ErrTimeout, ErrNoServers
from securityMonkey_handler import SM_Handler
from falco_agent_handler import FalcoAgentHandler
import configparser

config = configparser.ConfigParser()
config.read("config.ini")
cloudId = config['cloud_details']['cloudId']
token = config['cloud_details']['token']
cloudtype = config['cloud_details']['cloudtype']





class AgentClass:

    def __init__(self):
        self.__NATSserversList = ["nats://SCF_IP:4222"]
        self.__natsClient = NATS()
        print("Starting registration")



    def start_registration(self):
        arg = {'cloudId':cloudId}
        arg.update({'token':token})
        reg_data = json.dumps(arg)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.register(loop, "agent_registration_queue", reg_data))
        #loop.close()
        loop.run_forever()

    
    def register(self, loop, queue_name, data):

        yield from self.__natsClient.connect(servers = self.__NATSserversList, io_loop=loop)
        response = yield from self.__natsClient.request(queue_name, bytes(data, 'utf-8'), 2.6)
        res = response.data.decode()
        #yield from nc.close()
        #jsondata = ast.literal_eval(res)
        jsondata = json.loads(res)

        if jsondata['status'] == 'SUCCESS':

            agent_queue = jsondata['queue_name']
            #self.run_subscriber(agent_queue)
            print('success......queue name....{}'.format(agent_queue))
            print(jsondata['auditors'])
            print(type(jsondata['auditors']))

            if jsondata['auditors']:
                if cloudtype == 'AWS':
                    SM_Handler.set_config(jsondata['auditors'])
                elif cloudtype == 'KUBERNETES':
                    FalcoAgentHandler.set_config(jsondata['auditors'])
                else:
                    pass
                
            #self.run(loop, agent_queue)
            yield from self.__natsClient.subscribe(agent_queue, "workers", self.message_handler)
        #yield from nc.close()



    """
    def run_subscriber(self, queue):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.run(loop, queue))
        loop.run_forever()
    """


    # def run(self, loop, queue_name):
    #     nc = NATS()
    #     yield from nc.connect(servers=["nats://SCF_IP:4222"], io_loop=loop)

    @asyncio.coroutine
    def message_handler(self, msg):
        subject = msg.subject
        reply = msg.reply
        data = msg.data.decode()
        print("Received a message on message_handler'{subject} {reply}': {data}".format(
            subject=subject, reply=reply, data=data))
        yield from self.__natsClient.publish(reply, bytes('I can help', 'utf-8'))


        jsondata = ast.literal_eval(data)
        purpose = jsondata['purpose']
        data = jsondata['data']

        if purpose == 'runAudit':
            if cloudtype == 'AWS':
                finalresult = SM_Handler.hit_audit_request(data)
            elif cloudtype == 'KUBERNETES':
                finalresult = FalcoAgentHandler.hit_audit_request(data)
            else:
                pass
            yield from self.__natsClient.publish('audit_result_queue', bytes(json.dumps(finalresult), 'utf-8'))

        elif purpose == 'Topology':
            pass
        elif purpose == 'SetConfig':
            if cloudtype == 'AWS':
                SM_Handler.set_config(data)
            elif cloudtype == 'KUBERNETES':
                FalcoAgentHandler.set_config(data)
            else:
                pass
        else:
            pass

        #yield from self.__natsClient.publish('audit_result_queue', bytes(json.dumps(finalresult), 'utf-8'))

        # print('subscribing on queue.....{}'.format(queue_name))
        # yield from nc.subscribe(queue_name, "workers", message_handler)





if __name__ == "__main__":
    rac = AgentClass()
    rac.start_registration()


