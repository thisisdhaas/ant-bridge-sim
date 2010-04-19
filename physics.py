#!/usr/bin/env python
# encoding: utf-8
"""
physics.py

CS266 Ant Sim
"""

import sys
import pygame, random, math, time
import numpy as np
from pygame.locals import *

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
