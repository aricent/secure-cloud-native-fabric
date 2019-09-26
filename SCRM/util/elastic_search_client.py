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
#This is a client to acces the elastic search database.
import sys
import requests
import json
import datetime
from elasticsearch import Elasticsearch, exceptions
import yaml

"""---This request gets documents for the given index - Default, 10 documents--- """
def get_request(index):
    url = 'http://localhost:9200/'+ index  +'/_search?q=*&pretty'
    res = requests.get(url)
    #print(res.content)
    return res


"""---Posts given document body to the given index, if the Identity is specified then it is set, else _id is assigned by ES ---"""
def post_request(index, data, identity=None):
    url = "http://localhost:9200/"+ index  +"/_doc/"
    if identity != None:
        url = url + identity

    headers = {'Content-type': 'application/json'}
    #print("url : " + url)
    sys.stdout.flush()

    """ts = datetime.datetime.now().timestamp()

    data_dict = json.loads(data)
    data_dict.update({'timestamp':ts})

    final_data = json.dumps(data_dict)"""
    final_data = data

    #print("DATA : " + final_data)
    sys.stdout.flush()

    res =  requests.post(url, data=data, headers=headers)
    #print(res.content)
    #sys.stdout.flush()
    return res.content.decode('utf-8')


"""---Gets all documents for a an index. first fetches count and then count number of documents. If sort dictionary is given then fetches in that sort order. ---"""
def get_all_documents(index, sort_dict = None, raw_data = False):
    count = get_count_for_index(index)
    if count == 0:
        return []    
    else:
        url = 'http://localhost:9200/'+ index +'/_search?pretty=true&q=*:*&size='+ str(count) + '&filter_path=hits.hits._source'
        if raw_data:
            url = 'http://localhost:9200/'+ index +'/_search?pretty=true&q=*:*&size='+ str(count) 
        #print(url)
        if sort_dict == None:
            res = requests.get(url)
            #print(res.content)
            res_json = json.loads(res.content.decode('utf-8'))
            #print(res_json.get('hits').get('hits'))
            return res_json.get('hits').get('hits')

        else:
            #print("---Sorting---")
            headers = {'Content-type': 'application/json'}
            dictlist = []
            for key, value in sort_dict.items():
                temp = {key:value}
                dictlist.append(temp)
            
            req_body = {"query": { "match_all": {} }, "sort": dictlist }
            res =  requests.post(url, data=json.dumps(req_body), headers=headers)
            res_json = json.loads(res.content.decode('utf-8'))
            #print(res_json.get('hits').get('hits'))
            return res_json.get('hits').get('hits')
            

"""---Gets all documents for a an index and returns a single array. ---"""
def get_all_documents_in_array(index, sort_dict = None):

    all_data = get_all_documents(index, sort_dict)
    final_data = []
    for data in all_data:
        final_data.append(data['_source'])

    return final_data




"""---gets the document count for given index ---"""
def get_count_for_index(index):
    url = 'http://localhost:9200/'+ index +'/_count'
    res =  requests.post(url)

    if res.ok:
        res_content = json.loads(res.content.decode('utf-8'))
        count = res_content["count"]
        #print(count)
        return count
    else:
        return 0


"""---Searches the 'quey_dict' dictionary in the given index and gets documents that match the query patterns ---"""
def get_search_results(index, query_dict):
    url = 'http://localhost:9200/'+ index +'/_search?pretty=true&q='

    for k, v in query_dict.items():
        #print(k, v)
        url = url +  k + ":" +  v + '%20AND%20'
    #print(url)
    last = url.rfind('%20AND%20')
    #print(last)
    finalUrl = url[:last]
    #print(finalUrl)
    finalUrl = finalUrl + '&filter_path=hits.hits'
    print(finalUrl)
    res = requests.get(finalUrl)
    #print(res.content.decode('utf-8'))
    return res.content.decode('utf-8')


