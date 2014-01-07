'''
Created on Dec 30, 2013

@author: avneeshsarwate
'''
import MelodyServer
import MelodyClient
import OSC
import threading


oscServSelf = OSC.OSCServer(("127.0.0.1", 50505)) #LANdini 50505, 5174 chuck
oscServSelf.addDefaultHandlers()


server = MelodyServer.MelServer("testvoice2.txt", "keyfile1.txt", "testaddrs.txt")


client = MelodyClient.MelClient(["testvoice1.txt", "testvoice2.txt"])

def doublePlay(addr, tags, stuff, source):
    client.realPlay(addr, tags, stuff, source)
    server.stepper(addr, tags, stuff, source)
    
def blank(*args):
    return

oscServSelf.addMsgHandler("/played", doublePlay)
oscServSelf.addMsgHandler('/landini/member/reply', blank)

client.setSelfServer(oscServSelf)
server.setSelfServer(oscServSelf)
server.uiStart()

audioThread = threading.Thread(target=oscServSelf.serve_forever)
audioThread.start()

try :
    #print "starting loop"
    while 1 :
        continue

except KeyboardInterrupt :
    #print "\nClosing oscServSelf."
    oscServSelf.close()
    server.oscServUI.close()
    #print "Waiting for Server-thread to finish"
    if audioThread != 0:
        audioThread.join() ##!!!
    if server.uiThread != 0:
        server.uiThread.join() ##!!!
    #self.chuckThread.join()
    #print "Done"      
