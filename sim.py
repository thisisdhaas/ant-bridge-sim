#!/usr/bin/env python
# encoding: utf-8
"""
sim.py

CS266 Ant Sim
"""

import numpy as np
from param import G
from ant import Ant
from physics import *

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
			if self.checkBridge():
				return False
			self.addJoints(self.ant)
			self.antId = self.antId + 1
			self.numAnts += 1
			self.ant = Ant(self.antId)
			self.resetPhysics()
			self.checkPhysics()
			self.updateShaking()
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
			if (maxForce > G.killThreshold):
				G.state[coord] = G.DEAD
			elif (maxForce > G.shakeThreshold):
				G.state[coord] = G.SHAKING
			else:
				G.state[coord] = G.NORMAL
				
	def checkPhysics(self):
		"""Updates shaking of ants"""
		checknew = 0.0
		checkold = -1.0
		# try to converge
		run = 0
		while run < 100:
			checkold = checknew
			run += 1
			error = 0.0
			delta = 0.0
			# initialize weights into the system, work upwards
			for y in reversed(range(G.numBlocksY)):
				# order of the row doesn't matter
				for x in range(G.numBlocksX):
					if G.state[(x,y)]:
						vectors = np.array([j.vector for j in G.jointRef[(x,y)]])
						currForce = np.apply_along_axis(sum, 0, np.array([j.force() * j.vector for j in G.jointRef[(x,y)]]))
						weight = np.array([0,-1])
						output = distributeForce(vectors, currForce + weight)
						effect = np.transpose(np.transpose(vectors) * output)
						for i in range(len(G.jointRef[(x,y)])):
							G.jointRef[(x,y)][i].add(np.dot(effect[i], G.jointRef[(x,y)][i].vector))
			
			for coord in random.sample(G.jointRef.keys(), len(G.jointRef.keys())):
				x = coord[0]
				y = coord[1]
				vectors = np.array([j.vector for j in G.jointRef[(x,y)]])
				currForce = np.apply_along_axis(sum, 0, np.array([j.force() * j.vector for j in G.jointRef[(x,y)]]))
				weight = np.array([0,-1])
				error += np.sum(np.abs(currForce + weight))
				output = distributeForce(vectors, currForce + weight)
				effect = np.transpose(np.transpose(vectors) * output)
				for i in range(len(G.jointRef[(x,y)])):
					diff = np.dot(effect[i], G.jointRef[(x,y)][i].vector)
					G.jointRef[(x,y)][i].add(diff)
			#print error


			checknew = 0.0
			for coord in random.sample(G.jointRef.keys(), len(G.jointRef.keys())):
				x = coord[0]
				y = coord[1]
				for joint in G.jointRef[(x,y)]:
					if joint.to[1] == -1:
						checknew += joint.force() * np.dot(joint.vector, np.array([0.0,1.0]))
					   
		maxm = 0.0
		for coord in random.sample(G.jointRef.keys(), len(G.jointRef.keys())):
				x = coord[0]
				y = coord[1]
				for joint in G.jointRef[(x,y)]:
					if maxm < np.abs(joint.force() * np.dot(joint.vector, np.array([0.0,1.0]))):
						maxm = np.abs(joint.force() * np.dot(joint.vector, np.array([0.0,1.0])))
		if run < 99: print run, maxm, checknew
		else: print run, maxm, checknew, "Warning, convergence failure"

		
	def resetPhysics(self):
		# reset forces
		G.jointData = np.random.random(G.numBlocksX * G.numBlocksY * 3)-0.5

	def checkBridge(self):
		if self.ant.y == G.numBlocksY-1:
			if G.verbose:
				print >> G.outfile, "Ant bridge sucessfully reached the bottom!"
			G.running = False
			return True
		return False
