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
import os
import sys
import traceback
import re

from nameko.events import EventDispatcher
from nameko.rpc import rpc, RpcProxy
from nameko.standalone.rpc import ClusterRpcProxy

from neomodel import (StructuredNode, JSONProperty, StringProperty, IntegerProperty,
                      UniqueIdProperty, RelationshipTo, RelationshipFrom, ArrayProperty,
                      Relationship, RelationshipDefinition)
from neomodel.match import NodeSet, EITHER, OUTGOING, INCOMING, Traversal
from neomodel import config


sys.path.append('./util/')
sys.path.append('./audit/')

from elastic_search_client import get_request, post_request, post_request_ver2, get_document_by_url
from gphmodels import *


def replaceNonAlNum(s):
    return re.sub('[^0-9a-zA-Z]+', '', s)


class CrispNodeCreator:
    name="CrispNodeCreator"

    def buildCrispNodeTypes(componentsJson):
        typesDict = dict()
        for item in componentsJson:
            if not "nodeType" in item:
                continue
            typeName = replaceNonAlNum(item["nodeType"])
            classAttrs = dict()
            classAttrs["__name__"] = typeName
            classAttrs["name"] = StringProperty(unique_index=True, required=True)
            classAttrs["displayName"] = StringProperty(unique_index=True, required=True)
            classAttrs["viewType"] = StringProperty(default="crisp")
            classAttrs["documentLink"] = StringProperty()
            classAttrs["category"] = StringProperty(default=replaceNonAlNum(item["nodeType"]))
            try:
                newCrispClass = type(typeName,
                                     (CrispNode,),
                                     classAttrs)
                typesDict[typeName] = newCrispClass            
            except Exception as e:
                print("[%s] Class already Exists in CRISP Node Type" %(typeName))
        return typesDict

    def createCrispNodeType(item):
        newCrispClass = None
        if item:
            if not "nodeType" in item:
                return None
            typeName = replaceNonAlNum(item["nodeType"])
            classAttrs = dict()
            classAttrs["__name__"] = typeName
            classAttrs["name"] = StringProperty(unique_index=True, required=True)
            classAttrs["displayName"] = StringProperty(unique_index=True, required=True)
            classAttrs["viewType"] = StringProperty(default="crisp")
            classAttrs["documentLink"] = StringProperty()
            classAttrs["category"] = StringProperty(default=replaceNonAlNum(item["nodeType"]))
            try:
                newCrispClass = type(typeName,
                                     (CrispNode,),
                                     classAttrs)
            except Exception as e:
               print("[%s] Class already Exists in CRISP Node Type" %(typeName))
        return newCrispClass

                            
    def addRelationToNodeType(crispClass, relName, relTo, relFrom):
        if relTo:
            rel = RelationshipTo(relTo, relName)
        elif relFrom:
            rel = RelationshipFrom(relFrom, relName)
        setattr(crispClass, relName, rel)
        return rel

    def buildRelations(crispObject):
        for name in crispObject.__class__.__dict__.keys():
            obj = crispObject.__class__.__dict__[name]
            if isinstance(obj, RelationshipDefinition):
                setattr(crispObject.__class__, name, obj.build_manager(crispObject, name))


def main():
    components = []
    with open('crisp/components.json') as f:
        components = json.load(f)
        f.close()
    print("--- Create Classes from Components.json ---")
    clsDict = CrispNodeCreator.buildCrispNodeTypes(components)
    #print("--- Dictionary contents ---") 
    #print(clsDict)
    print("--- End ---")
    prevNode = None
    for key in clsDict:
        value = clsDict[key]
        if prevNode:
            # and not hasattr(value(), "MAPS_TO"):
            CrispNodeCreator.addRelationToNodeType(value, "MAPS_TO", type(prevNode), None)
            print("Added attribute MAPS_TO: %s" %(hasattr(value(), "MAPS_TO")))
        neoObject = value(name=str(key + "-SomeName"))
        neoObject = neoObject.save()
        CrispNodeCreator.buildRelations(neoObject)
        if prevNode:
            neoObject.MAPS_TO.connect(prevNode)
        prevNode = neoObject

    
    
if __name__ == "__main__":


    main()
