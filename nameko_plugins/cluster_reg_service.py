
from nameko.standalone.rpc import ClusterRpcProxy
from nameko.events import EventDispatcher, event_handler
from nameko.rpc import rpc
from nameko.timer import timer

from kubernetes import client, watch
from kubernetes import config as kub_config
import boto3 as boto3

import ast
import sys
import json
import collections

from common_def import *
from aws_service import connect_ec2_instance, get_ec2_resource

sys.path.append('../SCRM/')
from util.gphmodels import *
from util.kube_watch import create_object_mapping 
from util.elastic_search_client import post_request

CONFIG = {'AMQP_URI' : "amqp://guest:guest@localhost:5672"}
from scrm.settings import config as testconfig


class ClusterRegistryService:
    name="ClusterRegistryService"

    dispatch = EventDispatcher()
    __procedureState = dict()
   
    __registry = defaultdict(dict)
    __organization = "Aricent-default"

    def __getConfig(self):
        return testconfig        


    #@event_handler("AgentRegistration", "Event_getCloudConfigFromRegistry")
    @rpc
    def getCloudConfigFromRegistry(self, cid):
        return __registry.get(cid)

    @rpc
    def registerCloudInstance(self, configDict):
        '''
        Register Cloud instance, API GW connection params
        '''
        rsp = "Unexpected Error"
        try:
            if configDict:
                if configDict["Organization"] and configDict["Organization"]["Name"]:
                    org = GphDB.getGphObject(configDict["Organization"]["Name"], Organization)
                    if not org:
                        org = Organization(name=configDict["Organization"]["Name"])
                        org = GphDB.addGphObject(org)
                        print("Add Organization in DB : %s" %(configDict["Organization"]["Name"]))
                if configDict["Organization"] and configDict["Organization"]["Clouds"]:
                    ClusterRegistryService.__organization = configDict["Organization"]["Name"]
                    cloudList = configDict["Organization"]["Clouds"].split(',')
                    print("---> %s" %(cloudList))
                    for cloud in cloudList:
                        print("Cloud : %s" %(cloud))
                        if configDict[cloud]:
                            ClusterRegistryService.__registry[configDict[cloud]["Id"]] = {cloud:configDict[cloud]}
                            print("Added to registry [%s]=[%s]" %(configDict[cloud]["Id"], {cloud:configDict[cloud]}
))
                            rsp = rsp + ", " + "Added" + cloud + " to registry"
                            ClusterRegistryService.__procedureState[configDict[cloud]["Id"]] = "INIT"
                        else:
                            print("Config for \"%s\" not available" %(cloud))
                            rsp = rsp + ", " + "Config for \"" + cloud  + "\" not available"
                    print("Cloud Registry updated")
            else:
                print("Empty configuration, Nothing to do")
                rsp = "Empty configuration, Nothing to do"
        except Exception as e:
            service_logger.error(e)
            print(e)
        finally:
            return {"Result":rsp}


    @timer(interval=60)
    def periodicRefresh(self):
        '''
        Start Periodic Refresh of Cloud-Ids in Registry
        '''
        print("Starting Periodic Refresh ...")
        if not(len(ClusterRegistryService.__registry) > 0):
            conf = self.__getConfig()
            self.registerCloudInstance(conf)
            print("Registry was empty, loaded default config")
        if len(ClusterRegistryService.__registry) > 0:
            for cloudId in ClusterRegistryService.__registry.keys():
                cloudName = list(ClusterRegistryService.__registry[cloudId].keys())[0]
                cloudParams =  ClusterRegistryService.__registry[cloudId][cloudName]
                if cloudParams["CloudType"] == "KUBERNETES":
                    print("Starting refresh of Cloud:%s, type:KUBERNETES ..." %(cloudName))
                    if ClusterRegistryService.__procedureState[cloudId] == "RUNNING":
                        print("Skipped refresh of Cloud:%s, type:KUBERNETES ..." %(cloudName))
                    else:
                        ClusterRegistryService.__procedureState[cloudId] = "RUNNING"
                        self.__refreshK8sCloudData(cloudParams)
                        ClusterRegistryService.__procedureState[cloudId] = "IDLE"
                    print("... Completed refresh of Cloud:%s, type:KUBERNETES ..." %(cloudName))
                elif cloudParams["CloudType"] == "AWS":
                    print("Starting refresh of Cloud:%s, type:AWS ..." %(cloudName))
                    if ClusterRegistryService.__procedureState[cloudId] == "RUNNING":
                        print("Skipped refresh of Cloud:%s, type:AWS ..." %(cloudName))
                    else:
                        ClusterRegistryService.__procedureState[cloudId] = "RUNNING"
                        self.__refreshAWSCloudData(cloudParams)
                        ClusterRegistryService.__procedureState[cloudId] = "IDLE"
                    print("... Completed refresh of Cloud:%s, type:AWS ..." %(cloudName))
        else:
            print("... Ending Refresh, no clouds in registry")
        print("... Ending Periodic Refresh")

    @event_handler("AgentRegistration", "Event_fetchK8sCloudData")
    @rpc
    def fetchK8sCloudData(self, connection):
        return self.__refreshK8sCloudData(connection)


    def __refreshK8sCloudData(self, connection):
        '''
        Refresh Kubernetes Cloud data in Graph-DB
        '''
        try:
            print("Connecting to Kubernetes API GW ..." + connection["admin_config"])
            #kub_config.load_kube_config(connection["admin_config"])
            #v1 = client.CoreV1Api()
            #v1_ext = client.ExtensionsV1beta1Api()
            #apiClient = client.ApiClient()
            print("... Connected to Kubernetes API GW ")
            print("Refreshing Kubernetes objects ...")
            create_object_mapping(orgName=ClusterRegistryService.__organization, 
                                  conn=connection)
            print("... Done Refreshing Kubernetes objects")
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("!!!! Exception !!!!")
            print(exc_type, fname, exc_tb.tb_lineno)
            print(e)

        finally:
            "Do we need to close v1 or v1_ext ?"

    @rpc
    def fetchAWSCloudData(self, connection):
        return self.__refreshAWSCloudData(connection)


    def __refreshAWSCloudData(self, connection):
        '''
        Refresh AWS Cloud data in Graph-DB
        '''
        print("Refreshing AWS objects ...")


        assetGrp = GphDB.getGphObject("AWS Infrastructure", AssetGroup)
        secControl = GphDB.getGphObject("Network Communications Security", SecurityControl)
        auditor = GphDB.getGphObject("AWS Audit", Auditor)
        clusterNameInConfig = connection["CloudName"]
        awsObsDict = dict()
        try:
            awsConn = connect_ec2_instance(connection["Region"],
                                           connection["aws_access_key_id"],
                                           connection["aws_secret_access_key"])
            vpcObs = awsConn.describe_vpcs()
            print("Organization : %s" %(ClusterRegistryService.__organization))
            org = GphDB.getGphObject(ClusterRegistryService.__organization, Organization)
            cloud = GphDB.getGphObject(connection["CloudName"], Cloud)
            if not cloud:
                cloud = Cloud(name=connection["CloudName"],
                              cloudType="AWS",
                              cloudId=connection["Id"])
                cloud = GphDB.addGphObject(cloud)
            org.hasCloud.connect(cloud)
            for vpcob in vpcObs["Vpcs"]:
                #print("--------")
                #print("VPC Objects : %s" %(vpcob))
                clus = Cluster(name= clusterNameInConfig + "_" + vpcob["VpcId"],
                               organization=ClusterRegistryService.__organization,
                               zone=connection["Region"],
                               cloudId=connection["Id"],
                               cloudType="AWS")
                clus = GphDB.addGphObject(clus)
                awsObsDict[clus.name] = clus
                cloud.hasCluster.connect(clus)
                if assetGrp:
                    assetGrp.instanceCluster.connect(clus)
                #print("--------")
            secgrps = awsConn.describe_security_groups()
            for secgrp in secgrps["SecurityGroups"]:
                #print("--------")
                #print("SG Objects : %s" %(secgrp))
                print("----------POLICY NAME-------------")
                print(secgrp["GroupName"])

                pol = Policy(name= clusterNameInConfig + "_" + secgrp["GroupName"],
                             version=secgrp["GroupId"],
                             metaData=secgrp["Description"],
                             cloudType="AWS",
                             spec=secgrp,
                             policyRules={"IpPermissions":secgrp["IpPermissions"], 
                                          "IpPermissionsEgress":secgrp["IpPermissionsEgress"]})
                polExisting = GphDB.getGphObject(clusterNameInConfig + "_" + secgrp["GroupName"], Policy)
                clus = GphDB.getGphObject(clusterNameInConfig + "_" + secgrp["VpcId"], Cluster)
                if polExisting:

                    #polExistingRules = ast.literal_eval(polExisting.policyRules)
                    #polRules = ast.literal_eval(pol.policyRules)
                    print("POLICY EXISTS!!")
                    polExistingRules = polExisting.policyRules
                    polRules = pol.policyRules

                    someObjName = secgrp["GroupName"]
                    alarmClass = 'CRITICAL'
                    alarmText = 'Policy tampered'
                    alarmState = "ACTIVE"

                    if polExistingRules == polRules:
                        GphDB.removeAlarmFromObject(clusterNameInConfig + "_" + someObjName, alarmText)
                    else:
                        alarmPaylod = {}
                        alarmPaylod['objectName'] = someObjName
                        alarmPaylod['criticality'] = alarmClass
                        alarmPaylod['alarmDescription'] = alarmText

                        GphDB.updateAlarmForObject(clusterNameInConfig + "_" + someObjName, alarmClass, alarmText, alarmState)
                        post_request('alarms',  json.dumps(alarmPaylod)) 
                   
                    pol = polExisting                    
                else:
                    print("POLICY IS NEW")
                    pol = GphDB.addGphObject(pol)
                awsObsDict[pol.name] = pol
                if clus:
                    pol.appliesToCluster.connect(clus)
                    print("Connect Policy %s to Cluster %s" %(pol.name, clus.name))
                if secControl:
                    secControl.implPolicy.connect(pol)
                #print("--------")
            ec2_resources = get_ec2_resource(connection["Region"],
                                             connection["aws_access_key_id"],
                                             connection["aws_secret_access_key"])
            instances = ec2_resources.instances.filter(Filters=[{"Name":"instance-state-name",
                                                                 "Values":["running"]}])
            for inst in instances:
                #print("--------")
                print("Instances : %s in %s" %(inst.id, inst.vpc_id))
                node = Nodes(name= clusterNameInConfig + "_" + inst.private_ip_address,
                             cloudType="AWS")
                node = GphDB.addGphObject(node)
                awsObsDict[node.name] = node
                clus = GphDB.getGphObject(clusterNameInConfig + "_" + inst.vpc_id, Cluster)
                if clus:
                    node.cluster.connect(clus)
                    print("Connect Node %s to Cluster %s" %(node.name, clus.name))
            print("Objects in Cluster :")
            print(awsObsDict.keys())
            allObjs = Policy.nodes.all() + Nodes.nodes.all() + Cluster.nodes.all()
            for ob in allObjs:
                if awsObsDict.get(str(ob.name)) is None and ob.name.startswith(clusterNameInConfig):
                    try:
                        ob.delete()
                    except Exception as e:
                        print("Warning: Failed to delete %s" %(ob.name))
            print("... Done Refreshing AWS objects")
            return True
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("!!!! Exception !!!!")
            print(exc_type, fname, exc_tb.tb_lineno)
            print(e)
        finally:
            return False
            "Do we need to close awsConn ?"

  
 


def main():
    "Test Periodic Refresh"
    registry = ClusterRegistryService()
    registry.registerCloudInstance(testconfig)
    registry.periodicRefresh()

if __name__ == '__main__':
    main()

