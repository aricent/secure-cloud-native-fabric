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

