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
