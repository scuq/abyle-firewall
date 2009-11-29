import logging
import logging.handlers

class logger:
	logfile = '/var/log/abyle.log'
	logfileSize = 5000
	logfileBackupFiles = 2
	logfileMode = 'w'
	consoleFormat = ('%(name)s: %(message)s')
	fileFormat = ('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
	#dateFormat = ('%a, %d %b %Y %H:%M:%S')
	colorized_log_messages = True
	colors = {'warning':'\033[33m', 'info':'\033[0m', 'debug':'\033[36m', 'error':'\033[31m', 'reset':'\033[1;0m', 'start_stop':'\033[32m'}
	

	def __init__(self, name=''):
		self.loggerName = name
		#create the logging instance (called "log")
		self.log = logging.getLogger(self.loggerName)
		self.log.setLevel(logging.DEBUG)
		#setup file logger - logs DEBUG and above
		self.fh = logging.handlers.RotatingFileHandler(self.logfile,maxBytes=self.logfileSize, backupCount=self.logfileBackupFiles, mode=self.logfileMode)
		self.fh.setLevel(logging.DEBUG)
		self.fh.setFormatter(logging.Formatter(self.fileFormat))
		#setup console logger - logs INFO and above
		self.ch = logging.StreamHandler()
		self.ch.setLevel(logging.INFO)
		self.ch.setFormatter(logging.Formatter(self.consoleFormat))
		#add the console and file handler to our logger instance
		self.log.addHandler(self.fh)
		self.log.addHandler(self.ch)
		
			
	def debug(self, msg):
		self.message = msg
		if self.colorized_log_messages == True:
			self.log.debug(self.colors['debug']+self.message+self.colors['reset'])
		else:
			self.log.debug(self.message)
		
	def info(self, msg):
		self.message = msg
		if self.colorized_log_messages == True:
			self.log.info(self.colors['info']+self.message+self.colors['reset'])
		else:
			self.log.info(self.message)
		
	def warning(self, msg):
		self.message = msg
		if self.colorized_log_messages == True:
			self.log.warning(self.colors['warning']+self.message+self.colors['reset'])
		else:
			self.log.warning(self.message)
		
	def error(self, msg):
		self.message = msg
		if self.colorized_log_messages == True:
			self.log.error(self.colors['error']+self.message+self.colors['reset'])
		else:
			self.log.error(self.message)
			
	def start_stop(self, msg):
		self.message = msg
		#self.log.removeHandler(self.fh)
		if self.colorized_log_messages == True:
			self.log.info(self.message+'\033[40G['+self.colors['start_stop']+'  DONE  '+self.colors['reset']+']')
		else:
			print(123)
			self.log.info(self.message+'\033[40G[  DONE  ]')
		
	def colorizeMessages(self, x):
		self.x = x
		self.colorized_log_messages = self.x
