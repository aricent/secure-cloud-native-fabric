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
from django.shortcuts import render
from .models import Region, SecurityGroup, Vpc, SmIssues, RunningCloudTable
from .serializers import RegionSerializer, SecurityGroupSerializer, VpcSerializer, SmSerializer, OnlyVpcSerializer, CloudSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
import pdb
import datetime
import time
import json
#import sys
from nameko.events import EventDispatcher, event_handler
from nameko.standalone.rpc import ClusterRpcProxy
from nameko.rpc import rpc
from django_filters.rest_framework import DjangoFilterBackend
import logging
from util.kubernetes_service import KubernetesCloud, KubernetesCloudInterfce, kubernetesPodInterface
from util.kube_watch import update_policy_object, create_object_mapping, getAlarmJSONgraph, patch_namespaced_network_policy, create_namespaced_network_policy, create_pod_security_policy, create_network_policy, delete_namespaced_network_policy, replace_network_policy
from util.gphmodels import GphDB, Component, WorkLoad, Policy, Cluster, Alarm, Cloud
import string
from util.elastic_search_client import *
#from util.elastic_search_client import get_request, post_request, get_all_documents, get_search_results, update_document, delete_document, get_document_by_id,get_audit_report, post_request_ver2, get_search_results_in_array, check_index_exists
import yaml
from util.common_def import *
import base64
import urllib.parse

#from util.gphmodels import Policy
#class PolSerializer(serializers.ModelSerializer):
#    class Meta:
#            model = Policy

logger = logging.getLogger(__name__)

CONFIG = {'AMQP_URI': "amqp://guest:guest@localhost:5672"}


def index(request):
    return render(request, '../templates/index.html', None)

def timeDelta(last_updated):
    last_updated = last_updated[0].LastUpdated
    time_now = datetime.datetime.utcnow().replace(tzinfo=utc)
    time_delta = (time_now -  last_updated)
    time_delta = time_delta.total_seconds()
    return time_delta

def timeDiff(last_updated):
    last_updated = last_updated.LastUpdated
    time_now = datetime.datetime.utcnow().replace(tzinfo=utc)
    time_delta = (time_now -  last_updated)
    time_delta = time_delta.total_seconds()
    return time_delta

def secgrp(request):
    secgrp_details = {}
    return render(request, '../templates/aws_secgrp.html', secgrp_details)




class VpcList(APIView):
    """
    get: List all Vpcs.
    """
    def get(self, request, format=None):
        logger.info("Request for VPC List received")
        tmp = request.query_params.get('cloudType', None)
        crispReq = request.query_params.get('viewType', None)
        if crispReq == 'crisp':
            postureName = request.query_params.get('postureName', None)
            ret_val=getAlarmJSONgraph("crisp", postureName)
            return Response(ret_val)
        if(tmp == 'KUBERNETES' ):
            ret_val=getAlarmJSONgraph("KUBERNETES")
            return Response(ret_val)
        if(tmp == 'AWS' ):
            ret_val=getAlarmJSONgraph("AWS")
            return Response(ret_val)

        else:
            ret_val=getAlarmJSONgraph("BOTH")
            return Response(ret_val)


