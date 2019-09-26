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
import datetime

from nameko.standalone.rpc import ClusterRpcProxy
from sqlalchemy import *
from nameko.events import EventDispatcher, event_handler
from nameko.rpc import rpc
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
import sys
import json
from common_def import *


Base = declarative_base()
def convert_to_str(var):
    return json.dumps(var)

def update_policy_object(payload):
    service_logger.info("%s %s %s ", sys._getframe().f_code.co_name, "Payload:-", payload)
    for item in payload.items:
        service_logger.info("%s %s ", "namespace:-", item.metadata.namespace)
        service_logger.info("%s %s ", "name:-", item.metadata.name)
        service_logger.info("%s %s ", "spec:-", item.spec)
        service_logger.info("%s %s ", "spec (ingress):-", item.spec.ingress)
        service_logger.info("%s %s ", "spec(egress):-", item.spec.egress)
           
'''
class SuportedCloud(Base):
    __tablename__ = 'SupportedCloudTable'

    id = Column(Integer,primary_key=True)
    cloudType = Column(String)
    cat = Column(String)


class CloudCapabilities(Base):
    __tablename__ = 'CloudCapabilityTable'

    id = Column(Integer, primary_key=True)
    Name = Column(String)

class CloudCapabilityMatrix(Base):
    __tablename__ = 'CloudCapabilityMatrixTable'
    cloudTypeId = Column(Integer,ForeignKey('SupportedCloudTable.id'),primary_key=True)
    capabilityId = Column(Integer,ForeignKey('CloudCapabilityTable.id'),primary_key=True)#, )

    Name = Column(String)
'''


class CloudTable(object):
    pass

class Region(object):
    pass

class SecurityGroup(object):
    pass

class Vpc(object):
    pass

class Issue(object):
    pass

