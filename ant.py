#!/usr/bin/env python
# encoding: utf-8
"""
ant.py

CS266 Ant Sim
"""

import sys, random
from param import G
from error import *

def randomDiscrete(choices, probs):
	assert len(choices) == len(probs)
	k = float(sum(probs))
	norm_probs = [p/k for p in probs]
	
	cumulatives = [sum(norm_probs[:i+1]) for i in range(len(norm_probs))]
	x = random.random()
	for i,choice in enumerate(choices):
		if x < cumulatives[i]:
			return choice
	assert False
	
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

class Ant(object):
	def __init__(self, id):
		self.id = id
		#self.x = random.choice(range(G.numBlocksX))
		#self.x = random.choice(range(G.numBlocksX/2-3, G.numBlocksX/2+3))
		self.x = G.numBlocksX/2
		self.y = 0
		self.pos = (self.x, self.y) #purely for syntax simplicity
		self.settled = False
		self.supportMode = False
		self.moveRight = random.choice([True,False])
		if G.verbose:
			print >> G.outfile, "ant %d is moving" % (self.id)

	def move(self):
		if (not self.supportMode):
			neighbors = [self.pos]
			if G.antSenseRadius == 1:
				neighbors += getNeighbors(self.pos)
			for neighbor in neighbors:
				if (G.state[neighbor]) == G.SHAKING:
					self.supportMode = True
					if (G.supportAlgo == G.HORIZONTAL_SUPPORT):
						self.supportDirection = random.choice([-1,1])
					break
		
		try:
			if not G.state[self.pos]:
				newCoord = self.pos
			else:
				if (self.supportMode):
					if (G.supportAlgo == G.HORIZONTAL_SUPPORT):
						newCoord = (self.x+self.supportDirection, self.y)
					elif (G.supportAlgo == G.NONUNIFORM_SUPPORT):	
						horizontalProb = 4.0
						verticalProb = 1.0
						neighbors = []
						probs = []
						x, y = self.pos
						if not self.moveRight and x > 0:
							neighbors.append((x-1, y))
							probs.append(horizontalProb)
						if self.moveRight and x < G.numBlocksX-1:
							neighbors.append((x+1, y))
							probs.append(horizontalProb)
						neighbors.append((x, y+1))
						probs.append(verticalProb)
						newCoord = randomDiscrete(neighbors, probs)
						
						if not newCoord in getNeighbors(self.pos):
							raise SimulationError("OutOfBoundsError", "Ant cannot move any further in desired direction")
					elif (G.supportAlgo == G.RANDOM_SUPPORT):
						neighbors = [n for n in getNeighbors(self.pos)]
						newCoord = random.choice(neighbors)
				else:
					if (G.baseMoveAlgo == G.RANDOM_WALK):
						horizontalProb = 1.0
						verticalProb = 1.0
						neighbors = []
						probs = []
						x, y = self.pos
						if not self.moveRight and x > 0:
							neighbors.append((x-1, y))
							probs.append(horizontalProb)
						if self.moveRight and x < G.numBlocksX-1:
							neighbors.append((x+1, y))
							probs.append(horizontalProb)
						neighbors.append((x, y+1))
						probs.append(verticalProb)
						newCoord = randomDiscrete(neighbors, probs)
						
					elif (G.baseMoveAlgo == G.STRAIGHT_DOWN):
						x, y = self.pos
						newCoord = (x, y+1)
					elif (G.baseMoveAlgo == G.NONUNIFORM):
						horizontalProb = 1.0
						verticalProb = 3.0
						neighbors = []
						probs = []
						x, y = self.pos
						if not self.moveRight and x > 0:
							neighbors.append((x-1, y))
							probs.append(horizontalProb)
						if self.moveRight and x < G.numBlocksX-1:
							neighbors.append((x+1, y))
							probs.append(horizontalProb)
						neighbors.append((x, y+1))
						probs.append(verticalProb)
						newCoord = randomDiscrete(neighbors, probs)
						


			if not G.state[newCoord]:
				x, y = newCoord
				try:
					while (y > 0 and (G.state[(x-1,y-1)] == G.NOANT and G.state[(x,y-1)] == G.NOANT and G.state[(x+1,y-1)] == G.NOANT)):
						if (G.state[(x-1,y)]):
							newCoord = (x-1,y-1)
						elif (G.state[(x+1,y)]):
							newCoord = (x+1,y-1)
						else:
							raise WeirdError("There are no ants around us or above us, yet here we are!")
						x, y = newCoord

				except IndexError as e:
					raise SimulationError("OutOfBoundsError", "Ant cannot move any further in desired direction")

				G.state[newCoord] = G.NORMAL
				self.settled = True
			
			(self.x, self.y) = newCoord
			self.pos = newCoord								
		except Error as e:
			raise e
