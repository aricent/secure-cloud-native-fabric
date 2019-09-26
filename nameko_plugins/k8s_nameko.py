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
from nameko.events import EventDispatcher
from nameko.rpc import rpc
import json
import sys
from nameko.standalone.rpc import ClusterRpcProxy
from init_nameko_service import CloudFactory
from common_def import CONFIG, service_logger
import eventlet.tpool

class k8sService:
    """ Service to handle DB operations. """
    name = "k8sService"
    @event_handler("initHandler", "Event_updateCloudInterfaceList")
    def eventUpdateCloudTable(self, payload):
        try:
