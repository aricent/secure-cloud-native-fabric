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
    
