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
from collections import defaultdict

from nameko.events import EventDispatcher
from nameko.rpc import rpc, RpcProxy
from nameko.standalone.rpc import ClusterRpcProxy

sys.path.append('./util/')
sys.path.append('./audit/')

from gphmodels import Auditor as AuditorInGph
from gphmodels import Organization, UserAccount, ComplianceReq, AssetGroup, SecurityControl 
from gphmodels import GphDB, SecurityPosture, Alarm, Policy, Nodes, Cluster
from elastic_search_client import get_request, post_request, post_request_ver2, get_document_by_url, get_all_documents_in_array, get_search_results_in_array, check_index_exists,get_document_by_id, delete_document
from auditor_data import Auditor
from crisp.crisp_node_editor import CrispNodeCreator, replaceNonAlNum

CONFIG = {'AMQP_URI' : "amqp://guest:guest@localhost:5672"}

class SecurityPostureCatalog:
    name="SecurityPostureCatalog"
    componentsJson = None
    componentReg = None
    
class SecurityPostureGraph(object):
    name="SecurityPostureGraph"

    def populate_components(self):
        if check_index_exists('components') == False:
            data = None
            with open('crisp/components.json') as f:
                data = json.load(f)
            for d in data:
                post_request('components', json.dumps(d), identity=d['id'])

        self.refreshCrispCatalogs(orgName="Aricent")
        #print("Loading Catalog into registry ....")
        components = SecurityPostureCatalog.componentsJson
        
        if len(components) > 0:
            SecurityPostureCatalog.componentReg = CrispNodeCreator.buildCrispNodeTypes(components)

        #print(".... Loaded Catalog into registry successfully")
        '''for nm in SecurityPostureCatalog.componentReg.keys():
            cls = SecurityPostureCatalog.componentReg[nm]
            print("Loaded %s, label %s, instance-count %s" %(nm, cls.__label__, len(cls.nodes)))'''

    def __findConnected(self, postureJsonDict, opId, exceptId):
        '''
        Return a dictionary of operators connected to this operator-node
        '''
        cnctedOps = dict()
        for lnkId in postureJsonDict["links"].keys():
            lnkNode = postureJsonDict["links"][lnkId]
            print("... Looking at lnk Id:%s" %(lnkId))
            if lnkNode["fromOperator"] == opId and not (lnkNode["fromOperator"] ==  exceptId):
                cnctedOps.update({lnkNode["toOperator"]:postureJsonDict["operators"][lnkNode["toOperator"]]}) 
            elif lnkNode["toOperator"] == opId and not (lnkNode["toOperator"] ==  exceptId):
                cnctedOps.update({lnkNode["fromOperator"]:postureJsonDict["operators"][lnkNode["fromOperator"]]})
        print("found connected nodes ..")
        print(cnctedOps)
        return cnctedOps

    def __createSecPosInGphDBv2(self, postureJsonDict, orgGphNd, postureGphNd):
        '''
        Create the nodes for Security Posture in Graph DB.
        This function is used when Posture components are editable.
        '''

        'First build the dynamic classes from Crsip Posture'
        self.populate_components()

        docLink = postureGphNd.documentLink
        if SecurityPostureCatalog.componentReg is None:
            print("Loading Catalog into registry ....")
            self.populate_components()
            if SecurityPostureCatalog.componentsJson:
                print("Component JSON avlbl.")
            else:
                print("Component JSON NOT avlbl. !!")
                SecurityPostureGraph.populate_components()
                print("Loaded available Components from file")
            components = SecurityPostureCatalog.componentsJson
            SecurityPostureCatalog.componentReg = \
                      CrispNodeCreator.buildCrispNodeTypes(components)
            print(".... Loaded Catalog into registry successfully")
        else:
            print(".... Catalog already in registry")

        'Next, add the MAPS_TO relations to the dynamic classes'
        'Then build the Graph Node and add to the Graph'
        'Locate the relation conenction and connec the nodes in Graph'            
        try:
            print(".. Creating Graph-Nodes")
            nodesToGphObjDict = dict()
            gphObjectRels = defaultdict(lambda:dict())
            print('Iterate through all operators in the Posture:')
            print("------ Start Posture ------")
            print(json.dumps(postureJsonDict["operators"]))
            print(json.dumps(postureJsonDict["links"]))
            print("------ End Posture ------")
            for opId, opNode in postureJsonDict["operators"].items():
                classTypeName = replaceNonAlNum(opNode["nodeType"])
                classType = SecurityPostureCatalog.componentReg[classTypeName]
                instanceName = replaceNonAlNum(opNode["properties"]["name"])
                if classType:
                    print('Find all links in the Posture for this operator %s' %(classTypeName))
                    for lnId, lnkNode in postureJsonDict["links"].items():
                        if lnkNode["fromOperator"] == opId:
                            toOpNode = postureJsonDict["operators"][lnkNode["toOperator"]]
                            toOpNodeInstanceName= replaceNonAlNum(toOpNode["properties"]["name"])
                            toClassTypeName = replaceNonAlNum(toOpNode["nodeType"])    
                            toClassType = SecurityPostureCatalog.componentReg[toClassTypeName]
                            relIndex = len(gphObjectRels[instanceName].keys())
                            relMaps = "MAPS_TO_" + toClassTypeName.upper()
                            print('Add relation : %s -- %s --> %s'
                                  %(classType, relMaps, toClassType))
                            CrispNodeCreator.addRelationToNodeType(classType, 
                                                                   relMaps, 
                                                                   toClassType, 
                                                                   None)
                            CrispNodeCreator.addRelationToNodeType(classType,
                                                                   "PART_OF",
                                                                   postureGphNd.__class__,
                                                                   None)
                            gphObjectRels[instanceName][relMaps] = toOpNodeInstanceName
                    nodesToGphObjDict[instanceName] = {"dispName":opNode["properties"]["name"], 
                                                       "gphObj":classType}
            for instanceName, classType in nodesToGphObjDict.items():      
                print('Now create the Graph Node')
                gphNodeObj = classType["gphObj"](name=str(instanceName))
                gphNodeObj.displayName = classType["dispName"]
                gphNodeObj.documentLink = postureGphNd.documentLink
                try:
                    print("Adding %s to Graph-DB .." %(gphNodeObj.name))
                    gphNodeObj = GphDB.addGphObject(gphNodeObj)
                    print(".. Added")
                except Exception as e:
                    print("Warning : %s" %(e))
                    print("!! Exception !! \n.. Add failed")
                CrispNodeCreator.buildRelations(gphNodeObj)
                'Replace Graph-Object class with Graph-DB object'
                nodesToGphObjDict[instanceName] = gphNodeObj
            print('Finally, start connecting Graph nodes')
            for instanceName, relatedTypesSet in gphObjectRels.items():
                gphNodeObj = nodesToGphObjDict[instanceName]
                for relName, relatedGphNodeName in relatedTypesSet.items():
                    relatedGphNodeObj = nodesToGphObjDict[relatedGphNodeName]
                    try:
                        print("Connecting : %s -- %s --> %s .. " %(gphNodeObj.name, relName, relatedGphNodeObj.name))
                        rel = getattr(gphNodeObj, relName)
                        rel.connect(relatedGphNodeObj)
                        gphNodeObj.PART_OF.connect(postureGphNd)
                        print(".. Connected")
                    except Exception as e:
                        print("!! Exception !! \n Connect failed : %s to %s because - %s" %(gphNodeObj.name, relatedGphNodeObj.name, e))
                        print(".. Connect failed")
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Exception : [file:%s,line:%s] %s" %(fname, exc_tb.tb_lineno, e))
            sys.stdout.flush()
            
        #except Exception as e:
        #    print("Exception : %s" %(e))
        #    traceback.print_tb(e.__traceback__)
        #    sys.stdout.flush()

    @rpc
    def getSecurityPostureNames(self, orgName="Aricent"):
        org = GphDB.getGphObject(orgName, Organization)
        if org:
            postureNames = []
            postureNodeList = org.implementsSecPolPosture.all()
            if postureNodeList:
                for posture in postureNodeList:
                   postureNames.append(posture.name)
                return postureNames
            else:
                return [{"Error":"No Postures created for this Org"}]
        else:
            return [{"Error": "No such Organization"}]

    @rpc
    def getSecurityPostureGraph(self, orgName="Aricent", postureName="default"):
        org = GphDB.getGphObject(orgName, Organization)
        if org:
            postureJsonStr = None
            if postureName == "default":
                postureJsonStr = []

            postureNodeList = org.implementsSecPolPosture.all()
            if postureNodeList:
                for posture in postureNodeList:
                   # If there is a specific posture-name requested, match it
                   # otherwise return all postures
                   if not postureName == "default":
                       if postureName == posture.name:
                           print(posture.documentLink)
                           postureJsonStr = get_document_by_url(posture.documentLink)
                           return postureJsonStr
                   else:
                       postureJsonStr.append(get_document_by_url(posture.documentLink))
                if postureJsonStr == None or len(postureJsonStr) == 0:
                    return [{"Error":"No Postures found for Org"}]
                else:
                    return postureJsonStr
            else:
                return [{"Error":"No Postures created for this Org"}]  
        else:
            return [{"Error": "No such Organization"}]

    @rpc
    def createSecurityPostureGraph(self, postureName, jsonDoc, orgName="Aricent"):
        print("In createSecurityPostureGraph")
        org = GphDB.getGphObject(orgName, Organization)
        resp =  [{"result":"Failure", "error":"Service error"}]
        try:
            if org:
                print("Store posture in EL DB")
                res_url = post_request_ver2('securityposture', json.dumps(jsonDoc),  postureName)
                print("Create posture in Graph-DB")       
                posture = GphDB.addGphObject(SecurityPosture(name=postureName, 
                                                             documentLink=res_url,
                                                             version='1.0'))
                print("Added Posture %s in GraphDB" %(postureName))
                org.implementsSecPolPosture.connect(posture)
                print("Connected Posture %s to Org %s in GraphDB" %(postureName, org.name))
                try:
                    self.__createSecPosInGphDBv2(jsonDoc, org, posture)
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print("!!! Exception in createSecPosInGphDB !!!")
                    print(exc_type, fname, exc_tb.tb_lineno)
                    print(e)
                    sys.stdout.flush()
            
                valNodes = list(jsonDoc['operators'].values())
                if valNodes:
                    print("Looking for policies in posture %s" %(postureName))
                    for nd in valNodes:
                        if nd['nodeType'] == 'Policies' or nd['nodeType'] == 'Security Configurations': 
                            # Note: Add 'type' and 'name' as a property in sample-posture JSON
                            pol = GphDB.getGphObject(nd['properties']['name'], replaceNonAlNum(nd["nodeType"]))
                            if pol:
                                posture.usesPolicy.connect(pol)
                                print("Connected posture with Policy : ", nd['properties']['name'])
                            else:
                                print("Posture has an Unknown Policy : ", nd['properties']['name'])
                resp = [{"result":"Success", "error":None}]
            else:
                print("Organization %s was not found in graph-DB" %(orgName))
                resp = [{"result":"Failure", "error":"No such Organization"}]
                print("----createSecurityPostureGraph END ------")
        finally:
            print("Finished Creating EVA-Map objects for %s" %(postureName))
            print(resp)
            sys.stdout.flush()
        return resp

    @rpc
    def updateSecurityPostureGraph(self, postureName, jsonDoc, orgName="Aricent"):
        'Update Policy Posture'

    '''Gets all components, Org name not used '''
    @rpc        
    def getCrispCatalogs(self, orgName="Aricent"):
        all_data =  get_all_documents_in_array('components')
        SecurityPostureCatalog.componentsJson = all_data
        return all_data
        '''if not SecurityPostureCatalog.componentsJson:        
            with open('crisp/components.json') as f:
                SecurityPostureCatalog.componentsJson = json.load(f)
        return (SecurityPostureCatalog.componentsJson)'''
    @rpc
    def refreshCrispCatalogs(self, orgName="Aricent"):
        all_data =  get_all_documents_in_array('components')
        #print("length of components ---" + str(len(all_data)))
        SecurityPostureCatalog.componentsJson = all_data
        print("---SecurityPostureCatalog.componentsJson---")
        print(json.dumps(SecurityPostureCatalog.componentsJson))
        sys.stdout.flush()

    @rpc
    def deleteCrispComponent(self, component_id, component=None, orgName="Aricent"):
        if component == None:
            component = get_document_by_id('components', component_id)
            if component['found'] == True:
                component = component['_source']
            else:
                return
        if component['parent'] ==  "topLevel": 
            '''Delete the parent and all its children '''   
            query_dict_children = {"parent": component['id'] }
            search_data_children = get_search_results_in_array('components', query_dict_children)
            for child in search_data_children:
                delete_document('components', child['id'])


        ''' Sample code to check with Graph DB, needs to be put properly before delete and update
        print("Sample code for delete")
        classTypeName = replaceNonAlNum(component["nodeType"])
        classType = SecurityPostureCatalog.componentReg[classTypeName]
        instanceName = replaceNonAlNum(component["text"])

        print("classType : " +  str(classType))
        print("instanceName : " + instanceName)
        component_relationships = GphDB.listRelatedObjsFor(instanceName, classType)
        #return classType
        if len(component_relationships) > 0:
            return "Component is linked, cannot delete"
        else:
            return "Component is not linkd, can be deleted"
        ENd of Code '''


        delete_document('components', component['id'])
        self.populate_components()

    @rpc
    def addCrispComponent(self, component,orgName="Aricent"):
        if component['parent'] != None :
            query_dict_children = {"parent": component['parent'] }
            search_data_children = get_search_results_in_array('components', query_dict_children)
            max_child_id = 0
            max_seq_no = 0
            component_id = None
            if component['parent'] == "topLevel":
                #get all toplevel components and get id of next
                for child in search_data_children:
                    child_id = int(child['id'].split("_",1)[1])
                    seq_no = child['sequence']
                    print("child id - " + str(child_id))
                    if child_id > max_child_id:
                        max_child_id = child_id
                    if seq_no > max_seq_no:
                        max_seq_no = seq_no

                component_id = 'node_' + str(max_child_id + 1)
                component['sequence'] = max_seq_no + 1
   
            else:    
                #get the components of the parent and then add the next component
                for child in search_data_children:
                    child_id = int(child['id'].split(".",1)[1])
                    print("child id - " + str(child_id))
                    if child_id > max_child_id:
                        max_child_id = child_id

                component_id = component['parent'] + '.' + str( max_child_id + 1 )

            if component_id != None:
                component['id'] = component_id
                resp = post_request('components', json.dumps(component), identity=component_id)
                self.populate_components()
                return resp



