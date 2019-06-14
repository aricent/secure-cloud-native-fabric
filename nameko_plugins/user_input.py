from nameko.events import EventDispatcher
from nameko.rpc import rpc
import json
import sys
from nameko.standalone.rpc import ClusterRpcProxy
from init_nameko_service import CloudFactory
from common_def import CONFIG, service_logger
import eventlet.tpool


import os
from kubernetes import client, watch
from kubernetes import config as kub_config
import sys
from kubernetes.client.rest import ApiException
import json



def check_cid_key(payload):
    buf = json.loads(payload)
    if buf['CloudId']:
        if int(buf['CloudId']) >= 0 :
            return int(buf['CloudId'])
        else:
            return -1

    else:
        service_logger.error("%s %s ", sys._getframe().f_code.co_name, "Cloud ID not present ")
        return 0
class GuiHandler:
    name = "guiHandler"
    dispatch = EventDispatcher()

    """def __init__(self):
       service_logger.info("-----INIT GUI-HAdler----")
       kub_config.load_kube_config('/home/ubuntu/admin.conf')
       self.v1 = client.CoreV1Api()
       self.v1_ext = client.ExtensionsV1beta1Api()
       self.apiClient = client.ApiClient() """
    
    @rpc
    def dispatchRegion(self, payload):
        service_logger.info("%s %s %s ", sys._getframe().f_code.co_name, "Payload:-", payload)
        cid = check_cid_key(payload)
        if (cid >= 0):
            service_logger.info("--------AAA Cloud found--------")
            resp = CloudFactory.getInstance(cid).getRegion(payload)
            service_logger.info("--------After Cloud found--------")
            return resp
            #for item in resp:
                #item.update({'CloudId': cid})
            #resp.update({'CloudId': cid})
            #self.dispatch("Event_updateRegionTable", resp)
        else:
            service_logger.error("%s %s ", sys._getframe().f_code.co_name, "Cloud ID not present ")

    def _dispatchSecurityGroup(self, payload):
        service_logger.info("%s %s %s ", sys._getframe().f_code.co_name, "Payload:-", payload)
        import pdb
        #pdb.set_trace()
        cid = check_cid_key(payload)
        if (cid >= 0):
            try:
                resp = CloudFactory.getInstance(cid).getSecurityGroup(payload)
                service_logger.error("%s %s %s ", sys._getframe().f_code.co_name, "resp: ",resp)
                resp.update({'CloudId': cid})
                self.dispatch("Event_updateSecurityGroupTable", ({'CloudId': cid},resp))
            except:
                raise Exception("tmp error:".join(traceback.format_exception(*sys.exc_info())))
        else:
            service_logger.error("%s %s ", sys._getframe().f_code.co_name, "Cloud ID not present ")

    @rpc
    def dispatchSecurityGroup(self, payload):
        service_logger.info("%s %s %s ", sys._getframe().f_code.co_name, "Payload:-", payload)
        #eventlet.tpool.execute(self._dispatchSecurityGroup, payload) 
        self._dispatchSecurityGroup(payload) 

    @rpc
    def dispatchVpc(self, payload):
        service_logger.info("%s %s %s ", sys._getframe().f_code.co_name, "Payload:-", payload)
        cid = check_cid_key(payload)
        if (cid >= 0):
            resp = CloudFactory.getInstance(cid).getVpc(payload)
            #resp.update({'CloudId': cid})
            #self.dispatch("Event_updateVpcTable", resp)
            return resp
        else:
            service_logger.error("%s %s ", sys._getframe().f_code.co_name, "Cloud ID not present ")

    @rpc
    def dispatchCreateSecurityGroup(self, payload, tags):
        service_logger.info("------dispatchCreateSecurityGroup-------------")
        service_logger.info("%s %s %s ", sys._getframe().f_code.co_name, "Payload:-", payload)
        cid = check_cid_key(payload)
        if (cid >= 0):
            service_logger.info("-------before calling AWS Service-------------")
            resp = CloudFactory.getInstance(cid).addSecurityGroup(payload, tags)
            service_logger.info("------After calling AWS Service-------------" + json.dumps(resp))
            return json.dumps(resp)
            """if resp == True:
                service_logger.info("------Response true-------------")
                return True"""
                #with ClusterRpcProxy(CONFIG) as rpc:
                    #rpc.guiHandler.dispatchSecurityGroup(payload)
        else:
            service_logger.error("%s %s ", sys._getframe().f_code.co_name, "Cloud ID not present ")
            return False

    @rpc
    def dispatchDeleteSecurityGroup(self, payload):
        service_logger.info("%s %s %s ", sys._getframe().f_code.co_name, "Payload:-", payload)
        cid = check_cid_key(payload)
        if (cid >= 0):
            resp = CloudFactory.getInstance(cid).deleteSecurityGroup(payload)
            return resp
            """if resp == True:
                with ClusterRpcProxy(CONFIG) as rpc:
                    rpc.guiHandler.dispatchSecurityGroup(payload) """
        else:
            service_logger.error("%s %s ", sys._getframe().f_code.co_name, "Cloud ID not present ")

    @rpc
    def dispatchUpdateSgRulesEgress(self, payload):
        service_logger.info("%s %s %s ", sys._getframe().f_code.co_name, "Payload:-", payload)
        cid = check_cid_key(payload)
        if (cid >= 0):
            resp = CloudFactory.getInstance(cid).updateEgressRule(payload)
            service_logger.info("-------Dispatch complete-----------")
            return resp
            """if resp == True:
                with ClusterRpcProxy(CONFIG) as rpc:
                    rpc.guiHandler.dispatchDeleteSecurityGroup(payload)
                with ClusterRpcProxy(CONFIG) as rpc:
                    rpc.guiHandler.dispatchSecurityGroup(payload)"""
        else:
            service_logger.error("%s %s ", sys._getframe().f_code.co_name, "Cloud ID not present ")

    @rpc
    def dispatchUpdateSgRulesIngress(self, payload):
        service_logger.info("%s %s %s ", sys._getframe().f_code.co_name, "Payload:-", payload)
        cid = check_cid_key(payload)
        service_logger.info("After CID check------------------")
        if (cid >= 0):
            service_logger.info("CID found")
            resp = CloudFactory.getInstance(cid).updateIngressRule(payload)
            service_logger.info("-------Dispatch complete-----------")
            return resp
            """if resp == True:
                with ClusterRpcProxy(CONFIG) as rpc:
                    rpc.guiHandler.dispatchDeleteSecurityGroup(payload)
                with ClusterRpcProxy(CONFIG) as rpc:
                    rpc.guiHandler.dispatchSecurityGroup(payload)"""
        else:
            service_logger.error("%s %s ", sys._getframe().f_code.co_name, "Cloud ID not present ")





        
    """---KUBERNETES CODE---"""

    """@rpc
    def dispatchCreateKubernetesPolicy(self, req_namespace, req_body):
        service_logger.info("%s %s %s ", sys._getframe().f_code.co_name, "Payload:-", req_body)
        kub_config.load_kube_config('/home/ubuntu/admin.conf')
        v1 = client.CoreV1Api()
        v1_ext = client.ExtensionsV1beta1Api()
        apiClient = client.ApiClient()


        create_response = {}
        if req_namespace == None:
            req_namespace = req_body.get('metadata').get('namespace')

        try:
            api_response = v1_ext.create_namespaced_network_policy(namespace=req_namespace, body = req_body, pretty='true')
            service_logger.info("---------RESPONSE create_network_policy  -----------------")
            service_logger.info(api_response)
            final_response = {}
            final_response['status'] = 'Success'
            final_response['uid'] = api_response.metadata.uid
            create_response = final_response
            #pprint(api_response)
        except ApiException as e:
            service_logger.info("Exception when calling ExtensionsV1beta1Api->create_namespaced_network_policy: %s\n" % e)
            create_response =  e.body

  
        create_response = {"status" : "Success", "uid" : "sdkjfh987wfyoudlhf"}
        service_logger.info(json.dumps(create_response))
        return create_response """
