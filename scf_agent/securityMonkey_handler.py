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
import requests








class SM_Handler(object):

    #API_ENDPOINT = "http://localhost:5000/startaudit"

    @classmethod
    def hit_audit_request(cls, jsondata):
        API_ENDPOINT = "http://localhost:5000/startaudit"
        auditor_type = jsondata['auditorType']
        cluster = jsondata['cluster']
        auditorConfig = jsondata['auditorConfig']
        print("[Received on {} ************'{}'] : {}".format(auditor_type,cluster,auditorConfig))

        finaldata = {"auditor_type":auditor_type, "cluster":cluster, "json_body":auditorConfig}
        headers = {'content-type': 'application/json'}
        r = requests.post(url = API_ENDPOINT, data = json.dumps(finaldata), headers=headers)
        print("--------------r.text-----------------")
        print(r.text)
        result = json.loads(r.text)
        finalresult = {}
        finalresult['auditor_type'] = auditor_type
        finalresult['cluster'] = cluster
        finalresult['audit_report'] = result
        return finalresult


    @classmethod
    def set_config(cls, auditor_data):
        pass