class SecurityPostureMap(object):
    'Handles EVA Mapping Requests'
    name="SecurityPostureMap"

    def __markParentNodes(self, node, evaMapBase, statusString):
        'Update parent nodes of EVA map as error'
        
    def __getClusterForAuditor(self, audkey, audnode, evaMapBase):
        'get parent cluster node'

        links = evaMapBase['links'].items()
        assetNodeToFind = ""
        for linkID, linkNode in links:
            if (linkNode["toOperator"] == audkey):
                assetNodeToFind = linkNode["fromOperator"]
            elif (linkNode["fromOperator"] == audkey):
                assetNodeToFind = linkNode["toOperator"]
        if not assetNodeToFind == "":
            for k, nd in evaMapBase['operators'].items():
                if k == assetNodeToFind:
                    return nd
        else:
            return None
    @rpc
    def getBaselineEVAmap(self, orgNm="Aricent"):
        'Get EVA Map base-line policy posture'
        securityPostureGraph = SecurityPostureGraph()
        evaMapBase = securityPostureGraph.getSecurityPostureGraph(orgName=orgNm)
        #evaMapBase = json.loads(evaMapBase)
        return evaMapBase

    @rpc
    def getEVAmap(self, orgNm="Aricent", postureName="default"):
        'Get EVA Map policy posture running status'
        securityPostureGraph = SecurityPostureGraph()
        evaMapBase = securityPostureGraph.getSecurityPostureGraph(orgName=orgNm, postureName=postureName)
        if evaMapBase is None:
            return [{'Error':'No such Organization'}]

        evaMapResponse = None
        if postureName == "default":
            evaMapResponse = []
            for evagraph in evaMapBase:
                evaMap = self.__getEVAmapForGraph(evagraph, orgNm)
                evaMapResponse.append(evaMap)

        else:
            evaMapResponse = self.__getEVAmapForGraph(evaMapBase, orgNm)

        return evaMapResponse
            

       
    def __getEVAmapForGraph(self, evaMapBase, orgNm):
        
        for key, node in evaMapBase['operators'].items():
            if 'nodeType' in node and node['nodeType'] == 'Auditors':
                #Auditor node, get last results if an audit is not running
                cluster = self.__getClusterForAuditor(key, node, evaMapBase)
                print("For Auditor \'", node['properties']['name'], "\', Cluster : ", cluster['properties']['name'])
                #Check if this node in EVA-Map is actually a Clsuter
                if GphDB.getGphObject(cluster['properties']['name'], Cluster):
                    print("Found Auditor in EVA-Map :", node['properties']['name'], "Check status ..")
                    node['properties']['status'] = \
                        Auditor.getAuditorState(node['properties']['name'],
                                                cluster['properties']['name']) 
                    print("... ", node['properties']['name'], " is ", node['properties']['status'])
                    if not (node['properties']['status'] == "RUNNING"): 
                        node['properties']['results'] = \
                            Auditor.getAuditResults(node['properties']['name'],
                                                    cluster['properties']['name'])
                        if node['properties']['results']['verdict'] == "AUDIT RESULTS FAIL":
                            self.__markParentNodes(node, 
                                                   evaMapBase, 
                                                   "AUDIT RESULTS FAIL")
                            print("Marking parent nodes in EVA-Map as failed")
                        else:
                            print("Audit results of Auditor :", node['properties']['name'], " are OK")
                else:
                    print("Suspicious node :", cluster['properties']['name'], 
                          "connected to Auditor : ", node['properties']['name'])
            elif 'type' in  node['properties'] and node['properties']['type'] == "Policies":
                #Check if policy version in evaMapBAse is same as current version in GraphDB
                'TODO'
        return evaMapBase


                         
