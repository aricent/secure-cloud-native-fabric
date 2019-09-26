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
import os
import sys
import logging
from logging import config
import yaml
import configparser


with open("conf.yaml") as file:
    config_param = yaml.load(file, Loader=yaml.FullLoader)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config = configparser.ConfigParser()
config.optionxform =str
config.read(os.path.join(BASE_DIR, 'config.ini'))

RUNNING_PUBLIC_CLOUD_LIST =[]
RUNNING_PRIVATE_CLOUD_LIST =[]
awsFlag=gcpFlag=kubernetesFlag=0
for each_section in config.sections():
    if "Common_Param" in each_section:
        for (key, val) in config.items(each_section):
            if key == "DB_PATH":
                DB_PATH = val
            if key == "LOG_FILE":
                config_param['LOGGING']['handlers']['file']['filename'] = val
    if "CloudInterfce_" in each_section:
        tmp_dict={}
        tmp_dict={'cat':'','type':'','name':''}
        for (key,val) in config.items(each_section):
            if key== "CloudCat":
                tmp_dict['cat']=val
            elif key == "CloudType":
                tmp_dict['type'] = val
            elif key == "CloudName":
                tmp_dict['name'] = val
            else:
                tmp_dict[key] = val

        if(tmp_dict['cat'] == "PUBLIC"):
            RUNNING_PUBLIC_CLOUD_LIST.append(tmp_dict)
        elif(tmp_dict['cat'] == "PRIVATE"):
            RUNNING_PRIVATE_CLOUD_LIST.append(tmp_dict)

class CloudConfig:
    
    cloud = dict()
    dirPath = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    def populateConfig():

        clconfig = configparser.ConfigParser()
        clconfig.optionxform =str
        clconfig.read(os.path.join(CloudConfig.dirPath, 'config.ini'))
        #print("Config Path : %s" %(os.path.join(CloudConfig.dirPath, 'config.ini')))
        avlblClds = []
        allClds = dict()
        for section in clconfig.sections():
            #print("Read section : %s" %(section))
            dictRepr = dict(clconfig.items(section))
            if "Organization" in section:
                #print("Split : %s" %(dictRepr))
                avlblClds = dictRepr["Clouds"].split(',')
                #print("Found Clouds : %s"%(avlblClds))
            elif "CloudInterfce_" in section:
                allClds[section] = dictRepr
        #print("Clouds : %s" %(allClds))
        for cldIf in avlblClds:
            CloudConfig.cloud[allClds[cldIf]["Id"]] = allClds[cldIf]
        #print("Config : %s" %(CloudConfig.cloud))

CloudConfig.populateConfig()

logging.config.dictConfig(config_param['LOGGING'])
service_logger = logging.getLogger()
service_logger.setLevel(logging.CRITICAL)
sql_log_file=os.path.dirname(config_param['LOGGING']['handlers']['file']['filename'])+'/sql.log'
sql_logger = logging.getLogger('sqlalchemy')
sql_logger.propagate = False
sql_logger.addHandler(logging.FileHandler(sql_log_file))
sql_logger.setLevel(logging.ERROR)
CONFIG = {'AMQP_URI': config_param['AMQP_URI'] } # e.g. "pyamqp://guest:guest@localhost"


if __name__ == "__main__":
    import json
    print(json.dumps(CloudConfig.cloud))


