'''
Created on Dec 26, 2013

@author: avneeshsarwate
'''
import phrase
import OSC
import MultiLoop2
import threading
import copy
import random

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
        
        self.lenKeys = lenKeys
        
        fileStrings = []
        for i in range(len(voiceList)):
            fileStrings.append(open(voiceList[i]).read())
        
        m = MultiLoop2.MultiLoop
        self.m = m
        
        self.trans = [self.naiveNoise, self.smartNoise, self.simplify, self.gameOfLife]
        
        print fileStrings[0].split("\n")
        
        self.voices = []
        self.grids = []
        self.scales = []
        self.roots = []
        
        self.origVoices = []
        self.origGrids = []
        self.origScales = []
        self.origRoots = []
        
        for i in range(len(voiceList)):
            self.voices.append([])
            self.grids.append([])
            self.scales.append([])
            self.roots.append([])
            nStates = int(fileStrings[i].split("\n")[1])
            for j in range(nStates):
                miniStateFile = voiceList[i].split("/")[0] + "/" + fileStrings[i].split("\n")[2].split(" ")[j]
                print miniStateFile
                grid, scale, root, colsub = m.stringToMiniState(open(miniStateFile).read())
                self.voices[i].append(m.gridToProg(grid, scale, root))
                self.grids[i].append(grid)
                self.scales[i].append(scale)
                self.roots[i].append(root)
        
        self.origVoices = copy.deepcopy(self.voices)
        self.origGrids = copy.deepcopy(self.grids)
        self.origScales = copy.deepcopy(self.scales)
        self.origRoots = copy.deepcopy(self.roots)
        
            
        #code to populate voices
        
        #code to set up handlers
    
    def realPlay(self, addr, tags, stuff, source):
        #print "               played"
        self.progInd = stuff[0] 
        if stuff[0] == 0:#self.progInd==0 and self.playingBackup:
            self.playing = self.playingBackup
            self.stateInd = self.stateIndBackup
            self.voiceInd = self.voiceIndBackup
            self.playingBackup = False
            
        for k in self.stateInd.keys():
            c = self.voices[k][self.stateInd[k]].c[stuff[0]]
            #print "              ", k, c, stuff[0] TODO: test
            phrase.play(c, channel=k)
        if stuff[0] == 15:
            self.stateInd.clear()
            self.playing = False
    
    def startVoice(self, addr, tags, stuff, source):
        print "voice start      ", "channel", stuff[0], "     state", stuff[1], "     progInd", self.progInd
        self.voiceIndBackup = stuff[0]
        self.stateIndBackup[stuff[0]] = stuff[1]
        self.playingBackup = True
        
    def changeState(self,addr, tags, stuff, source):
        self.stateInd[stuff[0]] = stuff[1]
            
    
    def pianoKey(self,addr, tags, stuff, source):
        print "                           ",stuff
        if stuff[1] == "off": return
        
        directions = ["up", "down", "right", "left"]
        
        
        
        if stuff[3]%2 == 0:
            print "shifting " + directions[int(stuff[3])/2]
            for i in range(self.lenKeys):
                self.grids[stuff[2]][i] = self.gridShift(self.grids[stuff[2]][i], directions[int(stuff[3])/2])
                self.voices[stuff[2]][i] = self.m.gridToProg(self.grids[stuff[2]][i], self.scales[stuff[2]][i], self.roots[stuff[2]][i])
        else:
            print "transformation ", int(stuff[3])/2
            for i in range(self.lenKeys):
                self.grids[stuff[2]][i] = self.trans[int(stuff[3])/2](self.grids[stuff[2]][i], random.randrange(5)+1)
                self.voices[stuff[2]][i] = self.m.gridToProg(self.grids[stuff[2]][i], self.scales[stuff[2]][i], self.roots[stuff[2]][i])
        
        if stuff[3] == 7:
            "RESTORED"
            self.voices = copy.deepcopy(self.origVoices)
            self.grids = copy.deepcopy(self.origGrids)
        
#        c = phrase.Chord()
#        c.append(stuff[0])
#        phrase.play(c, channel=stuff[2], toggle=stuff[1])
    
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
                
    def gridShift(self, g, direction):
        grid = copy.deepcopy(g)
        
        if direction == "up":
            print "up"
            for i in range(len(grid)):
                grid[i].insert(0, grid[i].pop())            
                    
        if direction == "down":
            for i in range(len(grid)):
                grid[i] = grid[i][1:len(grid[i])] + [grid[i][0]]
                    
        if direction == "right":
            grid.insert(0, grid.pop())
        
        if direction == "left": 
            grid = grid[1:len(grid)] + [grid[0]]
        
        return grid
    
    def naiveNoise(self, grid, lev):
        l = len(grid)
        p = 1.0 * lev / (l*l)
        newG = [[0 for i in range(l)] for k in range(l)]
        for i in range(l):
            for j in range(l):
                if random.uniform(0, 1) < p:
                    if grid[i][j] != 0:
                        newG[i][j] = 0
                    else: 
                        newG[i][j] = 1
                else: 
                    newG[i][j] = grid[i][j]
        return newG
    
    def smartNoise(self, grid, si):
        newgrid = [[0 for i in range(16)] for j in range (16)]
        vert = [i for i in range(1, 6)] + [i for i in range(-5, 0)]
        hor = [i for i in range(1, 4)] + [i for i in range(-3, 0)]
        v = random.choice(vert)
        h = random.choice(hor)
        for i in range(len(grid)):
            for j in range(len(grid)):
                if grid[i][j] != 0:
                    if random.uniform(0, 1) < (1.0 * si) / 20: #if any change happens
                        if random.uniform(0, 1) < .2: #probability of add/remove
                            if random.uniform(0, 1) < .5:
                                newgrid[i][j] = 0
                            else:
                                newgrid[(i+h)%len(grid)][(j+v)%len(grid)] = 1
                        else:
                            newgrid[i][(j+v)%len(grid)] = 1 
                    else:
                        newgrid[i][j] = 1
        return newgrid
    
    def simplify(self, grid, voices):
        sets = [[] for i in range(len(grid))]
        newG = [[0 for i in range(16)] for j in range (16)]
        for i in range(len(grid)):
            for j in range(len(grid)):
                if grid[i][j] != 0:
                    sets[i].append(j)
        for i in range(len(sets)):
            for j in range(voices):
                if len(sets[i]) == 0: break
                k = random.choice(sets[i])
                newG[i][k] = 1
                sets[i].remove(k)
        return newG
    
    def neighborCount(self, grid, i, j):
        count = 0
        for m in [-1, 0, 1]:
            for k in [-1, 0, 1]:
                if abs(m) + abs(k) == 0:
                    continue
                if grid[(i+m)%len(grid)][(j+k)%len(grid)] != 0:
                    count += 1
        return count       
        
    def gameOfLifeStep(self, oldG):
        newG = [[0 for i in range(len(oldG))] for j in range(len(oldG))]
        for i in range(len(oldG)):
            for j in range(len(oldG)):
                c = self.neighborCount(oldG, i, j)
                if c < 2 or c > 3:
                    newG[i][j] = 0
                if c in [2, 3]:
                    newG[i][j] = oldG[i][j]
                if c == 3:
                    newG[i][j] = 1
        return newG
    
    def gameOfLife(self, grid, steps):
        g = copy.deepcopy(grid)
        for i in range(steps):
            g = self.gameOfLifeStep(g)
        return g


#client = MelClient(["testvoice1.txt", "testvoice2.txt"])
#client.playStart()
#client.loopStart()