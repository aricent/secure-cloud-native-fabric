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
import os
import ast
import json
from nats.aio.client import Client as NATS
from nats.aio.errors import ErrConnectionClosed, ErrTimeout, ErrNoServers
import configparser
import subprocess
import threading

config = configparser.ConfigParser()
config.read("config.ini")
rulesPath = config['falco']['rulesPath']
rulesLocalPath = config['falco']['rulesLocalPath']
restartFalco = config['falco']['restartFalco']
rootPath = config['falco']['rootPath']


class FalcoAgentHandler:

    __instance = None

    def __init__(self):
        self.__natsServerSCF = "nats://SCF_IP:4222"
        self.__queueNameSCF = "k8s.alarms"

        self.__natsServerK8s = "nats://10.111.117.177:9222"
        self.__queueNameK8s = "FALCO"
        self.__cloudName = "SDWAN-Ctrlr-K8s"

        self.loop = asyncio.new_event_loop()
        self.__ncSCF = NATS()
        self.__ncK8s = NATS()
        FalcoAgentHandler.__instance = self


    @classmethod
    def set_config(cls, auditor_data):
        'Set Config API for Rule-Sets'
        print('setting config in Falco auditor......{}'.format(auditor_data))
        
        for obj in auditor_data:
            if obj['auditor_type'] == 'SDWANBranchSysCalls':
                auditorConfig = obj['auditor_body']
                with open(rulesPath, 'w') as outfile:
                    yaml.dump(auditorConfig[0], outfile, default_flow_style=False)
                with open(rulesLocalPath, 'w') as outfile:
                    yaml.dump(auditorConfig[1], outfile, default_flow_style=False)

        print('*****configuration setting done********')


    @classmethod
    def start_falco(cls):
        'Run Event-Loop to start getting notif.'

        print('running thread start falco...')
        if FalcoAgentHandler.__instance == None:
            os.chdir(rootPath)
            subprocess.call(restartFalco)
            rac = FalcoAgentHandler()
            asyncio.set_event_loop(rac.loop)
            rac.loop.run_until_complete(rac.createConnections())
            rac.loop.run_until_complete(rac.addSubscriber())
            rac.loop.run_forever()


    @classmethod
    def hit_audit_request(cls, jsondata):
        'Start audit and return report.'

        
        thread = threading.Thread(target=FalcoAgentHandler.start_falco, args=())
        thread.daemon = True
        thread.start()
        

        finalresult = {}
        finalresult['auditor_type'] = jsondata['auditorType']
        finalresult['cluster'] = jsondata['cluster']
        repObj = { 'auditors' : [] }
        repObj['auditors'].append({ 'items' : [] })
        obj = {'name':'Falco Auditor', 'audit_issues':[ {'issue':'Running', 'notes':'Running', 'score': 5} ] }
        repObj['auditors'][0]['items'].append(obj)
        finalresult['audit_report'] = repObj
        print('**** successful audit hit on Falco *****')
        return finalresult

        
    async def __message_handler(self, msg):
        'Message filter, forwarder'
        print("Message handler invoked:")
        try:
            msgOb = json.loads(msg.data.decode('utf-8'))
            alarmText = msgOb["output"].split(':')[3]
            criticality = alarmText.split(' ')[1]
            print("--%s--" %(criticality))
            fields = json.loads(json.dumps(msgOb["output_fields"]))
            if not fields["k8s.pod.name"]:
                #return
                fields["k8s.pod.name"] = "ip-10-0-0-177"
            alarms = list()
            alarms.append({"objectName":(self.__cloudName + "_" + fields["k8s.pod.name"]),
                           "criticality":criticality,
                           "alarmDescription":alarmText}) 
            print("Constructed Alarm")
            await self.__ncSCF.publish(self.__queueNameSCF,
                                       bytes(json.dumps(alarms), 'utf-8'))
            print("Alarm sent to SCF")
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("!!!! Exception !!!!")
            print(exc_type, fname, exc_tb.tb_lineno)
            print(e)

    async def createConnections(self):
        try:
            print("Creating Connections ..")
            await self.__ncK8s.connect(self.__natsServerK8s, self.loop)
            await self.__ncSCF.connect(self.__natsServerSCF, self.loop)
            print(".. Connected")
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("!!!! Exception !!!!")
            print(exc_type, fname, exc_tb.tb_lineno)
            print(e)

    async def addSubscriber(self):
        try:
            await self.__ncK8s.subscribe(self.__queueNameK8s, 
                                         self.__queueNameK8s,
                                         cb=self.__message_handler)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("!!!! Exception !!!!")
            print(exc_type, fname, exc_tb.tb_lineno)
            print(e)

if __name__ == "__main__":
    rac = FalcoAgentHandler()
    asyncio.set_event_loop(rac.loop)
    rac.loop.run_until_complete(rac.createConnections())
    rac.loop.run_until_complete(rac.addSubscriber())
    rac.loop.run_forever()
