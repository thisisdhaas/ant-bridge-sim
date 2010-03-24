#!/usr/bin/env python
# encoding: utf-8
"""
main.py

CS266 Ant Sim
"""

import sys
import getopt

import pygame, random, math, time
from pygame.locals import *

help_message = '''
The help message goes here.
'''


# global parameters
# TODO: move to separate file?
blockSize = 20
lineWidth = 1
screenHeight = 300
screenWidth = 300
lineColor = (0, 0, 0)
freeBlockColor = (255, 255, 255)
searchBlockColor = (0, 255, 0)
settledBlockColor = (0, 0, 255)

antId = 0
running = True

def pygameInit():
	pygame.init()
	pygame.font.init()
	random.seed()
	global screen
	screen = pygame.display.set_mode((screenWidth, screenHeight))
	pygame.display.set_caption("AntBridgeSim")
	global clock
	clock = pygame.time.Clock()
	
def setupGrid():
	global numBlocksX
	global numBlocksY
	
	numBlocksX = int(math.floor(screenWidth/blockSize))
	numBlocksY = int(math.floor(screenHeight/blockSize))
	
	global blockGrid
	blockGrid = []
	
	for x in range(numBlocksX):
		blockRow = []
		for y in range(numBlocksY):
			blockRow.append(Block(y,x))
		blockGrid.append(blockRow)

def drawGrid():		
	for x in range(numBlocksX):
		for y in range(numBlocksY):
			blockGrid[x][y].draw()

	for x in range(numBlocksX+1):
		pygame.draw.line(screen, lineColor, (x*blockSize, 0), (x*blockSize, screenHeight), lineWidth)
		
	for y in range(numBlocksY+1):
		pygame.draw.line(screen, lineColor, (0, y*blockSize), (screenWidth, y*blockSize), lineWidth)
		
def eventHandler():
	global running
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		elif event.type == MOUSEBUTTONDOWN:
			running = False

class Block(object):
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.free = True
		self.search = False
	
	def draw(self):
		color = None
		if self.search:
			color = searchBlockColor
		elif self.free:
			color = freeBlockColor
		else:
			color = settledBlockColor
			
		rect = pygame.draw.rect(screen, color, (self.x*blockSize, self.y*blockSize, blockSize, blockSize), 0)
		screen.fill(color, rect)
	
	def setSearch(self):
		self.search = True
	
	def unsetSearch(self):
		self.search = False
		
	def setFree(self):
		self.free = True
		
	def setSettled(self):
		self.free = False

class Ant(object):
	def __init__(self, id):
		self.id = id
		self.x = 0
		self.y = int(numBlocksY/2)
		blockGrid[self.x][self.y].setSearch()
		self.settled = False
		print "ant %d is moving" % (self.id)
		
	def bridge(self):
		if blockGrid[self.x][self.y].free:
			blockGrid[self.x][self.y].unsetSearch()
			blockGrid[self.x][self.y].setSettled()
			self.settled = True
		else:
			blockGrid[self.x][self.y].unsetSearch()
			directions = []
			#if self.x > 0:
			#	directions.append((self.x-1, self.y))
			if self.x < numBlocksX-1:
				directions.append((self.x+1, self.y))
			if self.y > 0:
				directions.append((self.x, self.y-1))
			if self.y < numBlocksY-1:
				directions.append((self.x, self.y+1))
		 	self.x, self.y = random.choice(directions)
			blockGrid[self.x][self.y].setSearch()
		
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
				
		pygameInit()
		setupGrid()
		
		global antId
		global running
		ant = Ant(antId)
		while running:
			#time.sleep(0.1)
			drawGrid()
			eventHandler()
			if not ant.settled:
				ant.bridge()
			else:
				if ant.x == numBlocksX-1:
					print "Ant bridge sucessfully reached the bottom!"
					running = False
					break
				antId = antId + 1
				ant = Ant(antId)
			pygame.display.flip()
	
	except Usage, err:
		print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
		print >> sys.stderr, "\t for help use --help"
		return 2


if __name__ == "__main__":
	sys.exit(main())
