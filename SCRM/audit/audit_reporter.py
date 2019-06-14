import asyncio
import yaml
import sys
import ast
import json
import requests
from nats.aio.client import Client as NATS
from nats.aio.errors import ErrConnectionClosed, ErrTimeout, ErrNoServers
sys.path.append('./util')
from elastic_search_client import get_request, post_request, post_request_ver2



class AuditReporter(object):

    def run_reporter(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.run(loop, 'audit_result_queue'))
        #loop.close()
        loop.run_forever()


    def run(self, loop, queue_name):
        nc = NATS()
        yield from nc.connect(servers=["nats://SCF_IP:4222"], io_loop=loop)

        @asyncio.coroutine
        def message_handler(msg):
            subject = msg.subject
            reply = msg.reply
            data = msg.data.decode()
            print("Received a message on message_handler'{subject} {reply}': {data}".format(
                subject=subject, reply=reply, data=data))
            print("\n\ntype of data {}".format(str(type(data))))
            #yield from nc.publish(reply, bytes('I can help', 'utf-8'))
              
            report = json.loads(data)

            metadata = dict()
            metadata.update({'auditor_type' : report['auditor_type'] })
            metadata.update({'cluster' : report['cluster']})
            post_request_ver2('audit_reports', json.dumps(report), None, metadata)

            print("************* data saved ************** ")



        yield from nc.subscribe(queue_name,'workers' ,message_handler)



        #yield from nc.subscribe(queue_name, "workers", message_handler)
        #yield from asyncio.sleep(60, loop=loop)
        #yield from nc.close()







if __name__ == "__main__":
    rac = AuditReporter()
    rac.run_reporter()


