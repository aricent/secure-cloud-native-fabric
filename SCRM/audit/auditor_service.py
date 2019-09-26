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
import json
import os
import sys
import asyncio
import base64
import collections
from nameko.events import EventDispatcher
from nameko.rpc import rpc, RpcProxy
from nameko.standalone.rpc import ClusterRpcProxy
from datetime import datetime
from nats.aio.client import Client as NATS
#from auditor_data import Auditor
from audit.auditor_data import Auditor
from audit.run_audit import RunAuditClass
import configparser
import yaml
import eventlet.tpool
import urllib.parse

sys.path.append('./util/')
from elastic_search_client import get_request, post_request, post_request_ver2, get_document_by_url, get_document_by_id_ver2, update_document, get_all_documents, create_auditor_index
from gphmodels import GphDB, AuditorInstance, Cluster
from gphmodels import Auditor as GphAuditor

CONFIG = {'AMQP_URI' : "amqp://guest:guest@localhost:5672"}

class AuditorService:
    name = 'AuditorService'
    cloud_configurations = []

    
    def __init__(self):
        self.__NATSserversList = ["nats://SCF_IP:4222"]
        self.__natsClient = NATS()
        self.__subject = 'audit_result_queue'
        self.__msgReader = self.__reportHandler
        self.__loop = asyncio.new_event_loop()
        print("Created a NatsEventSubscriberService")
    



    ''' Method loads the default configurations for existing Auditor types in Auditor table '''
    @staticmethod
    def loadAuditorTypeRegistry(auditor_dict):
        'loads the Auditor dict'
        print('Loading Auditor service ....')
        try:
            #url = auditor_dict[0]
            config = configparser.ConfigParser()
