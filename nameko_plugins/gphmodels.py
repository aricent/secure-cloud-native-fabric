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
from collections import defaultdict
from neomodel import (StructuredNode, StringProperty, IntegerProperty, UniqueIdProperty, RelationshipTo, RelationshipFrom)
from neomodel import config

config.DATABASE_URL='bolt://neo4j:scfadmin@10.206.57.12:7687'

def tree(): return defaultdict(tree)


class Policy(StructuredNode):
    name = StringProperty(unique_index=True, required=True)
    version = StringProperty()
    metaData = StringProperty()
    spec = StringProperty()
    policyRules = StringProperty()
    appliesToNS = RelationshipFrom('Namespace', 'APPLIES_TO')
    appliesToCluster = RelationshipFrom('Cluster', 'APPLIES_TO')
    appliesToWorkLoad = RelationshipFrom('WorkLoad', 'APPLIES_TO')


class Nodes(StructuredNode):
    name = StringProperty(unique_index=True, required=True)
    cluster = RelationshipFrom('Cluster', 'PART_OF')
    workload = RelationshipFrom('WorkLoad', 'RUNNING')


class Cluster(StructuredNode):
    name = StringProperty(unique_index=True, required=True)
    organization = StringProperty()
    zone = StringProperty()
    namespaces = RelationshipFrom('Namespace', 'PART_OF')
    clusternodes = RelationshipFrom('Nodes', 'PART_OF')


class Namespace(StructuredNode):
    name = StringProperty(unique_index=True, required=True)
    version = StringProperty()
    metaData = StringProperty()
    spec = StringProperty()
    workload = RelationshipFrom('WorkLoad', 'PART_OF')


class WorkLoad(StructuredNode):
    name = StringProperty(unique_index=True, required=True)
    workLoadType = StringProperty()
    version = StringProperty()
    metaData = StringProperty()
    spec = StringProperty()    
    component = RelationshipFrom('Component', 'PART_OF')


class Component(StructuredNode):
    name = StringProperty(unique_index=True, required=True)
    componentType = StringProperty()
    version = StringProperty()
    metaData = StringProperty()
    spec = StringProperty() 


class GraphModel():
    def __init__(self):
        self.__myTree = tree()
        self.__myClusters = []

    def getTreeGraph(self):
        __myClusters = [Cluster.nodes]
        for node in __myClusters:
            __myTree = __myClusters[node]
        return json.dumps(self.__myTree)


