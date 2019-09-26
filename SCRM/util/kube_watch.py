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
#!/usr/bin/python
import os
from kubernetes import client, watch
from kubernetes import config as kub_config
import logging
import sys
import datetime

from kubernetes.client.rest import ApiException
from util.gphmodels import *
from util.elastic_search_client import post_request, get_document_by_id_ver2 
from util.common_def import service_logger as logger
from util.nats_utility import NATSservice
import json
import ast
from util.common_def import *

#from nameko.standalone.rpc import ClusterRpcProxy
#from nameko.rpc import rpc

import asyncio
from nats.aio.client import Client as NATS



CONFIG = {'AMQP_URI': "amqp://guest:guest@localhost:5672"}


#kub_config.load_kube_config('/home/ubuntu/admin.conf')
v1 = client.CoreV1Api()
v1_ext = client.ExtensionsV1beta1Api()
apiClient = client.ApiClient()

def jsonfiyForDB(obj):
    #return apiClient.sanitize_for_serialization(obj)
    return str(obj).replace("\"", "\'").replace("\n", "").replace("None", "null")

def revertJsonifyForDd(obj):
    return str(obj).replace( "\'", "\"").replace("null", "None")

def get_namespaced_pods(namespaced_name):
    return v1.list_namespaced_pod(namespaced_name)     

def get_namespaced_network_policy(namespaced_name):
    return v1_ext.list_namespaced_network_policy(namespaced_name)     

def get_all_network_policy():
    return v1_ext.list_network_policy_for_all_namespaces()

def get_all_pod_security_policy():
    return v1_ext.list_pod_security_policy()

def get_network_policy_obj(namespace,name):
    policy_list = get_namespaced_network_policy(namespace)
    for  net_policy in policy_list.items:
         if (net_policy.metadata.name == name):
             return net_policy
    return None




def create_network_policy(req_namespace, req_body, cloudId=None):
    logger.info("---------------IN create_network_policy ----------------")
    logger.info("------------- [%s] --------------" % sys._getframe().f_code.co_name)
    global v1_ext
    if cloudId != None:
        try:
            cloud = CloudConfig.cloud[cloudId]
            kub_config.load_kube_config(cloud["admin_config"])
            v1 = client.CoreV1Api()
            v1_ext = client.ExtensionsV1beta1Api()
            apiClient = client.ApiClient()
        except KeyError as e:
            logger.info("Cloud not found")
            response = {}
            response['status'] = 'Failure'
            response['message'] = 'Cloud not found'
            return response



    if req_namespace == None:
        req_namespace = req_body.get('metadata').get('namespace')
        
    try:
        api_response = v1_ext.create_namespaced_network_policy(namespace=req_namespace, body = req_body, pretty='true')
        logger.info("---------RESPONSE create_network_policy  -----------------")
        logger.info(api_response)
        final_response = {}
        final_response['status'] = 'Success'
        final_response['uid'] = api_response.metadata.uid
        return final_response
        #pprint(api_response)
    except ApiException as e:
        logger.info("Exception when calling ExtensionsV1beta1Api->create_namespaced_network_policy: %s\n" % e)
        return json.loads(e.body)




def replace_network_policy(req_name, req_namespace, req_body, cloudId=None  ):
    logger.info("---------------IN create_network_policy ----------------")
    logger.info("------------- [%s] --------------" % sys._getframe().f_code.co_name)
    global v1_ext

    if cloudId != None:
        try:
            cloud = CloudConfig.cloud[cloudId]
            kub_config.load_kube_config(cloud["admin_config"])
            v1 = client.CoreV1Api()
            v1_ext = client.ExtensionsV1beta1Api()
            apiClient = client.ApiClient()
        except KeyError as e:
            logger.info("Cloud not found")
            response = {}
            response['status'] = 'Failure'
            response['message'] = 'Cloud not found'
            return response



    if req_namespace == None or req_name==None:
        final_response = {}
        final_response['status'] = 'Failure'
        final_response['message'] = 'Mandatory data missin'
        return final_response

    try:
        api_response = v1_ext.replace_namespaced_network_policy(name = req_name, namespace=req_namespace, body = req_body, pretty='true')
        logger.info("---------RESPONSE create_network_policy  -----------------")
        logger.info(api_response)
        final_response = {}
        final_response['status'] = 'Success'
        #final_response['uid'] = api_response.metadata.uid
        return final_response
        
    except ApiException as e:
        logger.info("Exception when calling ExtensionsV1beta1Api->create_namespaced_network_policy: %s\n" % e)
        return json.loads(e.body)


'''def replace_network_policy(req_name, req_namespace, req_body):
    logger.info("---------------IN create_network_policy ----------------")
    logger.info("------------- [%s] --------------" % sys._getframe().f_code.co_name)
    if req_namespace == None or req_name==None:
        final_response = {}
        final_response['status'] = 'Failure'
        final_response['message'] = 'Mandatory data missin'
        return final_response

    try:
        api_response = v1_ext.replace_namespaced_network_policy(name = req_name, namespace=req_namespace, body = req_body, pretty='true')
        logger.info("---------RESPONSE create_network_policy  -----------------")
        logger.info(api_response)
        final_response = {}
        final_response['status'] = 'Success'
        #final_response['uid'] = api_response.metadata.uid
        return final_response
        
    except ApiException as e:
        logger.info("Exception when calling ExtensionsV1beta1Api->create_namespaced_network_policy: %s\n" % e)
        return json.loads(e.body)'''






