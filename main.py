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
from button import Button

help_message = '''
CS266 Ant Sim 
Usage: python main.py [options]
Options are:
	-b numRuns	  # run simulation numRuns times as a batch with no graphics
	-o outfile	  # output batch data to file
	-v			  # print verbose output to stdout or output file (with -o)
	--batch		   # same as -b
	--output	# same as -o
'''

def norm(v):
	return np.sqrt(np.dot(v,v))

def linComb(c,v):
	return np.apply_along_axis(sum, 0, np.transpose(c*np.transpose(v)))

def distributeForceSimple(vectors, force):
	"""Finds a linear combination of vectors that equals the force"""
	#TODO: implement http://www.springerlink.com/content/u3171n0894523423/
	# as to minimize the strain on each ant's body
	output, res, rank, s = np.linalg.lstsq(np.transpose(vectors), -force)
	if not np.sum(np.abs(linComb(output, vectors) + force)) < 0.0001:
		raise ForceResolutionError
	
	return output

def distributeForce(vectors, force):
	"""Finds a linear combination of vectors that equals the force, least distance coefficient"""
	#output, res, rank, s = np.linalg.lstsq(np.transpose(vectors), -force)
	try:
		output = np.dot(np.dot(vectors, np.linalg.inv(np.dot(np.transpose(vectors),vectors))), -force)
	except: # singular matrix
		output, res, rank, s = np.linalg.lstsq(np.transpose(vectors), -force)
	if not np.sum(np.abs(linComb(output, vectors) + force)) < 0.0001:
		raise ForceResolutionError
	
	return output

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