class MonitoredObject(APIView):

    def post(self, request, format=None):
        action = self.request.query_params.get('action', None)
        podName = request.data.get('objectName')
        alarmText = request.data.get('alarmText')

        if(podName is None or alarmText is None):
            return Response({"message" : "Incomplete delete request"}, status = status.HTTP_400_BAD_REQUEST)

        podData = GphDB.getGphObject(podName, WorkLoad)
        if(podData == None):
            return Response({"message" : "POD not found"}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            podMetaData = podData.metaData
        #logger.info("----------------META DATA------------")
        #logger.info(podMetaData)
        new_metadata = str.replace(podMetaData, '\'', '\"')
        metaDataNoneFix = str.replace(new_metadata, 'None', 'null')
        metadataTrueFix = str.replace(metaDataNoneFix, 'True', 'true')
        metadataFalseFix = str.replace(metadataTrueFix, 'False', 'false')
        next_metadata = metadataFalseFix
        splitMetaOne = next_metadata.split('\"creation_timestamp\":', 1 )[0]
        splitMetaTwo = next_metadata.split('\"creation_timestamp\":', 1 )[1]
        splitMetaThree = splitMetaTwo.split('\"', 1 )[1]
        finalMetaData = splitMetaOne + '\"' + splitMetaThree


        next_metadata = finalMetaData
        splitMetaOne = next_metadata.split('\"deletion_timestamp\":', 1 )[0]
        splitMetaTwo = next_metadata.split('\"deletion_timestamp\":', 1 )[1]
        splitMetaThree = splitMetaTwo.split('\"', 1 )[1]
        finalMetaData = splitMetaOne + '\"' + splitMetaThree

        logger.info("-----------------------METADATA2-----")
        logger.info(finalMetaData)
        podMetaDataJson = json.loads(finalMetaData)

        if(action == 'delete' ):
            deleteRespone =  self.delete_pod(podMetaDataJson, podName, alarmText) 
            if(deleteRespone == 0):
                for i in range(len(alarmText)):
                    alarmData = alarmText[i].get('alarmText')
                    GphDB.removeAlarmFromObject(podName, alarmData) 
                return Response({"message" : "Success"})
            else:
                return Response({"message" : "Delete POD failed"}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)

        elif(action == 'isolate'):
            isloateResponse =  self.isolate_pod(podMetaDataJson,podName, alarmText)
            if(isloateResponse == 0):
                for i in range(len(alarmText)):
                    alarmData = alarmText[i].get('alarmText')
                    GphDB.removeAlarmFromObject(podName, alarmData)
                return Response({"message" : "Isolation Triggered Successfully!"})
            elif(isloateResponse == 1):
                return Response({"message" : "Pod Security Policy created successfully but Namespaced Network Policy creation failed"}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
            elif(isloateResponse == 2):
                return Response({"message" : "Namespaced Network Policy created successfully but Pod Security Policy creation failed"}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response({"message" : "Isolation Policy creation failed"}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)

        elif(action == 'isolate_delete'):
            isloateResponse =  self.isolate_pod(podMetaDataJson,podName, alarmText)
            deleteRespone =  self.delete_pod(podMetaDataJson, podName, alarmText)
     
            if(isloateResponse == 0 and deleteRespone == 0):
                GphDB.removeAlarmFromObject(podName, alarmText)
                return Response({"message" : "Success"})
            elif(isloateResponse == 0 and deleteRespone != 0):
                GphDB.removeAlarmFromObject(podName, alarmText)
                return Response({"message" : "Isolate Successful, Delete Failed"})
            elif(deleteRespone == 0 and isloateResponse != 0 ):
                GphDB.removeAlarmFromObject(podName, alarmText)
                return Response({"message" : "Delete Successful, Isolate Failed"})
            else:
                return Response({"message" : "Both Requests failed"}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:  
            return Response({"message" : "Action not supported"}, status = status.HTTP_400_BAD_REQUEST) 
	   
    def delete_pod(self,podMetaDataJson, podName, alarmText):
        podNameSpace = podMetaDataJson.get('namespace')
        #logger.info("----------------META DATA JSON AFTER------------")
        #logger.info(podNameSpace)
        kubeResponse = kubernetesPodInterface.deletePod(podName, podNameSpace)
        if(kubeResponse == "Success"):
            #GphDB.removeAlarmFromObject(podName, alarmText)
            return 0
            #method to delete the pod
        else:
            logger.info("----------------DELETE POD FAILED RESPONSE-----------------")
            logger.info(kubeResponse)
            return 1

    def isolate_pod(self,podMetaDataJson, podName, alarmText):
        podNameSpace = podMetaDataJson.get('namespace')
        podLabel = podMetaDataJson.get('labels')

        create_namespaced_network_policy_response = create_namespaced_network_policy(podName, podNameSpace, podLabel )
        logger.info("----------------CREATE NAMESPACED NETWORK POLICY RESPONSE------------")
        logger.info(create_namespaced_network_policy_response)

        create_pod_security_policy_response = create_pod_security_policy(podName, podNameSpace, podLabel )
        logger.info("----------------CREATE POD SECURITY POLICY RESPONSE------------")
        logger.info(create_pod_security_policy_response)

        if(create_namespaced_network_policy_response == 'failure' and create_pod_security_policy_response != 'failure'):
            return 1 #Response({"message" : "Pod Security Policy created successfully but Namespaced Network Policy creation failed"}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
        elif(create_pod_security_policy_response == 'failure' and create_namespaced_network_policy_response != 'failure'):
            return 2 #Response({"message" : "Namespaced Network Policy created successfully but Pod Security Policy creation failed"}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
        elif(create_pod_security_policy_response == 'failure' and create_namespaced_network_policy_response == 'failure'):
            return 3 #Response({"message" : "Isolation Policy creation failed"}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            #GphDB.removeAlarmFromObject(podName, alarmText)
            return 0 #Response({"message" : "Isolation Triggered Successfully!"})


class Policies(APIView):
    def get(self, request, format=None):
        if 'GroupId' in request.GET : 
            GroupId = request.GET['GroupId']
            policy_document = get_document_by_id('policies', request.GET['GroupId'])
            if 'found' not in policy_document.keys() or not policy_document.get('found'):
                return Response({"message" : "Policy not Found."}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
            elif policy_document.get('_source').get('cloudType') == 'KUBERNETES':
                policy_document_yaml = yaml.dump(policy_document.get('_source').get('requestData'))
                return Response(data = policy_document_yaml, content_type='application/x-yaml')
            else:
                policy_document_yaml = yaml.dump(policy_document.get('_source'))
                return Response(data = policy_document_yaml, content_type='application/x-yaml')
                #return Response(policy_document.get('_source'))

        policies = get_all_documents('policies')
        #logger.info(policies)
        return Response(policies)


    def post(self, request, format=None):
        cloudType = self.request.query_params.get('cloudType', None)#request.data.get('cloudType')
        #post_request('policies', json.dumps(request.data))
        response = {}

        if cloudType == 'AWS':
            request_data = yaml.load(request.body, Loader=yaml.FullLoader)
        
            cid = request_data['cloudId']
            region = request_data['region']
            ingress_request = None
            egress_request = None
            if 'ingressRules' in request_data:
                ingress_request = request_data['ingressRules']
            if 'egressRules'  in request_data:
                egress_request = request_data['egressRules']
            group_request = {}
            group_request['GroupName'] = request_data['GroupName']
            group_request['VpcId']   = request_data['VpcId']
            group_request['Description'] = request_data['Description']

            aws_resp = self.create_aws_securitygroup(group_request, region, cid)
            aws_resp_dict = json.loads(aws_resp)   
            logger.info("resp ----" + aws_resp)
            if 'GroupId' in aws_resp_dict:
                reasons = []
                sgSuccessResponse = {}
                securityGroupSuccess = {}
                securityGroupSuccess['status'] = 'Success'
                securityGroupSuccess['policyId'] = aws_resp_dict['GroupId']
                sgReason = {}
                sgReason['securityPolicy'] = 'Successfully Created'
                reasons.append(sgReason)
                #sgSuccessResponse['securityPolicy'] = securityGroupSuccess
                #response.update(sgSuccessResponse)
                

                if ingress_request != None and ingress_request['New_IpPermissions']:
                    ingress_request.update({'GroupId' : aws_resp_dict['GroupId']})
                    ingress_resp = self.add_aws_ingress_rules(ingress_request, region, cid)
                    #logger.info("------------SUCCESSFULLY ADDED INGRESS------------")
                    if 'ResponseMetadata' in ingress_resp:
                        ingress_response_metadata = ingress_resp['ResponseMetadata']
                        if ingress_response_metadata['HTTPStatusCode'] == 200:
                            #response.update({"ingress" : {"status":"Success"}})
                            ingressReason = {}
                            ingressReason['ingress'] = 'Successfully Created'
                            reasons.append(ingressReason)
                        else:
                            securityGroupSuccess['status'] = 'Failure'
                            #response.update({"ingress" :{"status": "Failure"}})
                    else:
                        ingressReason = {}
                        ingressReason['ingress'] = ingress_resp['exception']
                        reasons.append(ingressReason)
                        securityGroupSuccess['status'] = 'Failure'
                        '''failureReason = {} 
                        ingressError = {}
                        ingressError['status'] = "Failure"
                        ingressError['reason'] = "Ingress-Error : " + ingress_resp['exception']
                        failureReason['ingress'] = ingressError
                        response.update(failureReason)'''


                #Add check for If Egress list is provided
                if egress_request != None and egress_request['New_IpPermissions']:
                    egress_request.update({'GroupId' : aws_resp_dict['GroupId']})
                    egress_resp = self.add_aws_egress_rules(egress_request, region, cid)
                    #logger.info("------------SUV^?CCESSFULLY ADDED EGRESS------------")
                    if 'ResponseMetadata' in egress_resp:
                        egress_response_metadata = egress_resp['ResponseMetadata']
                        if egress_response_metadata['HTTPStatusCode'] == 200:
                            #response.update({"egress" : {"status":"Success"}})
                            egressReason = {}
                            egressReason['egress'] = 'Successfully Created'
                            reasons.append(egressReason)
                        else:
                            securityGroupSuccess['status'] = 'Failure'
                            #response.update({"egress" :{"status": "Failure"}})
                    else:
                        egressReason = {}
                        egressReason['egress'] = egress_resp['exception']
                        reasons.append(egressReason)
                        securityGroupSuccess['status'] = 'Failure'

                        '''failureReason = {}
                        egressError = {}
                        egressError['status'] = "Failure"
                        egressError['reason'] = "Egress-Error : " +  egress_resp['exception']
                        failureReason['egress'] = egressError
                        response.update(failureReason)'''
                request_data['GroupId'] = aws_resp_dict['GroupId']
                request_data['cloudType'] = "AWS"
                post_request('policies', json.dumps(request_data), identity=aws_resp_dict['GroupId'])

                securityGroupSuccess['reasons'] = reasons
                response.update(securityGroupSuccess)

            else:
               
                reasons = [] 
                securityGroupFailure = {}
                securityGroupFailure['status'] = "Failure"
                sgReason = {}
                sgReason['securityPolicy'] = aws_resp_dict['exception']
                reasons.append(sgReason)
                securityGroupFailure['reasons'] = reasons
                response.update(securityGroupFailure)


        elif cloudType == 'KUBERNETES':
            'Add code to communicate with KUBERNETES'
            #logger.info("In KUBERNETES")
            request_dict = yaml.load(request.body, Loader=yaml.FullLoader)
            json_req_part = {}
            name_space = None
            kube_response = None

            kube_response = create_network_policy(name_space, request_dict)
            #logger.info("---------------RESPONSE---------------")
            #logger.info(kube_response)
   
 
            if 'status' in kube_response.keys() and kube_response.get('status') == 'Success':
                #logger.info("------STATUS is SUccess for Kube Policy")
                temp_response = {}
                temp_response['status'] = "Success"
                temp_response['GroupId'] = kube_response['uid']
                reasons = []
                sgReason = {}
                sgReason['securityPolicy'] = 'Successfully Created'
                reasons.append(sgReason)
                temp_response['reasons'] = reasons
                response.update(temp_response)

                """----Add to DB when Success-----"""
                db_data = {}
                db_data['cloudType'] = "KUBERNETES"
                db_data['GroupId'] = kube_response['uid']
                db_data['requestData'] = request_dict
                respo = post_request('policies', json.dumps(db_data), identity=kube_response['uid'])
                #logger.info("KUBER POST RESPONSE _ " + respo)
            elif 'status' in kube_response.keys() and kube_response.get('status') == 'Failure':
                temp_response = {}
                temp_response['status'] = "Failure"
                reasons = []
                sgReason = {}
                sgReason['securityPolicy'] = kube_response['message']
                reasons.append(sgReason)
                temp_response['reasons'] = sgReason
                reasons.append(temp_response)
                response.update(temp_response)
                #temp_response['reason'] = kube_response['message']
                #response['securityPolicy'] = temp_response
            else:
                temp_response = {}
                temp_response['status'] = "Failure"
                reasons = []
                sgReason = {}
                sgReason['securityPolicy'] = 'Undefined status or fields'
                reasons.append(sgReason)
                temp_response['reasons'] = sgReason
                reason.append(temp_response)
                response.update(temp_response)
                #temp_response['reason'] = 'Undefined status or fields'
                #response['securityPolicy'] = temp_response

        else:
            reasons = []
            sgReason = {}
            sgReason['securityPolicy'] = 'Invalid cloud type'
            reasonsupdate(sgReason)
            response['status'] = 'Failure'
            response['reasons'] = reasons
            return Response(response, status = status.HTTP_400_BAD_REQUEST)

        if (response['status'] == 'Failure'):
            return Response(response, status = status.HTTP_500_INTERNAL_SERVER_ERROR)

        else:
            return Response(response, status = status.HTTP_201_CREATED)


    def put(self, request, format=None):
        #logger.info("------------UPDATE REQUEST------------")
        response = {}
        if 'GroupId' not in request.GET :
            reasons = []
            sgReason = {}
            sgReason['securityPolicy'] = 'Policy Id Missing in request'
            response['status'] = 'Failure'
            response['reasons'] = sgReason
            return Response(response, status = status.HTTP_400_BAD_REQUEST)

        GroupId = request.GET['GroupId']

        policy_document = get_document_by_id('policies', request.GET['GroupId'])

        if 'found' not in policy_document.keys() or not policy_document.get('found'):
            reasons = []
            sgReason = {}
            sgReason['securityPolicy'] = 'Policy not found'
            response['status'] = 'Failure'
            response['reasons'] = sgReason
            return Response(response, status = status.HTTP_400_BAD_REQUEST)

        request_dict = yaml.load(request.body, Loader=yaml.FullLoader)

        cloudType =  policy_document.get('_source').get('cloudType')


        if cloudType == 'AWS':
            cid = policy_document.get('_source').get('cloudId')
            region = policy_document.get('_source').get('region')
            ingress_request = None
            egress_request = None
            securityGroupResponse = {}
            securityGroupResponse['status'] = 'Success'
            reasons = []

            if 'ingressRules' in request_dict:
                ingress_request = request_dict['ingressRules']
            if 'egressRules'  in request_dict:
                egress_request = request_dict['egressRules']
	
            if ingress_request != None and (len(ingress_request['Old_IpPermissions']) != 0 or len(ingress_request['New_IpPermissions']) != 0):
                ingress_request.update({'GroupId' : GroupId})
                ingress_resp = self.add_aws_ingress_rules(ingress_request, region, cid)
                #logger.info("------------SUV^?CCESSFULLY ADDED INGRESS------------")
                if 'ResponseMetadata' in ingress_resp:
                    ingress_response_metadata = ingress_resp['ResponseMetadata']
                    if ingress_response_metadata['HTTPStatusCode'] == 200:
                        #response.update({"ingress" : {"status":"Success"}})
                        ingressReason = {}
                        ingressReason['ingress'] = 'Successfully Updated'
                        reasons.append(ingressReason)

                        update_object = {}
                        update_object['ingressRules'] = ingress_request
                        update_document('policies', GroupId, update_object)
                    else:
                        securityGroupResponse['status'] = 'Failure'
                        #response.update({"ingress" :{"status": "Failure"}})
                else:
                    ingressReason = {}
                    ingressReason['ingress'] = ingress_resp['exception']
                    reasons.append(ingressReason)
                    securityGroupResponse['status'] = 'Failure'
                    
                    '''failureReason = {}
                    ingressError = {}
                    ingressError['status'] = "Failure"
                    ingressError['reason'] = "Ingress-Error : " + ingress_resp['exception']
                    failureReason['ingress'] = ingressError
                    response.update(failureReason)'''
            if egress_request != None and (len(egress_request['Old_IpPermissions']) != 0 or len(egress_request['New_IpPermissions']) != 0):
                #logger.info("-------EGRESS UPDATE REQUEST-----")
                egress_request.update({'GroupId' : GroupId})
                egress_resp = self.add_aws_egress_rules(egress_request, region, cid)
                #logger.info("------------SUV^?CCESSFULLY ADDED EGRESS------------")
                if 'ResponseMetadata' in egress_resp:
                    egress_response_metadata = egress_resp['ResponseMetadata']
                    if egress_response_metadata['HTTPStatusCode'] == 200:
                        #response.update({"egress" : {"status":"Success"}})
                        egressReason = {}
                        egressReason['egress'] = 'Successfully Updated'
                        reasons.append(egressReason)

                        update_object = {}
                        update_object['egressRules'] = egress_request
                        update_document('policies', GroupId, update_object)
                    else:
                        securityGroupResponse['status'] = 'Failure'
                        #response.update({"egress" :{"status": "Failure"}})
                else:
                    egressReason = {}
                    egressReason['egress'] = egress_resp['exception']
                    reasons.append(egressReason)
                    securityGroupResponse['status'] = 'Failure'

                    '''failureReason = {}
                    egressError = {}
                    egressError['status'] = "Failure"
                    egressError['reason'] = "Egress-Error : " + egress_resp['exception']
                    failureReason['egress'] = egressError
                    response.update(failureReason)'''

            securityGroupResponse['reasons'] = reasons
            response.update(securityGroupResponse)

        elif cloudType == 'KUBERNETES':
            name = policy_document.get('_source').get('requestData').get('metadata').get('name')
            namespace = policy_document.get('_source').get('requestData').get('metadata').get('namespace')

            kube_response = replace_network_policy(name, namespace, request_dict)
            #logger.info("---------------RESPONSE---------------")
            #logger.info(kube_response)

            temp_response = {}
            temp_response['status'] = "Success"
            reasons = []

            if 'status' in kube_response.keys() and kube_response.get('status') == 'Success':
                sgReason = {}
                sgReason['securityPolicy'] = "Successfully Updated"
                reasons.append(sgReason)
                #temp_response['GroupId'] = kube_response['uid']
                #response['securityPolicy'] = temp_response

                """----Add to DB when Success-----"""
                db_data = {}
                db_data['cloudType'] = "KUBERNETES"
                db_data['GroupId'] = policy_document.get('_source').get('GroupId')
                db_data['requestData'] = request_dict
                post_request('policies', json.dumps(db_data), policy_document.get('_source').get('GroupId'))
            elif 'status' in kube_response.keys() and kube_response.get('status') == 'Failure':
                temp_response['status'] = "Failure"
                sgReason = {}
                sgReason['securityPolicy'] = kube_response['message']
                reasons.append(sgReason)
                #temp_response['reason'] = kube_response['message']
                #response['securityPolicy'] = temp_response
            else:
                temp_response['status'] = "Failure"
                sgReason = {}
                sgReason['securityPolicy'] = kube_response['message']
                reasons.append(sgReason)
                #temp_response['reason'] = 'Undefined status or fields in reponse'
                #response['securityPolicy'] = temp_response
            
            temp_response['reasons'] = reasons
            response.update(temp_response)

        else:
            reasons = []
            sgReason = {}
            sgReason['securityPolicy'] = 'Invalid cloud type'
            response['status'] = 'Failure'
            response['reasons'] = sgReason
            return Response(response, status = status.HTTP_400_BAD_REQUEST)


        if (response['status'] == 'Failure'):
            return Response(response, status = status.HTTP_500_INTERNAL_SERVER_ERROR)

        else:
            return Response(response)


    def delete(self, request, format=None):
        logger.info("------------DELETE REQUEST------------")
        
        if 'GroupId' not in request.GET :
            return Response({"message" : "Policy Id Missing in request"}, status = status.HTTP_400_BAD_REQUEST)    
        GroupId = request.GET['GroupId']
        policy_document = get_document_by_id('policies', request.GET['GroupId'])
        if 'found' not in policy_document.keys() or not policy_document.get('found'): 
            return Response({"message" : "Policy not Found."}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        cloudType = policy_document.get('_source').get('cloudType')
        response = {}
        if cloudType == 'AWS':
            cid = policy_document.get('_source').get('cloudId')
            region = policy_document.get('_source').get('region')
            payload = {}
            payload['GroupId'] = GroupId 
            delete_resp = self.delete_security_group(payload, region, cid)
            logger.info("------------DELETE SECURITY GROUP------------" + json.dumps(delete_resp))
            delete_document('policies', GroupId)
            response.update({'message' : 'Success'})
        elif cloudType == 'KUBERNETES':
            name = policy_document.get('_source').get('requestData').get('metadata').get('name')
            namespace = policy_document.get('_source').get('requestData').get('metadata').get('namespace')
            del_response = delete_namespaced_network_policy(name, namespace)
            logger.info(del_response)
            delete_document('policies', GroupId)
            response['status'] = 'Success'
            
        else:
            return Response({"message" : "Invalid cloud type"}, status = status.HTTP_400_BAD_REQUEST)
        return Response(response)


    def create_aws_securitygroup(self, request, region, cid):
        logger.info("--------------SECURITY GROUP LIST------------")

        with ClusterRpcProxy(CONFIG) as rpc:
            data = {}
            data['CloudId'] = cid
            data['region'] = region  #.RegionName_id
            data['payload'] = request
            json_data = json.dumps(data)
            logger.info("--------------Before RPC------------" + json_data)
            res = rpc.guiHandler.dispatchCreateSecurityGroup(payload=json_data, tags=[])

        print("----------AFTER response back to views------------------" )
        return res

    def add_aws_ingress_rules(self, request, region, cid):
        logger.info("---------------BEFORE INGRESS------------" + json.dumps(request))
        with ClusterRpcProxy(CONFIG) as rpc:
            data = {}
            data['CloudId'] = cid
            data['region'] = region
            data['payload'] = request
            json_data = json.dumps(data)
            response = rpc.guiHandler.dispatchUpdateSgRulesIngress(json_data )

        return response


    def add_aws_egress_rules(self, request, region, cid):
        logger.info("---------------BEFORE EGRESS------------" + json.dumps(request))
        with ClusterRpcProxy(CONFIG) as rpc:
            data = {}
            data['CloudId'] = cid
            data['region'] = region
            data['payload'] = request
            json_data = json.dumps(data)
            response = rpc.guiHandler.dispatchUpdateSgRulesEgress(json_data )

        return response

    def delete_security_group(self, request, region, cid):
        logger.info("---------------BEFORE EGRESS------------" + json.dumps(request))
        with ClusterRpcProxy(CONFIG) as rpc:
            data = {}
            data['CloudId'] = cid
            data['region'] = region
            data['payload'] = request
            json_data = json.dumps(data)
            response = rpc.guiHandler.dispatchDeleteSecurityGroup(json_data )

        return response


class CrispPostureGraph(APIView):
    """
    get: Retrieve a Posture Graph.

    put: Update a Posture Graph.

    post: Create a Posture Graph.

    """
    def __createSecurityPostureGraph(self, postureName, jsonDoc, orgName):
        with ClusterRpcProxy(CONFIG) as rpc:
            resp = None
            try:
                if postureName and orgName and jsonDoc:
                    logger.info("calling SecurityPostureGraph.createSecurityPostureGraph ----1") 
                    resp = rpc.SecurityPostureGraph.createSecurityPostureGraph(postureName,
                                                                               jsonDoc,
                                                                               orgName)
                    logger.info("---------RPC RESPONSE______________")
                    logger.info(resp)
                elif postureName and jsonDoc:
                    logger.info("calling SecurityPostureGraph.createSecurityPostureGraph ----2")
                    resp = rpc.SecurityPostureGraph.createSecurityPostureGraph(postureName,
                                                                               jsonDoc)
            #except Exception as e:
            finally:
                "logger.info(e)"

            logger.info("---Back to views after RPC---")
            logger.info(resp)
            return resp

    def get(self, request, format=None):
        logger.info("Get Policy Posture")
        with ClusterRpcProxy(CONFIG) as rpc:
            req = request.data
            postureName = None
            orgName = None
            resp = [{"result":"Failure", "error":"cause unknown"}]
            
            if 'catalog'  in request.GET and request.GET['catalog']=='true':
                catalog = None
                if 'orgname' in request.GET :
                    orgName = request.GET['orgname']
                    catalog = rpc.SecurityPostureGraph.getCrispCatalogs(orgName=orgName)
                else:
                    catalog = rpc.SecurityPostureGraph.getCrispCatalogs()

                logger.info(catalog)
                return Response(catalog)
           
            if 'postureNames'  in request.GET and request.GET['postureNames']=='true':
                postureNames = None
                if 'orgname' in request.GET :
                    orgName = request.GET['orgname']
                    postureNames = rpc.SecurityPostureGraph.getSecurityPostureNames(orgName=orgName)
                else:
                    postureNames = rpc.SecurityPostureGraph.getSecurityPostureNames()

                logger.info(postureNames)
                return Response(postureNames)

            if 'posturename' in request.GET :
                postureName = request.GET['posturename']

            if 'orgname' in request.GET :
                orgName = request.GET['orgname']

            try:
                if postureName and orgName:
                    logger.info(orgName)
                    logger.info(postureName)
                    resp = rpc.SecurityPostureGraph.getSecurityPostureGraph(orgName=orgName,
                                                                            postureName=postureName)
                elif postureName:
                    resp = rpc.SecurityPostureGraph.getSecurityPostureGraph(postureName=postureName)
                elif orgName:
                    resp = rpc.SecurityPostureGraph.getSecurityPostureGraph(orgName=orgName)
                else:
                    resp = [{"result":"Failure",
                             "error":"Invalid params recd postureName : {postureName}, orgname : {orgName}  ".format(postureName, orgName)}]
            except Exception as e:
                print(e)
            logger.info(resp)
            return Response(resp)
    def put(self, request, pk, format=None):
        return Response({"message":"Operation not supported ... yet :)"},
                        status = status.HTTP_400_BAD_REQUEST)
    def delete(self, request,format=None):
        if 'catalog'  in request.GET and request.GET['catalog']=='true' and 'id' in request.GET :
            component_id = request.GET['id']
            with ClusterRpcProxy(CONFIG) as rpc:
                logger.info("calling SecurityPostureGraph.deleteCrispComponent(---1")
                delete_res =  rpc.SecurityPostureGraph.deleteCrispComponent(component_id, component=None, orgName="Aricent")        
                logger.info("----------DELETE RES---------------")
                logger.info(delete_res)

            return Response({'status' : 'success'})
        else:
            return Response({"message":"Operation not supported ... yet :)"},
                        status = status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        logger.info("Post Policy Posture")
        req = request.data
        resp = {"Result":"Failure, cause unknown"}
        if(len(request.data) < 1):
            return Response({"message" : "Empty request"}, status = status.HTTP_400_BAD_REQUEST)
        if "json" not in request.content_type:
            req = json.loads(request.data)


        if 'catalog'  in request.GET and request.GET['catalog']=='true':
            with ClusterRpcProxy(CONFIG) as rpc:
                logger.info("calling SecurityPostureGraph.addCrispComponent(---1")
                resp = rpc.SecurityPostureGraph.addCrispComponent(component = req)
            resp = json.loads(resp)
            #return Response(resp)
            if resp['result'] == 'created':
                return Response({'status' : 'Success', 'reason':'Created Successfully'})    
            else:
                return Response({'status' : 'Failure', 'reason':'Creation Failed'}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)

        posturename = req['posturename']
        orgname = req['orgname']
        jsondoc = req['jsondoc']

        logger.info(orgname)
        logger.info( posturename)
        resp = self.__createSecurityPostureGraph(postureName = posturename,
                                                 jsonDoc = jsondoc,
                                                 orgName = orgname)
        logger.info(resp)
        return Response(resp)


class CrispPostureMap(APIView):
    def get(self, request, format=None):
        with ClusterRpcProxy(CONFIG) as rpc:
            logger.info("in CrispPostureMap get request")
            orgName = None
            posturename = None
            resp = [{"result":"Failure", "error":"cause unknown"}]
            if 'baseline'  in request.GET and request.GET['baseline']=='true':                
                logger.info("---baseline")
                if 'orgname' in request.GET :
                    orgName = request.GET['orgname']
                    resp = rpc.SecurityPostureMap.getBaselineEVAmap(orgNm=orgName)
                else:
                    resp = rpc.SecurityPostureMap.getBaselineEVAmap()
                logger.info(resp)
            else:
                logger.info("---baseline FALSE")

                if 'posturename' in request.GET :
                    posturename = request.GET['posturename']

                if 'orgname' in request.GET :
                    orgName = request.GET['orgname']
                    
                if(orgName != None and posturename != None):
                    resp = rpc.SecurityPostureMap.getEVAmap(orgNm=orgName, postureName = posturename)
    
                elif(orgName != None and posturename == None):
                    resp = rpc.SecurityPostureMap.getEVAmap(orgNm=orgName)

                elif(orgName == None and posturename != None):
                    resp = rpc.SecurityPostureMap.getEVAmap(postureName = posturename)
    
                else:
                    resp = rpc.SecurityPostureMap.getEVAmap()
                logger.info(resp)
            return Response(resp)


        
class Auditor(APIView):
    def get(self, request, format=None):
        logger.info("Get from Auditor")
        if 'types'  in request.GET and request.GET['types']=='true':
            'return the Auditor types'
            with ClusterRpcProxy(CONFIG) as rpc:
                resp = rpc.AuditorService.getAuditorTypes()

            #logger.info(resp)
            return Response(resp)


        elif 'auditortype' in request.GET:
            auditor_type = request.GET['auditortype']
            'return all the auditors for the auditor type'
            query_dict = {'jsondoc.auditor_type':auditor_type}
            auditors = get_search_results('auditors', query_dict)
            res = json.loads(auditors)['hits']['hits']
            if res:
                auditor_string = ''
                for obj in res:
                    auditor_string += obj['_source']['jsondoc']['auditor_name'] + ','

                default_auditor_name = auditor_type + '_default'
                res = get_document_by_id('auditors', default_auditor_name)
                #auditor_yaml = yaml.dump(res['_source']['jsondoc']['auditor_body'])
                auditor_yaml = base64.b64decode(res['_source']['blob']).decode('ascii')
                response = Response(data=auditor_yaml, content_type='application/x-yaml')
                response['auditors'] = auditor_string
                return response
            else:
                return Response({"message" : "Auditor Type Not Supported"}, status = status.HTTP_400_BAD_REQUEST)
                
        elif 'auditorname'  in request.GET:
            auditor_name = request.GET['auditorname']
            'return the auditor with the auditor name'
            res = get_document_by_id('auditors', urllib.parse.quote_plus(auditor_name))
            if 'found' not in res.keys() or not res.get('found'):
                return Response({"message" : "Auditor not Found."}, status = status.HTTP_400_BAD_REQUEST)
            #auditor_yaml = yaml.dump(res['_source']['jsondoc']['auditor_body'])
            auditor_yaml = base64.b64decode(res['_source']['blob']).decode('ascii')
            response = Response(data=auditor_yaml, content_type='application/x-yaml')
            response['auditortype'] = res['_source']['jsondoc']['auditor_type']
            response['auditorname'] = res['_source']['jsondoc']['auditor_name']
            return response

        elif 'reports'  in request.GET and request.GET['reports']=='true':
            final_res = None
            if 'cluster' in request.GET and 'auditor_type' in request.GET:
                
                if 'start_time' in request.GET and 'end_time' not in request.GET:
                    return Response({"status" : "Failure", "message" : "End time needed."}, status = status.HTTP_400_BAD_REQUEST)
  
                elif 'start_time' not in request.GET and 'end_time'  in request.GET:
                    return Response({"status" : "Failure", "message" : "Start time needed."}, status = status.HTTP_400_BAD_REQUEST)
             
                elif 'start_time' in request.GET and 'end_time'  in request.GET: 
                    if request.GET['start_time'] > request.GET['end_time']:
                        return Response({"status" : "Failure", "message" : "Start time should be less than end time."}, status = status.HTTP_400_BAD_REQUEST)
                    else:
                        res = get_audit_report(request.GET['cluster'], request.GET['auditor_type'], request.GET['start_time'], request.GET['end_time'])
                        final_res = self._buildAuditReport(res)
                      


                else:
                    #get the latest report on this auditor instance
                    res = get_audit_report(request.GET['cluster'], request.GET['auditor_type'])
                    final_res = self._buildAuditReport(res)
                                
            else:
                ''' fetch all the records from Elastic DB for reports sorted by time'''
                res = get_all_documents('audit_reports')
                ''' CALL _buildAuditReport()'''
                final_res = self._buildAuditReport(res)
                
            return Response(final_res)

        else:
            'either return error/ or all the auditors'
            res = get_all_documents('auditor_cluster_registry')
            result = []
            for obj in res:
                data = obj.get("_source").get("jsondoc")
                result.append(data)
            
            return Response(result)
            

    def post(self, request, format=None):

        if 'HTTP_AUDITORTYPE' not in request.META or 'HTTP_POSTURENAME' not in request.META \
                or 'HTTP_CLUSTERS' not in request.META:
            return Response({"status": "Failure", 'reason': 'Mandatory headers missing'},
                            status=status.HTTP_400_BAD_REQUEST)

        auditor_type = request.META['HTTP_AUDITORTYPE']
        posture_name = request.META['HTTP_POSTURENAME']
        clusters = request.META['HTTP_CLUSTERS']
        cluster_list = clusters.split(',')
        auditor_body = request.body.decode('utf-8')


        logger.info("Before calling get auditor types")
        with ClusterRpcProxy(CONFIG) as rpc:
            available_auditor_types = rpc.AuditorService.getAuditorTypes()

        if auditor_type not in available_auditor_types:
            return Response({"status": "Failure", 'reason': 'Invalid Auditor Type'}, status=status.HTTP_400_BAD_REQUEST)

        mapping_data = {
            'auditorType': auditor_type,
            'postureName': posture_name,
            'clusters': cluster_list,
            'auditorBody': auditor_body
        }
        logger.info("Before callingCreate")
        with ClusterRpcProxy(CONFIG) as rpc:
            result = rpc.AuditorService.createAuditorAndMapCluster(mapping_data)

        return Response({'message': result})

    def _buildAuditReport(self, data):
        #data_dict = json.loads(data)
        final_audit_report = []
        for obj in data:
            metadata = obj['_source']['metadata']
            data_body = obj['_source']['jsondoc']
            cluster = data_body['cluster']
            auditor_type = data_body['auditor_type']
            audit_report = data_body['audit_report']
            
            auditors = []            
            for mon_auditor in audit_report['auditors']:
                auditor = {}
                items = []
                for mon_item in mon_auditor['items']:
                    item = {}
                    item['objectName']   = mon_item['name']
                    audit_issues = []
                    for mon_audit_issue in mon_item['audit_issues']:
                        issue = {}
                        issue_description = None
                        if mon_audit_issue['issue'] != None:
                            issue_description = mon_audit_issue['issue'] 

                        if mon_audit_issue['notes'] != None:
                            issue_description = issue_description + ' - '+ mon_audit_issue['notes']

                        issue['description'] = issue_description

                        if mon_audit_issue['score'] <10:
                            issue['criticality'] = 'Minor'
                        else:
                            issue['criticality'] = 'Critical'
                        audit_issues.append(issue)
                    item['audit_issues'] = audit_issues
                    items.append(item)
                auditor['items'] = items
                auditors.append(auditor)


            final_audit_obj = {}
            final_audit_obj['cluster'] = cluster
            final_audit_obj['auditor_type'] = auditor_type
            final_audit_obj['timestamp'] = metadata['timestamp']
            final_audit_obj['audit_result'] = auditors    

            final_audit_report.append(final_audit_obj)
        return final_audit_report

class RunAuditor(APIView):

    def post(self, request, format=None):
        auditor_type = request.data['auditortype']
        cluster = request.data['cluster']

        with ClusterRpcProxy(CONFIG) as rpc:
            available_auditor_types = rpc.AuditorService.getAuditorTypes()
        if auditor_type not in available_auditor_types:
            return Response({"status": "Failure", 'reason': 'Invalid Auditor Type'}, status=status.HTTP_400_BAD_REQUEST)

        data = {
            'auditorType' : auditor_type,
            'cluster' : cluster
        }
        with ClusterRpcProxy(CONFIG) as rpc:
            result = rpc.AuditorService.runAuditorForCluster(data)

        return Response({'message': result})
                                                                  


class PolicyTemplate(APIView):

    def __add_policy_template_to_components(self, template_name, cloudType):
        query_dict_parent = {"parent": "topLevel", "text": "Security Configurations"}
        search_data_parent = get_search_results_in_array('components', query_dict_parent)
        if len(search_data_parent) < 1:
            return

        parent = search_data_parent[0]

        #data = {}
        classLabels = {}
        classLabels['cloudType'] = cloudType
        #data['classLabels'] = classLabels      

        component_data = {}
        component_data['text'] = template_name
        component_data['description']  = template_name
        component_data['type'] = 'level2'
        component_data['parent'] = parent['id']
        component_data['nodeType'] = parent['text']
        component_data['classLabels'] = classLabels

        with ClusterRpcProxy(CONFIG) as rpc:
            logger.info("calling SecurityPostureGraph.addCrispComponent(---1")
            resp = rpc.SecurityPostureGraph.addCrispComponent(component = component_data)

    def __delete_policy_template_from_components(self, template_name):
        query_dict_component = {'nodeType' : "Security Configurations", 'text' : template_name}
        component_search = get_search_results_in_array('components', query_dict_component)

        if len(component_search) < 1:
            return

        component = component_search[0]
        with ClusterRpcProxy(CONFIG) as rpc:
            logger.info("calling SecurityPostureGraph.deleteCrispComponent(---1")
            resp = rpc.SecurityPostureGraph.deleteCrispComponent( component['id'], component=component, orgName="Aricent")

    def post(self, request, format=None):

        cloudType = self.request.query_params.get('cloudType', None)
        request_data = yaml.load(request.body, Loader=yaml.FullLoader)
        metadata = {}
         
        metadata['cloudType'] = cloudType

        template_name = None
        if cloudType == 'AWS':
            template_name = request_data['GroupName']
        else:
            template_name = request_data['metadata']['name']

        if(check_index_exists('policy_templates')):
            check_template = get_document_by_id('policy_templates', template_name)
            if (check_template['found']):
                return Response({'status' : 'Failure', "reason" :  "Policy already exists."}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)

        res = post_request_ver2(index = 'policy_templates', data = json.dumps(request_data), identity = template_name, metadata=metadata)

        self.__add_policy_template_to_components(template_name, cloudType)  
        return Response({'status': 'Success'})

    def get(self, request, format=None):

        '''---Add code to get if Policy Template with given id is being referred by some policy ---'''
        if 'cloudType' in request.GET:
            cloudType = request.GET['cloudType']
            policyTemplates = []
            searchResp = json.loads(get_search_results('policy_templates', {'metadata.cloudType' : cloudType})).get('hits').get('hits')
            if cloudType == 'AWS':
                for template in searchResp:
                    temp = {}
                    temp['name'] =  template.get('_source').get('jsondoc').get('GroupName')
                    temp['id'] = template.get('_id')
                    policyTemplates.append(temp)
            elif cloudType == 'KUBERNETES':
                for template in searchResp:
                    temp = {}
                    temp['name'] =  template.get('_source').get('jsondoc').get('metadata').get('name')
                    temp['id'] = template.get('_id')
                    policyTemplates.append(temp)
            else:
                return Response({'status' : 'Failure', "reason" : "Invalid CloudType"}, status = status.HTTP_400_BAD_REQUEST) 

            return Response(policyTemplates)

        elif 'id' in request.GET :
            policy_document = get_document_by_id('policy_templates', request.GET['id'])
            if 'found' not in policy_document.keys() or not policy_document.get('found'):
                return Response({'status' : 'Failure', "reason" :  "Policy not Found."}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                policy_document_yaml = yaml.dump(policy_document.get('_source').get('jsondoc'))
                logger.info(json.dumps(policy_document))
                return Response(data = policy_document_yaml, content_type='application/x-yaml')
        else:
            policies = get_all_documents('policy_templates', raw_data=True)
        
            returnPolicies = []
            for policy in policies:
                temp_policy = {}
                temp_policy['id'] = policy['_id']
                temp_policy['cloudType'] = policy['_source']['metadata']['cloudType']
                if policy.get('_source').get('metadata').get('cloudType') == 'AWS':
                    temp_policy['name'] = policy['_source']['jsondoc']['GroupName']
                    temp_policy['description'] = policy['_source']['jsondoc']['Description']
                else:
                    temp_policy['name'] = policy['_source']['jsondoc']['metadata']['name']
                #temp_policy['request_data'] = policy['_source']['jsondoc']['request_data']
                returnPolicies.append(temp_policy)
            return Response(returnPolicies)
 
        
    def delete(self, request, format=None):

        if 'id' not in request.GET :
             return Response({'status' : 'Failure', "reason" : "Policy Template Id Missing in request"}, status = status.HTTP_400_BAD_REQUEST)
        policy_document = get_document_by_id('policy_templates', request.GET['id'])
        if 'found' not in policy_document.keys() or not policy_document.get('found'):
            return Response({'status' : 'Failure', "reason" : "Policy-Template not Found."}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)

        self.__delete_policy_template_from_components(request.GET['id'])
        delete_document('policy_templates', request.GET['id'])
        return Response({'status': 'Success'})


    def put(self, request, format=None):
        if 'id' not in request.GET :
            return Response({'status' : 'Failure', "reason" : "Policy Template Id Missing in request"}, status = status.HTTP_400_BAD_REQUEST)

        policy_document = get_document_by_id('policy_templates', request.GET['id'])

        if 'found' not in policy_document.keys() or not policy_document.get('found'):
            return Response({'status' : 'Failure', "reason" : "Policy-Template not Found."}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)

        dataBody = {}
        dataBody['cloudType'] = policy_document['_source']['metadata']['cloudType']
        dataBody['request_data'] = yaml.load(request.body, Loader=yaml.FullLoader)
        post_request_ver2(index = 'policy_templates', data = json.dumps(dataBody), identity = request.GET['id'], metadata=None)
        return Response({'status': 'Success'})


class PolicyInstances(APIView):

    def post(self, request, format=None):

        response = {}
        response['status'] = 'yet to be set'
        reasons = []

        templateId = request.data.get('templateId')
        if templateId is None :
            reasons.append({'securityPolicy' : "Policy Template Id Missing in request"})
            return Response({'status': 'Failure', 'reasons' : reasons }, status = status.HTTP_400_BAD_REQUEST)

        policy_document = get_document_by_id('policy_templates', templateId)

        if 'found' not in policy_document.keys() or not policy_document.get('found'):
            reasons.append({'securityPolicy' : "Policy Template not found"})
            return Response({'status': 'Failure', 'reasons' : reasons }, status = status.HTTP_500_INTERNAL_SERVER_ERROR)


        '''If Cloud type is AWS '''
        if policy_document['_source']['metadata']['cloudType'] == 'AWS':
            region = request.data.get('region')
            vpcId = request.data.get('vpcId')
            cloudId = request.data.get('cloudId')

            if(region is None or vpcId is None or cloudId is None):           
                reasons.append({'securityPolicy' : "Mandatory fields missing"})
                return Response({'status': 'Failure', 'reasons' : reasons }, status = status.HTTP_400_BAD_REQUEST)
        
            response = self.create_aws_securitygroup(request, policy_document)

        elif policy_document['_source']['metadata']['cloudType'] == 'KUBERNETES':
            response = self.create_kubernetes_policy(request, policy_document)

        else:
            reasons.update({'securityPolicy' : 'Cloud Type not supported'})
            return Response({'status': 'Failure', 'reasons' : reasons}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
      
        if (response['status'] == 'Failure'):
            return Response(response, status = status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(response, status = status.HTTP_201_CREATED)


    def get(self, request, format=None):
        '''if 'policyId' in request.GET :
            policy_document = get_document_by_id('policy_instances', request.GET['policyId'])
            if 'found' not in policy_document.keys() or not policy_document.get('found'):
                return Response({'status' : 'Failure', "reason" : "Policy not Found."}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
            policy_document_yaml = yaml.dump(policy_document.get('_source').get('jsondoc'))
            return Response(data = policy_document_yaml, content_type='application/x-yaml')

        policies = get_all_documents('policy_instances')
        formatted_policies = []
        for policy in policies:
            temp_policy = {}
            #temp_policy.update(policy.get('_source').get('jsondoc'))
            temp_policy['policyId'] = policy.get('_source').get('metadata').get('policyId')
            temp_policy['cloudId'] =  policy.get('_source').get('metadata').get('cloudId')
            #temp_policy['template'] = policy.get('_source').get('metadata').get('template')
            temp_policy['cloudType'] = policy.get('_source').get('metadata').get('cloudType')

            if policy.get('_source').get('metadata').get('cloudType') == 'AWS':
                temp_policy['name'] = policy.get('_source').get('jsondoc').get('GroupName')
                temp_policy['description'] = policy.get('_source').get('jsondoc').get('Description')
            else:
                temp_policy['name'] =  policy.get('_source').get('jsondoc').get('metadata').get('name')
            formatted_policies.append(temp_policy)'''

        policies = GphDB.getAllGphObjects(Policy)
        response_policies = []
        if policies != None:
            for policy in policies:
                temp = {}
                if policy.cloudType == 'AWS':
                    temp['cloudType'] = policy.cloudType
                    temp['name'] = policy.spec['GroupName']
                    temp['cluster'] = policy.spec['VpcId']
                    temp['description'] = policy.spec['Description']
                    #temp['tags'] = policy.spec['tags']
                    temp['id'] = policy.spec['GroupId']
                    response_policies.append(temp)
                    #cluster = GphDB.getGphObject(policy.spec['VpcId'],Policy)
                    #logger.info("----Policy ---")
                    #logger.info(policy)
                elif policy.cloudType == 'Kubernetes':
                    temp['cloudType'] = policy.cloudType
                    temp['name'] = policy.name
                    #temp['cluster'] = policy.spec['VpcId']
                    #temp['description'] = policy.spec['Description']
                    #temp['id'] = policy.spec['GroupId']
                    response_policies.append(temp)



        #logger.info("---All Policies---")
        #logger.info(policies)
        
        return Response(response_policies)
 

    def delete(self, request, format=None):

        if 'policyId' not in request.GET :
            return Response({'status': 'Failure', "reason" : "Policy Id Missing in request"}, status = status.HTTP_400_BAD_REQUEST)
        policy_document = get_document_by_id('policy_instances', request.GET['policyId'])
        if 'found' not in policy_document.keys() or not policy_document.get('found'):
            return Response({'status' : 'Failure', 'reason' : "Policy not Found."}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)

        cloudType = policy_document.get('_source').get('metadata').get('cloudType')
        response = {}
        if cloudType == 'AWS':
            cid = policy_document.get('_source').get('metadata').get('cloudId')
            region = policy_document.get('_source').get('jsondoc').get('region')
            payload = {}
            payload['GroupId'] = request.GET['policyId']
            delete_resp = self.delete_aws_securitygroup(payload, region, cid)
            delete_document('policy_instances', request.GET['policyId'])
        else:
            name = policy_document.get('_source').get('jsondoc').get('metadata').get('name')
            namespace = policy_document.get('_source').get('jsondoc').get('metadata').get('namespace')
            cid = policy_document.get('_source').get('metadata').get('cloudId')
            del_response = delete_namespaced_network_policy(name, namespace, cid)
            logger.info(del_response)

        delete_document('policy_instances', request.GET['policyId'])
        response.update({'status' : 'Success'})
 
        return Response(response)


    def put(self, request, format=None):
        response = {}
        reasons = []
        if 'policyId' not in request.GET :
            reasons.append({'securityPolicy' : 'Policy Id Missing in request'})
            response['status'] = 'Failure'
            response['reasons'] = reasons
            return Response(response, status = status.HTTP_400_BAD_REQUEST)

        policyId = request.GET['policyId']

        policy_document = get_document_by_id('policy_instances', request.GET['policyId'])

        if 'found' not in policy_document.keys() or not policy_document.get('found'):
            reasons.append({'securityPolicy' : 'Policy not found'})
            response['status'] = 'Failure'
            response['reasons'] = reasons
            return Response(response, status = status.HTTP_400_BAD_REQUEST)

        request_data = yaml.load(request.body, Loader=yaml.FullLoader)

        cloudType =  policy_document.get('_source').get('metadata').get('cloudType')

        if cloudType == 'AWS':
            response = self.update_aws_securitygroup(request_data, policy_document, policyId)


        elif cloudType == 'KUBERNETES':
            response = self.update_kubernetes_policy(request_data, policy_document, policyId)


        if (response['status'] == 'Failure'):
            return Response(response, status = status.HTTP_500_INTERNAL_SERVER_ERROR)

        else:
            return Response(response)




    '''updates AWS security group and adds egress and ingress rules '''
    def update_kubernetes_policy(self, request_data, policy_document, policyId):
        response = {}
        reasons = []
        policy_data = policy_document['_source']
        name = policy_data.get('jsondoc').get('metadata').get('name')
        namespace = policy_data.get('jsondoc').get('metadata').get('namespace')

        kube_response = replace_network_policy(name, namespace, request_data, policy_data['metadata']['cloudId'])
        if 'status' in kube_response.keys() and kube_response.get('status') == 'Success':
            response['status'] = 'Success'
            reasons.append({'securityPolicy':'Successfully Updated'})

            """----Add to DB when Success-----"""
            '''metadata = policy_data.get('metadata')
            post_request_ver2(index = 'policy_instances', data = json.dumps(request_data), identity=policyId, metadata=metadata)'''

        elif 'status' in kube_response.keys() and kube_response.get('status') == 'Failure':
            response['status'] = "Failure"
            reasons.append({'securityPolicy': kube_response['message']})
        else:
            response['status'] = "Failure"
            sgReason = {}
            sgReason['securityPolicy'] = kube_response['message']
            reasons.append({'securityPolicy' : 'Undefined status or fields in reponse'} )

        response.update({'reasons':reasons})
        return response


    '''updates AWS security group and adds egress and ingress rules '''
    def update_aws_securitygroup(self,request_data, policy_document, policyId):
        response = {}
        reasons = []
        policy_data = policy_document['_source']


        '''Update Ingress Rules '''
        if request_data.get('ingressRules') != None and (len(request_data.get('ingressRules').get('Old_IpPermissions')) != 0 or len(request_data.get('ingressRules').get('New_IpPermissions')) != 0):
            
            ingress_resp = self.add_aws_ingress_rules(request_data['ingressRules'], policyId, policy_data.get('jsondoc').get('region'), policy_data.get('metadata').get('cloudId'))
            response['status'] = ingress_resp['status']
            reasons.append({'ingress' : ingress_resp['reason']})
            '''if response['status'] == 'Success':
                update_object = {}
                update_object['ingressRules'] = request_data.get('ingressRules')
                update_document('policy_instances', policyId, update_object)   '''

        '''Update Egress Rules '''
        if request_data.get('egressRules') != None and (len(request_data.get('egressRules').get('Old_IpPermissions')) != 0 or len(request_data.get('egressRules').get('New_IpPermissions')) != 0):
            egress_resp = self.add_aws_egress_rules(request_data['egressRules'], policyId, policy_data.get('jsondoc').get('region'), policy_data.get('metadata').get('cloudId'))
            response['status'] = egress_resp['status']
            reasons.append({'egress' : egress_resp['reason']})
            '''if response['status'] == 'Success':
                update_object = {}
                update_object['egressRules'] = request_data.get('egressRules')
                update_document('policy_instances', policyId, update_object)'''

        response.update({'reasons' : reasons})
        return response



    '''Create Policy on Kubernetes '''
    def create_kubernetes_policy(self, request, policy_document):
        response = {}
        reasons = []
        request_dict = policy_document['_source']['jsondoc']

        '''Update the incoming parameters in the template '''
        if request_dict['metadata'] != None:
            if request.data.get('namespace') != None:
                request_dict['metadata']['namespace'] = request.data.get('namespace')

            request_dict['metadata']['labels'] = {'template' : policy_document['_id'] }

        if(request.data.get('podSelectorLabels') != None):
            podSelectorLabels = request.data.get('podSelectorLabels')
            podSelector = {}
            matchLabels = {}

            '''for key in podSelectorLabels.keys():
                matchLabels[key] = podSelectorLabels[key]'''

            for pod in podSelectorLabels:
                pod_key = pod.split(":",1)[0]
                pod_value = pod.split(":",1)[1]
                matchLabels[pod_key] = pod_value

            podSelector['matchLabels'] = matchLabels
            
            if request_dict['spec'] != None:
                request_dict['spec']['podSelector'] = podSelector

        kube_response = None
        kube_response = create_network_policy(request.data.get('namespace'), request_dict, request.data.get('cloudId'))

        if 'status' in kube_response and kube_response.get('status') == 'Success':
            response['status'] = 'Success'
            response['policyId'] = kube_response['uid']
            reasons.append({'securityPolicy' : 'Successfully Created'})

            '''Add the Policy Instance to Elastic DB '''
            '''metadata = {}
            metadata['policyId'] = kube_response['uid']
            metadata['cloudId'] = request.data.get('cloudId')   #this will be needed when multiple k8s will be supported
            metadata['cloudType'] = policy_document['_source']['metadata']['cloudType']
            metadata['template'] = policy_document['_id']
            metadata['cloudId'] = request.data.get('cloudId')
            post_request_ver2(index = 'policy_instances', data = json.dumps(request_dict), identity=kube_response['uid'], metadata=metadata) '''

        elif 'status' in kube_response and kube_response.get('status') == 'Failure':
            response['status'] = 'Failure'
            reasons.append({'securityPolicy' : "Failed on kubernetes - " + kube_response['message']})

        else:
            response['status'] = 'Failure'
            reasons.append({'securityPolicy' : 'Undefined status or fields'})
 
        response.update({'reasons' : reasons})

        return response


    '''Creates AWS security group and adds egress and ingress rules '''
    def create_aws_securitygroup(self,request, policy_document):
        response = {}
        reasons = []
        request_data = policy_document['_source']['jsondoc']
        aws_resp = self.add_aws_securitygroup(request_data, request.data, policy_document['_id'])
        aws_resp_dict = json.loads(aws_resp)
        logger.info(aws_resp)

        '''AWS security policy created successfully '''
        if 'GroupId' in aws_resp_dict:
            response['status'] = 'Success'
            response['policyId'] = aws_resp_dict['GroupId']
            reasons.append({'securityPolicy' : 'Successfully Created'})

            '''Update Ingress Rules '''
            if request_data.get('ingressRules') != None and request_data.get('ingressRules').get('New_IpPermissions'):
                ingress_resp = self.add_aws_ingress_rules(request_data['ingressRules'], aws_resp_dict['GroupId'], request.data.get('region'), request.data.get('cloudId'))
                response['status'] = ingress_resp['status']
                reasons.append({'ingress' : ingress_resp['reason']})

            '''Update Egress Rules '''
            if request_data.get('egressRules') != None and request_data.get('egressRules').get('New_IpPermissions'):
                egress_resp = self.add_aws_egress_rules(request_data['egressRules'], aws_resp_dict['GroupId'], request.data.get('region'), request.data.get('cloudId'))
                response['status'] = egress_resp['status']
                reasons.append({'egress' : egress_resp['reason']})

            '''Add the Policy Instance to Elastic DB '''
            '''metadata = {}
            metadata['policyId'] = aws_resp_dict['GroupId']
            metadata['cloudId'] = request.data.get('cloudId')
            metadata['cloudType'] = policy_document['_source']['metadata']['cloudType']
            metadata['template'] = policy_document['_id']
            request_data['region'] = request.data.get('region')
            request_data['vpcId'] = request.data.get('vpcId')
            post_request_ver2(index = 'policy_instances', data = json.dumps(request_data), identity=aws_resp_dict['GroupId'], metadata=metadata)'''

        else:
            reasons.append({'securityPolicy' : aws_resp_dict['exception']})
            response['status'] = 'Failure'

        response.update({'reasons' : reasons})
        return response


    '''Calls the RPC to create the security group on AWS '''
    def add_aws_securitygroup(self, yaml_data, request_input, template_id):
        request = {}
        request['GroupName'] = yaml_data['GroupName']
        request['VpcId']   = request_input['vpcId']
        request['Description'] = yaml_data['Description']

        tags = [{'Key': 'template', 'Value': template_id}]    

        with ClusterRpcProxy(CONFIG) as rpc:
            data = {}
            data['CloudId'] = request_input['cloudId']
            data['region'] = request_input['region']
            data['payload'] = request
            res = rpc.guiHandler.dispatchCreateSecurityGroup(payload=json.dumps(data), tags=tags)
        return res

    '''Adds the ingress Rules to the given security group id '''
    def add_aws_ingress_rules(self, request, groupId, region, cid):
        request.update({'GroupId' : groupId})

        with ClusterRpcProxy(CONFIG) as rpc:
            data = {}
            data['CloudId'] = cid
            data['region'] = region
            data['payload'] = request
            ingress_resp = rpc.guiHandler.dispatchUpdateSgRulesIngress(json.dumps(data))

        ingress_response = {}
        if 'ResponseMetadata' in ingress_resp:
            if ingress_resp['ResponseMetadata']['HTTPStatusCode'] == 200:
                ingress_response['status'] = 'Success'
                ingress_response['reason'] = 'Successfully Created'
            else:
                ingress_response['status'] = 'Failure'
                ingress_response['reason'] = 'Failure reason unknown'
        else:
            ingress_response['status'] = 'Failure'
            ingress_response['reason'] = ingress_resp['exception']
  
        return ingress_response


    '''Adds the ingress Rules to the given security group id '''
    def add_aws_egress_rules(self, request, groupId, region, cid):
        request.update({'GroupId' : groupId})

        with ClusterRpcProxy(CONFIG) as rpc:
            data = {}
            data['CloudId'] = cid
            data['region'] = region
            data['payload'] = request
            egress_resp = rpc.guiHandler.dispatchUpdateSgRulesEgress(json.dumps(data))

        egress_response = {}
        if 'ResponseMetadata' in egress_resp:
            if egress_resp['ResponseMetadata']['HTTPStatusCode'] == 200:
                egress_response['status'] = 'Success'
                egress_response['reason'] = 'Successfully Created'
            else:
                egress_response['status'] = 'Failure'
                egress_response['reason'] = 'Failure reason unknown'
        else:
            egress_response['status'] = 'Failure'
            egress_response['reason'] = egress_resp['exception']

        return egress_response

    '''Deletes an AWS securtiy group  '''
    def delete_aws_securitygroup(self, request, region, cid):
        with ClusterRpcProxy(CONFIG) as rpc:
            data = {}
            data['CloudId'] = cid
            data['region'] = region
            data['payload'] = request
            json_data = json.dumps(data)
            response = rpc.guiHandler.dispatchDeleteSecurityGroup(json_data )

        return response


class Clouds(APIView):


    def get(self, request, format=None):
        '''Gets the List of clouds for given cloud type '''
        if 'cloudType' in request.GET:
            cloudType = request.GET['cloudType']
            response_cloud_list = []
            scf_clouds = CloudConfig.cloud
            for key in scf_clouds.keys():
                cloud = scf_clouds[key]
                if cloud['CloudType'] == cloudType:
                    response_cloud_list.append(cloud)

            return Response(response_cloud_list) 
        elif 'cloudId' in request.GET and 'clusters' in request.GET and request.GET['clusters']=='True':
            cloudId = request.GET['cloudId']
            regions = []
            cloud = CloudConfig.cloud[cloudId]
            if cloud != None:
                regions = cloud['Region'].split(',')
            else:
                return Response({'status' : 'Failure', "reason" :  "Cloud not Found for given ID."}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
                    
            if len(regions) == 0:
                return Response({'status' : 'Failure', "reason" :  "Regions not Found."}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)                 


            final_vpc_list = []
            for region in regions:

                region_vpc = {}
                region_vpc['region'] = region
                vpcs = []
                with ClusterRpcProxy(CONFIG) as rpc:
                    data = {}
                    data['region'] = region 
                    data['CloudId'] = request.GET['cloudId']
                    response = rpc.guiHandler.dispatchVpc(json.dumps(data))
                #logger.info("AWS describe rgions response - " + json.dumps(response))
                for vpc in response['Vpcs']:
                    vpcs.append(vpc['VpcId'])

                region_vpc['clusters'] = vpcs
                final_vpc_list.append(region_vpc)
            

            return Response(final_vpc_list)

        elif 'cloudId' in request.GET and 'labels' in request.GET and request.GET['labels']=='True':
            cloudId = request.GET['cloudId']
            labels = []      
            resp = GphDB.getLabelsByCloudid(cloudId)
            if resp != None:
                labels = resp.keys()
            return Response(labels)

        elif 'cloudId' in request.GET and 'namespaces' in request.GET and request.GET['namespaces']=='True':
            cloudId = request.GET['cloudId']
            namespaces = []
            resp = GphDB.getNamespacesByCloudid(cloudId)
            if resp != None:
                namespaces = resp
            return Response(namespaces)



        else:
            response_cloud_list = []
            scf_clouds = CloudConfig.cloud
            for key in scf_clouds.keys():
                cloud = scf_clouds[key]
                response_cloud_list.append(cloud)
            return Response(response_cloud_list)



        '''gets all the regions for given cloudId
        elif 'cloudId' in request.GET:
            cloudId = request.GET['cloudId']
            with ClusterRpcProxy(CONFIG) as rpc:
                data = {}
                data['CloudId'] = cloudId
                response = rpc.guiHandler.dispatchRegion(json.dumps(data))
            logger.info("AWS describe rgions response - " + json.dumps(response))
            return Response(response)'''