def create_namespaced_network_policy(podName, podNameSpace, podLabel):
    logger.info("------------- [%s] --------------" % sys._getframe().f_code.co_name)
    body = client.V1beta1NetworkPolicy()
    body.metadata = client.V1ObjectMeta()
    body.metadata.name = podName + '-zerotrustnetwork'
    pod_selector = client.V1LabelSelector()
    pod_selector.match_labels = podLabel
    body.spec = client.V1beta1NetworkPolicySpec(pod_selector = pod_selector)
    try:
        api_response = v1_ext.create_namespaced_network_policy(podNameSpace, body, pretty='true')
        return api_response
        #pprint(api_response)
    except ApiException as e:
        logger.info("Exception when calling ExtensionsV1beta1Api->create_namespaced_network_policy: %s\n" % e)
        return "failure"


def create_pod_security_policy(podName, podNameSpace, podLabel):
    logger.info("------------- [%s] --------------" % sys._getframe().f_code.co_name)
    body = client.ExtensionsV1beta1PodSecurityPolicy()
    body.metadata = client.V1ObjectMeta()
    body.metadata.name = podName + '-podsecuritypolicy'
    body.metadata.namespace = podNameSpace
    body.metadata.labels = podLabel

    fs_group = client.ExtensionsV1beta1FSGroupStrategyOptions(rule = 'RunAsAny')
    run_as_user = client.ExtensionsV1beta1RunAsUserStrategyOptions(rule = 'RunAsAny')
    se_linux = client.ExtensionsV1beta1SELinuxStrategyOptions(rule = 'RunAsAny')
    supplemental_groups = client.ExtensionsV1beta1SupplementalGroupsStrategyOptions(rule = 'RunAsAny')
    body.spec = client.ExtensionsV1beta1PodSecurityPolicySpec(fs_group=fs_group,run_as_user=run_as_user,se_linux=se_linux,supplemental_groups =supplemental_groups)

    try:
        api_response = v1_ext.create_pod_security_policy(body, pretty='true')
        return api_response
    except ApiException as e:
        logger.info("Exception when calling ExtensionsV1beta1Api->create_pod_security_policy: %s\n" % e)
        return "failure"


def convert(in_param):
    import re
    import json
    test =in_param
    test=re.sub('\'','\"',test)
    test=re.sub('None','\"None\"',test)
    test=re.sub('datetime\.','\"datetime\.',test)
    test=re.sub('tzlocal\(\)\)','tzlocal\(\)\)\"',test)
    test=re.sub('\\\\','',test)
    return json.loads(test)
def dict_compare(obj,d1, d2):
    d1_keys = set(d1.keys())
    d2_keys = set(d2.keys())
    intersect_keys = d1_keys.intersection(d2_keys)
    added = d1_keys - d2_keys
    removed = d2_keys - d1_keys
    modified = {o : (d1[o], d2[o]) for o in intersect_keys if d1[o] != d2[o]}
    for o in intersect_keys:
        if d1[o] != d2[o]:
            obj.o = d2[o]   
    same = set(o for o in intersect_keys if d1[o] == d2[o])
    return added, removed, modified, same

def patch_namespaced_network_policy(in_polObj):
    logger.info("[%s] - type:%s  payload:%s" , sys._getframe().f_code.co_name,type(in_polObj),in_polObj)
    polObj = (in_polObj['metaData'])
    #polObj = convert(in_polObj['metaData'])
    #pdb.set_trace()
    namespace = polObj['namespace']
    pretty = 'pretty_example' # str | If 'true', then the output is pretty printed. (optional)
    name = polObj['name']#tmp1'
    body = get_network_policy_obj(namespace,name)
    body1=(in_polObj['spec'])
    #body1=convert(in_polObj['spec'])
  
    if( not body):
        logger.info("Object (%s) not found \n" % name )
        return
    try:
        
        #added, removed, modified, same = dict_compare(body.spec,(body.spec).to_dict(),body1)
        
        if body1['egress']:
            if not body.spec.egress:
                body.spec.egress = client.V1beta1NetworkPolicyEgressRule()
            count = 0
            for i in body1['egress']:
                body.spec.egress[count].ports=[]
                for j in i['ports']:
                    body.spec.egress[count].ports.append(j)
                count =count+1
        else:
            body.spec.egress = None
        if body1['ingress']:
            if not body.spec.ingress:
                body.spec.ingress = client.V1beta1NetworkPolicyIngressRule()
            count =0
            for i in body1['ingress']:
                body.spec.ingress[count].ports=[]
                for j in i['ports']:
                    body.spec.ingress[count].ports.append(j)
                count =count+1
        else:
            body.spec.ingress = None
        logger.info("APi req >patch_namespaced_network_policy: %s\n" % body) 
        api_response = v1_ext.patch_namespaced_network_policy(name, namespace, body, pretty=pretty)
        logger.info("APi resp >patch_namespaced_network_policy: %s\n" % api_response)
    except ApiException as e:
        logger.info("Exception when calling ExtensionsV1beta1Api->patch_namespaced_network_policy: %s\n" % e)