class GphDB(object):
    
    def addGphObject(SomeNode):
        if StructuredNode in SomeNode.__bases__:
            SomeNode.save()
            return SomeNode.refresh()
        else:
            ValueError("Object-type is not supported")

    def delGphObject(SomeNode):
        if StructuredNode in SomeNode.__bases__:
            SomeNode.delete()
        else:
            ValueError("Object-type is not supported")

    def addNodeToCluster(ClusterName, Node):
        cls = Cluster.nodes.filter(name=ClusterName)[0]
        Node.save()
        cls.clusternodes.connect(Node)


    def removeNodeFromCluster(ClusterName, NodeName, deleteNode=False):
        cls = Cluster.nodes.filter(name=ClusterName)[0]
        nodeObject = Nodes.nodes.filter(name=NodeName)[0]
        if cls.clusternodes.is_connected(nodeObject):
            cls.clusternodes.disconnect(nodeObject)
        if deleteNode:
            nodeObject.delete() 

    def addNamespaceToCluster(ClusterName, Namespace):
        cls = Cluster.nodes.filter(name=ClusterName)[0]
        Namespace.save()
        cls.namespaces.connect(Namespace)


    def removeNamespaceFromCluster(ClusterName, NamesapceName, deleteNamespace=False):
        cls = Cluster.nodes.filter(name=ClusterName)[0] 
        nodeObject = Namespace.nodes.filter(name=NamesapceName)[0]
        if cls.namespaces.is_connected(nodeObject):
            cls.namespaces.disconnect(nodeObject)
        if deleteNamespace:
            nodeObject.delete()

    def addWorkLoadToNamespace(NamespaceName, WorkLoad):
        cls = Namespace.nodes.filter(name=NamespaceName)
        if type(cls) is list:
            cls = cls[0]
        if cls:
            WorkLoad.save()
            cls.workload.connect(WorkLoad)
        else:
            ValueError("Unknown NamespaceName")

    def removeWorkLoadFromNamespace(NamespaceName, WorkLoadName, deleteWorkload=False):
        cls = Namespace.nodes.filter(name=NamespaceName)
        nodeObject = WorkLoad.nodes.filter(name=WorkLoadName)
        if type(cls) is list:
            cls = cls[0]
        if type(nodeObject) is list:
            nodeObject = nodeObject[0]
        if cls and nodeObject:
            if cls.workload.is_connected(nodeObject):
                cls.workload.disconnect(nodeObject)
            if deleteWorkload:
                nodeObject.delete()
        else:
            ValueError("Namespace or WorkLoad of this name not known")


    def addComponentToWorkLoad(WorkLoadName, Component):
        cls = WorkLoad.nodes.filter(name=WorkLoadName)
        print(type(cls))
        if type(cls) is list:
            cls = cls[0]
        if cls:
            print(type(cls))
            Component.save()
            cls.component.connect(Component)
        else:
            ValueError("Unknown WorkLoadName")
        

    def removeComponentFromWorkload(WorkLoadName, ComponentName, deleteComponent=False):
        cls = WorkLoad.nodes.filter(name=WorkLoadName)
        nodeObject = Component.nodes.filter(name=ComponentName)
        if type(cls) is list:
            cls = cls[0]
        if type(nodeObject) is list:
            nodeObject = nodeObject[0]
        if cls and nodeObject:
            if cls.component.is_connected(nodeObject):
                cls.component.disconnect(nodeObject)
            if deleteComponent:
                nodeObject.delete()
        else:
            ValueError("WorkLoad or Component unknown")

    def addPolicyToNamespace(NamespaceName, Policy):
        cls = Namespace.nodes.filter(name=NamespaceName)
        if type(cls) is list:
            cls = cls[0]
        if cls:
            Policy.save()
            Policy.appliesToNS.connect(cls)
        else:
            ValueError("Unknown Namespace")

    def removePolicyFromNamespace(NamespaceName, PolicyName, deletePolicy=False):
        cls = Namespace.nodes.filter(name=NamespaceName)
        nodeObject = Policy.nodes.filter(name=PolicyName)
        if type(cls) is list:
            cls = cls[0]
        if type(nodeObject) is list:
            nodeObject = nodeObject[0]
        if cls and nodeObject:
            if nodeObject.appliesToNS.is_connected(cls):
                nodeObject.appliesToNS.disconnect(cls)
            if deletePolicy:
                nodeObject.delete()
        else:
            ValueError("Policy or Namespace unknown")

    def addPolicyToWorkload(WorkLoadName, Policy):
        cls = WorkLoad.nodes.filter(name=WorkLoadName)
        if type(cls) is list:
            cls = cls[0]
        if cls:
            Policy.save()
            Policy.appliesToWorkLoad.connect(cls)
        else:
            ValueError("Unknown WorkLoad")

    def removePolicyFromWorkload(WorkLoadName, PolicyName, deletePolicy=False):
        cls = WorkLoad.nodes.filter(name=WorkLoadName)
        nodeObject = Policy.nodes.filter(name=PolicyName)
        if type(cls) is list:
            cls = cls[0]
        if type(nodeObject) is list:
            nodeObject = nodeObject[0]
        if cls and nodeObject:
            if nodeObject.appliesToWorkLoad.is_connected(cls):
                nodeObject.appliesToWorkLoad.disconnect(cls)
            if deletePolicy:
                nodeObject.delete()
        else:
            ValueError("WorkLoad or Policy unknown")

    def listObjectsForPolicy(policyName):
        listRelatedNodes = list()
        policyObj = Policy.nodes.filter(name=policyName)
        if type(policyObj) is list:
            policyObj = policyObj[0]
        if policyObj:
           listRelatedNodes.append(policyObj.appliesToNS.all())
           listRelatedNodes.append(policyObj.appliesToCluster.all())
           listRelatedNodes.append(policyObj.appliesToWorkLoad.all())
        return listRelatedNodes
        


#----------------------------------------------------------------------------



#---------------------------------------------------------------------------------

def main():
    clusCluster = Cluster(name="cluster-asdas").save()
    ndNodes = Nodes(name="node-dffff").save()
    polPolicy = Policy(name="pol-sdsdfsdf").save()
    nameNamespace = Namespace(name="ns-dsdfsd").save()
    wkWorkLoad = WorkLoad(name="pod-djsbdf", workLoadType="Pod").save()
    cmpComponent = Component(name= "comp-sdbmn", componentType="Container").save()
    
    GphDB.addNodeToCluster(clusCluster.name, ndNodes)   
    GphDB.removeNodeFromCluster(clusCluster.name, ndNodes.name, True)
    
    GphDB.addNamespaceToCluster(clusCluster.name, nameNamespace)
    GphDB.removeNamespaceFromCluster(clusCluster.name, nameNamespace.name, True)

    GphDB.addWorkLoadToNamespace(nameNamespace.name, wkWorkLoad)
    GphDB.removeWorkLoadFromNamespace(nameNamespace.name, wkWorkLoad.name, True)

    GphDB.addComponentToWorkLoad(wkWorkLoad.name, cmpComponent)
    GphDB.removeComponentFromWorkload(wkWorkLoad.name, cmpComponent.name, True)
    
    GphDB.addPolicyToNamespace(nameNamespace.name, polPolicy)
    GphDB.removePolicyFromNamespace(nameNamespace.name, polPolicy.name, True)

    GphDB.addPolicyToWorkload(wkWorkLoad.name, polPolicy)
    GphDB.removePolicyFromWorkload(wkWorkLoad.name, polPolicy.name, True)

    print(GphDB.listObjectsForPolicy(polPolicy.name))
    
    


if __name__ == "__main__":
       main()




