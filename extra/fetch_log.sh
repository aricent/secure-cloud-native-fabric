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
#!/bin/sh
SM_AUTH_FILE_NAME=SM_Key_1.pem
K8S_AUTH_FILE_NAME=SM_Key_1.pem
SM_IP=18.218.26.245
K8S_IP=52.15.107.108
SM_LOG_FILE=/var/log/security_monkey/sample_alerter.log
K8S_LOG_FILE=/var/log/kubewatch_out.log
#rsysnc -av --remove-source-files -e "ssh -i $SM_AUTH_FILE_NAME" ubuntu@$SM_IP:$SM_LOG_FILE .
#rsync -av --remove-source-files -e "ssh -i $K8S_AUTH_FILE_NAME" ubuntu@$K8S_IP:$K8S_LOG_FILE .
while true; do
    rsysnc -av --remove-source-files -e "ssh -i $SM_AUTH_FILE_NAME" --rsync-path="sudo rsync" ubuntu@$SM_IP:$SM_LOG_FILE ../nameko_service/.
    rsync -av --remove-source-files -e "ssh -i $K8S_AUTH_FILE_NAME" --rsync-path="sudo rsync" ubuntu@$K8S_IP:$K8S_LOG_FILE ../nameko_service/.
    sleep 5
done