def delete_namespaced_network_policy(policyName, policyNamespace, cloudId=None):

    logger.info("------------- [%s] --------------" % sys._getframe().f_code.co_name)
    global v1_ext

    if cloudId != None:
        try:
            cloud = CloudConfig.cloud[cloudId]
            kub_config.load_kube_config(cloud["admin_config"])
            v1 = client.CoreV1Api()
            v1_ext = client.ExtensionsV1beta1Api()
            apiClient = client.ApiClient()
        except KeyError as e:
            logger.info("Cloud not found")
            response = {}
            response['status'] = 'Failure'
            response['message'] = 'Cloud not found'
            return response




    namespace = policyNamespace # str | object name and auth scope, such as for teams and projects
    body = client.V1DeleteOptions()
    #pretty = 'pretty_example' # str | If 'true', then the output is pretty printed. (optional)
    #grace_period_seconds = 56 
    #propagation_policy = 'propagation_policy_example' 
    name = policyName

    try: 
        api_response = v1_ext.delete_namespaced_network_policy(name,namespace, body, pretty='true')
        return api_response
        #pprint(api_response)
    except ApiException as e:
        logger.info("Exception when calling ExtensionsV1beta1Api->delete_namespaced_network_policy: %s\n" % e)
        return e


def delete_pod_security_policy():
    logger.info("------------- [%s] --------------" % sys._getframe().f_code.co_name)
    namespace = 'default' # str | object name and auth scope, such as for teams and projects
    body = client.V1DeleteOptions()
    pretty = 'pretty_example' # str | If 'true', then the output is pretty printed. (optional)
    grace_period_seconds = 56 
    propagation_policy = 'propagation_policy_example' 
    name = 'tmp2'

    try: 
        api_response = v1_ext.delete_pod_security_policy(name, body, pretty=pretty, grace_period_seconds=grace_period_seconds, propagation_policy=propagation_policy)
        #pprint(api_response)
    except ApiException as e:
        logger.info("Exception when calling ExtensionsV1beta1Api->delete_pod_security_policy: %s\n" % e)

def print_pod(pod_list):
    logger.info("------------- [%s] --------------" % sys._getframe().f_code.co_name)
    ret_dict=[]
    for pod in pod_list.items:
       tmp={'name':pod.metadata.name,'labels':pod.metadata.labels}
       ret_dict.append(tmp)
    return ret_dict

def get_policy_from_lable(obj_name,lable,policy):
    #logger.info("------------- [%s] --------------" % sys._getframe().f_code.co_name)
    for obj_key, obj_value in lable.items():
        for item in policy:
            if(item['ingress']):
                for loop in item['ingress']:
                    for i in loop._from:
                        match_label = i.pod_selector.match_labels
                        pol_key = [key for key, value in match_label.items() if value == obj_value]
                        if pol_key:
                            logger.info("Ingress rule for policy : %s is applicable on pod:%s " %(item['name'],obj_name))
            if(item['egress']):
                for loop in item['egress']:
                    for i in loop._from:
                        match_label = i.pod_selector.match_labels
                        pol_key = [key for key, value in match_label.items() if value == obj_value]
                        if pol_key:
                            logger.info("Egress rule for policy : %s is applicable on pod:%s" %(item['name'],obj_name))
                
    
def get_pod_policy_mapping(item):
    #logger.info("------------- [%s] --------------" % sys._getframe().f_code.co_name)
    if not item['objects']:
        logger.info("\nNo pods created in  Naamespace: [%s]  " %(item['namespace']))
        return
    for obj in item['objects']:
        for lable  in obj['labels']:
            policy_list=get_policy_from_lable(obj['name'],{lable:obj['labels'][lable]},item['policies'])


def print_net_policies(net_policy_list):
    logger.info("------------- [%s] --------------" % sys._getframe().f_code.co_name)
    ret_dict=[]
    for  net_policy in net_policy_list.items:
       #tmp_egress={'match_labels':net_policy.spec.egress
       tmp={'name':net_policy.metadata.name,'egress':net_policy.spec.egress,'ingress':net_policy.spec.ingress}
       ret_dict.append(tmp)
    return ret_dict

def update_policy_object(payload):
    logger.info("%s %s %s ", sys._getframe().f_code.co_name, "Payload:-", payload)
    logger.info("%s %s ", "type Payload:-", type(payload))
    dict_item = payload['items']
    logger.info("%s %s %s %s", "type item:-", type(dict_item),"item",dict_item)
    for item in (dict_item):
        tmp = Policy.nodes.filter(name=item['metadata']['name'])
        if len(tmp) == 0:
            #objPolicy = Policy(name=item['metadata']['name'], metaData=json.dumps(item['metadata']),
            #               spec=json.dumps(item['spec'])).save()
            objPolicy = Policy(name=item['metadata']['name'], metaData=item['metadata'],
                           spec=item['spec']).save()
        else:
            objPolicy = tmp[0]
            objPolicy.spec=(item['spec'])
            objPolicy.metaData=(item['metadata'])
            objPolicy.save()
        #ret_data.append(objPolicy.properties__)
        GphDB.addPolicyToNamespace(item['metadata']['namespace'], objPolicy) 
        logger.info("%s %s ", "namespace:-", item['metadata']['namespace'])
    ret_data = GphDB.getJSONgraph(cypherQuery=('MATCH p=()-[r:APPLIES_TO]->() RETURN p'))
    logger.info("ret_data type:%s ret_data:%s ", type(ret_data),ret_data)
    return ret_data