#           config.read("/home/ubuntu/scrm_git/config.ini")
            config.read("PROJ_PATH/config.ini")

      
            '''Load Autior type default conficguration in Elastic DB '''      
            if config['Auditor_data'] and  config['Auditor_data']['Auditors']:
                auditor_name_list = config['Auditor_data']["Auditors"].split(',')

                auditor_list = []

                for auditor_name in auditor_name_list:
                    availableAuditors = Auditor.getAvailableAuditors()
                    if(config[auditor_name]['Type'] in availableAuditors.keys()):
                        resp = AuditorService.__createDefaultEntryForAuditor(config[auditor_name]['Default_yaml_path'], config[auditor_name]['Type'])                   
                    else:
                        print("Auditor Type not found in Registry : " + config[auditor_name]['Type']) 

            '''Load the Auditor-Cluster Registry '''
            auditorClusterRegistries = get_all_documents('auditor_cluster_registry')
            for registry in auditorClusterRegistries:
                Auditor.createAuditorInClusterRegistry(registry.get('_source').get('jsondoc').get('cluster'), registry.get('_source').get('jsondoc').get('auditor_type'), registry.get('_source').get('jsondoc').get('config'), registry.get('_source').get('jsondoc').get('runState'))  



            '''Load the cloud configurations for refernce in cloud_configurations '''
            cloudList = config['Organization']['Clouds'].split(',')
            for cloudName in cloudList:
                cloud = {'Id' : config[cloudName]['Id'], 'cloudName' : config[cloudName]['CloudName'], 'nats_queue' : config[cloudName]['nats_queue']}
                AuditorService.cloud_configurations.append(cloud)

            #print("----Clouds----")
            #print(self.cloud_configurations)
                

            print('Done loading!!')
            #AuditorService.createNatsSubscriber()

        except Exception as e:
            print("Exception : %s" %(e))
            sys.stdout.flush()
        print("End")
        return [{"result":"SUCCESS"}]

    @rpc
    def getAuditorTypes(self):
        print("---getAuditorTypes--")
        print(Auditor.getAvailableAuditors())
        auditor_dict =  Auditor.getAvailableAuditors()
        auditor_types = []
        if auditor_dict != None:  
            auditor_types = list(auditor_dict.keys())

        sys.stdout.flush()
        return auditor_types
       

    def __createDefaultEntryForAuditor(filePath, auditorType):
        try:
            with open(filePath, "r") as f:
                auditorBodystr = f.read()
                
            auditorName = auditorType+'_default'

            auditor = dict()
            auditor.update({'auditor_type' : auditorType })
            auditor.update({'auditor_name' : auditorName})
            #auditor.update({'auditor_body': auditorBody})

            blobdata = base64.b64encode(bytes(auditorBodystr, 'utf-8')).decode('ascii')

            metadata = dict()
            metadata.update({'auditor_type' : auditorType })
            metadata.update({'cluster' : None})

            #resp = post_request_ver2('auditors', json.dumps(auditor), auditorName, metadata)

            post_request_ver2('auditors', data = json.dumps(auditor), identity = auditorName, metadata = metadata, blob = blobdata)
            print('successful for {}'.format(auditorType))
            return None

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("!!!! Exception while reading default yaml !!!!")
            print(exc_type, fname, exc_tb.tb_lineno)
            print(e) 

    '''Creates an auditor with given config, for each cluster in the list and adds a mapping for the same '''
    @rpc
    def createAuditorAndMapCluster(self,requestData):
        print("***** Enter Method - " + str(datetime.now()))
        sys.stdout.flush()
        
        auditorType = requestData['auditorType']
        postureName = requestData['postureName']
        auditorBody = requestData['auditorBody']
        clusters = requestData['clusters']
        auditorRelations = []
        relationDict = dict()
        for cluster in clusters:
            
            ''' Create the Auditors in Databse'''
            auditorName = auditorType + '_' + cluster
 
            auditor = dict()
            auditor.update({'auditor_type' : auditorType })
            auditor.update({'auditor_name' : auditorName })
            #auditor.update({'auditor_body' : auditorBody})        

            metadata = dict()
            metadata.update({'auditor_type' : auditorType })
            metadata.update({'cluster' : cluster })
            blob = base64.b64encode(bytes(auditorBody, 'utf-8')).decode('ascii') 
            auditorUrl = post_request_ver2('auditors', json.dumps(auditor), urllib.parse.quote_plus(auditorName), metadata, blob )

                  
            if auditorType == 'SDWANBranchSysCalls':
                try:
                    cluster_obj = GphDB.getGphObject(cluster, Cluster)
                    agent_obj = get_document_by_id_ver2('agents', str(cluster_obj.cloudId))
                    finaldata = {'purpose' : 'SetConfig', 'data' : [] }
                    aud_obj = dict()
                    aud_obj.update({'auditor_type' : auditorType })
                    aud_obj.update({'auditor_name' : auditorName})
                    aud_obj.update({'auditor_body' : list(yaml.load_all(auditorBody))})
                    finaldata['data'].append(aud_obj)
                    loop = asyncio.new_event_loop()
                    loop.run_until_complete(RunAuditClass.publishAudit(loop, agent_obj['agent_queue'], json.dumps(finaldata)))
                    loop.close()
                except Exception as e:
                    print("Exception while setting config on agent : \n %s" %(e))
            


            ''' Add the AuditorType-Auditor-Cluster relationships to the node graph''' 
            relationData = dict()
            relationData.update({'cluster': cluster})
            relationData.update({'auditorName' : auditorName})
            relationData.update({'auditorUrl' : auditorUrl})
            auditorRelations.append(relationData)
            ''' Update the Cluster Auditor Registry'''
            registryResp = Auditor.createAuditorInClusterRegistry(cluster, auditorType, auditorUrl)
            print("Registry entry created, Status - " + registryResp)

            ''' Add AuditorInstance to Graph DB '''
            audInst = AuditorInstance(name=auditorName, documentLink=auditorUrl, state=registryResp).save()
            print("auditor instance saved to graph DB !!!")
            try:
                audiInGph = GphDB.getGphObject(auditorType, GphAuditor)
                audInst.instanceOf.connect(audiInGph)
            except Exception as e:
                print("Exception while linkinf AuditorInstance to Auditor : \n %s" %(e))
     
            ''' Update index to add Registry data'''
            registryEntry = {'cluster': cluster, 'auditor_type' : auditorType, 'config' : auditorUrl, 'runState' : registryResp, 'auditor_name' : auditorName}
            post_request_ver2('auditor_cluster_registry', json.dumps(registryEntry), urllib.parse.quote_plus(auditorName), None )
            print("data saved to auditor_cluster_registry !!!")
   
        relationDict.update({'posture' : postureName}) 
        relationDict.update({'relations' : auditorRelations})
        #call the node graph method
        try:
            GphDB.addAudInstRelationsBulk(relationDict)
        except Exception as e:
            print("Exception while linkinf AuditorInstance to Auditor : \n %s" %(e))

        return "Success"    
        

    @rpc
    def runAuditorForCluster(self, requestData):
        print("----runAuditorForCluster-------")
        auditorType = requestData.get('auditorType')
        cluster = requestData.get('cluster')

        #set the cloudid for the cloud of the cluster ----
        #There will be a difference NATs queue for each cloud.
        
        clusterInDB = GphDB.getGphObject(cluster, Cluster)
        if clusterInDB:
            cloudId = clusterInDB.cloudId
        else:       
            cloudId = '1'

        cloud = self.__getCloudConfigurationForId(cloudId)      


        print("auditor type " + auditorType)
        print("cluster" + cluster)
        runstate = Auditor.runAuditor(auditorType, cluster, cloud)
        '''Update the runstate in DB '''
        cluster_auditor_id = auditorType + '_' + cluster
        cluster_auditor_entry =  get_document_by_id_ver2('auditor_cluster_registry', urllib.parse.quote_plus(cluster_auditor_id))       

        print('**************cluster_auditor_entry***************' + str(cluster_auditor_entry))
        print("rubstate" + runstate)
  
        update_object ={'jsondoc' : {'runState' : runstate}}

        cluster_auditor_entry['runState'] = runstate
        
        update_document('auditor_cluster_registry', cluster_auditor_id , update_object)   
        try:
            ''' Update status in Gph DB ''' 
            audiInGph = GphDB.getGphObject(cluster_auditor_id, AuditorInstance) 
            if audiInGph:
                audiInGph.state = runstate
                audiInGph.save() 
        except Exception as e:
            print("---------EXCEPTION IN updating auditor_cluster_registry in elasticDB----------------    %s\n" % e)
        return cluster_auditor_entry




    #@rpc
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



    def __natsReaderLoop(self, loop):
        try:
            yield from self.__natsClient.connect(servers=self.__NATSserversList,
                                                 io_loop=self.__loop)
            yield from self.__natsClient.subscribe(self.__subject,
                                                       "nats-subscriber",
                                                       self.__msgReader)
            print("Subscribed")
            sys.stdout.flush()
        except Exception as e:
            print(e)
            sys.stdout.flush()
            sys.exit(1)


      
    async def __reportHandler(self, msg):
        
        print("Received message on Topic: {subject} : Data {data}"
              .format(subject = msg.subject, data = msg.data.decode()))
       
        report = json.loads(msg.data.decode())
        metadata = dict()
        metadata.update({'auditor_type' : report['auditor_type'] })
        metadata.update({'cluster' : report['cluster']})
        post_request_ver2('audit_reports', json.dumps(report), None, metadata)

        print('******** successfuly saved report in elastic DB ********')

        #Update the runstate in DB 
        runstate = Auditor.finishedAuditorRun(report['auditor_type'], report['cluster'])
        print('******** successfuly updated status in registry *********')
        cluster_auditor_id = report['auditor_type']  + '_' + report['cluster']
        cluster_auditor_entry =  get_document_by_id_ver2('auditor_cluster_registry', urllib.parse.quote_plus(cluster_auditor_id))

        update_object ={'jsondoc' : {'runState' : runstate}}

        cluster_auditor_entry['runState'] = runstate

        update_document('auditor_cluster_registry', cluster_auditor_id , update_object)
        print('******* successfuly updated auditor_cluster_registry in elastic DB *******')
        audiInGph = GphDB.getGphObject(cluster_auditor_id, AuditorInstance)
        if audiInGph:
            audiInGph.state = runstate
            audiInGph.save()
            print('******** successfuly updated status in GphDB ********')


        print("************* data saved ************** ")







    def __getCloudConfigurationForId(self, cloudId):
        for cloud in self.cloud_configurations:
            if cloud['Id'] == cloudId:
                return cloud

        return None



from nameko.containers import ServiceContainer
from nameko.runners import ServiceRunner
from nameko.testing.utils import get_container

runner = ServiceRunner(config=CONFIG)
runner.add_service(AuditorService)
runner.start()
create_auditor_index()
AuditorService.loadAuditorTypeRegistry(None)
aud = AuditorService()
aud.createNatsSubscriber()



if __name__ == '__main__':
    print("main")
    """request = [{'type' : 'K8S', 'class' : 'kubeaud'}, {'type' : 'secmonk', 'class' : 'awsaud'}]
    ob = AuditorService()
    ob.loadAuditorTypeRegistry(request)
    print(Auditor.AuditorTypeRegistry)"""
    f = open("/home/ubuntu/SCF/SCRM/audit/K8S.Falco/default.yaml", "r")
    #print(f.read())
    file_object = yaml.load(f, Loader=yaml.FullLoader)
    print(file_object)






