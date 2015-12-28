'''
Scheduling system written for EyeRCbot.
For use to take advantage of Twisted scheduling implimentation. 
'''

# This is so we can gain access to the reactor.
from EyeRCbot import reactor
import time
from twisted.internet import task

# TODO: Make sure this will work as a deferred or task
class Task(object):
	def __init__(self, name, start_time, repeat,  function,  *arguments):
		'''Init a task.
		name:			Name of the task
		start_time:	str in either countdown form or in cronlike form(notyet)
		function:		function to be called
		arguments:	additional arguments for the function'''
		self.name = name
		self.start_time = start_time
		self.function = function
		self.arguments = arguments
		self.firstrun = True
		self.repeat = repeat
		self.calculate()

	def calculate(self):
		'''
		This will calculate the following
		1) If this is a one time event or repeated
		2) Convert input time into countdown for first run
		3) Convert time into number of seconds for repeated runs
		
		Commands which just need reactor.callLater(delay, callable, *args, **kw)
		or l = task.LoopingCall(runEverySecond) / l.start(1.0) /	l.stop() 
		or d = task.deferLater(reactor, 3.5, f, "hello, world") / def called(result): print result / d.addCallback(called)
		should call these things directly for now
		
		Syntax of start_time
		'00:00:00'
		'''
		# TODO: Reduce this function to only process the raw time string and return seconds
		# This section will determine if the time proposed is the next day or not
		current = time.strftime('%H:%M:%S',time.gmtime())
		cTime = int(current[0] + current[1]) * 3600 + int(current[3] + current[4]) * 60 + int(current[6] + current[7])
		tTime = int(current[0] + current[1]) * 3600 + int(current[3] + current[4]) * 60 + int(current[6] + current[7])
		
		if cTime < tTime:
			# Then our scheduled action will happen today!
			exicute_time = tTime - cTime
			
		if self.repeat is False:
			reactor.callLater(exicute_time, function)
			return
	
	def function(self):
		'''This will execute the function, pass any parameters, and if a repeate then the function will repeate every 24 hours.'''
		self.function(self.arguments)
		if self.repeat and self.firstrun:
			self.loop.start(86400)
		self.firstrun = False