def getAlarmJSONgraph(params="KUBERNETES", postureName=None):
    if params == "KUBERNETES":
        return GphDB.getAlarmJSONgraph(cypherQuery=('START n=node(*) MATCH (n)-[r]-(m) WHERE n.cloudType = \'Kubernetes\' OR m.cloudType = \'Kubernetes\' RETURN n,r'))
    elif params == "AWS":
        return GphDB.getAlarmJSONgraph(cypherQuery=('START n=node(*) MATCH (n)-[r]-(m) WHERE n.cloudType = \'AWS\' OR  m.cloudType = \'AWS\'  RETURN n,r'))
    elif params == "BOTH":
        return GphDB.getAlarmJSONgraph(cypherQuery=('START n=node(*) MATCH (n)-[r]-(m) WHERE n.cloudType = \'AWS\' OR  m.cloudType = \'AWS\' OR n.cloudType = \'Kubernetes\' OR m.cloudType = \'Kubernetes\'  RETURN n,r'))
    elif params == "crisp":
        logger.critical("Received CRISP Request")
        if postureName:
            return GphDB.getAlarmJSONgraph(cypherQuery=('match (pos:SecurityPosture {name:"'+ postureName  +'"}) MATCH path = shortestPath( (pos)-[rels]-(nodes) ) return nodes, rels'))
        else:
            return GphDB.getAlarmJSONgraph(cypherQuery=('START n=node(*) MATCH (n)-[r]-(m) WHERE n.viewType = \'crisp\' OR m.viewType = \'crisp\'  RETURN n,r'))

def addToLabelDict(lblDict, label, obj):
    res = lblDict.get(label)
    if res is None:
        res = list()
        lblDict[label] = res
    res.append(obj)

def changeLabelDictToObjNames(lblDict):
    newDict = dict()
    for key, lstVal in lblDict.items():
        nmList = list()
        for val in lstVal:
            nmList.append(val.name)
        newDict[key] = nmList
    return newDict


def extractLabels(label):
    return str(label).replace("}","").replace("{","").replace("\"","").replace("\'","").split(',')[0]


class GenericGraphObject(object):

    def __init__(self, dictionary):
        """Constructor"""
        for key, value in dictionary.items():
            setattr(self, key, value)




def create_object_mapping(orgName="Aricent", conn=None):
    """TODO : It's the circle of life, And it moves us all
    Through despair and hope, Through faith and love
    ~ Elton John"""

    cloud_id = conn['Id']
    agent_obj = get_document_by_id_ver2('agents', str(cloud_id))
    print("Agent Q %s " %(agent_obj))
    topo_data = {'orgName' : orgName}
    nats_data = {'purpose' : 'Topology', 'data' : topo_data}
    response = NATSservice.send_request(agent_obj['agent_queue'], json.dumps(nats_data))
    topoString = json.loads(response)
    for key, value in topoString.items():
        topoString[key] = GenericGraphObject(value)
        
    #print("************* FINALRESPONSE IS *****************")
    #print(topoString)

 
    #topoString = read_topology_k8s(orgName, conn)
    if topoString:
        try:
            'Change this line based on encoding of JSON'
            topo = topoString
            'First create objects, later create relations'
            objectDictionary = dict()
            objectRelationsLst = list()  
            for obName in topo.keys():
               ob = topo[obName]
               gphObClass = globals()[ob.obtype]
               if gphObClass:
                   gphObj = gphObClass(name=ob.name)
                   if gphObj:
                       for propname in ob.properties.keys():
                           value = ob.properties[propname]
                           setattr(gphObj, propname, value)
                       gphObj = GphDB.addGphObject(gphObj)
                       objectDictionary[obName] = gphObj
                       for relname in ob.relations.keys():
                           for toobname in ob.relations[relname]:
                               objectRelationsLst.append((gphObj, relname, toobname))
                               print(".... Need relation %s from %s to %s" %(relname, gphObj.name, toobname))
            'Now create relations'
            for tup in objectRelationsLst:
                '''Create relation from relations tuple'''
                fromObRel = getattr(tup[0], tup[1])
                toObj = objectDictionary.get(tup[2])
                if toObj:
                    fromObRel.connect(toObj)
                    print(".... Relating %s to %s" %(tup[1] + "." + tup[0].name, tup[2]))
                elif not fromObRel:
                    print(".... Can't find %s src obj relation name" %(tup[0].name + "." + tup[1]))
                elif not toObj:
                    print(".... Can't find %s tgt obj for relation" %(tup[2]))
            
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("!!!! Exception, K8s Object mapping failed !!!!")
            print(exc_type, fname, exc_tb.tb_lineno)
            print(e)

    else:
        return None


