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
import sys
import json
import base64
import urllib.parse
from audit.run_audit import RunAuditClass
from nats.aio.client import Client as NATS
from nats.aio.errors import ErrConnectionClosed, ErrTimeout, ErrNoServers
sys.path.append('./util/')
from elastic_search_client import get_request, post_request, post_request_ver2, get_document_by_url, get_document_by_id_ver2, get_document_by_id
import yaml

class AuditorType(type):
    '''MetaClass for Auditor type Regsitry
    '''
    def __new__(cls, name, bases, attrs):
        print("In AuditorType")     
        auditorType = attrs['auditorType']   #getattr(attrs, "auditorType", None)
        print("Registering this auditor, type : ", 
              auditorType, 
              " Class : ", cls)
        Auditor.AuditorTypeRegistry[auditorType] = name
        x = super(AuditorType, cls).__new__(cls, name, bases, attrs)
        #.attr = 100
        return x


class Auditor(object):
    '''Auditor Base-Class, maintains registry of auditors.
       Provides generic methods for -
       - Running Auditors on a Cluster
       - Get Audit results from all Auditors on a Cluster
       - Add / Update Auditor for a Cluster
    '''

    AuditorTypeRegistry = {}
    ClusterAuditorRegistry = {}

    @staticmethod
    def loadAuditorTypeRegistryFromConfig(configJson):
        print("----------loadAuditorTypeRegistryFromConfig---------")
        print(configJson)
        for auditor in configJson:
            auditorType = auditor['Type']
            auditorClass = auditor['Class']
            #print(auditorClass)
            #Auditor.AuditorTypeRegistry[auditorType] = auditorClass
            try:
                klass = globals()[auditorClass]
                instance = klass()
                print("--type of object---")
                print(str(type(instance)))
            except Exception as e:
                print("---------EXCEPTION CLASS NOT FOUND----------------    ")            
                print(e)
        
        """Auditor.AuditorTypeRegistry[KubeBenchAuditor.auditorType] = KubeBenchAuditor
        Auditor.AuditorTypeRegistry[FalcoAuditor.auditorType] = FalcoAuditor
        print(Auditor.AuditorTypeRegistry) """

    @staticmethod
    def getAuditorInClusterRegistry(clusterName, auditorType):
        'get Auditor in Registry'
        return Auditor.ClusterAuditorRegistry[clusterName][auditorType]

    @staticmethod
    def getAuditorsForCluster(clusterName):
        'Get all Auditors avaialble for a Cluster'
        return Auditor.ClusterAuditorRegistry[clusterName] 

    @staticmethod
    def getAvailableAuditors():
        'Get all Auditors avaialble for a Cluster'
        return Auditor.AuditorTypeRegistry

    @staticmethod
    def createAuditorInClusterRegistry(clusterName, auditorType, config, runState=None):
        'Save Auditor in Registry and in Elastic-DB'
        auditorClass = Auditor.AuditorTypeRegistry[auditorType]
        klass = globals()[auditorClass]
        auditor = klass()
        print("--type of object---")
        print(str(type(auditor)))
        print(auditor)
        print(str(type(auditor)))
        auditor.config = config
        if(runState != None):
            auditor.runState = runState
        if not clusterName in Auditor.ClusterAuditorRegistry.keys():
            Auditor.ClusterAuditorRegistry[clusterName] = {}
        Auditor.ClusterAuditorRegistry[clusterName][auditorType] = auditor
        return auditor.runState

    @staticmethod    
    def updateAuditorInClusterRegistry(clusterName, auditor):
        'Save Auditor in Registry and in Elastic-DB'
        Auditor.ClusterAuditorRegistry[clusterName][auditor.auditorType] = auditor

    @staticmethod
    def deleteAuditorFromCluster(clusterName, auditorType):
        'Delete Auditor from registry and Elastic-DB'
        Auditor.ClusterAuditorRegistry[clusterName].pop(auditorType)

    @staticmethod
    def runAuditor(auditorType, clusterName, cloud):
        'Run the auditor on a cluster'
        auditor = Auditor.ClusterAuditorRegistry[clusterName][auditorType] 
        print("config URL - " + auditor.config) 
        aud_name = auditorType + '_' + clusterName
        res = get_document_by_id('auditors', urllib.parse.quote_plus(aud_name))
        yaml_str = base64.b64decode(res['_source']['blob']).decode('ascii')
        yaml_obj = list(yaml.load_all(yaml_str))
        #auditorData = get_document_by_url(auditor.config)
        if (len(yaml_obj) > 1) :
            audBody = yaml_obj
        else:
            audBody = yaml_obj[0]
        #print(" queue name - " + cloud['nats_queue'])
        auditorConfig = {'cluster' : clusterName, 'auditorType' : auditorType, 'auditorConfig' : audBody}
        finaldata = {'purpose' : 'runAudit', 'data' : auditorConfig}
        print("Cloud Id  : %s -------" %(cloud['Id']))
        cloudId = cloud['Id']
        try:
            agent_obj = get_document_by_id_ver2('agents', str(cloudId))
            print("Agent Q %s " %(agent_obj))
            response = auditor.runAudit(finaldata, agent_obj['agent_queue'])
            print("run triggered!!")
            auditor.runState = 'TRIGGERED'
            
        except Exception as e:
            print("---------EXCEPTION IN CREATE KUBE POLICYs----------------    %s\n" % e)

        print(auditor.runState)
        return auditor.runState
            


    @staticmethod
    def updateAuditorRuleset(auditorType, clusterName, ruleSet):
        'Run the auditor on a cluster'
        auditor = Auditor.ClusterAuditorRegistry[clusterName][auditorType] 
        auditor.updateRuleSet(ruleSet)

    @staticmethod
    def updateAuditorResults(auditorType, clusterName, auditResults):
        'Run the auditor on a cluster'
        auditor = Auditor.ClusterAuditorRegistry[clusterName][auditorType] 
        auditor.runState = 'AUDIT OK'
        auditor.updateResults(auditResults)

    @staticmethod
    def finishedAuditorRun(auditorType, clusterName):
        'Run the auditor on a cluster'
        auditor = \
            Auditor.ClusterAuditorRegistry[clusterName][auditorType]
        auditor.runState = 'REPORT_AVAILABLE'
        return auditor.runState

    @staticmethod
    def getAuditResults(auditorType, clusterName):
        'Get Last audit results from Elastic-DB'
        print("Getting Audit Results for: [", 
               auditorType,"][", clusterName,"]")
        auditor = \
            Auditor.ClusterAuditorRegistry[clusterName][auditorType]
        return {"verdict":"AUDIT RESULTS FAIL",
                "lastrun":"",
                "details":""}

    @staticmethod
    def getAuditorState(auditorType, clusterName):
        print("Getting Auditor State for: [", 
               auditorType,"][", clusterName,"]")
        auditor = \
            Auditor.ClusterAuditorRegistry[clusterName][auditorType]
        return auditor.runState

    @staticmethod       
    def runAllAuditors(clusterName):
        'Run all the auditors on a cluster'
        for auditor in Auditor.ClusterAuditorRegistry[clusterName].values():
            auditor.runAudit(clusterName)
            auditor.runState = 'RUNNING'

    @staticmethod
    def getAllAuditResults(clusterName):
        'Get All the Last audit results'


