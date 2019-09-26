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
import boto3 as boto3
from gphmodels import *
import sys
import json
import collections



def connect_ec2_instance(region,access_key,secret_access_key):
    if(region):
        ec2 = boto3.resource('ec2', region_name=region,aws_access_key_id=access_key, aws_secret_access_key=secret_access_key)
        client = ec2.meta.client
    else:
        client = boto3.client('ec2')
    return client

def get_ec2_resource(region,access_key,secret_access_key):
    return boto3.resource('ec2', region_name=region,aws_access_key_id=access_key, aws_secret_access_key=secret_access_key)


class aws_service:
    def getAWSCloudData(self, connection):
        '''
        Refresh AWS Cloud data in Graph-DB
        '''
        print("Refreshing AWS objects ...")
        try:
            awsConn = connect_ec2_instance(connection["Region"],
                                           connection["aws_access_key_id"],
                                           connection["aws_secret_access_key"])
            vpcObs = awsConn.describe_vpcs()
            org = GphDB.getGphObject(connection['organization'], Organization)
            for vpcob in vpcObs["Vpcs"]:
                print("--------")
                print("VPC Objects :" + json.dumps(vpcob))
                clus = Cluster(name=vpcob["VpcId"],
                               organization=connection['organization'],
                               zone=connection["region"],
                               cloudType="AWS")
                clus = GphDB.addGphObject(clus)
                org.hasNetworkCluster.connect(clus)
                print("--------")
            secgrps = awsConn.describe_security_groups()
            for secgrp in secgrps["SecurityGroups"]:
                print("--------")
                print("SG Objects : %s" %(secgrp))
                pol = Policy(name=secgrp["GroupName"],
                             version=secgrp["GroupId"],
                             metaData=secgrp["Description"],
                             cloudType="AWS",
                             spec=secgrp,
                             policyRules={"IpPermissions":secgrp["IpPermissions"],
                                          "IpPermissionsEgress":secgrp["IpPermissionsEgress"]})
                pol = GphDB.addGphObject(pol)
                clus = GphDB.getGphObject(secgrp["VpcId"], Cluster)
                if clus:
                    pol.appliesToCluster.connect(clus)
                    print("Connect Policy %s to Cluster %s" %(pol.name, clus.name))
                print("--------")
            ec2_resources = get_ec2_resource(connection["Region"],
                                             connection["aws_access_key_id"],
                                             connection["aws_secret_access_key"])
            instances = ec2_resources.instances.filter(Filters=[{"Name":"instance-state-name",
                                                                 "Values":["running"]}])
            for inst in instances:
                print("--------")
                print("Instances : %s in %s" %(inst.id, inst.vpc_id))
                node = Nodes(name=inst.private_ip_address,
                             cloudType="AWS")
                node = GphDB.addGphObject(node)
                clus = GphDB.getGphObject(inst.vpc_id, Cluster)
                if clus:
                    node.cluster.connect(clus)
                    print("Connect Node %s to Cluster %s" %(node.name, clus.name))

            print("... Done Refreshing AWS objects")
            return True
        except Exception as e:
            print(e)
            return e
        finally:
            "Do we need to close awsConn ?"


if __name__== "__main__":
    awsService = aws_service()

    connection = {}
    connection["Region"] = 'us-east-2' 
    connection["aws_access_key_id"] = 'AKIAJX7L2QWKWCX4D4YQ'  
    connection["aws_secret_access_key"] = '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'
    connection['organization'] = 'Aricent'

    awsService.getAWSCloudData(connection)


