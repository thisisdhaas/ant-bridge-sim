#!/usr/bin/env python
# encoding: utf-8
"""
ant.py

CS266 Ant Sim
"""

import random
from param import G

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
		#self.x = random.choice(range(G.numBlocksX/2-3, G.numBlocksX/2+3))
		self.x = G.numBlocksX/2
		self.y = 0
		self.pos = (self.x, self.y) #purely for syntax simplicity
		self.settled = False
		self.supportMode = False
		if G.verbose:
			print >> G.outfile, "ant %d is moving" % (self.id)

	def move(self):
		if (not self.supportMode):
			if (G.state[self.pos]) == G.SHAKING:
				self.supportMode = True
				if (G.supportAlgo == G.HORIZONTAL_SUPPORT):
					self.supportDirection = random.choice([-1,1])
			
		if (self.supportMode):
			if (G.supportAlgo == G.HORIZONTAL_SUPPORT):
				if G.state[self.pos]:
					newCoord = (self.x+self.supportDirection, self.y)
					if not newCoord in getNeighbors(self.pos):
						raise OutOfBoundsError
				else:
					newCoord = self.pos
			elif (G.supportAlgo == G.NONDOWN_SUPPORT):
				if G.state[self.pos]:
					neighbors = [n for n in getNeighbors(self.pos) if n[1] <= self.y]
					newCoord = random.choice(neighbors)
				else:
					newCoord = self.pos
		else:
			if (G.baseMoveAlgo == G.RANDOM_WALK):
				if G.state[self.pos]:
					neighbors = [n for n in getNeighbors(self.pos) if n[1] >= self.y]
				 	newCoord = random.choice(neighbors)
				else:
					newCoord = self.pos
			elif (G.baseMoveAlgo == G.STRAIGHT_DOWN):	
				if G.state[self.pos]:
					x, y = self.pos
					newCoord = (x, y+1)
				else:
					newCoord = self.pos

		if not G.state[newCoord]:
			x, y = newCoord
			while (y > 0 and (G.state[(x-1,y-1)] == G.NOANT and G.state[(x,y-1)] == G.NOANT and G.state[(x+1,y-1)] == G.NOANT)):
				if (G.state[(x-1,y)]):
					newCoord = (x-1,y-1)
				elif (G.state[(x+1,y)]):
					newCoord = (x+1,y-1)
				else:
					raise WHYARETHERENOANTSNEXTTOUS_ERROR
				x, y = newCoord
			G.state[newCoord] = G.NORMAL
			self.settled = True
			
		(self.x, self.y) = newCoord
		self.pos = newCoord								
