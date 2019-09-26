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
from security_monkey.alerters import custom_alerter
import logging
import os

class SplunkAlerter(object):
    __metaclass__ = custom_alerter.AlerterType
    fname = "/var/log/security_monkey/sample_alerter.log"
    def logger_info(self,log_str):
        if os.path.isfile(self.fname):
            with open(self.fname, "a+") as in_file:
                in_file.write("\n")
                in_file.write(log_str)
        else:
            with open(self.fname, "w+") as in_file:
                in_file.write(log_str)

    def report_watcher_changes(self, watcher):
        """
        Collect change summaries from watchers defined logs them
        """
        """
        Logs created, changed and deleted items for Splunk consumption.
        """

        for item in watcher.created_items:
            self.logger_info(
                "|action=\"Item created\"| "
                "|id={}| "
                "|resource={}| "
                "|account={}| "
                "|region={}| "
                "|name=\"{}\"|".format(
                    item.db_item.id,
                    item.index,
                    item.account,
                    item.region,
                    item.name))

        for item in watcher.changed_items:
            self.logger_info(
                "|action=\"Item changed\"| "
                #"id={} "
                "|resource={}| "
                "|account={}| "
                "|region={}| "
                "|name=\"{}\"|".format(
                    #item.db_item.id,
                    item.index,
                    item.account,
                    item.region,
                    item.name))

        for item in watcher.deleted_items:
            self.logger_info(
                "|action=\"Item deleted\"| "
                "|id={}| "
                "|resource={}| "
                "|account={}| "
                "|region={}| "
                "|name=\"{}\"|".format(
                    item.db_item.id,
                    item.index,
                    item.account,
                    item.region,
                    item.name))

    def report_auditor_changes(self, auditor):
     # try:
        for item in auditor.items:
            for issue in item.confirmed_new_issues:
                self.logger_info(
                    "|action=\"Issue created\"| "
                    "|id={}| "
                    "|resource={}| "
                    "|account={}| "
                    "|region={}| "
                    "|name=\"{}\"| "
                    "|issue=\"{}\" Notes={}|".format(
                        issue.id,
                        item.index,
                        item.account,
                        item.region,
                        item.name,
                        issue.issue,issue.notes))

            for issue in item.confirmed_fixed_issues:
                self.logger_info(
                    "|action=\"Issue fixed\"| "
                    "|id={}| "
                    "|resource={}| "
                    "|account={}| "
                    "|region={}| "
                    "|name=\"{}\"| "
                    "|issue=\"{}\" Notes={}|".format(
                        issue.id,
                        item.index,
                        item.account,
                        item.region,
                        item.name,
                        issue.issue,issue.notes))
      #except Exception as e:  # EC2ResponseError
      #    self.logger.error("Exception:{}",str(e))


