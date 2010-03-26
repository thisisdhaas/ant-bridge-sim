#!/usr/bin/env python
# encoding: utf-8
"""
param.py: global parameters for the simulator

CS266 Ant Sim
"""

import math

# global parameters
class G(object):
    # parameters for simulator
    antWeight = 1.0

    # parameters for frontend
    numBlocksX = 15
    numBlocksY = 15
    screenHeight = 300
    screenWidth = 300
    lineWidth = 1
    sleep = 0.
    blockSize = int(math.floor(min(screenWidth/numBlocksX,screenHeight/numBlocksY)))
    lineColor = (0, 0, 0)
    emptyColor  = (255, 255, 255)
    fillColor   = (0, 0, 200)
    shakeColor  = (100, 0, 200)
    searchColor = (0, 200, 0)


    # global datastructures
    shake = None
    state = None
    weight = None
    running = True
