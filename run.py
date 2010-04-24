#!/usr/bin/env python
# encoding: utf-8
"""
frontend.py

CS266 Ant Sim
"""

import sys
import pygame, math, time
from pygame.locals import *
import numpy as np

from param import G
from sim import Sim
from button import Button
from error import *

class BatchRun(object):
	def __init__(self, numRuns, output):
		# desired statistics
		antsPerRun = 0
		successfulRuns = 0
		failedRuns = 0
		
		success = True

		if output is not None:
			outfile = open(output, "w");
			G.outfile = outfile
		
		for i in range(numRuns):
			if G.verbose:
				print >> G.outfile, "RUNNING BATCH " + str(i+1)
			try:
				self.sim = Sim()
				while G.running:
					if not self.sim.step():
						break
				G.running = True
			except Error as e:
				print e
				success = None
			
			# accumulate statistics
			if success:
				antsPerRun += self.sim.numAnts
				successfulRuns+=1
			else:
				failedRuns +=1
				success = True

		#sanity check
		if numRuns != successfulRuns + failedRuns:
			raise WeirdError("Runs weren't counted right... weird!")

		# summarize statistics
		print >> G.outfile, "Ran a batch of " + str(numRuns) \
			+ " simulations. \nAverage Ants To Complete a Bridge: " \
			+ str(float(antsPerRun) / float(numRuns)) \
			+ "\n Percentage of Successful Runs: " \
			+ str(float(successfulRuns) * 100.0 / float(numRuns)) \
			+ "%"

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
			pygame.draw.line(self.screen, G.lineColor, (x*G.blockWidth, 0),
							 (x*G.blockWidth, G.screenHeight-G.buttonPanelHeight), G.lineWidth)

		for y in range(G.numBlocksY+1):
			pygame.draw.line(self.screen, G.lineColor, (0, y*G.blockHeight),
							 (G.screenWidth, y*G.blockHeight), G.lineWidth)
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
                                        (x*G.blockWidth + G.lineWidth, y*G.blockHeight + G.lineWidth,
                                         G.blockWidth - G.lineWidth, G.blockHeight - G.lineWidth), 0)
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
			pygame.draw.line(self.screen, color, ((at[0]+0.5)*G.blockWidth, (at[1]+0.5)*G.blockHeight),
							 ((joint.to[0]+0.5)*G.blockWidth, (joint.to[1]+0.5)*G.blockHeight), width)
