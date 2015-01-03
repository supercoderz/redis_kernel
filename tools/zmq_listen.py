from __future__ import print_function
from zmqwrapper import *
import sys

def print_message(topic,message):
    print(message)

def get_data(host,port):
    #create the subscriber
    s=subscriber("tcp://%s:%s"%(host,port),[u''],print_message,STRING)
    #and start it so that we can process the messages
    s.start()
    
if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('Usage: python zmq_listen host port')
    else:
        try:
            get_data(sys.argv[1],sys.argv[2])
        except:
            pass