def read_topology_k8s(orgName="Aricent", conn=None):
    "For ending is better than mending ― Aldous Huxley, Brave New World"

    print("--> create_object_mapping(): %s" %(datetime.datetime.now()))
    global kub_config, v1, v1_ext, client, apiClient
    if conn:
        kub_config.load_kube_config(conn["admin_config"])
        v1 = client.CoreV1Api()
        v1_ext = client.ExtensionsV1beta1Api()
        apiClient = client.ApiClient()
    print("... Connected, fetching objects")

    objectDictionary = dict()

    cloud = GenericGraphObject(name=conn["CloudName"],
                               obtype="Cloud")
    objectDictionary[cloud.name] = cloud
    assetGrp = GenericGraphObject(name="Kubernetes Infrastructure", 
                                  obtype="AssetGroup")
    objectDictionary[assetGrp.name] = assetGrp
    secControl = GenericGraphObject(name="Network Communications Security", 
                                    obtype="SecurityControl")
    objectDictionary[secControl.name] = secControl
    auditor = GenericGraphObject(name="SDWANControllerSysCalls", 
                                 obtype="Auditor")
    objectDictionary[auditor.name] = auditor
    parentObjURI = cloud.name
    try:

        org = GenericGraphObject(name=orgName, 
                                 obtype="Organization")
        objectDictionary[org.name] = org
        cloud.properties = {"name":conn["CloudName"],
                              "cloudType":"Kubernetes",
                              "cloudId":conn["Id"]}
        addToLabelDict(org.relations, "hasCloud", cloud.name)

        namespace_list = v1.list_namespace()
        labelDict = dict()
        for item in namespace_list.items:
            parentObjURI = cloud.name
            if (not item.metadata.cluster_name):
                cluster_name=cloud.name + "-" + "Cluster"
            else:
                cluster_name=item.metadata.cluster_name

            if objectDictionary.get(parentObjURI + "/" + cluster_name):
                clusInDB = objectDictionary[parentObjURI + "/" + cluster_name]
            else:
                clusInDB = GenericGraphObject(name=parentObjURI + "/" +cluster_name,
                                              obtype="Cluster")
                objectDictionary[clusInDB.name] = clusInDB
                clusInDB.properties = {"organization":orgName,
                                       "zone":conn["Region"],
                                       "cloudId":conn["Id"],
                                       "cloudType":"Kubernetes"}
            if cloud:
                addToLabelDict(cloud.relations, "hasCluster", clusInDB.name)
            if assetGrp:
                addToLabelDict(assetGrp.relations, "instanceCluster", clusInDB.name)
             
            nspInDB = GenericGraphObject(name=parentObjURI + "/" + item.metadata.name,
                                         obtype="Namespace")
            objectDictionary[nspInDB.name] = nspInDB
            nspInDB.properties = {"labels":jsonfiyForDB(item.metadata.labels)}
            addToLabelDict(labelDict,
                           extractLabels(nspInDB.properties["labels"]),
                           nspInDB)
            addToLabelDict(clusInDB.relations, "namespaces", nspInDB.name)

            pod_list = get_namespaced_pods(item.metadata.name)

            if pod_list:
                for pod in pod_list.items:
                    if not pod.spec.node_name:
                        node_name='Node-Unknown'
                    else:
                        node_name=pod.spec.node_name

                    ndNodes = objectDictionary.get(parentObjURI + "/" + cluster_name + "/" + node_name)
                    if not ndNodes:
                        ndNodes = GenericGraphObject(name=parentObjURI + "/" +cluster_name + "/" + node_name, 
                                                     obtype="Nodes")
                        objectDictionary[ndNodes.name] = ndNodes
                    if assetGrp:
                        addToLabelDict(assetGrp.relations, "instanceNode", ndNodes.name)

                    podInDB = objectDictionary.get(parentObjURI + "/" + cluster_name \
                                               + "/" + node_name + "/" + pod.metadata.name)
                    if not podInDB:
                        podInDB = GenericGraphObject(name = parentObjURI + "/" + cluster_name \
                                                     + "/" + node_name + "/" + pod.metadata.name,
                                                     obtype="WorkLoad")
                        objectDictionary[podInDB.name] = podInDB
                    podInDB.properties = {"workLoadType":"Pod",
                                            "version":pod.metadata.resource_version,
                                            "metaData":jsonfiyForDB(pod.metadata),
                                            "spec":jsonfiyForDB(pod.spec),
                                            "labels":json.dumps(jsonfiyForDB(pod.metadata.labels))}
                        
                    #logger.info("%s %s ","Pod Updated:",podInDB)
                    addToLabelDict(labelDict,
                                   extractLabels(podInDB.properties["labels"]),
                                   podInDB)


                    addToLabelDict(objectDictionary[clusInDB.name].relations, "clusternodes", ndNodes.name) 
                    addToLabelDict(objectDictionary[nspInDB.name].relations, "workload", podInDB.name)

                    for cont in pod.spec.containers:
                        #print(".... Component : %s" %(cont.name))
                        contInDB = objectDictionary.get(podInDB.name + "/" + cont.name)
                        if not contInDB:
                            contInDB = GenericGraphObject(name=podInDB.name + "/" + cont.name,
                                                          obtype="Component")
                            objectDictionary[contInDB.name] = contInDB
                        contInDB.properties = {"componentType":"Container",
                                                 "version":cont.image}
                        # logger.info("%s %s ","Container Added:",contInDB)

        if cloud:
            cloud.properties["usedLabels"] = json.dumps(changeLabelDictToObjNames(labelDict))
            print("... Updated labels in Cloud Object")

        print("... Fetched all objects, getting Policies")
        netPolicies = get_all_network_policy()
        parentObjURI = cloud.name
        for pol in netPolicies.items:
            #print("Found a policy")
            polInDB = objectDictionary.get(parentObjURI + "/" + pol.metadata.name)
            if polInDB:
                ''' Check if policy has been changed then send an alert'''
            else:
                polInDB = GenericGraphObject(name=parentObjURI + "/" + pol.metadata.name,
                                             obtype="Policy")
                objectDictionary[polInDB.name] = polInDB
            template = None
            if pol.metadata.labels: 
                template = pol.metadata.labels.get("template")
            polInDB.properties = {"version":pol.metadata.resource_version,
                                    "metadata":jsonfiyForDB(pol.metadata),
                                    "spec":jsonfiyForDB(pol.spec),
                                    "policyRules":json.dumps(jsonfiyForDB(
                                                   {"ingress":pol.spec.egress,
                                                    "egress":pol.spec.ingress})),
                                    "labels":json.dumps(jsonfiyForDB(pol.spec.pod_selector.match_labels))}
                #logger.info("%s %s ","NetworkPolicy Updated:",polInDB)
            if secControl:
                addToLabelDict(secControl.relations, "implPolicy", polInDB.name)

            strppolInDBlabels = extractLabels(polInDB.properties.get("labels"))
            if labelDict and labelDict.get(strppolInDBlabels):
                for appliedOn in labelDict.get(strppolInDBlabels):
                    #logger.info("%s %s : %s","Relationship Updated:", polInDB.name, appliedOn.name)
                    if appliedOn.obtype is "Namespace":
                        addToLabelDict(polInDB.relations, "appliesToNS", appliedOn.name)
                    elif appliedOn.obtype is "WorkLoad":
                        addToLabelDict(polInDB.relations, "appliesToWorkLoad", appliedOn.name)
            if template:
                addToLabelDict(polInDB.relations, "MAPS_TO_SECURITYCONFIGURATIONS", template)

        podSecPolicies = get_all_pod_security_policy()
        for pol in podSecPolicies.items:
            polInDB = objectDictionary.get(parentObjURI + "/" + pol.metadata.name)
            if not polInDB:
                polInDB = GenericGraphObject(name=parentObjURI + "/" + pol.metadata.name,
                                             obtype="Policy")
                objectDictionary[polInDB.name] = polInDB
            template = None
            if pol.metadata.labels:
                template = pol.metadata.labels.get("template")
            polInDB.properties["version"] = pol.metadata.resource_version
            polInDB.properties["metadata"] = jsonfiyForDB(pol.metadata)
            polInDB.properties["spec"] = jsonfiyForDB(pol.spec)
            polInDB.properties["policyRules"] = json.dumps(jsonfiyForDB(
                                           {"allow_privilege_escalation":pol.spec.allow_privilege_escalation,
                                            "allowed_capabilities":pol.spec.allowed_capabilities,
                                            "allowed_flex_volumes":pol.spec.allowed_flex_volumes,
                                            "allowed_host_paths":pol.spec.allowed_host_paths,
                                           }))
            polInDB.properties["labels"]=json.dumps(jsonfiyForDB(pol.metadata.labels))
               
            #logger.info("%s %s ","PodSecurityPolicy Updated:",polInDB)
            if secControl:
                addToLabelDict(secControl.relations, "implPolicy", polInDB.name)

            strppolInDBlabels = extractLabels(polInDB.properties["labels"])
            if labelDict and labelDict.get(strppolInDBlabels):
                for appliedOn in labelDict.get(strppolInDBlabels):
                    logger.critical("%s %s : %s","Relationship Updated:", polInDB.name, appliedOn.name)
                    if appliedOn.obtype is "Namespace":
                        addToLabelDict(polInDB.relations, "appliesToNS", appliedOn.name)
                    elif appliedOn.obtype is "WorkLoad":
                        addToLabelDict(polInDB.relations, "appliesToWorkLoad", appliedOn.name)
            if template:
                addToLabelDict(polInDB.relations, "MAPS_TO_SECURITYCONFIGURATIONS", template)

        print("..... Objects in Cluster : ")
        print(objectDictionary.keys())
        print("..... Done")
        print("<-- create_object_mapping(): %s" %(datetime.datetime.now()))

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print("!!!! Exception, Object mapping failed !!!!")
        print(exc_type, fname, exc_tb.tb_lineno)
        print(e)
    finally:
        #print("-------------- START JSON DUMP --------------")
        #for key in objectDictionary.keys():
        #    print(":: %s :: \n %s" %(key, json.dumps(objectDictionary[key].__dict__)))
        #print("-------------- END JSON DUMP --------------") 
        return objectDictionary

