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
                        output = Physics.distributeForce(vectors, currForce + weight)
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
                output = Physics.distributeForce(vectors, currForce + weight)
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
    checkPhysics = staticmethod(checkPhysics)
    
    def resetPhysics():
        # reset forces
        G.jointData = np.random.random(G.numBlocksX * G.numBlocksY * 3)-0.5
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