class dbService:
    """ Service to handle DB operations. """
    name = "dbService"
    result = "FALSE"
    engine = create_engine(DB_PATH)
    metadata = MetaData(engine)
    regionTbl = Table('region', metadata, autoload=True)
    sgTbl = Table('securityGroup', metadata, autoload=True)
    vpcTbl = Table('vpc', metadata, autoload=True)
    issueTbl = Table('issues', metadata, autoload=True)
    runningCloudTbl = Table('RunningCloudTable', metadata, autoload=True)
    mapper(Region, regionTbl)
    mapper(SecurityGroup, sgTbl)
    mapper(Vpc, vpcTbl)
    mapper(Issue, issueTbl)
    mapper(CloudTable, runningCloudTbl)

    def getTabledata(worker_ctx, engine, table):
        Session = sessionmaker(bind=engine, autoflush=True)
        session = Session(autocommit=True)
        session.begin()
        row = session.query(table).all()
        session.close()
        # service_logger.info("is_row_exist:",row)
        #row={'instance_id':'AWS','instance_type':1}
        return row

    def is_row_exist(worker_ctx, engine, table, key_str, key_val):
        Session = sessionmaker(bind=engine, autoflush=True)
        session = Session(autocommit=True)
        session.begin()
        row = session.query(table).filter(key_str == key_val).first()
        session.close()
        # service_logger.info("is_row_exist:",row)
        return row

    def delete_issue(worker_ctx, engine, key):
        Session = sessionmaker(bind=engine, autoflush=True)
        session = Session(autocommit=True)
        session.begin()
        rows = session.query(Issue).filter(Issue.Name == key)
        for row in rows:
            print(row)
            session.delete(row)
        session.commit()
        session.close()

    def save_data(worker_ctx, engine, obj):
        # service_logger.info("%s %s %s ",sys._getframe().f_code.co_name,"Obj:-", obj)
        Session = sessionmaker(bind=engine, autoflush=True)
        session = Session(autocommit=True)
        session.begin()
        session.add(obj)
        session.commit()
        session.close()

    def delete_all_data(worker_ctx, engine, table, region):
        # service_logger.info("%s %s %s ",sys._getframe().f_code.co_name,"table:-", table)
        Session = sessionmaker(bind=engine, autoflush=True)
        session = Session(autocommit=True)
        session.begin()
        vpcs = session.query(Vpc).filter(Vpc.RegionName_id == region)
        for vpc in vpcs:
            rows = session.query(SecurityGroup).filter(SecurityGroup.VpcId_id == vpc.VpcId)
            for row in rows:
                session.delete(row)
        session.commit()
        session.close()

    def is_k8s_instance(self,cid):
        table_var = self.is_row_exist(self.engine, CloudTable, CloudTable.CloudId, cid)
        if (table_var.CloudType == 'KUBERNETES'):
            return 1
        else:
            return 0



    @event_handler("initHandler", "Event_updateCloudInterfaceList")
    def eventUpdateCloudTable(self, payload):
        try:
            service_logger.info("%s %s %s ", sys._getframe().f_code.co_name, "Payload:-", payload)
            # tmp = json.dumps(payload)
            # service_logger.info("%s %s %s ",sys._getframe().f_code.co_name,"Payload json dumps:-", tmp)
            # service_logger.info("%s %s %s ",sys._getframe().f_code.co_name,"Payload json loads:-", json.loads(tmp))
            for row in payload:
                table_var = self.is_row_exist(self.engine, CloudTable, CloudTable.CloudId, row['index'])
                if table_var == None:
                    table_var = CloudTable()
                table_var.CloudId = row['index']
                table_var.CloudType = row['type']
                table_var.CloudName = row['name']
                table_var.CloudCat = row['cat']
                table_var.LastUpdated = datetime.datetime.now(datetime.timezone.utc)
                self.save_data(self.engine, table_var)
            tmp =self.getTabledata(self.engine,CloudTable)
        except Exception as e:  # EC2ResponseError
            service_logger.error("%s %s %s ", sys._getframe().f_code.co_name, "Exception:-", str(e))

    @event_handler("guiHandler", "Event_updateRegionTable")
    def eventUpdateRegion(self, payload):
        try:
            service_logger.info("%s %s %s ", sys._getframe().f_code.co_name, "Payload:-", payload)
            # tmp = json.dumps(payload)
            # service_logger.info("%s %s %s ",sys._getframe().f_code.co_name,"Payload json dumps:-", tmp)
            # service_logger.info("%s %s %s ",sys._getframe().f_code.co_name,"Payload json loads:-", json.loads(tmp))
            for row in payload:
                region = self.is_row_exist(self.engine, Region, Region.RegionName, row['RegionName'])
                if region == None:
                    region = Region()
                region.EndPoint = row['Endpoint']
                region.RegionName = row['RegionName']
                region.LastUpdated = datetime.datetime.now(datetime.timezone.utc)
                self.save_data(self.engine, region)
        except Exception as e:  # EC2ResponseError
            service_logger.error("%s %s %s ", sys._getframe().f_code.co_name, "Exception:-", str(e))

    @event_handler("guiHandler", "Event_updateSecurityGroupTable")
    def eventUpdateSecurityGroup(self, payload):
        service_logger.info("%s %s %s ", sys._getframe().f_code.co_name, "Payload:-", payload)
        if not isinstance(payload, list):
            return
        cid=payload.pop(0)
        payload = payload.pop(0)
        if(is_k8s_instance(cid)):
            update_policy_object(payload)
            return
        for row in payload:
            sg = self.is_row_exist(self.engine, SecurityGroup, SecurityGroup.GroupId, row['GroupId'])
            if sg == None:
                sg = SecurityGroup()
            sg.GroupId = row['GroupId']
            sg.GroupName = row['GroupName']
            sg.Description = row['Description']
            sg.OwnerId = row['OwnerId']
            sg.ingress = convert_to_str(row['IpPermissions'])
            sg.egress = convert_to_str(row['IpPermissionsEgress'])
            sg.VpcId_id = row['VpcId']
            sg.CloudId_id = cid['CloudId']
            sg.LastUpdated = datetime.datetime.now(datetime.timezone.utc)
            self.save_data(self.engine, sg)

    @event_handler("awsService", "Event_deleteSecurityGroupTable")
    def eventDeleteSecurityGroup(self, payload):
        service_logger.info("%s %s %s ", sys._getframe().f_code.co_name, "Payload:-", payload)
        self.delete_all_data(self.engine, SecurityGroup, payload['region'])

    @event_handler("guiHandler", "Event_updateVpcTable")
    def eventUpdateVpc(self, payload):
        service_logger.info("%s %s %s ", sys._getframe().f_code.co_name, "Payload:-", payload)
        region = payload['region']
        CloudId = payload['CloudId']
        try:
            for row in payload['vpcs']:
                vpc = self.is_row_exist(self.engine, Vpc, Vpc.VpcId, row['VpcId'])
                if vpc == None:
                    vpc = Vpc()
                vpc.CloudId_id = CloudId
                vpc.VpcId = row['VpcId']
                vpc.apiDump = convert_to_str(row)
                vpc.IsDefault = row['IsDefault']
                vpc.State = row['State']
                vpc.RegionName_id = region
                vpc.LastUpdated = datetime.datetime.now(datetime.timezone.utc)
                self.save_data(self.engine, vpc)
        except Exception as e:  # EC2ResponseError
            service_logger.error("%s %s %s ", sys._getframe().f_code.co_name, "Exception:-", str(e))

    @event_handler("k8sWatcherService", "Event_updateIssueTable")
    @event_handler("awsAlertService", "Event_updateIssueTable")
    def eventUpdateIssue(self, payload):
        service_logger.info("%s %s %s ", sys._getframe().f_code.co_name, "Payload:-", payload)
        try:
            for row in payload:
                issue = None
                if row['Component'] == 'kubernetes':
                    issue = self.is_row_exist(self.engine, Issue, Issue.Name, row['name'])
                if issue == None:
                    issue = Issue()
                issue.Component = row['Component']
                issue.Resource = row['resource']
                issue.Name = row['name']
                issue.Region = row['region']
                issue.Action = row['action']
                issue.Issue = row['issue']
                issue.LastUpdated = datetime.datetime.now(datetime.timezone.utc)
                # service_logger.info("%s",issue)
                self.save_data(self.engine, issue)
        except Exception as e:  # EC2ResponseError
            service_logger.error("%s %s %s ", sys._getframe().f_code.co_name, "Exception:-", str(e))

    @event_handler("awsAlertService", "Event_deleteIssueTable")
    def eventDeleteIssue(self, payload):
        service_logger.info("%s %s %s ", sys._getframe().f_code.co_name, "Payload:-", payload)
        self.delete_issue(self.engine, payload)

    @event_handler("guiHandler", "Event_getCloudInterfaceList")
    def eventGetCloudInterfaceList(self, payload):
        service_logger.info("%s %s %s ", sys._getframe().f_code.co_name, "Payload:-", payload)
        ret_payload = self.getTabledata(self.engine, table="InterfaceTable")
        with ClusterRpcProxy(CONFIG) as rpc:
            rpc.dbService.dispatchCloudInterfaceList(ret_payload)

    dispatch = EventDispatcher()
    @rpc
    def dispatchCloudInterfaceList(self, payload):
        service_logger.info("%s %s %s ", sys._getframe().f_code.co_name, "Payload:-", payload)
        payload = json.dumps(payload)
        self.dispatch("Event_cloudInterfaceList", payload)

