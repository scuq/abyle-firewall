import logging
import logging.handlers

class logger:
	colorized_log_messages = True
	colors = {'warning':'\033[33m', 'info':'\033[0m', 'debug':'\033[36m', 'error':'\033[31m', 'reset':'\033[1;0m', 'start_stop':'\033[32m'}
	
	def __init__(self, name=""):
		self.loggerName = name
		self.log1 = logging.getLogger(self.loggerName)

	def debug(self, msg):
		self.message = msg
		if self.colorized_log_messages == True:
			self.log1.debug(self.colors['debug']+self.message+self.colors['reset'])
		else:
			self.log1.debug(self.message)
		
	def info(self, msg):
		self.message = msg
		if self.colorized_log_messages == True:
			self.log1.info(self.colors['info']+self.message+self.colors['reset'])
		else:
			self.log1.info(self.message)
		
	def warning(self, msg):
		self.message = msg
		if self.colorized_log_messages == True:
			self.log1.warning(self.colors['warning']+self.message+self.colors['reset'])
		else:
			self.log1.warning(self.message)
		
	def error(self, msg):
		self.message = msg
		if self.colorized_log_messages == True:
			self.log1.error(self.colors['error']+self.message+self.colors['reset'])
		else:
			self.log1.error(self.message)
	
	def exception(self, msg):
		self.message = msg
		if self.colorized_log_messages == True:
			self.log1.error(self.colors['error']+self.message+self.colors['reset'])
		else:
			self.log1.error(self.message)

	def start_stop(self, msg, startup_status="DONE"):
		self.message = msg
		self.startup_status = startup_status
		rootLogger = logging.getLogger()
		filt = logging.Filter("somthing_but_not_empty")
		rootLogger.handlers[1].addFilter(filt)
		if self.colorized_log_messages == True:
			self.log1.warning(self.message+'\033[40G['+self.colors['start_stop']+'  '+self.startup_status+'  '+self.colors['reset']+']')
		else:
			self.log1.warning(self.message+'\033[40G[  '+self.startup_status+'  ]')
		rootLogger.handlers[1].removeFilter(filt)
		
	def colorizeMessages(self, x):
		self.x = x
		self.colorized_log_messages = self.x
