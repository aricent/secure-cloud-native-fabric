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
from subprocess import call, Popen

from nameko.containers import ServiceContainer
from nameko.events import EventDispatcher
from nameko.rpc import rpc
from nameko.standalone.rpc import ClusterRpcProxy

from common_def import *
from db_service import dbService
from cluster_reg_service import ClusterRegistryService

from aws_service import AwsCloud
from cloud_framework import CloudFactory
from common_def import RUNNING_PUBLIC_CLOUD_LIST, RUNNING_PRIVATE_CLOUD_LIST, service_logger, cloud_config
from kubernetes_service import KubernetesCloud



cloud_constructor_mapper = {'AWS': AwsCloud,'KUBERNETES':KubernetesCloud}
SUPPORTED_PUBLIC_CLOUD=('AWS','GCP')
SUPPORTED_PIVATE_CLOUD=('KUBERNETES')

class InitHandler:
    name = "initHandler"
    dispatch = EventDispatcher()
    @rpc
    def dispatchUpdateCloudTable(self, payload):
        service_logger.info("%s %s %s ", sys._getframe().f_code.co_name, "Payload:-", payload)
        self.dispatch("Event_updateCloudInterfaceList", payload)

def get_clouds():
    db_data=[]
    for item in (RUNNING_PUBLIC_CLOUD_LIST) :
        if item['type'] in SUPPORTED_PUBLIC_CLOUD:
            obj=cloud_constructor_mapper[item['type']](item)
            item.update({'index': obj.index})
            db_data.append(item)


    for item in (RUNNING_PRIVATE_CLOUD_LIST) :
        if item['type'] in SUPPORTED_PIVATE_CLOUD:
            obj = (cloud_constructor_mapper[item['type']])(item['name'])
            item.update({'index': obj.index})
            db_data.append(item)
    return db_data

#def update_cloud_table(db_data):


def init_cloud_framework():
    service_logger.info("%s %s %s ", sys._getframe().f_code.co_name, "RUNNING_PUBLIC_CLOUD_LIST:-", RUNNING_PUBLIC_CLOUD_LIST)
    service_logger.info("%s %s %s ", sys._getframe().f_code.co_name, "RUNNING_PRIVATE_CLOUD_LIST:-", RUNNING_PRIVATE_CLOUD_LIST)
    db_data = get_clouds()
    with ClusterRpcProxy(CONFIG) as rpc:
        rpc.initHandler.dispatchUpdateCloudTable(payload=db_data)
    with ClusterRpcProxy(CONFIG) as rpc:
        rpc.ClusterRegistryService.registerCloudInstance(configDict=cloud_config)
    #with ClusterRpcProxy(CONFIG) as rpc:
    #    rpc.AuditorService.loadAuditorTypeRegistry(auditor_dict=cloud_config)

from nameko.containers import ServiceContainer
from nameko.runners import ServiceRunner
from nameko.testing.utils import get_container

runner = ServiceRunner(config=CONFIG)
runner.add_service(InitHandler)
runner.add_service(ClusterRegistryService)
runner.start()

service_logger.info("%s %s %s ", sys._getframe().f_code.co_name, "DB_PATH:-", DB_PATH)
init_cloud_framework()

