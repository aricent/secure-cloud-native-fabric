#!/usr/bin/python
import os
from kubernetes import client, config, watch
import logging
import os

fname = "/var/log/kubewatch_out.log"
def logger_info(log_str):
    if os.path.isfile(fname):
        with open(fname, "a+") as in_file:
            in_file.write("\n")
            in_file.write(log_str)
    else:
        with open(fname, "w+") as in_file:
            in_file.write(log_str)

config.load_kube_config('/etc/kubernetes/admin.conf')

v1 = client.CoreV1Api()

pod_list = v1.list_namespaced_pod("default")
for pod in pod_list.items:
    logger_info("%s\t%s\t%s" % (pod.metadata.name,
                          pod.status.phase,
                          pod.status.pod_ip))


stream = watch.Watch().stream(v1.list_namespaced_pod, "default")
for event in stream:
#    print("Event: %s %s" % (event['type'], event['object'].metadata.name))
     logger_info(
          "|action={}| "
          "|region={}| "
          "|resource={}| "
          "|name=\"{}\"|".format(
               event['type'],
               event['object'].spec.node_name,
               event['object'].spec.service_account_name,
               event['object'].metadata.name))