class FrontEnd(object):
	def __init__(self):
		self.sim = Sim()
		
		pygame.init()
		pygame.font.init()
		self.screen = pygame.display.set_mode((G.screenWidth, G.screenHeight))
		pygame.display.set_caption("AntBridgeSim")
		self.clock = pygame.time.Clock()
		self.setupButtons()
		self.drawGrid()
		for button in self.buttons:
			button.draw(self.screen)
			
		oldpos = self.sim.ant.pos
		oldId = self.sim.antId
		while G.running:
			time.sleep(G.sleep)
			self.eventHandler()
			self.drawBlock(self.sim.ant.pos)
			self.drawJoint(self.sim.ant.pos)
			self.drawBlock(oldpos)
			self.drawJoint(oldpos)
			oldpos = self.sim.ant.pos
			if self.sim.antId != oldId:
				oldId = self.sim.antId
				self.drawGrid()
			self.drawJoints() #TODO incrementally draw
			pygame.display.flip()

			if not self.sim.step():
				break
			
	def eventHandler(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				G.running = False
			for button in self.buttons:
				button.checkPressed(event)
				
	def drawGrid(self):		   
		for x in range(G.numBlocksX):
			for y in range(G.numBlocksY):
				self.drawBlock((x,y))
				
		for x in range(G.numBlocksX+1):
			pygame.draw.line(self.screen, G.lineColor, (x*G.blockSize, 0),
							 (x*G.blockSize, G.screenHeight-G.buttonPanelHeight), G.lineWidth)

		for y in range(G.numBlocksY+1):
			pygame.draw.line(self.screen, G.lineColor, (0, y*G.blockSize),
							 (G.screenWidth, y*G.blockSize), G.lineWidth)
	def setupButtons(self):
		self.buttons = []
		
		buttonTexts = []
		actions = []
		
		# Button for speeding up animation
		buttonTexts.append("Speed up!")
		def action(button):
			G.sleep = G.sleep / 2.0
			print "Speed up! New speed %f" % (G.sleep) 
		actions.append(action)
		
		# Button for slowing down animation
		buttonTexts.append("Slow down.")
		def action(button):
			G.sleep = G.sleep * 2.0
			print "Slow down. New speed %f" % (G.sleep) 
		actions.append(action)
		
		# Button for pausing animation
		buttonTexts.append("Pause")
		def action(button):
			button.text = "Resume"
			button.draw(self.screen)
			pygame.display.flip()
			paused = True
			while paused:
				for event in pygame.event.get():
					if event.type == MOUSEBUTTONDOWN:
						paused = False
					elif event.type == pygame.QUIT:
						paused = False
						G.running = False
			button.text = "Pause"
			button.draw(self.screen)
			pygame.display.flip()
		actions.append(action)
		
		# This sets up all the buttons based on the above definitions
		# To add a new button, just append the appropriate text and action above.
		# When adding buttons, you don't need to change the code below.
		numButtons = float(len(actions))
		for i, (text, action) in enumerate(zip(buttonTexts, actions)):
			button = Button(text, i*G.screenWidth/numButtons, G.screenHeight-G.buttonPanelHeight, G.screenWidth/numButtons, G.buttonPanelHeight, action)
			self.buttons.append(button)

		
	def drawBlock(self, (x,y)):
		if self.sim.ant.pos == (x,y):
			color = G.searchColor
		elif G.state[(x,y)] == G.SHAKING: 
			color = G.shakeColor
		elif G.state[(x,y)] == G.NORMAL:
			color = G.fillColor
		elif G.state[(x,y)] == G.DEAD:
			color = G.deadColor
		else:
			color = G.emptyColor
		rect = pygame.draw.rect(self.screen, color,
								(x*G.blockSize + G.lineWidth, y*G.blockSize + G.lineWidth,
								 G.blockSize - G.lineWidth, G.blockSize - G.lineWidth), 0)
	def drawJoints(self):		 
		for at, _ in G.jointRef.items():
			self.drawJoint(at)

	def drawJoint(self, at):
		if not G.jointRef.has_key(at):
			return
		for joint in G.jointRef[at]:
			color = (255 * min(1.0,(0.2 + 0.8*np.abs(joint.force()))), 0, 0)
			if np.abs(joint.force()) > G.killThreshold:
				color = G.deadJointColor
			elif np.abs(joint.force()) > G.shakeThreshold:
				color = G.shakeJointColor
			width = G.jointWidth*(min(1.0,0.2 + 0.8*np.abs(joint.force())))
			pygame.draw.line(self.screen, color, ((at[0]+0.5)*G.blockSize, (at[1]+0.5)*G.blockSize),
							 ((joint.to[0]+0.5)*G.blockSize, (joint.to[1]+0.5)*G.blockSize), width)

	def setupButtons(self):
		self.buttons = []
		
		buttonTexts = []
		actions = []
		
		# Button for speeding up animation
		buttonTexts.append("Speed up!")
		def action(button):
			G.sleep = G.sleep / 2.0
			print "Speed up! New speed %f" % (G.sleep) 
		actions.append(action)
		
		# Button for slowing down animation
		buttonTexts.append("Slow down.")
		def action(button):
			G.sleep = G.sleep * 2.0
			print "Slow down. New speed %f" % (G.sleep) 
		actions.append(action)
		
		# Button for pausing animation
		buttonTexts.append("Pause")
		def action(button):
			button.text = "Resume"
			button.draw(self.screen)
			pygame.display.flip()
			paused = True
			while paused:
				for event in pygame.event.get():
					if event.type == MOUSEBUTTONDOWN:
						paused = False
					elif event.type == pygame.QUIT:
						paused = False
						G.running = False
			button.text = "Pause"
			button.draw(self.screen)
			pygame.display.flip()
		actions.append(action)
		
		# This sets up all the buttons based on the above definitions
		# To add a new button, just append the appropriate text and action above.
		# When adding buttons, you don't need to change the code below.
		numButtons = float(len(actions))
		for i, (text, action) in enumerate(zip(buttonTexts, actions)):
			button = Button(text, i*G.screenWidth/numButtons, G.screenHeight-G.buttonPanelHeight, G.screenWidth/numButtons, G.buttonPanelHeight, action)
			self.buttons.append(button)


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


	random.seed(2)
	if batch is None:
		FrontEnd()
	else: 
		BatchRun(numRuns, output)

if __name__ == "__main__":
	#sys.exit(main())

	import cProfile
	cProfile.run('main()', 'fooprof')

	import pstats
	p = pstats.Stats('fooprof')
	#p.sort_stats('cumulative').print_stats(50)
