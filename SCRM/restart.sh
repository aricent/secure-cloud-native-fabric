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
#!/bin/bash
service neo4j stop
rm -rf /var/lib/neo4j/data/databases/graph.db
curl -X DELETE "localhost:9200/securityposture"
curl -X DELETE "localhost:9200/agents"
curl -X DELETE "localhost:9200/auditors"
curl -X DELETE "localhost:9200/auditor_cluster_registry"
curl -X DELETE "localhost:9200/audit_reports"
curl -X DELETE "localhost:9200/_all"
service neo4j start
chmod -R 777  /var/lib/neo4j/data/databases/
sleep 10
neomodel_install_labels util/gphmodels.py --db "bolt://neo4j:neo4j@SCF_IP:7687"
supervisorctl restart all
