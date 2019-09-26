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

from util.cloud_framework import BaseCloudInterfce, CloudFactory
from util.common_def import service_logger
import os
from kubernetes import client, config, watch
from kubernetes.client.rest import ApiException
import json
import pdb
#pdb.set_trace()
#config.load_kube_config('/home/ubuntu/admin.conf')
#v1 = client.CoreV1Api()
#v1_ext = client.ExtensionsV1beta1Api()

def serialize(obj):
    if isinstance(obj, date):
        serial = obj.isoformat()
        return serial

    return obj.__dict__


class kubernetesPodInterface():
    def deletePod(podName, podNameSpace):
        name = podName
        namespace = podNameSpace
        body = client.V1DeleteOptions()
        grace_period_seconds = 0
        propagation_policy = 'Foreground'
        service_logger.info("-------DELETE POD Request------")
        service_logger.info("Podname: " + podName + " , Pod Namespace : " + podNameSpace)
        
        try: 
            api_response = v1.delete_namespaced_pod(name, namespace, body, pretty='true', grace_period_seconds=grace_period_seconds, propagation_policy=propagation_policy)
            service_logger.info("-------DELETE POD SUCCESS  Response------")
            service_logger.info(api_response)
            return("Success")
        except ApiException as e:
            service_logger.info("-------DELETE POD ERROR Response------")
            service_logger.info(e)
            return(e.body)

class KubernetesCloudInterfce(BaseCloudInterfce):
    """ Base class to define instance plugin interface. """

    def __init__(self):
        """ constructor method for instance"""
        #config.load_kube_config('/home/ubuntu/admin.conf')
        #v1 = client.CoreV1Api()
        #v1_ext = client.ExtensionsV1beta1Api()

    def connect_to_peer(self):
        """ establish connection with peer """
        pass

    def getRegion(self):
        """ returns instance list """
        service_logger.info("Udita KubernetesCloudInterfce :%s", self)
        return "K8sEvent_getRegion"

    def addRegion(self):
        service_logger.error("%s %s %s ", sys._getframe().f_code.co_name, "This service is not supported for :%s", self)

    def deleteRegion(self):
        service_logger.error("%s %s %s ", sys._getframe().f_code.co_name, "This service is not supported for :%s", self)

    def updateRegion(self):
        service_logger.error("%s %s %s ", sys._getframe().f_code.co_name, "This service is not supported for :%s", self)

    def getVpc(self,payload):
        service_logger.error("%s %s %s ", sys._getframe().f_code.co_name, "This service is not supported for :%s", self)

    def addVpc(self):
        service_logger.error("%s %s %s ", sys._getframe().f_code.co_name, "This service is not supported for :%s", self)

    def deleteVpc(self):
        service_logger.error("%s %s %s ", sys._getframe().f_code.co_name, "This service is not supported for :%s", self)

    def updateVpc(self):
        service_logger.error("%s %s %s ", sys._getframe().f_code.co_name, "This service is not supported for :%s", self)

    def getSecurityGroup(payload):
        service_logger.info("%s %s %s ", sys._getframe().f_code.co_name, "payload :", payload)

        import pdb
        #v1 = client.CoreV1Api()
        #v1_ext = client.ExtensionsV1beta1Api()
        #pdb.set_trace()
        buf = json.loads(payload)
        if('namespace' in buf):
            return v1_ext.list_namespaced_network_policy(buf['namespace'])     
        else:
            resp = v1_ext.list_network_policy_for_all_namespaces()
            service_logger.info("%s %s %s %s ", "resp type:", type(resp), "resp : ", resp)
            resp1= resp.to_dict()
            service_logger.info("%s %s %s %s ", "resp1 type:", type(resp1), "resp1 : ", resp1)
            return resp1

    def addSecurityGroup(self,payload):
        service_logger.info("%s %s %s ", sys._getframe().f_code.co_name, "payload :", payload)
        namespace = payload['namespace']
        body = client.V1beta1NetworkPolicy() # V1beta1NetworkPolicy |
        pretty = 'pretty_example' # str | If 'true', then the output is pretty printed. (optional)
        body.metadata = client.V1ObjectMeta()
        body.metadata.name = payload['name']
        try:
            body.metadata.name = payload['name']
            #api_response = self.v1_ext.create_namespaced_network_policy(namespace, body, pretty=pretty)
        except ApiException as e:
            service_logger.error("Exception when calling ExtensionsV1beta1Api->create_namespaced_network_policy: %s\n" % e)


    def deleteSecurityGroup(self):
        service_logger.error("%s %s %s ", sys._getframe().f_code.co_name, "This service is not supported for :%s", self)

    def updateSecurityGroup(self):
        service_logger.error("%s %s %s ", sys._getframe().f_code.co_name, "This service is not supported for :%s", self)

    def getIngressRule(self):
        service_logger.error("%s %s %s ", sys._getframe().f_code.co_name, "This service is not supported for :%s", self)
    
    def addIngressRule(self):
        service_logger.error("%s %s %s ", sys._getframe().f_code.co_name, "This service is not supported for :%s", self)

    def deleteIngressRule(self):
        service_logger.error("%s %s %s ", sys._getframe().f_code.co_name, "This service is not supported for :%s", self)

    def updateIngressRule(self,payload):
        service_logger.error("%s %s %s ", sys._getframe().f_code.co_name, "This service is not supported for :%s", self)

    def getEgressRule(self):
        service_logger.error("%s %s %s ", sys._getframe().f_code.co_name, "This service is not supported for :%s", self)

    def addEgressRule(self):
        service_logger.error("%s %s %s ", sys._getframe().f_code.co_name, "This service is not supported for :%s", self)

    def deleteEgressRule(self):
        service_logger.error("%s %s %s ", sys._getframe().f_code.co_name, "This service is not supported for :%s", self)

    def updateEgressRule(self,payload):
        service_logger.error("%s %s %s ", sys._getframe().f_code.co_name, "This service is not supported for :%s", self)
        namespace = payload['namespace']
        name = payload['name']
        body = get_network_policy_obj(namespace,name)
        if( not body):
            logger_info("Object (%s) not found \n" % name )
            return
        try:
            egress_len = len(body.spec.egress)     
            egress = [client.V1beta1NetworkPolicyEgressRule()]
            egress.ports = [{'port': 80, 'protocol': 'TCP'}]
            body.spec.egress.append(egress)
            #api_response = self.v1_ext.patch_namespaced_network_policy(name, namespace, body, pretty=pretty)
        except ApiException as e:
            logger_info("Exception when calling ExtensionsV1beta1Api->patch_namespaced_network_policy: %s\n" % e)


class KubernetesCloud(CloudFactory):
    def __init__(cls,name):
        super().__init__(KubernetesCloudInterfce())
        service_logger.info("Kubernetes instance (%s) created ", name)
        #cls.index = super(AwsCloud).counter
        #self.cloud_name = name
        #return obj
    '''    
    def __init__(self,name):
        service_logger.info("creating Kubernetes instance ")
        super().__init__(KubernetesCloudInterfce())
        self.cloud_name = name
        cls.index = super(AwsCloud).counter
    '''
    def getCloudName(self):
        return self.cloud_name