"""---Gets Search Results for an index in a single array. ---"""
def get_search_results_in_array(index, query_dict):

    all_data = json.loads(get_search_results(index, query_dict))
    final_data = []
    for data in all_data['hits']['hits']:
        final_data.append(data['_source'])

    return final_data

"""---updates the specific document with given identity in the given index, with the given request body ---"""
def update_document(index, identity, req_body):
    elasticsearch = Elasticsearch()
    es_req = {}
    es_req['doc'] = req_body
    resp =  elasticsearch.update(index=index, id=identity, doc_type='_doc', body = es_req )
    #print(resp)
    return resp


"""---Deletes the document with given identity in the given index ---"""
def delete_document(index, identity):
    url = 'http://localhost:9200/'+ index +'/_doc/' + identity
    #print(url)
    res =  requests.delete(url)
    #print(res)
    return res.content.decode('utf-8')



"""---Gets the document with given identity in the given index ---"""
def get_document_by_id(index, identity):
    url = 'http://localhost:9200/'+index+'/_doc/'+identity
    #print(url)
    res = requests.get(url)
    res_json = json.loads(res.content.decode('utf-8'))
    #print(res.status_code)
    #print(res.json)
    return res_json



"""---Gets the document with given identity in the given index, returns the jsondoc, correcponding to the post 2222 request !!!ONLY TO USE IF POST ver2 IS USED!!! ---"""
def get_document_by_id_ver2(index, identity):
    url = 'http://localhost:9200/'+index+'/_doc/'+identity
    #print(url)
    res = requests.get(url)
    res_json = json.loads(res.content.decode('utf-8'))
    res_source = res_json.get('_source')
    res_jsondoc = res_source.get('jsondoc')
    #print(res.status_code)
    #print(res_jsondoc)
    return res_jsondoc




"""---Posts the given body in the given index, for the given identity(if provided) and returns the GET url to fetch this document ---"""
def post_request_ver2(index, data, identity, metadata=None, blob = None):
    url = "http://localhost:9200/"+ index  +"/_doc/"

    headers = {'Content-type': 'application/json'}
    #print("url : " + url)
    #print("data-type : " + type(data))
    sys.stdout.flush()

    if metadata == None:
        metadata = dict()

    ts = datetime.datetime.now().timestamp()
    metadata.update({'timestamp':ts})
    if identity != None:
        url = url + identity
        metadata.update({'id': identity})
    
    jsondoc = None
    if data != None:
        jsondoc = json.loads(data)

    data_dict = dict()
    data_dict.update({'metadata' : metadata})
    data_dict.update({'jsondoc': jsondoc})
    #data_dict.update({'blob': blob})
    """if type(data) is str:
        data_dict = json.loads(data)
    elif type(data) is dict:
        data_dict = data
    else:
        data_dict.update({"data":data})"""

    final_data = json.dumps(data_dict)
    if blob != None:
        last = final_data.rfind('}')
        final_data = final_data[:last] + ', \"blob\": \"' + blob + '\"  }'
    #return final_data
    #print("---FINAL DATA BEFOEE POST---")
    #print(final_data)

    res =  requests.post(url, data=final_data, headers=headers)
    res_json = json.loads(res.content.decode('utf-8'))
    #return res_json
    #print("-----------RESPONSE----------------")
    #print(res_json)
    res_id = res_json.get('_id')
    #print(res_id)
    res_url = index  +"/_doc/" + res_id
    #print(res_url)
    return res_url


"""---Executes GET request on the provided URI ---"""
def get_document_by_url(uri):
    url = "http://localhost:9200/" + uri
    #print(url)
    res = requests.get(url)
    res_json = json.loads(res.content.decode('utf-8'))
    source = res_json.get('_source')
    #return source.get('metadata')
    return source.get('jsondoc')

        
