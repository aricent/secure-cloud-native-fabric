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
