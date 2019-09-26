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
#from util.common_def import service_logger as logger

from collections import defaultdict
from neomodel import (StructuredNode, JSONProperty, StringProperty, IntegerProperty, 
                      UniqueIdProperty, RelationshipTo, RelationshipFrom, ArrayProperty)
from neomodel.match import NodeSet, EITHER, OUTGOING, INCOMING, Traversal
from neomodel import config

config.DATABASE_URL='bolt://neo4j:neo4j@SCF_IP:7687'
DATABASE_REST_CONN ='http://neo4j:neo4j@SCF_IP:7474/db/data'

from neo4jrestclient.client import GraphDatabase
import sys
import json
gdb= None

def tree(): return defaultdict(tree)

class CrispNode(StructuredNode):
    pass

class Organization(StructuredNode):
    name = StringProperty(unique_index=True, required=True)
    viewType = StringProperty(default="crisp")
    cisoEmail = StringProperty(default="Jon.Doe@aricent.com")
    secOpsGroup = StringProperty(default="secops@aricent.com")
    implementsSecPolPosture = RelationshipTo('SecurityPosture', 'IMPLEMENTS')
    hasCloud = RelationshipFrom('Cloud', 'HAS')

class Cloud(StructuredNode):
    name = StringProperty(unique_index=True, required=True)
    cloudId = StringProperty(unique_index=True, required=True)
    config = StringProperty()
    cloudType = StringProperty(default="Kubernetes")
    hasCluster = RelationshipFrom('Cluster', 'HAS')
    usedLabels = StringProperty()
    viewType = StringProperty(default="crisp")

class UserAccount(StructuredNode):
    name = StringProperty(unique_index=True, required=True)
    roles = JSONProperty()
    rights = JSONProperty()
    accessToCluster = RelationshipTo('Cluster', 'CAN_ACCESS')
    ownsNamespace =  RelationshipTo('Namespace', 'OWNS')
    ownNode = RelationshipTo('Nodes', 'OWNS')

class ComplianceReq(StructuredNode):
    name = StringProperty(unique_index=True, required=True)
    viewType = StringProperty(default="crisp")
    description = StringProperty()
    documentLink = StringProperty()
    appliesToAssetGroup = RelationshipTo('AssetGroup', 'APPLIED_TO')

class AssetGroup(StructuredNode):
    name = StringProperty(unique_index=True, required=True)
    viewType = StringProperty(default="crisp")
    description = StringProperty()
    documentLink = StringProperty()
    instanceCluster = RelationshipTo('Cluster', 'INSTANCE')
    instanceNode = RelationshipTo('Nodes', 'INSTANCE')

class SecurityControl(StructuredNode):
    name = StringProperty(unique_index=True, required=True)
    viewType = StringProperty(default="crisp")
    description = StringProperty()
    documentLink = StringProperty()
    implPolicy = RelationshipTo('Policy', 'IMPLEMENTS')
    secures = RelationshipTo('AssetGroup', 'SECURES')
    

class Auditor(StructuredNode):
    name = StringProperty(unique_index=True, required=True)
    viewType = StringProperty(default="crisp")
    description = StringProperty()
    documentLink = StringProperty()
    monitors = RelationshipTo('SecurityControl', 'MONITORS')

class AuditorInstance(StructuredNode):
    name = StringProperty(unique_index=True, required=True)
    viewType = StringProperty(default="crisp")
    description = StringProperty()
    documentLink = StringProperty()
    state = StringProperty()
    targetCluster = RelationshipTo('Cluster', 'AUDITS')
    targetNode = RelationshipTo('Nodes', 'AUDITS')
    instanceOf = RelationshipTo('Auditor', 'INSTANCE_OF')
    hasAlarms = RelationshipTo('Alarm', 'FINDING')

class SecurityPosture(StructuredNode):
    name = StringProperty(unique_index=True, required=True)
    viewType = StringProperty(default="crisp")
    documentLink = StringProperty()
    version = StringProperty()
    usesPolicy = RelationshipTo('Policy', 'USES')
    requires = RelationshipTo('ComplianceReq', 'REQUIRES')