def get_search_results_ver2(index, query_dict):
    url = 'http://localhost:9200/'+ index +'/_search?pretty=true&q='

    for k, v in query_dict.items():
        #print(k, v)
        url = url +  k + ":" +  v + '%20AND%20'
    #print(url)
    last = url.rfind('%20AND%20')
    #print(last)
    finalUrl = url[:last]
    #print(finalUrl)
    res = requests.get(finalUrl)
    #print(res.content.decode('utf-8'))
    result = json.loads(res.content.decode('utf-8'))
    finalresult = result['hits']['hits']
    return finalresult


'''This method checks if an index exists in Elastic Search '''
def check_index_exists(index):
    es = Elasticsearch() 
    if es.indices.exists(index=index):
        return True
    return False



'''This method is specifically for Fetching the latest Audit report for given Auditor '''
def get_audit_report(cluster, auditor_type, start_time = None, end_time = None):
    url = "http://localhost:9200/audit_reports/_search"
    data = None

    if start_time == None and end_time == None:
        data = {
          "query": {
            "bool": {
              "must": [
                 { "match": { "metadata.auditor_type": auditor_type }},
                 { "match": { "metadata.cluster": cluster }}
               ]
             }
           },
          "sort" : {
            "metadata.timestamp": {"order": "desc"}
          },
          "size" : 1
       } 

    else:
        data = {
          "query" : {
            "bool": {        
                "must": [
                  { "match": { "metadata.auditor_type": auditor_type }},
 		  { "match": { "metadata.cluster": cluster }}
                ],
                "filter": {
                  "range": {"metadata.timestamp": {"gte": start_time, "lte": end_time}}
                }
            }
          },
           "sort" : {
                    "metadata.timestamp": {"order": "desc"}
                  }
         }
     

    headers = {'Content-type': 'application/json'}
    res =  requests.post(url, data=json.dumps(data), headers=headers)
    result = json.loads(res.content.decode('utf-8'))
    return  result['hits']['hits']
    #return res.content.decode('utf-8')

'''This method creates and index, with fieleds with given property types '''
def create_index_with_properties(index, properties):
    url = url = "http://localhost:9200/"+ index
    headers = {'Content-type': 'application/json'}    
    data = {"mappings": {"_doc": {"properties": properties}}}

    #print("---data--")
    #print(json.dumps(data))

    res =  requests.put(url, data=json.dumps(data), headers=headers)
    return res

'''Method adds auditors index with specific properties '''
def create_auditor_index():
    if check_index_exists('auditors') == False:
        properties = {"metadata" : {"type" : "object"}, "jsondoc" : {"type" : "object"}, "blob" : {"type" : "binary"}}
        create_index_with_properties('auditors', properties)


'''Search using querystring '''
def search_index_using_querystring(index, query_dict):
    url = 'http://localhost:9200/'+ index +'/_search'
    fields = []
    query = None

    for k, v in query_dict.items():
        fields.append(k)
        if query:
            query = query + 'AND' + v
        else:
            query = v
    #print(url)
    headers = {'Content-type': 'application/json'}

    print("url : " + url)

    query = {"query" : {"query_string" : {"fields" : fields, "query" : query}}}

    print("data : " + json.dumps(query))
   
    #res = requests.request(method='get', url=url, data=json.dumps(query), headers=headers)
 
    res =  requests.get(url, data = json.dumps(query), headers=headers)

    return json.loads(res.text)['hits']['hits']



