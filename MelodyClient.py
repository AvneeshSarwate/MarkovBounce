'''
Created on Dec 26, 2013

@author: avneeshsarwate
'''
import phrase
import OSC
import MultiLoop2

class MelodyClient(object):
    '''
    classdocs
    '''


    def __init__(self, voiceList): #list of names of markov files
        '''
        Constructor
        '''
        
        self.progInd = 0
        self.voiceInd = 0
        self.stateInd = 0
        self.playing = False
        
        self.voiceIndBackup = 0
        self.stateIndBackup = 0
        self.playingBackup = False
        
        lenKeys = 8
        
        fileStrings = []
        for i in range(len(voiceList)):
            fileStrings.append(open(voiceList[i]).read())
        
        m = MultiLoop2.MultiLoop()
        
        self.voices = []
        for i in range(len(voiceList)):
            self.voices.append([])
            nStates = int(fileStrings.split("/n")[1])
            for j in range(nStates):
                miniStateFile = fileStrings[i].split("/n")[2].split(" ")[j]
                grid, scale, root, colsub = m.stringToMiniState(open(miniStateFile).read())
                self.voices[i].append(m.gridToProg(grid, scale, root))
            
        self.oscServSelf = OSC.OSCServer(("127.0.0.1", 50505))
        
        self.oscServSelf.addMsgHandler("/played", self.realPlay)
        self.oscServSelf.addMsgHandler("/markovStep", self.startVoice)
        self.oscServSelf.addMsgHandler("/markovButton", self.changeState)
        self.oscServSelf.addMsgHandler("/pianoStep", self.pianoKey)
            
        #code to populate voices
        
        #code to set up handlers
    
    
    
    def realPlay(self, *args):
        if self.progInd==0 and self.playingBackup:
            self.playing = self.playingBackup
            self.stateInd = self.stateIndBackup
            self.voiceInd = self.voiceIndBackup
            self.playingBackup = False
            
        if self.playing:
            phrase.play(self.voices[self.voiceInd][self.stateInd][self.progInd], self.voiceInd)
            self.progInd += 1
            self.progInd %= 16
            if self.progInd == 0:
                self.playing = False
    
    def startVoice(self,addr, tags, stuff, source):
        self.voiceIndBackup = stuff[0]
        self.stateIndBackup = stuff[1]
        self.playingBacukup = True
        
    def changeState(self,addr, tags, stuff, source):
        self.stateInd = stuff[0]
    
    def pianoKey(self,addr, tags, stuff, source):
        c = phrase.Chord()
        c.append(stuff[0])
        phrase.play(c, channel=stuff[2], toggle=stuff[1])
    