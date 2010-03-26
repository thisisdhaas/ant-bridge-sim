#!/usr/bin/env python
# encoding: utf-8
"""
main.py

CS266 Ant Sim
"""

import sys
import getopt

import pygame, random, math, time
import numpy as np
from pygame.locals import *

from param import G

help_message = '''
CS266 Ant Sim 
Usage: python main.py [options]
Options are:
    -b numRuns  # run simulation numRuns times as a batch with no graphics
    -o outfile  # output batch data to file
    -v          # print verbose output to stdout or output file (with -o)
    --batch     # same as -b
    --output    # same as -o
'''

def eventHandler():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            G.running = False
        elif event.type == MOUSEBUTTONDOWN:
            G.running = False

def getNeighbors((x,y)):
    neighbors = []
    if x > 0:
        neighbors.append((x-1, y))
    if x < G.numBlocksX-1:
        neighbors.append((x+1, y))
    if y > 0:
        neighbors.append((x, y-1))
    if y < G.numBlocksY-1:
        neighbors.append((x, y+1))
    return neighbors


class Sim(object):
 
    def __init__(self):
        random.seed()
        G.state = np.zeros((G.numBlocksX, G.numBlocksY), dtype=np.bool)
        G.shake = np.zeros((G.numBlocksX, G.numBlocksY), dtype=np.bool)
        G.weight = np.ones((G.numBlocksX, G.numBlocksY))
        self.antId = 0
        self.ant = Ant(self.antId)
        self.numAnts = 1

    def step(self):
        if not self.ant.settled:
            self.ant.move()
        else:
            if self.checkBridge():
                return False
            self.antId = self.antId + 1
            self.numAnts += 1
            self.ant = Ant(self.antId)
            self.checkPhysics()
        return True
        
    def checkPhysics(self):
        """Checks integrity of ant struture and updates shaking of ants"""
        #TODO: implement
        for x in range(G.numBlocksX):
            for y in range(G.numBlocksY):
                if not G.state[(x,y)]:
                    continue
                count = 0
                for n in getNeighbors((x,y)):
                    if G.state[n]:
                        count += 1
                        if n[1] < y:
                            count += 1
                if count == 1:
                    G.shake[x][y] = True
                else:
                    G.shake[x][y] = False

    def checkBridge(self):
        if self.ant.y == G.numBlocksY-1:
            if G.verbose:
                print >> G.outfile, "Ant bridge sucessfully reached the bottom!"
            G.running = False
            return True
        return False


class Ant(object):
    def __init__(self, id):
        self.id = id
        self.x = int(G.numBlocksX/2)
        self.y = 0
        self.pos = (self.x, self.y) #purely for syntax simplicity
        self.settled = False
        if G.verbose:
            print >> G.outfile, "ant %d is moving" % (self.id)

    def move(self):
        if G.state[self.pos]:
            neighbors = [n for n in getNeighbors(self.pos) if n[1] >= self.y and not G.shake[n]]
            newCoord = random.choice(neighbors)
        else:
            newCoord = self.pos

        if not G.state[newCoord]:
            G.state[newCoord] = True
            self.settled = True
            
        (self.x, self.y) = newCoord
        self.pos = newCoord

class FrontEnd(object):
    def __init__(self):
        self.sim = Sim()
        
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((G.screenWidth, G.screenHeight))
        pygame.display.set_caption("AntBridgeSim")
        self.clock = pygame.time.Clock()
        self.drawGrid()

        oldpos = self.sim.ant.pos
        oldId = self.sim.antId
        while G.running:
            time.sleep(G.sleep)
            eventHandler()
            self.drawBlock(self.sim.ant.pos)
            self.drawBlock(oldpos)
            oldpos = self.sim.ant.pos

            if self.sim.antId != oldId:
                oldId = self.sim.antId
                self.drawGrid()

            pygame.display.flip()

            if not self.sim.step():
                break
            
            
    def drawGrid(self):     
        for x in range(G.numBlocksX):
            for y in range(G.numBlocksY):
                self.drawBlock((x,y))
                
        for x in range(G.numBlocksX+1):
            pygame.draw.line(self.screen, G.lineColor, (x*G.blockSize, 0),
                             (x*G.blockSize, G.screenHeight), G.lineWidth)

        for y in range(G.numBlocksY+1):
            pygame.draw.line(self.screen, G.lineColor, (0, y*G.blockSize),
                             (G.screenWidth, y*G.blockSize), G.lineWidth)

    def drawBlock(self, (x,y)):
        if self.sim.ant.pos == (x,y):
            color = G.searchColor
        elif G.shake[(x,y)]:
            color = G.shakeColor
        elif G.state[(x,y)]:
            color = G.fillColor
        else:
            color = G.emptyColor
        rect = pygame.draw.rect(self.screen, color,
                                (x*G.blockSize + G.lineWidth, y*G.blockSize + G.lineWidth,
                                 G.blockSize - G.lineWidth, G.blockSize - G.lineWidth), 0)


class BatchRun(object):
    def __init__(self, numRuns, output):
        # desired statistics
        antsPerRun = 0

        if output is not None:
            outfile = open(output, "w");
            G.outfile = outfile
        
        for i in range(numRuns):
            if G.verbose:
                print >> G.outfile, "RUNNING BATCH " + str(i+1)
            self.sim = Sim()
            while G.running:
                if not self.sim.step():
                    break
            G.running = True
            
            # accumulate statistics
            antsPerRun += self.sim.numAnts

        # summarize statistics
        print >> G.outfile, "Ran a batch of " + str(numRuns) \
            + " simulations. \nAverage Ants To Complete a Bridge: " \
            + str(float(antsPerRun) / float(numRuns))
        
class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg


def main(argv=None):
    output = None
    batch = None
    numRuns = 1

    if argv is None:
	argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "ho:vb:", ["help", "output=", "batch="])
        except getopt.error, msg:
            raise Usage(msg)
    
        # option processing
        for option, value in opts:
            if option == "-v":
                G.verbose = True
            if option in ("-h", "--help"):
                raise Usage(help_message)
            if option in ("-o", "--output"):
                output = value
            if option in ("-b", "--batch"):
                batch = True
                numRuns = int(value)

    except Usage, err:
        print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
        print >> sys.stderr, "\t for help use --help"
        return 2

    if batch is None:
        FrontEnd()
    else: 
        BatchRun(numRuns, output)

if __name__ == "__main__":
	sys.exit(main())


class A(object):
    def __init__(self, d):
        self.d = d
 
