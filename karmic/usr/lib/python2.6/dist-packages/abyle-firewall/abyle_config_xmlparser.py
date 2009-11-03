import xml.dom.minidom
import re
import sys

from xml.dom.minidom import Node
from abyle_output import abyle_output

class abyle_config_parse:
    def __init__(self, fwconfigpath, interface, xmlconfig):
        self.fwconfigpath = fwconfigpath
        self.pinterface = interface
        self.xmlconfig = xmlconfig
        self.configarr = []
        self.configvar = ''

        try:
            if self.pinterface == "default":
                self.abyle_config = xml.dom.minidom.parse(self.fwconfigpath+self.xmlconfig)
            else:
                self.abyle_config = xml.dom.minidom.parse(self.fwconfigpath+'interfaces/'+self.pinterface+'/'+self.xmlconfig)
        except (IOError):
            abyle_output(self.interface+"_config_xmlparsing", "", "", str(sys.exc_info()[1]))

    def getConfig(self,configstr):
        self.configstr = configstr
        self.configarr = []
        self.configvar = ''

        if self.configstr == "excluded_interfaces":
            for self.configtag in self.abyle_config.getElementsByTagName("interface"):
                if self.configtag.getAttribute("excluded") == "yes":
                    self.configarr.append(self.configtag.firstChild.nodeValue)

            return self.configarr



        else:

            for self.configtag in self.abyle_config.getElementsByTagName(self.configstr):
                self.configarr.append(self.configtag.firstChild.nodeValue)

            try:
                self.configvar = self.configarr[1]
                return self.configarr
            except (IndexError):
                return self.configarr[0]