class Alarm(StructuredNode):
    alarmClass = StringProperty()
    alarmText = StringProperty(unique_index=True, required=True)
    alarmState = StringProperty()
    viewType = StringProperty(default="crisp")
    cloudType = StringProperty(default="Kubernetes")
    raisedOnComponent = RelationshipTo('Component', 'RAISED_ON')
    raisedOnWorkLoad = RelationshipTo('WorkLoad', 'RAISED_ON')
    raisedOnCluster = RelationshipTo('Cluster', 'RAISED_ON')
    raisedOnPolicy = RelationshipTo('Policy', 'RAISED_ON')
    raisedOnNodes = RelationshipTo('Nodes', 'RAISED_ON')

class Policy(StructuredNode):
    name = StringProperty(unique_index=True, required=True)
    version = StringProperty()
    viewType = StringProperty(default="crisp")
    metaData = JSONProperty()
    spec = JSONProperty()
    policyRules = JSONProperty()
    labels = StringProperty()
    cloudType = StringProperty(default="Kubernetes")
    appliesToNS = RelationshipTo('Namespace', 'APPLIES_TO')
    appliesToCluster = RelationshipTo('Cluster', 'APPLIES_TO')
    appliesToWorkLoad = RelationshipTo('WorkLoad', 'APPLIES_TO')
    instanceOf = RelationshipTo(CrispNode, "MAPS_TO_SECURITYCONFIGURATIONS")

class Nodes(StructuredNode):
    name = StringProperty(unique_index=True, required=True)
    viewType = StringProperty(default="crisp")
    cloudType = StringProperty(default="Kubernetes")
    cluster = RelationshipFrom('Cluster', 'PART_OF')
    workload = RelationshipFrom('WorkLoad', 'RUNNING')


class Cluster(StructuredNode):
    name = StringProperty(unique_index=True, required=True)
    organization = StringProperty()
    viewType = StringProperty(default="crisp")
    zone = StringProperty()
    cloudId = StringProperty()
    cloudType = StringProperty(default="Kubernetes")
    namespaces = RelationshipFrom('Namespace', 'PART_OF')
    clusternodes = RelationshipFrom('Nodes', 'PART_OF')


class Namespace(StructuredNode):
    name = StringProperty(unique_index=True, required=True)
    version = StringProperty()
    metaData = JSONProperty()
    spec = JSONProperty()
    labels = StringProperty()
    cloudType = StringProperty(default="Kubernetes")
    workload = RelationshipFrom('WorkLoad', 'PART_OF')


class WorkLoad(StructuredNode):
    name = StringProperty(unique_index=True, required=True)
    workLoadType = StringProperty()
    version = StringProperty()
    metaData = JSONProperty()
    spec = JSONProperty()
    alarms = ArrayProperty()
    labels = StringProperty()
    cloudType = StringProperty(default="Kubernetes")    
    component = RelationshipFrom('Component', 'PART_OF')


class Component(StructuredNode):
    name = StringProperty(unique_index=True, required=True)
    componentType = StringProperty()
    version = StringProperty()
    metaData = JSONProperty()
    spec = JSONProperty()
    alarms = ArrayProperty() 
    cloudType = StringProperty(default="Kubernetes")

