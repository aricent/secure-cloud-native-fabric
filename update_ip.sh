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
old_ip=SCF_IP
new_ip=`/sbin/ifconfig eth0 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}'`
new_path="$PWD"
old_path="PROJ_PATH"

find ./scf_agent -type f -exec sed -i -e "s/$old_ip/$new_ip/g" {} \;
find ./SCRM -type f -exec sed -i -e "s/$old_ip/$new_ip/g" {} \;
find ./extra -type f -exec sed -i -e "s/$old_ip/$new_ip/g" {} \;

sed -i "s~$old_path~$new_path~g" SCRM/util/elastic_search_client.py;
sed -i "s~$old_path~$new_path~g" SCRM/audit/auditor_service.py;
#find ./SecurityControllerFabric -type f -exec sed -i -e "s/$old_ip/$new_ip/g" {} \;
#find ./static/assets -type f -exec sed -i -e "s/$old_ip/$new_ip/g" {} \;
#find ./update_ip.sh -type f -exec sed -i -e "s/$old_ip/$new_ip/g" {} \;
#find ./templates -type f -exec sed -i -e "s/$old_ip/$new_ip/g" {} \;
