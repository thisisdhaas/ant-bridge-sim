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

help_message = '''
The help message goes here.
'''

# global parameters
# TODO: move to separate file?
class G(object):
    # parameters for simulator
    antWeight = 1.0

    # parameters for frontend
    numBlocksX = 15
    numBlocksY = 15
    screenHeight = 300
    screenWidth = 300
    lineWidth = 1
    sleep = 0.
    blockSize = int(math.floor(min(screenWidth/numBlocksX,screenHeight/numBlocksY)))
    lineColor = (0, 0, 0)
    emptyColor  = (255, 255, 255)
    fillColor   = (0, 0, 200)
    shakeColor  = (100, 0, 200)
    searchColor = (0, 200, 0)


    # global datastructures
    shake = None
    state = None
    weight = None
    running = True

   
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

    def step(self):
        if not self.ant.settled:
            self.ant.move()
        else:
            if self.checkBridge():
                return False
            self.antId = self.antId + 1
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
            print "Ant bridge sucessfully reached the bottom!"
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
        print "ant %d is moving" % (self.id)

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
    def __init__(self, sim):
        self.sim = sim
        
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


        
class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg


def main(argv=None):
    if argv is None:
	argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "ho:v", ["help", "output="])
        except getopt.error, msg:
            raise Usage(msg)
    
        # option processing
        for option, value in opts:
            if option == "-v":
                verbose = True
            if option in ("-h", "--help"):
                raise Usage(help_message)
            if option in ("-o", "--output"):
                output = value

    except Usage, err:
        print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
        print >> sys.stderr, "\t for help use --help"
        return 2


    sim = Sim()
    FrontEnd(sim)

if __name__ == "__main__":
	sys.exit(main())


class A(object):
    def __init__(self, d):
        self.d = d
 
