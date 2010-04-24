#!/usr/bin/env python
# encoding: utf-8
"""
sim.py

CS266 Ant Sim
"""
EPS = 0.000001
import numpy as np
from param import G
from ant import Ant
from physics import Physics
from error import BridgeFailure

def norm(v):
	return np.sqrt(np.dot(v,v))

class Joint(object):
	def __init__(self, at, to, num):
		self.at = at
		self.to = to
		self.vector = np.array([at[0],at[1]]) - np.array([to[0],to[1]], dtype=np.float32)
		self.vector /= norm(self.vector)
		if num != -1:
			self.num = num
		else:
			self.num = G.numJoints
		if not G.jointRef.has_key(at):
			G.jointRef[at] = []
		G.jointRef[at].append(self)
		if -1 == num and to[1] > -1:
			Joint(to, at, G.numJoints)
		else:
			G.numJoints+=1

	def force(self):
		return G.jointData[self.num]

	def add(self, val):
		G.jointData[self.num] += val



def getAdjacent((x,y)):
	neighbors = []
	if x > 0:
		neighbors.append((x-1, y))
		if y > 0:
			neighbors.append((x-1, y-1))
		if y < G.numBlocksY-1:
			neighbors.append((x-1, y+1))
	if x < G.numBlocksX-1:
		neighbors.append((x+1, y))
		if y > 0:
			neighbors.append((x+1, y-1))
		if y < G.numBlocksY-1:
			neighbors.append((x+1, y+1))
	if y > 0:
		neighbors.append((x, y-1))
	if y < G.numBlocksY-1:
		neighbors.append((x, y+1))
	return neighbors		

class Sim(object):
	def __init__(self):
		G.state = np.zeros((G.numBlocksX, G.numBlocksY), dtype=np.int)
		G.weight = np.ones((G.numBlocksX, G.numBlocksY))
		self.antId = 0
		self.ant = Ant(self.antId)
		self.numAnts = 1

		G.jointData = np.zeros((G.numBlocksX * G.numBlocksY * 3))
		G.numJoints = 0
		G.jointRef = {}

	def step(self):
		if not self.ant.settled:
			self.ant.move()
		else:
			self.addJoints(self.ant)
			self.antId = self.antId + 1
			self.numAnts += 1
			self.ant = Ant(self.antId)
			Physics.resetPhysics()
			Physics.checkPhysics()
			self.updateShaking()
			if self.checkBridge():
				return False
		return True


	def addJoints(self, ant):
		for adjacent in getAdjacent(ant.pos):
			if G.state[adjacent]:
				Joint(ant.pos, adjacent, -1)
								 
			# attach anchor joints
		if ant.y == 0:
			Joint(ant.pos, (ant.x, ant.y-1), -1)
			Joint(ant.pos, (ant.x-1, ant.y-1), -1)
			Joint(ant.pos, (ant.x+1, ant.y-1), -1)

	def getForces(self, (x,y)):
		return [f.force() for f in G.jointRef[(x,y)]]


	def updateShaking(self):
		for coord in G.jointRef.keys():
			forces = self.getForces(coord)
			maxForce = max(map(abs, forces))
			if maxForce > G.killThreshold - EPS:
				G.state[coord] = G.DEAD
   			elif maxForce > G.shakeThreshold - 2*EPS:
				G.state[coord] = G.SHAKING
			else:
				G.state[coord] = G.NORMAL
				
	def checkBridge(self):
		deadAnts = [(x,y) for x in range(G.state.shape[0]) for y in range(G.state.shape[1]) if G.state[(x,y)] == G.DEAD]
		if deadAnts:
			raise BridgeFailure("Bridge collapsed at coordinate(s) %s" % " ".join(map(repr, deadAnts)))
		if self.ant.y == G.numBlocksY-1:
			if G.verbose:
				print >> G.outfile, "Ant bridge sucessfully reached the bottom!"
			G.running = False
			return True
		return False
