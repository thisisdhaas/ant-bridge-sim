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
np.set_printoptions(threshold=np.nan)

class Physics(object):

    def checkPhysics():
        """Updates shaking of ants"""
        #input: array or blocks, joint vectors

        ants = 0
        joints = 0
        CC = {}
        for y in range(G.numBlocksY):
            for x in range(G.numBlocksX):
                if G.state[(x,y)]:
                    CC[(x,y)] = ants
                    for J in G.jointRef[(x,y)]:
                        joints += 1
                    ants += 1
                        
        trans = np.zeros((2*ants,joints), dtype=np.double)
        weight = np.zeros((2*ants), dtype=np.double)
        for i in range(2*ants):
            if i % 2 == 1:
                weight[i] = -1.0
                
        an = 0; jn = 0
        for y in range(G.numBlocksY):
            for x in range(G.numBlocksX):
                if G.state[(x,y)]:
                    for J in G.jointRef[(x,y)]:
                        if J.at[1] >= 0:
                            trans[2*CC[J.at]][jn]   += J.vector[0]
                            trans[2*CC[J.at]+1][jn] += J.vector[1]
                            
                        if J.to[1] >= 0:
                            trans[2*CC[J.to]][jn]   += -J.vector[0]
                            trans[2*CC[J.to]+1][jn] += -J.vector[1]
                        jn += 1
                    an += 1
                    
        output, res, rank, s = np.linalg.lstsq(trans, -weight)
        
        an = 0; jn = 0
        for y in range(G.numBlocksY):
            for x in range(G.numBlocksX):
                if G.state[(x,y)]:
                    for J in range(len(G.jointRef[(x,y)])):
                        G.jointRef[(x,y)][J].add(output[jn])
                        jn += 1
                    an += 1

    checkPhysics = staticmethod(checkPhysics)
    
    def resetPhysics():
        # reset forces
          G.jointData = np.zeros((G.numBlocksX * G.numBlocksY * 3))
    resetPhysics = staticmethod(resetPhysics)

    def linComb(c,v):
	return np.apply_along_axis(sum, 0, np.transpose(c*np.transpose(v)))
    linComb = staticmethod(linComb)
