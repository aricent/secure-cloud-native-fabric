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
import time
import requests
from nats.aio.client import Client as NATS
from nats.aio.errors import ErrConnectionClosed, ErrTimeout, ErrNoServers
import configparser
import random
import string
import base64
import urllib.parse
import pdb
from nameko.events import EventDispatcher
from nameko.rpc import rpc, RpcProxy
from nameko.standalone.rpc import ClusterRpcProxy


#sys.path.append('/home/ubuntu/scrm_git/SCRM/util/')
sys.path.append('./util/')
from elastic_search_client import post_request_ver2, get_all_documents, get_search_results, get_document_by_id, update_document, search_index_using_querystring
from common_def import CloudConfig
from gphmodels import GphDB



CONFIG = {'AMQP_URI' : "amqp://guest:guest@localhost:5672"}

class AgentRegistration:
    name = "AgentRegistration"
    dispatch = EventDispatcher(use_confirms=False, persistence="transient")

    def __init__(self):
        self.__NATSserversList = ["nats://SCF_IP:4222"]
        self.__natsClient = NATS()
        self.__subject = 'agent_registration_queue'
        self.__msgReader = self.__agentHandler
        self.__loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.__loop)
        print("Created a AgentRegisterService")

    @rpc
    def createAgentSubscriber(self):
        'Create a NATS Subscriber and run its event loop'
        self.__loop.run_until_complete(self.__natsReaderLoop(self.__loop))
        print("Completed run until complete loop")
        try:
            print("Starting event Loop")
            self.__loop.run_forever()
        finally:
            print("Closing event Loop")
            self.__loop.close()



    def __natsReaderLoop(self, loop):
        try:
            yield from self.__natsClient.connect(servers=self.__NATSserversList,
                                                 io_loop=self.__loop)
            yield from self.__natsClient.subscribe(self.__subject,
                                                       "agent_register",
                                                       self.__msgReader)
            print("Subscribed")
            sys.stdout.flush()
        except Exception as e:
            print(e)
            sys.stdout.flush()
            sys.exit(1)



    @asyncio.coroutine
    def __agentHandler(self, msg):
    #async def __agentHandler(self, msg):

        print("Received message on Topic: {subject} : Data {data}"
              .format(subject = msg.subject, data = msg.data.decode()))

        agent_data = json.loads(msg.data.decode())
        CloudId = agent_data['cloudId']
        agent_token = agent_data['token']


        if str(CloudId) in CloudConfig.cloud:
            if agent_token == CloudConfig.cloud[str(CloudId)]['auth_token']:

                ran_str = ''.join(random.choice(string.ascii_letters) for i in range(20))
                queue_name = ran_str + str(CloudId)


                agent_obj = get_document_by_id('agents', str(CloudId))
                if 'found' not in agent_obj.keys() or not agent_obj.get('found'):
                    agent = dict()
                    agent.update({'agent_name' : 'Agent_' + str(CloudId) })
                    agent.update({'cloud_id' : str(CloudId) })
                    agent.update({'agent_queue' : queue_name })
                    agent.update({'status' : 'ready'})
                    post_request_ver2('agents', json.dumps(agent), str(CloudId), None)
                else:
                    update_object ={'jsondoc' : {'agent_queue' : queue_name}}
                    update_document('agents', str(CloudId), update_object)


   
                print('success......queue name....{}'.format(queue_name))
                resp_dict = {'status':'SUCCESS','queue_name':queue_name, 'auditors':[]} 
                response = json.dumps(resp_dict)

                """          
                print("Fetch Clusters for Cloud-Id : %s" %(CloudId))
                clstr = GphDB.getClusterByCloudid(str(CloudId))
                print('clusters received....: %s' %(clstr))
                print('type of cluster...{}'.format(type(clstr)))
                print(clstr)
                #pdb.set_trace()
                auditor_list = []
                for clr in clstr:
                    query_dict = {'metadata.cluster': clr.replace("/"," AND ")}
                    res = search_index_using_querystring('auditors', query_dict)
                    #res = json.loads(auditors)['hits']['hits']
                    print('res.....{}'.format(res))
                    if res:
                        for obj in res:
                            yaml_str = base64.b64decode(obj['_source']['blob']).decode('ascii')
                            yaml_obj = list(yaml.load_all(yaml_str))
                            #auditor_name = urllib.parse.unquote_plus(obj['_source']['jsondoc']['auditor_name'])
                            #obj['_source']['jsondoc'].update({'auditor_name' : auditor_name})
                            obj['_source']['jsondoc'].update({'auditor_body' : yaml_obj})
                            auditor_list.append(obj['_source']['jsondoc'])
                resp_dict['auditors'] = auditor_list
                print('auditor_list.................{}'.format(auditor_list))
                print('***** length of auditor_list.................{}'.format(len(auditor_list)))
                """
                
            else:
                response = json.dumps({'status':'FAILED','message': 'Authentication failed'})
        else:
            response = json.dumps({'status':'FAILED','message': 'Cloud not found'})

        yield from self.__natsClient.publish(msg.reply, bytes(response, 'utf-8'))
        print("************* data saved ************** ")






        """
        time.sleep(0.5)
        conn = None
        print("***** calling 1st rpc *******")
        sys.stdout.flush()
        with ClusterRpcProxy(CONFIG) as rpc:
            configDict = rpc.ClusterRegistryService.getCloudConfigFromRegistry.call_async(CloudId)
        #configDict = self.dispatch("Event_getCloudConfigFromRegistry", CloudId)
        #time.sleep(1.5)
        final = configDict.result()
        print("------- async call --------")
        print(final)
        #print("***** configdict *******\n %s" %(configDict.result()))
        sys.stdout.flush()
        
        if configDict:
            conn = configDict.values()[0]
        sys.stdout.flush()
        #with ClusterRpcProxy(CONFIG) as rpc:
        #    rpc.ClusterRegistryService.fetchK8sCloudData(conn)
        self.dispatch("Event_fetchK8sCloudData", conn)
        time.sleep(1.5)

        print("Fetch Clusters for Cloud-Id : %s" %(CloudId))
        clstr = GphDB.getClusterByCloudid(str(CloudId))
        print('clusters received....: %s' %(clstr))
        print('type of cluster...{}'.format(type(clstr)))
        print(clstr)
        #pdb.set_trace()
        auditor_list = []
        for clr in clstr:
            query_dict = {'metadata.cluster': clr.replace("/"," AND ")}
            res = search_index_using_querystring('auditors', query_dict)
            print('res.....{}'.format(res))
            if res:
                for obj in res:
                    yaml_str = base64.b64decode(obj['_source']['blob']).decode('ascii')
                    yaml_obj = list(yaml.load_all(yaml_str))
                    obj['_source']['jsondoc'].update({'auditor_body' : yaml_obj})
                    auditor_list.append(obj['_source']['jsondoc'])
        #resp_dict['auditors'] = auditor_list
        finaldata = {'purpose' : 'SetConfig', 'data' : auditor_list}
        yield from self.__natsClient.publish(queue_name, bytes(json.dumps(finaldata), 'utf-8'))
        """








from nameko.containers import ServiceContainer
from nameko.runners import ServiceRunner
from nameko.testing.utils import get_container

runner = ServiceRunner(config=CONFIG)
runner.add_service(AgentRegistration)
runner.start()


ar = AgentRegistration()
ar.createAgentSubscriber()
