#import xml.dom.minidom
import re
import sys

#from xml.dom.minidom import Node
from abyle_output import abyle_output
from abyle_log import logger

log = logger("xml_config_parser")

try:
    from lxml import etree
except (ImportError):
    log.error("xml parser import error, please install python lxml package")
    sys.exit(1)

class abyle_config_parse:
    def __init__(self, fwconfigpath, interface, xmlconfig, verbose):
        self.classname = "abyle_config_parse"
        self.verbose=verbose
        self.fwconfigpath = fwconfigpath
        self.pinterface = interface
        self.xmlconfig = xmlconfig
        self.configarr = []
        self.configvar = ''

        log = logger("xml_config_parser")

        if self.verbose:
           log.debug(self.classname+" object created.")

        try:
            if self.pinterface == "default":
                self.abyle_config = etree.parse(self.fwconfigpath+self.xmlconfig)
                if self.verbose:
                      log.debug("trying to parse "+self.fwconfigpath+self.xmlconfig)
            else:
                self.abyle_config = etree.parse(self.fwconfigpath+'interfaces/'+self.pinterface+'/'+self.xmlconfig)
                if self.verbose:
                      log.debug("trying to parse "+self.fwconfigpath+'interfaces/'+self.pinterface+'/'+self.xmlconfig)
        except (IOError):
            log.error(str(sys.exc_info()[1]))

    def getConfig(self,configstr):
        self.methodname="getConfig(self,"+configstr+")"
        self.configstr = configstr
        self.configarr = []
        self.configvar = ''

        log = logger("xml_config_parser")

        if self.verbose:
           log.debug("launched "+self.methodname+" of "+self.classname+".")

        if self.configstr == "excluded_interfaces":
            #for self.configtag in self.abyle_config.getElementsByTagName("interface"):
            configwalk = etree.iterwalk(self.abyle_config,events=("start","end"),tag=str("interface"))
            for action, elem, in configwalk:
                if action in ('start'):
                   attributes = elem.attrib
                   if str(attributes.get("excluded")).upper() == "YES":
                        if self.verbose:
                            log.debug(elem.text)
                        self.configarr.append(elem.text)

            return self.configarr



        else:

            #for self.configtag in self.abyle_config.getElementsByTagName(self.configstr):
            configwalk = etree.iterwalk(self.abyle_config,events=("start","end"),tag=str(self.configstr))
            for action, elem, in configwalk:
                if action in ('start'):
                   if self.verbose:
                       log.debug(elem.text)
                   self.configarr.append(elem.text)

            try:
                self.configvar = self.configarr[1]
                return self.configarr
            except (IndexError):
                return self.configarr[0]