class GphDB(object):

    def __getGphObj(SomeNodeName, typeof):    
        cls = None
        if typeof is Cluster:
            cls = Cluster.nodes.filter(name=SomeNodeName)
        elif typeof is Nodes:
            cls = Nodes.nodes.filter(name=SomeNodeName)
        elif typeof is Cloud:
            cls = Cloud.nodes.filter(name=SomeNodeName)
        elif typeof is Policy:
            cls = Policy.nodes.filter(name=SomeNodeName)
        elif typeof is Namespace:
            cls = Namespace.nodes.filter(name=SomeNodeName)
        elif typeof is WorkLoad:
            cls = WorkLoad.nodes.filter(name=SomeNodeName)
        elif typeof is Component:
            cls = Component.nodes.filter(name=SomeNodeName)
        elif typeof is Alarm:
            cls = Alarm.nodes.filter(alarmText=SomeNodeName)
        elif typeof is Organization:
            cls = Organization.nodes.filter(name=SomeNodeName)
        elif typeof is SecurityPosture:
            cls = SecurityPosture.nodes.filter(name=SomeNodeName)
        elif typeof is SecurityControl:
            cls = SecurityControl.nodes.filter(name=SomeNodeName)
        elif typeof is AssetGroup:
            cls = AssetGroup.nodes.filter(name=SomeNodeName)
        elif typeof is Auditor:
            cls = Auditor.nodes.filter(name=SomeNodeName)
        elif typeof is AuditorInstance:
            cls = AuditorInstance.nodes.filter(name=SomeNodeName)
        else:
            ValueError("Unknown Object type")
        return cls

    def getGphObject(SomeNodeName, typeof):
        cls = GphDB.__getGphObj(SomeNodeName, typeof)
        if type(cls) is NodeSet:
            cls = cls.first_or_none()
        return cls

    def getAllGphObjects(typeof):
        obs = typeof.nodes.all()
        print("type : %s" %(type(obs)))
        if obs and type(obs) is list:
            return obs
        else:
            return None

    def addGphObject(SomeNode):
        if isinstance(SomeNode, StructuredNode):
            existingNodes = SomeNode.nodes.filter(name=SomeNode.name)
            if ((type(existingNodes) is NodeSet)) and (existingNodes.first_or_none()):
                #print("GphDB: Object already exists : %s" %(SomeNode.name))
                return existingNodes.first_or_none()
            elif existingNodes:
                #print("GphDB: Object already exists : %s" %(SomeNode.name))
                return existingNodes
            else:
                #print("GphDB: Added node : %s" %(SomeNode.name))
                try:
                    SomeNode.save()
                except Exception as e:
                    print("!!! Exception !!! : %s" %(e))
                    print("GphDB: Add failed : %s" %(SomeNode.name))
                return SomeNode
        else:
            ValueError("Object-type is not supported")

    def delGphObject(SomeNode):
        if isinstance(SomeNode, StructuredNode):
            SomeNode.delete()
        else:
            ValueError("Object-type is not supported")

    def addClusterToOrg(orgName, Node):
        cls = Organization.nodes.filter(name=orgName)
        if type(cls) is NodeSet:
           cls = cls.first_or_none()
        if cls:
           cls.hasNetworkCluster.connect(Node)
        else:
            ValueError("Unknown Organization")

    def addSecPosToOrg(orgName, Node):
        cls = Organization.nodes.filter(name=orgName)
        if type(cls) is NodeSet:
           cls = cls.first_or_none()
        if cls:
           cls.implementsSecPolPosture.connect(Node)
        else:
            ValueError("Unknown Organization")

    def addPolicyToSecPos(polName, secPosObj):
        polObj = Policy.nodes.filter(name=polName)
        if type(polObj) is NodeSet:
           polObj = polObj.first_or_none()
        if polObj:
           secPosObj.usesPolicy.connect(polObj)
        else:
            ValueError("Unknown Policy")

    def addNodeToCluster(ClusterName, Node):
        cls = Cluster.nodes.filter(name=ClusterName)
        if type(cls) is NodeSet:
           cls = cls.first_or_none()
        if cls:
           cls.clusternodes.connect(Node)
        else:
            ValueError("Unknown Cluster")


    def removeNodeFromCluster(ClusterName, NodeName, deleteNode=False):
        cls = Cluster.nodes.filter(name=ClusterName)
        nodeObject = Nodes.nodes.filter(name=NodeName)
        if type(cls) is NodeSet:
            cls = cls.first_or_none()
        if type(nodeObject) is NodeSet:
            nodeObject = nodeObject.first_or_none()
        if cls and nodeObject:
            if cls.clusternodes.is_connected(nodeObject):
                cls.clusternodes.disconnect(nodeObject)
            if deleteNode:
                nodeObject.delete()
        else:
            ValueError("Unknown Node or Cluster names")

    def addNamespaceToCluster(ClusterName, Namespace):
        cls = Cluster.nodes.filter(name=ClusterName)
        if type(cls) is NodeSet:
            cls = cls.first_or_none()
        if cls:
            cls.namespaces.connect(Namespace)
        else:
            ValueError("Unknown Cluster")


    def removeNamespaceFromCluster(ClusterName, NamesapceName, deleteNamespace=False):
        cls = Cluster.nodes.filter(name=ClusterName) 
        nodeObject = Namespace.nodes.filter(name=NamesapceName)
        if type(cls) is NodeSet:
            cls = cls.first_or_none()
        if type(nodeObject) is NodeSet:
            nodeObject = nodeObject.first_or_none()
        if cls and nodeObject:
            if cls.namespaces.is_connected(nodeObject):
                cls.namespaces.disconnect(nodeObject)
            if deleteNamespace:
                nodeObject.delete()
        else:
            ValueError("Namespace or Cluter of this name not known")

    def addWorkLoadToNamespace(NamespaceName, WorkLoad):
        cls = Namespace.nodes.filter(name=NamespaceName)
        if type(cls) is NodeSet:
            cls = cls.first_or_none()
        if cls:
            cls.workload.connect(WorkLoad)
        else:
            ValueError("Unknown NamespaceName")

    def removeWorkLoadFromNamespace(NamespaceName, WorkLoadName, deleteWorkload=False):
        cls = Namespace.nodes.filter(name=NamespaceName)
        nodeObject = WorkLoad.nodes.filter(name=WorkLoadName)
        if type(cls) is NodeSet:
            cls = cls.first_or_none()
        if type(nodeObject) is NodeSet:
            nodeObject = nodeObject.first_or_none()
        if cls and nodeObject:
            if cls.workload.is_connected(nodeObject):
                cls.workload.disconnect(nodeObject)
            if deleteWorkload:
                nodeObject.delete()
        else:
            ValueError("Namespace or WorkLoad of this name not known")


    def addComponentToWorkLoad(WorkLoadName, Component):
        cls = WorkLoad.nodes.filter(name=WorkLoadName)
        if type(cls) is NodeSet:
            cls = cls.first_or_none()
        if cls:
            cls.component.connect(Component)
        else:
            ValueError("Unknown WorkLoadName")
        

    def removeComponentFromWorkload(WorkLoadName, ComponentName, deleteComponent=False):
        cls = WorkLoad.nodes.filter(name=WorkLoadName)
        nodeObject = Component.nodes.filter(name=ComponentName)
        if type(cls) is NodeSet:
            cls = cls.first_or_none()
        if type(nodeObject) is NodeSet:
            nodeObject = nodeObject.first_or_none()
        if cls and nodeObject:
            if cls.component.is_connected(nodeObject):
                cls.component.disconnect(nodeObject)
            if deleteComponent:
                nodeObject.delete()
        else:
            ValueError("WorkLoad or Component unknown")

    def addPolicyToNamespace(NamespaceName, Policy):
        cls = Namespace.nodes.filter(name=NamespaceName)
        if type(cls) is NodeSet:
            cls = cls.first_or_none()
        if cls:
            Policy.appliesToNS.connect(cls)
        else:
            ValueError("Unknown Namespace")

    def removePolicyFromNamespace(NamespaceName, PolicyName, deletePolicy=False):
        cls = Namespace.nodes.filter(name=NamespaceName)
        nodeObject = Policy.nodes.filter(name=PolicyName)
        if type(cls) is NodeSet:
            cls = cls.first_or_none()
        if type(nodeObject) is NodeSet:
            nodeObject = nodeObject.first_or_none()
        if cls and nodeObject:
            if nodeObject.appliesToNS.is_connected(cls):
                nodeObject.appliesToNS.disconnect(cls)
            if deletePolicy:
                nodeObject.delete()
        else:
            ValueError("Policy or Namespace unknown")

    def addPolicyToWorkload(WorkLoadName, Policy):
        cls = WorkLoad.nodes.filter(name=WorkLoadName)
        if type(cls) is NodeSet:
            cls = cls.first_or_none()
        if cls:
            Policy.appliesToWorkLoad.connect(cls)
        else:
            ValueError("Unknown WorkLoad")

    def removePolicyFromWorkload(WorkLoadName, PolicyName, deletePolicy=False):
        cls = WorkLoad.nodes.filter(name=WorkLoadName)
        nodeObject = Policy.nodes.filter(name=PolicyName)
        if type(cls) is NodeSet:
            cls = cls.first_or_none()
        if type(nodeObject) is NodeSet:
            nodeObject = nodeObject.first_or_none()
        if cls and nodeObject:
            if nodeObject.appliesToWorkLoad.is_connected(cls):
                nodeObject.appliesToWorkLoad.disconnect(cls)
            if deletePolicy:
                nodeObject.delete()
        else:
            ValueError("WorkLoad or Policy unknown")

    def addAuditorInstanceToCluster(ClusterName, auditorInstanceName):
        cls = Cluster.nodes.filter(name=ClusterName)
        audInstns = AuditorInstance.nodes.filter(name=auditorInstanceName)
        if type(cls) is NodeSet:
            cls = cls.first_or_none()
        if type(audInstns) is NodeSet:
            audInstns = audInstns.first_or_none()
        if cls and audInstns:
            audInstns.targetCluster.connect(cls)
        
    def removeAuditorInstanceFromCluster(ClusterName, auditorInstanceName, deleteAudIns=False):
        cls = Cluster.nodes.filter(name=ClusterName)
        audInstns = AuditorInstance.nodes.filter(name=auditorInstanceName)
        if type(cls) is NodeSet:
            cls = cls.first_or_none()
        if type(audInstns) is NodeSet:
            audInstns = audInstns.first_or_none()
        if cls and audInstns and audInstns.targetCluster.is_connected(cls):
            audInstns.targetCluster.disconnect(cls)
            if deleteAudIns:
                audInstns.delete()

    def addAudInstRelationsBulk(jsonReq):
        if isinstance(jsonReq, str):
            jsonReq = json.loads(jsonReq)
        if jsonReq["relations"] and len(jsonReq["relations"]) > 0:
            for relation in jsonReq["relations"]:
                GphDB.addAuditorInstanceToCluster(relation["cluster"], relation["auditorName"])

    def listRelatedObjsFor(objName, objType):
        listRelatedNodes = list()
        obj = objType.nodes.filter(name=objName)
        if type(obj) is NodeSet:
            obj = obj.first_or_none()
        if obj:
           travDefn = dict(direction=EITHER,
                           relation_type=None,
                           model=None)
           trav = Traversal(obj, objType.__label__, travDefn)
           listRelatedNodes.append(trav.all())
        return listRelatedNodes


    def listObjectsForPolicy(policyName):
        listRelatedNodes = list()
        policyObj = Policy.nodes.filter(name=policyName)
        if type(policyObj) is NodeSet:
            policyObj = policyObj.first_or_none()
        if policyObj:
           travDefn = dict(direction=EITHER, 
                           relation_type=None,
                           model=None)
           trav = Traversal(policyObj, Policy.__label__, travDefn)
           listRelatedNodes.append(trav.all())  
        return listRelatedNodes
    
    def updateAlarmForObject(someObjName, alarmClass, alarmText, alarmState):
        almObj = GphDB.getGphObject(alarmText, typeof=Alarm)
        if not almObj:
            almObj = Alarm(alarmClass=alarmClass, alarmText=alarmText, alarmState=alarmState).save() 
        onObj = GphDB.getGphObject(someObjName, typeof=Component)
        if almObj and onObj:
            almObj.raisedOnComponent.connect(onObj)
        onObj = GphDB.getGphObject(someObjName, typeof=WorkLoad)
        if almObj and onObj:
            almObj.raisedOnWorkLoad.connect(onObj)
        onObj = GphDB.getGphObject(someObjName, typeof=Cluster)
        if almObj and onObj:
            almObj.raisedOnCluster.connect(onObj)
        onObj = GphDB.getGphObject(someObjName, typeof=Policy)
        if almObj and onObj:
            almObj.raisedOnPolicy.connect(onObj)
        onObj = GphDB.getGphObject(someObjName, typeof=Nodes)
        if almObj and onObj:
            almObj.raisedOnNodes.connect(onObj)


    def removeAlarmFromObject(someObjName, alarmText):
        almObj = GphDB.getGphObject(alarmText, typeof=Alarm)
        onObj = GphDB.getGphObject(someObjName, typeof=Component)
        if almObj and onObj:
            if almObj.raisedOnComponent.is_connected(onObj):
                almObj.raisedOnComponent.disconnect(onObj)
        onObj = GphDB.getGphObject(someObjName, typeof=WorkLoad)
        if almObj and onObj:
            if almObj.raisedOnWorkLoad.is_connected(onObj):
                almObj.raisedOnWorkLoad.disconnect(onObj)
        onObj = GphDB.getGphObject(someObjName, typeof=Cluster)
        if almObj and onObj:
            if almObj.raisedOnCluster.is_connected(onObj):
                almObj.raisedOnCluster.disconnect(onObj)            
        onObj = GphDB.getGphObject(someObjName, typeof=Policy)
        if almObj and onObj:
            if almObj.raisedOnPolicy.is_connected(onObj):
                almObj.raisedOnPolicy.disconnect(onObj)
        onObj = GphDB.getGphObject(someObjName, typeof=Nodes)
        if almObj and onObj:
            if almObj.raisedOnNodes.is_connected(onObj):
                almObj.raisedOnNodes.disconnect(onObj)


    def getClusterByCloudid(cloudid):
        clusters = Cluster.nodes.filter(cloudId=cloudid)
        if clusters:
            if type(clusters) is NodeSet:
                clusArr = []
                for clus in clusters:
                    clusArr.append(clus.name)
                return clusArr
            else:
                return [clusters.name]
        return None
        
    def getLabelsByCloudid(cloudid):
        'TODO'
        cloud = Cloud.nodes.filter(cloudId=cloudid)
        if type(cloud) is NodeSet:
            cloud = cloud.first_or_none() 
        if cloud and cloud.usedLabels:
            return json.loads(cloud.usedLabels)
        else:
            return None
 

    def getNamespacesByCloudid(cloudid):
        clusters = Cluster.nodes.filter(cloudId=cloudid)
        namespaces = []
        if clusters != None:
            for cluster in clusters:
                if cluster.namespaces != None:
                    for namespace in cluster.namespaces:
                        namespaces.append(namespace.name)

        return namespaces


    def getJSONgraph(cypherQuery='MATCH (n) RETURN (n)'):
        global gdb
        if not gdb:
            gdb = GraphDatabase(DATABASE_REST_CONN)
        results = gdb.query(cypherQuery, data_contents=True)
        return results.graph

    def getAlarmJSONgraph(cypherQuery='MATCH (L:Alarm)-[R:RAISED_ON]->(O) RETURN L, O, R'):
        global gdb
        if not gdb:
            gdb = GraphDatabase(DATABASE_REST_CONN)
        results = gdb.query(cypherQuery, data_contents=True)
        jsonDp = results.graph
        nodeArray = dict()
        relArray = dict()
        if jsonDp is None:
            return {}
        for item in jsonDp:
            for rel in item["relationships"]:
                objNodes = item["nodes"]
                raisedOnNode = None
                alarmNode = None
                for nd in objNodes:
                    fromNodeArray = nodeArray.get(nd["id"], None)
                    useThisNode = None
                    if fromNodeArray:
                       useThisNode = fromNodeArray
                    else:
                       nodeArray[nd["id"]] = nd
                       useThisNode = nd
                       #logger.info("--> New Node: %s", useThisNode["id"])
                    if rel["type"] == "RAISED_ON":
                        if useThisNode["id"] == rel["endNode"]:
                            raisedOnNode = useThisNode
                        elif useThisNode["id"] == rel["startNode"]:
                           alarmNode = useThisNode
                        if raisedOnNode and alarmNode:
                            if not "alarms" in raisedOnNode["properties"].keys():
                                raisedOnNode["properties"]["alarms"] = list()
                            alarminfo = {
                                         "alarmText":alarmNode["properties"]["alarmText"],
                                         "alarmClass":alarmNode["properties"]["alarmClass"],
                                         "alarmState":alarmNode["properties"]["alarmState"]
                                        }
                            raisedOnNode["properties"]["alarms"].append(alarminfo)
                relArray[rel["id"]] = rel
                #logger.info("--> New Relationship: %s", rel["id"])
        d3json = [{"nodes":list(nodeArray.values())}, {"relationships":list(relArray.values())}]
        #logger.info("::getAlarmJSONgraph:: %s", d3json) 
        return d3json



def main():
    print("=== START ===")
    #docLink = "something"
    #audNode = {"properties":{"name":"theNAme"}}
    #audGphNode = Auditor(name=audNode["properties"]["name"],
    #                     documentLink=docLink) 
    print(GphDB.getAllGphObjects(Policy))   
    print("=== END ===")
if __name__ == '__main__':
    main()

