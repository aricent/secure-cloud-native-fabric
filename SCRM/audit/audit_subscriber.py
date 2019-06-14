import sys
import tornado.ioloop
import tornado.gen
import time
from nats.io.client import Client as NATS


@tornado.gen.coroutine
def main():
    nc = NATS()
    yield nc.connect("nats://127.0.0.1:4222")
    exitCondition = None

    @tornado.gen.coroutine
    def help_request_handler(msg):
        subject = msg.subject
        data = msg.data
        print("[Received on '{}'] : {}".format(subject, data.decode()))
        yield nc.publish(msg.reply, b'OK, I will help!')

    try: 
        yield nc.subscribe('agent_aws_1', "workers", help_request_handler)
    except Exception as e:
        print("!!! Exception : {}".format(e))
        exitCondition = True
    while not exitCondition:
        yield tornado.gen.sleep(60)



if __name__ == '__main__':
    tornado.ioloop.IOLoop.current().run_sync(main)
    #spawn_callback(main)
    
