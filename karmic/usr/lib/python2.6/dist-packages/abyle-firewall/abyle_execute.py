import re
from subprocess import Popen, PIPE, STDOUT
import sys

class abyle_execute:
	def __init__(self):
		self.command = ""
		self.dryrun = False
	
	def run(self, command, dryrun):

		self.command = command	
		self.dryrun = dryrun

		stdOut = ""
		stdErr = ""

		if not self.dryrun:
			p = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
			stdOut=str(p.stdout.read()).split("\n")
			stdErr=str(p.stderr.read()).split("\n")
		else:
			stdOut = ""
			stdErr = ""

		return stdOut, stdErr
