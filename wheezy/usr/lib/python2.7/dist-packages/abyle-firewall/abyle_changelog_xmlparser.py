import xml.dom.minidom
import re
from xml.dom.minidom import Node
from abyle_output import abyle_output

class abyle_changelog_parse:
    def __init__(self, fwconfigpath, changelogfile):
        self.fwconfigpath = fwconfigpath
        self.changelogfile = changelogfile
        self.configarr = []
        self.configvar = ''

        try:
            self.abyle_changelog = xml.dom.minidom.parse(self.fwconfigpath+self.changelogfile)
        except (IOError):
            abyle_output(self.changelogfile+"_xmlparsing", "", "", str(sys.exc_info()[1]))

    def getChangelog(self):
        self.clstr = "cl"
        self.clstr_l2 = "log"
        self.configarr = []
        self.configvar = ''

        for self.cltag in self.abyle_changelog.getElementsByTagName(self.clstr):
            print ()
            print (self.cltag.getAttribute("name")+' Version: '+self.cltag.getAttribute("version"))
            print ()

            for self.cltag_l2 in self.cltag.getElementsByTagName(self.clstr_l2):
                print (self.cltag_l2.getAttribute("version")+' - '+self.cltag_l2.firstChild.nodeValue)
