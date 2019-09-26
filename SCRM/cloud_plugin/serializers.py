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
from rest_framework import serializers
from .models import Region, SecurityGroup, Vpc, SmIssues, RunningCloudTable
import pdb

class RegionSerializer(serializers.ModelSerializer):
    class Meta:
            model = Region
            exclude = ("LastUpdated",)
            read_only = (
                "EndPoint",
                "RegionName"
            )

class VpcSerializer(serializers.ModelSerializer):

    Apidump = serializers.SerializerMethodField('get_apidump_val')
    class Meta:
            model = Vpc
            exclude = ("LastUpdated", "apiDump")
            read_only = (
                "VpcId",
                "RegionName",
                "ApiDump",
                "IsDefault",
                "State"
            )

    def get_apidump_val(self, obj):
        return obj.get_apidump

class OnlyVpcSerializer(serializers.ModelSerializer):
    Apidump = serializers.SerializerMethodField('get_apidump_val')
    class Meta:
            model = Vpc
            exclude = ("LastUpdated", "RegionName", "IsDefault", "State", "apiDump")
            read_only = (
                "VpcId"
                "ApiDump"
            )

    def get_apidump_val(self, obj):
        return obj.get_apidump

class SecurityGroupSerializer(serializers.ModelSerializer):
    Ingress = serializers.SerializerMethodField('get_ingress_val')
    Egress = serializers.SerializerMethodField('get_egress_val')
    class Meta:
            model = SecurityGroup
            fields = (
                "GroupId",
                "GroupName",
                "Description",
                "VpcId",
                "OwnerId",
                "Ingress",
                "Egress"
            )

    def get_ingress_val(self, obj):
        return obj.get_ingress

    def get_egress_val(self, obj):
        return obj.get_egress

class SmSerializer(serializers.ModelSerializer):
    class Meta:
            model = SmIssues
            fields = (
                "Component",
                "Resource",
                "Name",
                "Region",
                "Action",
                "Issue"
            )

class CloudSerializer(serializers.ModelSerializer):
    class Meta:
            model = RunningCloudTable
            fields = (
                "CloudName",
                "CloudId",
                "CloudType",
                "CloudCat"
            )