class SDWANBranchSysCallsAuditor(metaclass=AuditorType):

    #__metaclass__ = AuditorType
    auditorType = "SDWANBranchSysCalls"
    runState = "IDLE"

    def runAudit(self, auditorConfig, queue):
        try:
            loop = asyncio.new_event_loop()
            loop.run_until_complete(RunAuditClass.publishAudit(loop, queue, json.dumps(auditorConfig)))
            loop.close()
            
        except Exception as e:
            print("---------EXCEPTION in SDWANBranchSysCallsAuditor event loop----------------    %s\n" % e)

        

class SDWANControllerSysCallsAuditor(metaclass=AuditorType):

    #__metaclass__ = AuditorType
    auditorType = "SDWANControllerSysCalls"
    runState = "IDLE"

    def runAudit(self, auditorConfig, queue):
        try:
            loop = asyncio.new_event_loop()
            loop.run_until_complete(RunAuditClass.publishAudit(loop, queue, json.dumps(auditorConfig)))
            print('--------In run audit-----------')
            #print(response)
            loop.close()
        except Exception as e:
            print("---------EXCEPTION IN SDWANControllerSysCallsAuditor event loop----------------    %s\n" % e)



class NETAppsNetworkAuditor(metaclass=AuditorType):

    #__metaclass__ = AuditorType
    auditorType = "NETAppsNetwork"
    runState = "IDLE"

    def runAudit(self, auditorConfig, queue):
        try:
            loop = asyncio.new_event_loop()
            loop.run_until_complete(RunAuditClass.publishAudit(loop, queue, json.dumps(auditorConfig)))
            print('--------In run audit-----------')
            #print(response)
            loop.close()
        except Exception as e:
            print("---------EXCEPTION IN NETAppsNetworkAuditor event loop----------------    %s\n" % e)



class NETAppsS3Auditor(metaclass=AuditorType):

    #__metaclass__ = AuditorType
    auditorType = "NETAppsS3"
    runState = "IDLE"

    def runAudit(self, auditorConfig, queue):
        try:
            loop = asyncio.new_event_loop()
            loop.run_until_complete(RunAuditClass.publishAudit(loop, queue, json.dumps(auditorConfig)))
            print('--------In run audit-----------')
            #print(response)
            loop.close()
        except Exception as e:
            print("---------EXCEPTION IN NETAppsS3Auditor event loop----------------    %s\n" % e)



class K8sCISBenchMarksAuditor(metaclass=AuditorType):

    #__metaclass__ = AuditorType
    auditorType = "K8sCISBenchMarks"
    runState = "IDLE"

    def runAudit(self, auditorConfig, queue):
        try:
            loop = asyncio.new_event_loop()
            loop.run_until_complete(RunAuditClass.publishAudit(loop, queue, json.dumps(auditorConfig)))
            print('--------In run audit-----------')
            #print(response)
            loop.close()
        except Exception as e:
            print("---------EXCEPTION IN K8sCISBenchMarksAuditor event loop----------------    %s\n" % e)





if __name__ == '__main__':
    """AuditorList = [KubeBenchAuditor(), FalcoAuditor()]    
    Auditor.loadClusterRegistryFromConfig(json.loads("[{}]"))
    print(Auditor.getAvailableAuditors())
    Auditor.createAuditorInClusterRegistry("K8s_Cluster", 
                                           "K8S.KubeBench",
                                           json.loads("[{}]"))
    Auditor.createAuditorInClusterRegistry("K8s_Cluster", 
                                           "K8S.Falco",
                                           json.loads("[{}]"))
    print(Auditor.getAvailableAuditors())
    Auditor.runAllAuditors("K8s_Cluster")    """

    #aud1 = KubeBenchAuditor()
    #aud2 = FalcoAuditor()
    #print(KubeBenchAuditor.attr)
    print(Auditor.AuditorTypeRegistry)
    Auditor.createAuditorInClusterRegistry('AAA', "K8S.Falco", 'config')
    
