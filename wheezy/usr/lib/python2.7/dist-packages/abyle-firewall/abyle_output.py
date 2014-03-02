import re
import os
import sys

class abyle_output:
	def __init__(self, source_name, ErrMsg, StdMsg, DefaultMsg, color="default", logfile="/dev/null", verbose="true"):
		self.sourcename = source_name
		self.ErrMsg = ErrMsg
		self.StdMsg = StdMsg
		self.DefaultMsg = DefaultMsg
		self.color = color
		self.logfile = logfile
		self.colorcode = self.define_colorcode(self.color)
		self.verbose = verbose
		try:
			ofile = open(self.logfile,'a')
			if not self.ErrMsg and not self.StdMsg:
				if self.sourcename == "":
					if self.verbose:
						print (self.colorcode+self.DefaultMsg)
					ofile.write(self.DefaultMsg+"\n")
					os.system("tput sgr0") #set terminalcolor to default
				else:
					if self.verbose:
						print (self.colorcode+"MESSAGE from "+self.sourcename+": "+self.DefaultMsg)
					ofile.write("MESSAGE from "+self.sourcename+": "+self.DefaultMsg+"\n")
					os.system("tput sgr0") #set terminalcolor to default

			else:
				if self.ErrMsg:
					self.colorcode = "\033[1;31m"
					if type(self.ErrMsg) is list:
						#if self.verbose:
						print (self.colorcode+"\nMULTILINE ERROR MESSAGE from "+self.sourcename+":")
						ofile.write("\nMULTILINE ERROR MESSAGE from "+self.sourcename+":"+"\n")
						for l in self.ErrMsg:
							l = re.sub("\n$","",l)
							#if self.verbose:
							print (self.colorcode+l)
							ofile.write(l+"\n")
						#if self.verbose:
						print (self.colorcode+"END MULTILINE ERROR MESSAGE")
						ofile.write("END MULTILINE ERROR MESSAGE"+"\n")
						os.system("tput sgr0") #set terminalcolor to default
					else:
						#if self.verbose:
						print (self.colorcode+"ERROR MESSAGE from "+self.sourcename+": "+str(self.ErrMsg))
						ofile.write("ERROR MESSAGE from "+self.sourcename+": "+str(self.ErrMsg)+"\n")
						os.system("tput sgr0") #set terminalcolor to default
				if StdMsg:
					self.colorcode = "\033[0;00m"
					if type(self.StdMsg) is list:
						if self.verbose:
							print (self.colorcode+"MULTILINE MESSAGE from "+self.sourcename+":")
						ofile.write("MULTILINE MESSAGE from "+self.sourcename+":"+"\n")
						for l in self.StdMsg:
							l = re.sub("\n$","",l)
							if self.verbose:
								if "Chain " in l: # if line contain "Chain" print it in green, for "abyle -i"
									print ("\033[1;32m"+l)
								else: 
									print (self.colorcode+l)
							ofile.write(l+"\n")
						if self.verbose:
							print (self.colorcode+"END MULTILINE MESSAGE")
						ofile.write("END MULTILINE MESSAGE"+"\n")
						os.system("tput sgr0") #set terminalcolor to default
					else:
						if self.verbose:
							print (self.colorcode+"MESSAGE from "+self.sourcename+": "+str(self.StdMsg))
						ofile.write("MESSAGE from "+self.sourcename+": "+str(self.StdMsg)+"\n")
						os.system("tput sgr0") #set terminalcolor to default
			ofile.close()

		except (TypeError):
			print (sys.exc_info()[1])
		except (IOError):
			print (sys.exc_info()[1])

	
	
	def startup(self, msg, color="default", cr="no"):
		self.msg = msg
		self.color = color
		self.cr = cr

		self.colorcode = self.define_colorcode(color)
		
		if self.cr == "no":
			print (self.colorcode+msg,)
		else:
			print (self.colorcode+msg)

		sys.stdout.flush()
		os.system("tput sgr0") #set terminalcolor to default
	
	def define_colorcode(self, color):
		self.color = color
		
		if self.color == "white":
			self.colorcode = "\033[1;37m"
			return self.colorcode
		if self.color == "green":
			self.colorcode = "\033[1;32m"
			return self.colorcode
		if self.color == "red":
			self.colorcode = "\033[1;31m"
			return self.colorcode
		if self.color == "blue":
			self.colorcode = "\033[1;34m"
			return self.colorcode
		if self.color == "default":
			self.colorcode = "\033[0;00m"
			return self.colorcode
