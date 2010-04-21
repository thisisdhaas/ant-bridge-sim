#!/usr/bin/env python
# encoding: utf-8
"""
physics.py

CS266 Ant Sim
"""

import sys
import random, math
import numpy as np
from param import G
from error import SimulationError

class Physics(object):

    def checkPhysics():
        """Updates shaking of ants"""
        #input: array or blocks, joint vectors

        count = 0
        joints = 0
        CC = {}
        for y in range(G.numBlocksY):
            for x in range(G.numBlocksX):
                if G.state[(x,y)]:
                    CC[(x,y)] = count
                    count += 1
                    for J in G.jointRef[(x,y)]:
                        joints += 1
                        
        trans = np.zeros((2*count,joints), dtype=np.float)
        weight = np.zeros((2*count), dtype=np.float)
        for i in range(2*count):
            if i % 2 == 1:
                weight[i] = -1.0
        c = 0
        jj = 0
        for y in range(G.numBlocksY):
            for x in range(G.numBlocksX):
                if G.state[(x,y)]:
                    for J in G.jointRef[(x,y)]:
                        if J.at[1] >= 0:
                            trans[2*CC[J.at]][c] +=   J.vector[0]
                            trans[2*CC[J.at]+1][c] += J.vector[1]
                            
                        if J.to[1] >= 0:
                            trans[2*CC[J.to]][c] +=   -J.vector[0]
                            trans[2*CC[J.to]+1][c] += -J.vector[1]
                        c += 1
                    jj += 1
        output, res, rank, s = np.linalg.lstsq(trans, -weight)
        j = 0
        for y in range(G.numBlocksY):
            for x in range(G.numBlocksX):
                if G.state[(x,y)]:
                    CC[(x,y)] = count
                    count += 1
                    for J in range(len(G.jointRef[(x,y)])):
                        G.jointRef[(x,y)][J].add(output[j])
                        j += 1
        
    checkPhysics = staticmethod(checkPhysics)
    
    def resetPhysics():
        # reset forces
        G.jointData = np.random.random(G.numBlocksX * G.numBlocksY * 3)-0.5
        G.jointData *= 0
    resetPhysics = staticmethod(resetPhysics)

    def linComb(c,v):
	return np.apply_along_axis(sum, 0, np.transpose(c*np.transpose(v)))
    linComb = staticmethod(linComb)

    def distributeForceSimple(vectors, force):
	"""Finds a linear combination of vectors that equals the force"""
	#TODO: implement http://www.springerlink.com/content/u3171n0894523423/
	# as to minimize the strain on each ant's body
        try:
            output, res, rank, s = np.linalg.lstsq(np.transpose(vectors), -force)
            if not np.sum(np.abs(linComb(output, vectors) + force)) < 0.0001:
                raise SimulationError("ForceResolutionError", "Drew explain why this happened");
	except Error as e:
            print e
            sys.exit()
        return output
    distributeForceSimple = staticmethod(distributeForceSimple)



    def distributeForce(vectors, force):
	"""Finds a linear combination of vectors that equals the force, least distance coefficient"""
	#output, res, rank, s = np.linalg.lstsq(np.transpose(vectors), -force)
	try:
            try:
		output = np.dot(np.dot(vectors, np.linalg.inv(np.dot(np.transpose(vectors),vectors))), -force)
            except: # singular matrix
		output, res, rank, s = np.linalg.lstsq(np.transpose(vectors), -force)
            if not np.sum(np.abs(Physics.linComb(output, vectors) + force)) < 0.0001:
                raise SimulationError("ForceResolutionError", "Drew explain why this happened");
        except Error as e:
            print e
            sys.exit()
	return output
    distributeForce = staticmethod(distributeForce)



    def distributeForces(vectors, force):
	"""Finds a linear combination of vectors that equals the force, least distance coefficient"""
	#output, res, rank, s = np.linalg.lstsq(np.transpose(vectors), -force)
	try:
            try:
		output = np.dot(np.dot(vectors, np.linalg.inv(np.dot(np.transpose(vectors),vectors))), -force)
            except: # singular matrix
		output, res, rank, s = np.linalg.lstsq(np.transpose(vectors), -force)
            if not np.sum(np.abs(Physics.linComb(output, vectors) + force)) < 0.0001:
                raise SimulationError("ForceResolutionError", "Drew explain why this happened");
        except Error as e:
            print e
            sys.exit()
	return output
    distributeForces = staticmethod(distributeForces)
