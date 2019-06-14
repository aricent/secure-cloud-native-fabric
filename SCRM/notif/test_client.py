import asyncio
from nats.aio.client import Client as NATS
from nats.aio.errors import ErrConnectionClosed, ErrTimeout, ErrNoServers

def run(loop):
    nc = NATS()

    yield from nc.connect(servers=["nats://127.0.0.1:4222"], io_loop=loop)

    #yield from nc.publish("k8s.events", b'[{"cloudType":"K8s","action":"Item Created", "text":"Event from K8S"}]')
    yield from nc.publish("aws.events", b'[{"cloudType":"AWS","action":"Item Created", "text":"Event from AWS"}]')
    #yield from nc.publish("k8s.alarms", b'Alarm from K8S')
    #yield from nc.publish("aws.alarms", b'Alarm from AWS')

    yield from nc.close()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))
    loop.close()