"""---Main ti Test!! ---"""
if __name__== "__main__":

    #f = open("/home/ubuntu/test/git_code/SCF/SCRM/util/auditor.json", "r") 
    #print(f.read())
    #data = json.loads(f.read())
    #res = post_request('auditors', json.dumps(data), 'AAA')
    #print(res.content)

    #get_document_by_id_ver2('auditors', 'K8S.KubeBench_default')

    #data =  { "posturename": "Aricent-Cloud-Posture","orgname": "Aricent", "jsondoc": {"test" : "data"}}



    """{"id": "135", "action": "Item created", "cloudType": "AWS", "resource": "securitygroup", "account": "SM_for_AWS", "name": "temp201 (sg-aa12dedd in vpc-df7609a7)", "region": "us-east-1"}"""
    """metadata = {'type' : 'aws'}
    return_url = post_request_ver2('auditor', json.dumps(data), 'testid', metadata)
    response = get_document_by_url(return_url)
    print(response)"""
    #rep = get_count_for_index('policies')
    #get_all_documents('policies', { "timestamp": "desc"})
    #uery_dict = {"GroupName" : "test-Sec-Grp", "VpcId" : "vpc-0f31d867"}
    #et_search_results('policies', query_dict)
    """body = { "ingressRules": { "Old_IpPermissions": [      
    ],
    "New_IpPermissions": [
      {
        "IpProtocol": "tcp",
        "FromPort": 80,
        "ToPort": 80,
        "IpRanges": [
          {
            "CidrIp": "0.0.0.0/0",
            "Description": "tetsing"
          }
        ]
      }
    ]
  }}"""
    #rep = update_document('policies', 'sg-09638641e6d7278bc', body)
    #delete_document('policies', 'sg-072bb0a754075bd75')

    #rep2 = get_document_by_id('policies','sg-09638641e6d7278bc')
    #print(rep)

    #print("document")
    #print(rep2)


    #urk_data = get_document_by_url('auditors/_doc/K8S.Falco_vpc-0f31d867')
    #data = get_audit_report("vpc-test-s3", "AWS.SecMonk")
    #data = get_all_documents('policy_templates', raw_data = True)

    #query_dict = {"parent": "topLevel", "text": "Security Configurations"}
    #get_search_results('components', query_dict)
    
    if check_index_exists('components') == False:
        data = None
#        with open('/home/ubuntu/scrm_git/SCRM/util/components.json') as f:
        with open('PROJ_PATH/SCRM/util/components.json') as f:
            data = json.load(f)

        for d in data['components']:
            post_request('components', json.dumps(d), identity=d['id'])    


    #all_data =  get_all_documents_in_array('components')
    #all_data = check_index_exists('policy_templatesw')
    #print(all_data)
    #print(json.dumps(all_data))



    '''query_dict_parent = {"parent": "topLevel", "text": "AAASecurity Configurations44"}
    search_data_parent = json.loads(get_search_results('components', query_dict_parent))
    print("---PARENT----")
    print(search_data_parent)

    parent = search_data_parent['hits']['hits'][0]['_source']
    print(parent)'''

    '''print("---CHILDREN---")
    query_dict_children = {"parent": parent['id']}
    search_data_children = get_search_results_in_array('components', query_dict_children)
    print(json.dumps(search_data_children))'''

    #delete_document('components', '2')
    #auditor_yaml = base64.b64decode(res['_source']['blob']).decode('ascii')

    '''max_child_id = 0
    for child in search_data_children:
        print(child['id'].rsplit(".",1)[1])
        child_id = int(child['id'].split(".",1)[1])
        print("child id - " + str(child_id))
        if child_id > max_child_id:
            max_child_id = child_id

        print("max_child_id - " + str(max_child_id))

    input_data = {}
    input_data['text'] = "VPC Control"
    input_data['description']  = "VPC Control"
    input_data['type'] = 'level2'
    input_data['parent'] = parent['id']
    input_data['nodeType'] = parent['text']
    input_data['id'] = parent['id'] + '.' + str(max_child_id + 1)

    post_request('components', json.dumps(input_data), identity=input_data['id'])'''
 
    '''properties = {"name" : {"type" : "text"}, "blob" : {"type" : "binary"}}
    index = 'falco'
    result = create_index_with_properties(index, properties)'''

    query_dict = {"name" : "test AND scf AND 1"}
    result = search_index_using_querystring('temp', query_dict)
    #result = get_document_by_id('temp', "test%2Fscf")
    print(result)
 
    

