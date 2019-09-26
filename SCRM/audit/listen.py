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
import asyncio
import yaml
import sys
from nats.aio.client import Client as NATS
from nats.aio.errors import ErrConnectionClosed, ErrTimeout, ErrNoServers




class AuditSubscriber(object):

    def run_subscriber(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.run(loop, 'agent_aws_1'))
        #loop.close()
        loop.run_forever()


    def run(self, loop, queue_name):
        nc = NATS()
        yield from nc.connect(servers=["nats://127.0.0.1:4222"], io_loop=loop)

        @asyncio.coroutine
        def message_handler(msg):
            subject = msg.subject
            reply = msg.reply
            data = msg.data.decode()
            print("Received a message on message_handler'{subject} {reply}': {data}".format(
                subject=subject, reply=reply, data=data))
            yield from nc.publish(reply, bytes('I can help', 'utf-8'))
        

        yield from nc.subscribe(queue_name, "workers", message_handler)
        #yield from asyncio.sleep(60, loop=loop)
        #yield from nc.close()







if __name__ == "__main__":
    rac = AuditSubscriber()
    rac.run_subscriber()
