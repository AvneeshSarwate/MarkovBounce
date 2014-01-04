'''
Created on Dec 26, 2013

@author: avneeshsarwate
'''
import phrase
import OSC
import MultiLoop2
import threading

class MelClient:
    '''
    classdocs
    '''


    def __init__(self, voiceList): #list of names of markov files
        '''
        Constructor
        '''
        
        self.progInd = 0
        self.voiceInd = {}
        self.stateInd = {}
        self.playing = False
        
        self.voiceIndBackup = {}
        self.stateIndBackup = {}
        self.playingBackup = False
        
        lenKeys = 8
        
        fileStrings = []
        for i in range(len(voiceList)):
            fileStrings.append(open(voiceList[i]).read())
        
        m = MultiLoop2.MultiLoop
        
        print fileStrings[0].split("\n")
        
        self.voices = []
        for i in range(len(voiceList)):
            self.voices.append([])
            nStates = int(fileStrings[i].split("\n")[1])
            for j in range(nStates):
                miniStateFile = fileStrings[i].split("\n")[2].split(" ")[j]
                print miniStateFile
                grid, scale, root, colsub = m.stringToMiniState(open(miniStateFile).read())
                self.voices[i].append(m.gridToProg(grid, scale, root))
        
            
        #code to populate voices
        
        #code to set up handlers
    
    def realPlay(self, addr, tags, stuff, source):
        print "               played"
        if stuff[0] == 0:#self.progInd==0 and self.playingBackup:
            self.playing = self.playingBackup
            self.stateInd = self.stateIndBackup
            self.voiceInd = self.voiceIndBackup
            self.playingBackup = False
            
        for k in self.stateInd.keys():
            c = self.voices[k][self.stateInd[k]].c[stuff[0]]
            print "              ", k, c
            phrase.play(c, channel=k)
        if stuff[0] == 15:
            self.stateInd.clear()
            self.playing = False
    
    def startVoice(self, addr, tags, stuff, source):
        print "voice start      ", "channel", stuff[0], "     state", stuff[1]
        self.voiceIndBackup = stuff[0]
        self.stateIndBackup[stuff[0]] = stuff[1]
        self.playingBackup = True
        
    def changeState(self,addr, tags, stuff, source):
        self.stateInd = stuff[0]
    
    def pianoKey(self,addr, tags, stuff, source):
        print "                           ",stuff
        c = phrase.Chord()
        c.append(stuff[0])
        phrase.play(c, channel=stuff[2], toggle=stuff[1])
    
    def playStart(self):
        self.audioThread = threading.Thread(target=self.oscServSelf.serve_forever)
        self.audioThread.start()
    
    def setSelfServer(self, server):
        self.oscServSelf = server
        self.oscServSelf.addMsgHandler("/markovStep", self.startVoice)
        self.oscServSelf.addMsgHandler("/markovButton", self.changeState)
        self.oscServSelf.addMsgHandler("/pianoButton", self.pianoKey)
    
    def loopStart(self):
        try :
            #print "starting loop"
            while 1 :
                continue

        except KeyboardInterrupt :
            #print "\nClosing oscServSelf."
            self.oscServSelf.close()
            #print "Waiting for Server-thread to finish"
            if self.audioThread != 0:
                self.audioThread.join() ##!!!

#client = MelClient(["testvoice1.txt", "testvoice2.txt"])
#client.playStart()
#client.loopStart()