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
#import custom_alerter
import logging
import os
import requests
import json
import asyncio
from nats.aio.client import Client as NATS
from nats.aio.errors import ErrConnectionClosed, ErrTimeout, ErrNoServers


class SplunkAlerter(object):
    #__metaclass__ = custom_alerter.AlerterType
    #fname = "/var/log/security_monkey/sample_alerter.log"

    def __init__(self):
        self.loop = asyncio.get_event_loop()

    """def logger_info(self,log_str):
        if os.path.isfile(self.fname):
            with open(self.fname, "a+") as in_file:
                in_file.write("\n")
                in_file.write(log_str)
        else:
            with open(self.fname, "w+") as in_file:
                in_file.write(log_str)"""

    def report_watcher_changes(self):
        """
        Collect change summaries from watchers defined logs them
        """
        """
        Logs created, changed and deleted items for Splunk consumption.
        """
        data = []
        element1 = {"id": "12" ,"action" :"Item created", "resource" : "securitygroup","name" : "temp201 (sg-aa12dedd in vpc-df7609a7)", "account" : "SM_for_AWS", "region" : "us-east-1", "cloudType":"AWS"}
        element2 = {"id": "13" ,"action" :"Item created", "resource" : "securitygroup","name" : "temp201 (sg-aa12dedd in vpc-df7609a7)", "account" : "SM_for_AWS", "region" : "us-east-1", "cloudType":"AWS"}
        data.append(element1)
        data.append(element2)
        request_json = json.dumps(data)
        self.loop.run_until_complete(self.__run(self.loop, "aws.events", bytes(request_json, 'utf-8')))

    def report_auditor_changes(self, auditor):
        data = []
        element1 = { "objectName" : "nginx-65899c769f-zrdlh", "criticality" : "CRITICAL",  "alarmDescription" : "This is a test citical alarm from POD A",  "cloudType" : "KUBERNETES" }
        element2 = {"objectName" :"nginx-65899c769f-t6xbd","criticality" : "CRITICAL","alarmDescription" : "This is a test citical alarm from POD B", "cloudType" : "KUBERNETES"}

        data.append(element1)
        data.append(element2)
        request_json = json.dumps(data)
        self.loop.run_until_complete(self.__run(self.loop, "aws.alarms", bytes(request_json, 'utf-8')))

    def __run(self, loop, publisher , data):
        nc = NATS()
        print("before connect")
        yield from nc.connect(servers=["nats://127.0.0.1:4222"], io_loop=loop)
        print("after connect")
        yield from  nc.publish(publisher, data)
        #yield from asyncio.sleep(1, loop=loop)
        yield from nc.close()
        print("done")

if __name__== "__main__":
    print ("Hello Main!")
    s = SplunkAlerter()
    print(s)
    s.report_watcher_changes()
    #s.report_auditor_changes(None)

