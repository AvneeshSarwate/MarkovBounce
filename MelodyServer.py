'''
Created on Dec 26, 2013

@author: avneeshsarwate
'''

import random
import OSC

class MelodyServer(object):
    '''
    classdocs
    '''


    def __init__(self, voiceFile, keyFile, computerNames):
        '''
        Constructor
        '''
        self.markovChain = []
        self.addresses = open(computerNames).read().split("/n")
        self.markovAddress = 0
        self.pianoAddresses = {}
        self.keyToNote = open(keyFile).read().split("/n")
        self.progInd = 0
        self.voiceInd = 0
        self.stateInd = 0
        
        self.oscLANdiniClient = OSC.OSCClient()
        self.oscLANdiniClient.connect(("127.0.0.1", 50506))
        
        fileStr = open(voiceFile)
        lines = fileStr.split("/n")
        self.voiceInd = int(lines[0])
        nStates = int(lines[1])
        
        for i in range(nStates):
            self.markovChain.append([float(k) for k in lines[3+i].split(" ")])
        
        self.markovChain = self.normalize(self.markovChain)
        
        for i in range(nStates):
            for j in range(1, nStates):
                self.markovChain[i][j] += self.markovChain[i][j-1]
                #this summing makes it faster to select a random state
                #could see if there is a function in random.py to do this
        
    
    def normalize(self, grid):
        for i in range(len(grid)):
            grid[i] = [(1.0*grid[i][j])/sum(grid[i]) for j in grid[i]]
        return grid    
    
    def randomMarkovStep(self):
        r = random.uniform(0, 1)
        ind = 0
        for i in range(len(self.markovChain)):
            if r < self.markovChain[self.stateInd][i]:
                ind = i
        return ind
    
    def stepper(self, addr, tags, stuff, source):
        if self.progInd == 15:
            self.stateInd = self.randomMarkovStep()
            self.markovAddress = self.addresses[random.randrange(len(self.addresses))]
           
            #send the stuff
            msg = OSC.OSCMessage()
            msg.address("send/GD")
            msg.append(self.markovAddress)
            msg.append("/markovStep")
            msg.append(self.voiceInd)
            msg.append(self.stateInd)
            
            
            
            
    
    def markovButton(self, addr, tags, stuff, source):
        self.stateInd = int(addr.split("/")[2]) #address is /name/col/row and want col
        
        #send it over
        msg = OSC.OSCMessage()
        msg.address("send/GD")
        msg.append(self.markovAddress)
        msg.append("/markovButton")
        msg.append(self.stateInd)
        
    def pianoButton(self, addr, tags, stuff, source):
        keyInd = int(addr.split("/")[2])-1
        if stuff[0] == 1:
            self.pianoAddresses[keyInd] = self.addresses[random.randrange(len(self.addresses))]
            
            #send stuff
            msg = OSC.OSCMessage()
            msg.address("send/GD")
            msg.append(self.pianoAddresses[keyInd])
            msg.append("/pianoButton")
            msg.append(self.keyToNote[keyInd])
            msg.append("ON")
            msg.append(2+self.voiceInd)
        else:
            #send stuff
            msg = OSC.OSCMessage()
            msg.address("send/GD")
            msg.append(self.pianoAddresses[keyInd])
            msg.append("/pianoButton")
            msg.append(self.keyToNote[keyInd])
            msg.append("OFF")
            msg.append(2+self.voiceInd)
            
            self.pianoAddresses.remove(keyInd)
        
        
        
        
        