from nameko.containers import ServiceContainer
from nameko.runners import ServiceRunner
from nameko.testing.utils import get_container

runner = ServiceRunner(config=CONFIG)
runner.add_service(SecurityPostureMap)
runner.add_service(SecurityPostureGraph)
runner.start()
sec = SecurityPostureGraph()
sec.populate_components()

if __name__ == '__main__':
    main()
def main():
    print("Get Catalogs")
    SecurityPostureGraph.getCrispCatalogs()
    samplePosture = None
    with open('crisp/sample_posture.json') as f:
        samplePosture = json.load(f)
        for node in list(samplePosture['operators'].values()):
            dataId = int(node['properties']['dataId'])
            for comp in SecurityPostureCatalog.componentsJson:
                if comp['id'] == dataId:
                    node['properties']['type'] = comp['nodeType']
                    node['properties']['name'] = comp['text']
                    break
        f.close()
    with open('crisp/outPosture.json', 'w+') as f:
        json.dump(samplePosture, f, indent=4, separators=(',',':'), sort_keys=False)
        f.write('\n')
        f.close()
    print("---- Create Org ----")
    org = Organization(name='Aricent')
    GphDB.addGphObject(org)
    print("---- Create Auditor ----")
    Auditor.loadClusterRegistryFromConfig(json.loads("[{}]"))
    Auditor.createAuditorInClusterRegistry("Aricent-Default", 
                                           "K8S.KubeBench",
                                           json.loads("[{}]"))
    Auditor.createAuditorInClusterRegistry("Aricent-Default", 
                                           "K8S.Falco",
                                           json.loads("[{}]"))
    print("---- Create Security Posture ---- ")
    print(SecurityPostureGraph.createSecurityPostureGraph("Posture-BaseLine", samplePosture))
    #print("---- Get Security Posture Graph ----")
    #print(SecurityPostureGraph.getSecurityPostureGraph(postureName="Posture-BaseLine"))
    print("----Get EVA Map ----")
    SecurityPostureMap.getEVAmap(orgNm="Aricent")
    print("---- All Done ----")
    
    
   
