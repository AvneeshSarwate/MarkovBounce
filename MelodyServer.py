'''
Created on Dec 26, 2013

@author: avneeshsarwate
'''

import random
import OSC
import subprocess
import threading

class MelServer:
    '''
    classdocs
    '''


    def __init__(self, voiceFile, keyFile, computerNames):
        '''
        Constructor
        '''
        self.markovChain = []
        self.addresses = open(computerNames).read().split("\n")
        self.markovAddress = 0
        self.pianoAddresses = {}
        self.keyToNote = open(keyFile).read().split("\n")
        self.progInd = 0
        self.voiceInd = 0
        self.stateInd = 0
        
        numButtons = 8
        
        k = subprocess.check_output(["ifconfig | grep \"inet \" | grep -v 127.0.0.1"], shell=True)
        ip = k.split(" ")[1]
        selfIP = ip
        self.oscServUI = OSC.OSCServer((selfIP, 8000))        
        
        self.oscLANdiniClient = OSC.OSCClient()
        self.oscLANdiniClient.connect(("127.0.0.1", 50506))
        
        #self.oscServSelf = oscServer
#        self.oscServSelf = OSC.OSCServer(("127.0.0.1", 50505)) #LANdini 50505, 5174 chuck
#        self.oscServSelf.addDefaultHandlers()
#        self.oscServSelf.addMsgHandler("/played", self.stepper)
#        self.oscServSelf.addMsgHandler("/played", self.doublehandler)
        for i in range(8):
            self.oscServUI.addMsgHandler("/markovButton/" + str(i+1) + "/1", self.markovButton)
        for i in range(8):
            self.oscServUI.addMsgHandler("/pianoButton/" + str(i+1) + "/1", self.pianoButton)
        
        
        fileStr = open(voiceFile).read()
        lines = fileStr.split("\n")
        self.voiceInd = int(lines[0])
        nStates = int(lines[1])
        
        for i in range(nStates):
            self.markovChain.append([float(k) for k in lines[3+i].split(" ")])
        
        self.markovChain = self.normalize(self.markovChain)
        print self.markovChain
        
        for i in range(nStates):
            for j in range(1, nStates):
                self.markovChain[i][j] += self.markovChain[i][j-1]
                #this summing makes it faster to select a random state
                #could see if there is a function in random.py to do this
        print
        print self.markovChain
        
    
    def normalize(self, grid):
        for i in range(len(grid)):
            grid[i] = [(1.0*grid[i][j])/sum(grid[i]) for j in range(len(grid[i]))]
        return grid    
    
    def randomMarkovStep(self):
        r = random.uniform(0, 1)
        #print "                r", r, "     state", self.stateInd, "      dist", self.markovChain[self.stateInd]
        ind = 0
        for i in range(len(self.markovChain)):
            if r < self.markovChain[self.stateInd][i]:
                ind = i
                break
        return ind
    
    def doublehandler(self, addr, tags, stuff, source):
        print "double working"
    
    def stepper(self, addr, tags, stuff, source):
        
        if self.progInd == 15:
            self.stateInd = self.randomMarkovStep()
            self.markovAddress = self.addresses[random.randrange(len(self.addresses))]
            print "       ", self.stateInd, self.markovAddress
            #send the stuff
            msg = OSC.OSCMessage()
            msg.setAddress("/send/GD")
            msg.append(self.markovAddress)
            msg.append("/markovStep")
            msg.append(self.voiceInd)
            msg.append(self.stateInd)
            self.oscLANdiniClient.send(msg)
        else:
            print self.progInd
        
        self.progInd = (self.progInd+1) % 16
            
            
            
            
    
    def markovButton(self, addr, tags, stuff, source):
        if stuff[0] == 0: return
        self.stateInd = int(addr.split("/")[2])-1 #address is /name/col/row and want col
        print "    MARKOV", self.stateInd, self.markovAddress
        
        #send it over
        msg = OSC.OSCMessage()
        msg.setAddress("/send/GD")
        msg.append(self.markovAddress)
        msg.append("/markovButton")
        msg.append(self.stateInd)
        self.oscLANdiniClient.send(msg)
        
    def pianoButton(self, addr, tags, stuff, source):
        keyInd = int(addr.split("/")[2])-1
        print "    PIANO", keyInd
        if stuff[0] == 1:
            self.pianoAddresses[keyInd] = self.addresses[random.randrange(len(self.addresses))]
            
            #send stuff
            msg = OSC.OSCMessage()
            msg.setAddress("/send/GD")
            msg.append("all")#self.pianoAddresses[keyInd])
            msg.append("/pianoButton")
            msg.append(self.keyToNote[keyInd])
            msg.append("on")
            msg.append(self.voiceInd)
            self.oscLANdiniClient.send(msg)
        else:
            #send stuff
            msg = OSC.OSCMessage()
            msg.setAddress("/send/GD")
            msg.append("all")#self.pianoAddresses[keyInd])
            msg.append("/pianoButton")
            msg.append(self.keyToNote[keyInd])
            msg.append("off")
            msg.append(self.voiceInd)
            self.oscLANdiniClient.send(msg)
            
            self.pianoAddresses.pop(keyInd)
    
    def playStart(self):
        self.audioThread = threading.Thread(target=self.oscServSelf.serve_forever)
        self.audioThread.start()
    
    def uiStart(self):
        self.uiThread = threading.Thread(target=self.oscServUI.serve_forever)
        self.uiThread.start()
    
    def setSelfServer(self, server):
        self.oscServSelf = server
    
    def loopStart(self):
        try :
            #print "starting loop"
            while 1 :
                continue

        except KeyboardInterrupt :
            #print "\nClosing oscServSelf."
            self.oscServSelf.close()
            self.oscServUI.close()
            #print "Waiting for Server-thread to finish"
            if self.audioThread != 0:
                self.audioThread.join() ##!!!
            if self.uiThread != 0:
                self.uiThread.join() ##!!!
            #self.chuckThread.join()
            #print "Done"      
        
        
#server = MelServer("testvoice1.txt", "keyfile1.txt", "computernames.txt")
#server.playStart()
#server.uiStart()
#server.loopStart()
        
        