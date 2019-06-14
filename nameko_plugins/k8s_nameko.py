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
