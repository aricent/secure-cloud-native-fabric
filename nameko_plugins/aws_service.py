import json
import sys
import boto3 as boto3

from cloud_framework import BaseCloudInterfce, CloudFactory
from common_def import service_logger, CONFIG

default_payload_dict = {'region':'','payload':''}
def connect_ec2_instance(region,access_key,secret_access_key):
    if(region):
        ec2 = boto3.resource('ec2', region_name=region,aws_access_key_id=access_key, aws_secret_access_key=secret_access_key)
        client = ec2.meta.client
    else:
        client = boto3.client('ec2')
    return client



def check_region_key(payload):
    buf = json.loads(payload)
    if buf['region']:
        return True
    else:
        return False

def get_ec2_resource(region,access_key,secret_access_key):
    return boto3.resource('ec2', region_name=region,aws_access_key_id=access_key, aws_secret_access_key=secret_access_key)


class AwsCloudInterfce(BaseCloudInterfce):
    """ Base class to define instance plugin interface. """

    def __init__(self,param):
        """ constructor method for instance"""
        service_logger.info("%s %s %s ", sys._getframe().f_code.co_name, "param:-", param)
        self.aws_access_key_id=param['aws_access_key_id']
        self.aws_secret_access_key=param['aws_secret_access_key']

    def connect_to_peer(self):
        """ establish connection with peer """
        pass

    def getRegion(self,payload):
        """ returns instance list """
        service_logger.info("-------LOG----")
        service_logger.info("%s %s %s ", sys._getframe().f_code.co_name, "Payload:-", payload)
        resp = ""
        try:
            service_logger.info("--------BEFORE CONNECTION---------------  " + self.aws_access_key_id + "   " + self.aws_secret_access_key )
            ec2 = connect_ec2_instance("us-east-2",self.aws_access_key_id,self.aws_secret_access_key)
            service_logger.info("--------AFTER CONNECTION---------------")
            resp = ec2.describe_regions()
            return (resp['Regions'])
        except Exception as e:  # EC2ResponseError
            service_logger.error("%s %s %s ", sys._getframe().f_code.co_name, "Exception:-", str(e))
            return False

    def addRegion(self):
        service_logger.error("%s %s %s ", sys._getframe().f_code.co_name, "This service is not supported for :%s", self)

    def deleteRegion(self):
        service_logger.error("%s %s %s ", sys._getframe().f_code.co_name, "This service is not supported for :%s", self)

    def updateRegion(self):
        service_logger.error("%s %s %s ", sys._getframe().f_code.co_name, "This service is not supported for :%s", self)

    def getVpc(self,payload):
        """ returns instance list """
        service_logger.info("%s %s %s ", sys._getframe().f_code.co_name, "Payload:-", payload)
        #import pdb
        #pdb.set_trace()
        resp = ""
        buf = json.loads(payload)
        region = buf['region']
        try:
            ec2 = connect_ec2_instance(region,self.aws_access_key_id,self.aws_secret_access_key)
            resp = ec2.describe_vpcs() 
            return resp
            #return ({'region': region, 'vpcs': resp['Vpcs']})
        except Exception as e:  # EC2ResponseError
            service_logger.error("%s %s %s ", sys._getframe().f_code.co_name, "Exception:-", str(e))
            return {'reason of failure' : str(e)}
            #return False

    def addVpc(self):
        service_logger.error("%s %s %s ", sys._getframe().f_code.co_name, "This service is not supported for :%s", self)

    def deleteVpc(self):
        service_logger.error("%s %s %s ", sys._getframe().f_code.co_name, "This service is not supported for :%s", self)

    def updateVpc(self):
        service_logger.error("%s %s %s ", sys._getframe().f_code.co_name, "This service is not supported for :%s", self)

    def getSecurityGroup(self,payload):
        """ returns instance list """
        service_logger.info("%s %s %s ", sys._getframe().f_code.co_name, "Payload:-", payload)
        resp = ""
        buf = json.loads(payload)
        region = buf['region']
        try:
            ec2 = connect_ec2_instance(region,self.aws_access_key_id,self.aws_secret_access_key)
            if buf['payload']:
                arg = buf['payload']
                resp = ec2.describe_security_groups(**arg)
            else:
                resp = ec2.describe_security_groups()
            return (resp['SecurityGroups'])
        except Exception as e:  # EC2ResponseError
            service_logger.error("%s %s %s ", sys._getframe().f_code.co_name, "Exception:-", str(e))
            return False

    def addSecurityGroup(self,payload, tags):
        service_logger.info("-------Entered addSecurityGroup-------------")
        service_logger.info("%s %s %s ", sys._getframe().f_code.co_name, "Payload:-", payload)
        resp = ""
        buf = json.loads(payload)
        region = buf['region']
        try:
            if (buf['payload']):
                buf = buf['payload']

                service_logger.info("-----------Before connect-------------")
                ec2 = connect_ec2_instance(region,self.aws_access_key_id,self.aws_secret_access_key)
                service_logger.info("-----------After connect-------------")

                resp = ec2.create_security_group(**buf)
                service_logger.info("-----------After create-------------" + resp['GroupId'])
                groupId = resp['GroupId']
                ec2.create_tags(Resources=[groupId], Tags=tags)
                return resp
                """if groupId:
                    service_logger.info("--------true---------")
                    return True"""
            #return False
        except Exception as e:
            service_logger.error("%s %s %s ", sys._getframe().f_code.co_name, "Exception:-", str(e))
            data = {}
            data['exception'] = str(e)
            return data

    def deleteSecurityGroup(self,payload):
        service_logger.info("%s %s %s ", sys._getframe().f_code.co_name, "Payload:-", payload)
        resp = ""
        buf = json.loads(payload)
        region = buf['region']
        try:
            if (buf['payload']):
                buf = buf['payload']
                ec2 = connect_ec2_instance(region,self.aws_access_key_id,self.aws_secret_access_key)
                resp = ec2.delete_security_group(**buf)
                service_logger.info("Resp: %s", resp)
                return True
        except Exception as e:
            service_logger.error("%s %s %s ", sys._getframe().f_code.co_name, "Exception:-", str(e))
            return False

    def updateSecurityGroup(self):
        service_logger.error("%s %s %s ", sys._getframe().f_code.co_name, "This service is not supported for :%s", self)


    def getIngressRule(self):
        service_logger.error("%s %s %s ", sys._getframe().f_code.co_name, "This service is not supported for :%s", self)
    
    def addIngressRule(self):
        service_logger.error("%s %s %s ", sys._getframe().f_code.co_name, "This service is not supported for :%s", self)


    def deleteIngressRule(self):
        service_logger.error("%s %s %s ", sys._getframe().f_code.co_name, "This service is not supported for :%s", self)

    def updateIngressRule(self,payload):
        """ returns instance list """
        service_logger.info("%s %s %s ", sys._getframe().f_code.co_name, "Payload:-", payload)
        # pdb.set_trace()
        resp = ""
        buf = json.loads(payload)
        region = buf['region']
        try:
            ec2 = connect_ec2_instance(region,self.aws_access_key_id,self.aws_secret_access_key)
            buf = buf['payload']
            arg = dict([('GroupId', buf['GroupId']), ('IpPermissions', buf['Old_IpPermissions'])])
            if arg['IpPermissions']:
                resp = ec2.revoke_security_group_ingress(**arg)
            arg = dict([('GroupId', buf['GroupId']), ('IpPermissions', buf['New_IpPermissions'])])
            if arg['IpPermissions']:
                resp = ec2.authorize_security_group_ingress(**arg)

            service_logger.info('--------------------------------------Ingress Successfully Set %s' ,  resp)

            return resp
        except Exception as e:
            service_logger.error("%s %s %s ", sys._getframe().f_code.co_name, "Exception:-", str(e))

            data = {}
            data['exception'] = str(e)
            return data


    def getEgressRule(self):
        service_logger.error("%s %s %s ", sys._getframe().f_code.co_name, "This service is not supported for :%s", self)

    def addEgressRule(self):
        service_logger.error("%s %s %s ", sys._getframe().f_code.co_name, "This service is not supported for :%s", self)

    def deleteEgressRule(self):
        service_logger.error("%s %s %s ", sys._getframe().f_code.co_name, "This service is not supported for :%s", self)

    def updateEgressRule(self,payload):
        """ returns instance list """
        service_logger.info("%s %s %s ", sys._getframe().f_code.co_name, "Payload:-", payload)
        resp = ""
        buf = json.loads(payload)
        region = buf['region']
        try:
            ec2 = connect_ec2_instance(region,self.aws_access_key_id,self.aws_secret_access_key)
            buf = buf['payload']
            arg = dict([('GroupId', buf['GroupId']), ('IpPermissions', buf['Old_IpPermissions'])])
            if arg['IpPermissions']:
                resp = ec2.revoke_security_group_egress(**arg)
            arg = dict([('GroupId', buf['GroupId']), ('IpPermissions', buf['New_IpPermissions'])])
            if arg['IpPermissions']:
                resp = ec2.authorize_security_group_egress(**arg)
 
            service_logger.info('--------------------------------------Egress Successfully Set %s' ,  resp)
            return resp

        except Exception as e:
            service_logger.error("%s %s %s ", sys._getframe().f_code.co_name, "Exception:-", str(e))
            data = {}
            data['exception'] = str(e)
            return data



class AwsCloud(CloudFactory):
    
    def __init__(cls,param):
        super().__init__(AwsCloudInterfce(param))
        service_logger.info("AWS instance (%s) created ",param['name'])
        #index = super(AwsCloud).in
        #self.cloud_name = name
        #return obj

    def getCloudName(self):
        return self.cloud_name


