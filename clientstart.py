'''
Created on Jan 3, 2014

@author: avneeshsarwate
'''

import MelodyClient
import OSC
import threading

oscServSelf = OSC.OSCServer(("127.0.0.1", 50505)) #LANdini 50505, 5174 chuck
oscServSelf.addDefaultHandlers()

client = MelodyClient.MelClient(["testvoice1.txt", "testvoice2.txt"])

def blank(*args):
    return

oscServSelf.addMsgHandler("/played", client.realPlay)
oscServSelf.addMsgHandler('/landini/member/reply', blank)

client.setSelfServer(oscServSelf)

audioThread = threading.Thread(target=oscServSelf.serve_forever)
audioThread.start()

try :
    #print "starting loop"
    while 1 :
        continue

except KeyboardInterrupt :
    #print "\nClosing oscServSelf."
    oscServSelf.close()
    #print "Waiting for Server-thread to finish"
    if audioThread != 0:
        audioThread.join() ##!!!