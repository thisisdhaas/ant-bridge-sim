#!/usr/bin/env python
# encoding: utf-8
"""
main.py

CS266 Ant Sim
"""

import sys
import getopt

import random
from param import G
from run import FrontEnd, BatchRun

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


	random.seed(1)
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
