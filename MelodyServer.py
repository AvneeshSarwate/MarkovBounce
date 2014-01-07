'''
Created on Dec 26, 2013

@author: avneeshsarwate
'''

import random
import OSC
import subprocess
import threading
import copy

class MelServer:
    '''
    classdocs
    '''


    def __init__(self, voiceFile, keyFile, computerNames):
        '''
        Constructor
        '''
        self.markovChain = []
        self.addresses = [] # open(computerNames).read().split("\n") #make set?
        self.markovAddress = 0
        self.pianoAddresses = {}
        self.keyToNote = open(keyFile).read().split("\n")
        self.progInd = 0
        self.voiceInd = 0
        self.stateInd = 0
        self.playDecider = {}
        
        compNameFile = open("selfcomp.txt")
        oldCompName = compNameFile.read().strip("\n")
        compNameFile.close()
        compRead = raw_input("\n\nIs the name of your computer " + oldCompName +"?" +
                           "\n If so, hit enter. If not, type it in below:\n")
        if(compRead == ""): self.myAddress = oldCompName
        else:
            self.myAddress = compRead
            compNameFile = open("selfcomp.txt", "w")
            compNameFile.write(compRead)
            compNameFile.close()
            
        self.addresses.append(self.myAddress)
        
        self.priority = self.addresses.index(self.myAddress)
        
        self.numVoices = 3
        
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
        
    def userNamesCallback(self, addr, tags, stuff, source):
        print "            addresses", stuff
        self.addresses = stuff + self.addresses
    
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
        if stuff[0] == 14:
            self.addrPropose()
        if stuff[0] == 15:
            self.stateInd = self.randomMarkovStep()
#            self.markovAddress = self.addresses[random.randrange(len(self.addresses))]
            #  = random.sample(self.addresses.difference(self.playingset), 1)[0]
            
            
            #print "                    progInd", stuff[0], "state: ", self.stateInd, self.markovAddress
            #send the stuff
            msg = OSC.OSCMessage()
            msg.setAddress("/send/GD")
            msg.append(self.markovAddress)
            msg.append("/markovStep")
            msg.append(self.voiceInd)
            msg.append(self.stateInd)
            self.oscLANdiniClient.send(msg)
        else:
            if stuff[0] == 8:
                print self.progInd
        
        self.progInd = (self.progInd+1) % 16
            
            
    def addrPropose(self):
        propList = random.sample(self.addresses, self.numVoices)
        self.playDecider[self.priority] = propList #shouldn't cause problems even if sending to "all"
        #print self.priority, propList, 'pre'
        j = 1
        #print len(propList)
        #testing of address picker
#        for i in range(self.numVoices-1):
#            j += 1
#            stuff = []
#            stuff.append(";".join(random.sample(self.addresses, self.numVoices)))
#            stuff.append(i+3)
#            print stuff[1], stuff[0].split(";"), "pre"
#            if j == 3: print "              sanity check", j
#            self.addrRecv("a", "b", stuff, "c") 
        propString = ";".join(propList)
        msg = OSC.OSCMessage()
        msg.setAddress("/send/GD")
        msg.append("all") #is not working for "allButMe"
        msg.append("/addrProp")
        msg.append(propString)
        msg.append(self.priority)
        self.oscLANdiniClient.send(msg)
    
    def addrRecv(self, addr, tags, stuff, source):
        
        propList = stuff[0].split(";")
        priority = stuff[1]
        self.playDecider[priority] = propList
        
        print source, len(self.playDecider)
        
        if len(self.playDecider) == self.numVoices:
            #print "         len(playDecider) = ", len(self.playDecider)
            priList = sorted(self.playDecider.keys())
            #for i in sorted(self.playDecider.keys()):
                #print i, self.playDecider[i]
            priInds = [0] * self.numVoices
            for i in range(self.numVoices):
                for j in range(i+1, self.numVoices):
                    if self.playDecider[priList[i]][0] in self.playDecider[priList[j]]:
                        self.playDecider[priList[j]].remove(self.playDecider[priList[i]][0])
            
            print [self.playDecider[priList[i]][0] for i in range(self.numVoices)], "\n\n\n"    
            self.markovAddress = self.playDecider[self.priority][0]
            self.playDecider.clear()
            #print self.markovAddress
        
            
    
    def markovButton(self, addr, tags, stuff, source):
        if stuff[0] == 0: return
        self.stateInd = int(addr.split("/")[2])-1 #address is /name/col/row and want col
        print "    MARKOV", self.stateInd, self.markovAddress
        
        #send it over
        msg = OSC.OSCMessage()
        msg.setAddress("/send/GD")
        msg.append(self.markovAddress)
        msg.append("/markovButton")
        msg.append(self.voiceInd)
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
        self.oscServSelf.addMsgHandler("/addrProp", self.addrRecv)
        self.oscServSelf.addMsgHandler("/landini/userNames", self.userNamesCallback)
        msg = OSC.OSCMessage()
        msg.setAddress("/userNames")
        msg.append("please")
        self.oscLANdiniClient.send(msg)
    
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
        
        