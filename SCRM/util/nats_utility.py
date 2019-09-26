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
import sys
from nats.aio.client import Client as NATS
from nats.aio.errors import ErrConnectionClosed, ErrTimeout, ErrNoServers






class NATSservice:

    @staticmethod
    def send_request(queue_name, data):

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response = loop.run_until_complete(NATSservice.publish(loop, queue_name, data))
            loop.close()
            return response
        except Exception as e:
            print("---------EXCEPTION in NATS event loop----------------    %s\n" % e)



    @staticmethod
    def publish(loop, queue_name, data):

        nc = NATS()
        yield from nc.connect(servers=["nats://127.0.0.1:4222"], io_loop=loop)
        print("&&&&&&&&&&&&&&&&&&&&&&&&&&& connection established &&&&&&&&&&&&&&&&&&&&&&&")
        response = yield from nc.request(queue_name, bytes(data, 'utf-8'), 15)
        #print("****************response*****************", response.data.decode())
        yield from nc.close()
        return response.data.decode()

