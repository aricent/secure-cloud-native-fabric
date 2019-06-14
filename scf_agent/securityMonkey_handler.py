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