def create_object_mapping_orig(orgName="Aricent", conn=None):
    "The next day, a monolith appears near the apes. The apes erupt with fear." 
    "As they start to slowly calm down, they become more and more curious "
    "as they all reach and touch the surface of the monolith, starting with the leader ape"
    "- Stanley Kubrick, 2001 : A Space Odessey"

    print("--> create_object_mapping(): %s" %(datetime.datetime.now()))
    global kub_config, v1, v1_ext, client, apiClient
    if conn:
        kub_config.load_kube_config(conn["admin_config"])
        v1 = client.CoreV1Api()
        v1_ext = client.ExtensionsV1beta1Api()
        apiClient = client.ApiClient()
    print("... Connected, fetching objects")    
    assetGrp = GphDB.getGphObject("Kubernetes Infrastructure", AssetGroup)
    secControl = GphDB.getGphObject("Network Communications Security", SecurityControl)
    auditor = GphDB.getGphObject("SDWANControllerSysCalls", Auditor)
    clusterNameInConfig = conn["CloudName"]
    try:

        org = GphDB.getGphObject(orgName, Organization)        
        cloud = GphDB.getGphObject(conn["CloudName"], Cloud)
        if not cloud:
            cloud = Cloud(name=conn["CloudName"],
                          cloudType="Kubernetes",
                          cloudId=conn["Id"])
            cloud = GphDB.addGphObject(cloud)
            org.hasCloud.connect(cloud) 

        namespace_list = v1.list_namespace()
        k8sObjectDict = dict()
        labelDict = dict()
        for item in namespace_list.items:
            if (not item.metadata.cluster_name):
                cluster_name= clusterNameInConfig
            else:
                cluster_name=item.metadata.cluster_name
            clusInDB = GphDB.getGphObject(clusterNameInConfig + "_" + cluster_name, Cluster)
            if not clusInDB:
                clusInDB = Cluster(name=clusterNameInConfig + "_" + cluster_name,
                                   organization=orgName,
                                   zone=conn["Region"],
                                   cloudId=conn["Id"],
                                   cloudType="Kubernetes").save()
            if cloud:
                cloud.hasCluster.connect(clusInDB)
            if assetGrp:
                assetGrp.instanceCluster.connect(clusInDB)
            k8sObjectDict[str(clusInDB.name)]=clusInDB
            nspInDB = GphDB.getGphObject(clusterNameInConfig + "_" + item.metadata.name, Namespace)
            if not nspInDB:
                nspInDB = Namespace(name=clusterNameInConfig + "_" + item.metadata.name,
                                    labels=jsonfiyForDB(item.metadata.labels)).save()
            else:
                nspInDB.labels = jsonfiyForDB(item.metadata.labels)
    
            k8sObjectDict[str(nspInDB.name)]=nspInDB
            addToLabelDict(labelDict,
                           extractLabels(nspInDB.labels),
                           nspInDB)
            GphDB.addNamespaceToCluster(clusInDB.name, nspInDB)
            #logger.info("%s %s ","Cluster Added:",clusInDB)
            #logger.info("%s %s ","Namespace: Added",nspInDB)
            pod_list = get_namespaced_pods(item.metadata.name)
            if pod_list:
                for pod in pod_list.items:
                    if not pod.spec.node_name:
                        node_name='Node-Unknown'
                    else:
                        node_name=pod.spec.node_name
                
                    ndNodes = GphDB.getGphObject(clusterNameInConfig + "_" + node_name, Nodes)
                    if not ndNodes:
                        ndNodes = Nodes(name=clusterNameInConfig + "_" + node_name).save()
                    k8sObjectDict[str(ndNodes.name)]=ndNodes
                    if assetGrp:
                        assetGrp.instanceNode.connect(ndNodes)
                
                    podInDB = GphDB.getGphObject(clusterNameInConfig + "_" + pod.metadata.name, WorkLoad)
                    if not podInDB:
                        podInDB = WorkLoad(name=clusterNameInConfig + "_" + pod.metadata.name, 
                                           workLoadType="Pod", 
                                           version=pod.metadata.resource_version,
                                           metaData=jsonfiyForDB(pod.metadata),
                                           spec=jsonfiyForDB(pod.spec),
                                           labels=json.dumps(jsonfiyForDB(pod.metadata.labels)))
                        podInDB = GphDB.addGphObject(podInDB)
                        #logger.info("%s %s ","Pod Added:",podInDB) 
                    else:
                        podInDB.version=pod.metadata.resource_version
                        podInDB.metaData=jsonfiyForDB(pod.metadata)
                        podInDB.spec=jsonfiyForDB(pod.spec)
                        podInDB.labels=json.dumps(jsonfiyForDB(pod.metadata.labels))
                        podInDB.save()
                        podInDB = GphDB.getGphObject(clusterNameInConfig + "_" + pod.metadata.name, WorkLoad)
                        #logger.info("%s %s ","Pod Updated:",podInDB)
                    addToLabelDict(labelDict, 
                                   extractLabels(podInDB.labels),
                                   podInDB)  
                    k8sObjectDict[str(podInDB.name)]=podInDB
    
                
                    GphDB.addNodeToCluster(clusInDB.name, ndNodes)
                    GphDB.addWorkLoadToNamespace(nspInDB.name, podInDB)
    
                    for cont in pod.spec.containers:
                        #print(".... Component : %s" %(cont.name))
                        contInDB = GphDB.getGphObject(clusterNameInConfig + "_" + cont.name, Component)
                        if not contInDB:
                            contInDB = Component(name=clusterNameInConfig + "_" + cont.name, 
                                                 componentType="Container", 
                                                 version=cont.image)
                            contInDB = GphDB.addGphObject(contInDB) 
                            GphDB.addComponentToWorkLoad(podInDB.name, contInDB)
                            # logger.info("%s %s ","Container Added:",contInDB)
                        k8sObjectDict[str(contInDB.name)]=contInDB
    
                        # --- Test Alarms ---
                        #if cont.name == "test-cont":
                        #    GphDB.updateAlarmForObject(someObjName=cont.name, alarmClass="Critical", alarmText="Internet access attempt", alarmState="Active")
                        #    alarm = GphDB.getGphObject("Internet access attempt", Alarm)
                        #    if auditor and alarm:
                        #        auditor.hasAlarms.connect(alarm) 
        if cloud:
            cloud.usedLabels = json.dumps(changeLabelDictToObjNames(labelDict))
            cloud.save()
            print("... Updated labels in Cloud Object")
    
        print("... Fetched all objects, getting Policies")
        netPolicies = get_all_network_policy()
        for pol in netPolicies.items:
            #print("Found a policy")
            polInDB = GphDB.getGphObject(clusterNameInConfig + "_" + pol.metadata.name, Policy)
            if polInDB:
                ''' Check if policy has been changed then send an alert'''
                policyUpdated = __check_if_policy_updated(pol, polInDB, clusterNameInConfig)
    
     
            else:
                polInDB = Policy(name=clusterNameInConfig + "_" + pol.metadata.name,
                                 version=pol.metadata.resource_version,
                                 metadata=jsonfiyForDB(pol.metadata),
                                 spec=jsonfiyForDB(pol.spec),
                                 policyRules=json.dumps(jsonfiyForDB(
                                                        {"ingress":pol.spec.egress, 
                                                         "egress":pol.spec.ingress})),
                                 labels=json.dumps(jsonfiyForDB(pol.spec.pod_selector.match_labels))).save()
                #logger.info("%s %s ","NetworkPolicy Updated:",polInDB)
            if secControl:
                secControl.implPolicy.connect(polInDB)
    
            k8sObjectDict[str(polInDB.name)]=polInDB
            strppolInDBlabels = extractLabels(polInDB.labels)
            if labelDict and labelDict.get(strppolInDBlabels):
                for appliedOn in labelDict.get(strppolInDBlabels):
                    #logger.info("%s %s : %s","Relationship Updated:", polInDB.name, appliedOn.name)
                    if type(appliedOn) is Namespace:
                        polInDB.appliesToNS.connect(appliedOn)
                    elif type(appliedOn) is WorkLoad:
                        polInDB.appliesToWorkLoad.connect(appliedOn)
    
        podSecPolicies = get_all_pod_security_policy()
        for pol in podSecPolicies.items:
            polInDB = GphDB.getGphObject(clusterNameInConfig + "_" + pol.metadata.name, Policy)
            if polInDB:
                polInDB.version=pol.metadata.resource_version
                polInDB.metadata=jsonfiyForDB(pol.metadata)
                polInDB.spec=jsonfiyForDB(pol.spec)
                polInDB.policyRules=json.dumps(jsonfiyForDB(
                                               {"allow_privilege_escalation":pol.spec.allow_privilege_escalation, 
                                                "allowed_capabilities":pol.spec.allowed_capabilities,
                                                "allowed_flex_volumes":pol.spec.allowed_flex_volumes,
                                                "allowed_host_paths":pol.spec.allowed_host_paths,
                                               }))
                polInDB.labels=json.dumps(jsonfiyForDB(pol.metadata.labels))
                polInDB.save()
                #logger.info("%s %s ","PodSecurityPolicy Updated:",polInDB)
            else:
                polInDB = Policy(name=clusterNameInConfig + "_" + pol.metadata.name,
                             version=pol.metadata.resource_version,
                             metadata=jsonfiyForDB(pol.metadata),
                             spec=jsonfiyForDB(pol.spec),
                             policyRules=json.dumps(jsonfiyForDB(
                                           {"allow_privilege_escalation":pol.spec.allow_privilege_escalation, 
                                            "allowed_capabilities":pol.spec.allowed_capabilities,
                                            "allowed_flex_volumes":pol.spec.allowed_flex_volumes,
                                            "allowed_host_paths":pol.spec.allowed_host_paths,
                                            })),
                             labels=json.dumps(jsonfiyForDB(pol.metadata.labels))).save()
            #logger.info("%s %s ","PodSecurityPolicy Added:",polInDB)
            if secControl:
                secControl.implPolicy.connect(polInDB)

            k8sObjectDict[str(polInDB.name)]=polInDB
            strppolInDBlabels = extractLabels(polInDB.labels)
            if labelDict and labelDict.get(strppolInDBlabels):
                for appliedOn in labelDict.get(strppolInDBlabels):
                    logger.critical("%s %s : %s","Relationship Updated:", polInDB.name, appliedOn.name)
                    if type(appliedOn) is Namespace:
                        polInDB.appliesToNS.connect(appliedOn)
                    elif type(appliedOn) is WorkLoad:
                        polInDB.appliesToWorkLoad.connect(appliedOn)
    
        allObjs = Namespace.nodes.all() + WorkLoad.nodes.all() + Policy.nodes.all() + Component.nodes.all()
        logger.info("%s : %s", "allObjs", allObjs)
        for gpgObj in allObjs:
            # print("Gph Object in k8sObjectDict :" +  str(gpgObj.name) + str(k8sObjectDict.get(str(gpgObj.name))))
            if k8sObjectDict.get(str(gpgObj.name)) is None and gpgObj.name.startswith(clusterNameInConfig):
                try:
                    gpgObj.delete()
                    logger.warning("%s %s ", "Gph Object Deleted :", gpgObj.name)
                except Exception as e:
                    print("Warning: Failed to delete %s" %(gpgObj.name))
        print("..... Objects in Cluster : ")
        print(k8sObjectDict.keys())
        print("..... Done")
        print("<-- create_object_mapping(): %s" %(datetime.datetime.now()))
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print("!!!! Exception, Object mapping failed !!!!")
        print(exc_type, fname, exc_tb.tb_lineno)
        print(e)


