#!/usr/bin/env python
# encoding: utf-8
"""
main.py

CS266 Ant Sim
"""


class Success(Exception):
	def __init__(self, msg):
		self.msg = msg
		self.type = "Success"
		
	def __str__(self):
		return repr(self.type) + ": " + repr(self.msg)
	
class Error(Exception):
    #base class for errors
    pass

class SimulationError(Error):
    #errors from running the physics simulator
    def __init__(self, type, msg):
        self.msg = msg
        self.type = type

    def __str__(self):
        return repr(self.type) + ": " + repr(self.msg)

    

class WeirdError(Error):
    #errors that really shouldn't happen
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return "WeirdError: " + repr(self.msg)

class BridgeFailure(Error):
	def __init__(self, msg):
		self.msg = msg
	
	def __str__(self):
		return "BridgeFailure: " + repr(self.msg)
		
	