''' Method checks if Policy data during refresh is different from that in the DB for the same Policy'''
'''Looks for changes in PodSelector, Ingress and Egress blocks '''
def __check_if_policy_updated(policy, polInDB, clusterNameInConfig):

    
    dbSpec = ast.literal_eval(revertJsonifyForDd(polInDB.spec))
    policySpec = ast.literal_eval(str(policy.spec))

    someObjName = policy.metadata.name
    alarmClass = 'CRITICAL'
    alarmText = 'Policy tampered'
    alarmState = "ACTIVE"

    if dbSpec == policySpec:
        GphDB.removeAlarmFromObject(someObjName, alarmText)
        return True
    else:
        alarmPaylod = {}
        alarmPaylod['objectName'] = someObjName
        alarmPaylod['criticality'] = alarmClass
        alarmPaylod['alarmDescription'] = alarmText

        GphDB.updateAlarmForObject(someObjName, alarmClass, alarmText, alarmState)
        post_request('alarms',  json.dumps(alarmPaylod))
        ''' Don't update policy in DB'''
        '''
        polInDB.version=policy.metadata.resource_version
        polInDB.metadata=jsonfiyForDB(policy.metadata)
        polInDB.spec=jsonfiyForDB(policy.spec)
        polInDB.policyRules=json.dumps(jsonfiyForDB(
                                           {"ingress":policy.spec.ingress,
                                            "egress":policy.spec.egress}))
        polInDB.labels=json.dumps(jsonfiyForDB(policy.spec.pod_selector.match_labels))
        polInDB.save() 
        ''' 
        return False


