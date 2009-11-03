import sys
from abyle_output import abyle_output
from xml.dom.minidom import *
import codecs

try:
    from oldxml import xpath
except (ImportError):
    abyle_output("xml config parser import error, please install python xpath modules", "", "", str(sys.exc_info()[1]), "red")
    sys.exit(1)



class abyle_config_write:
    def __init__(self, fwconfigpath, interface, xmlconfig):
        self.fwconfigpath = fwconfigpath
        self.pinterface = interface
        self.xmlconfig = xmlconfig
        self.xmlfile = ""
        self.buildednode = ""


        try:
            if self.pinterface == "default":
                self.abyle_config = xml.dom.minidom.parse(self.fwconfigpath+self.xmlconfig)
                self.xmlfile = self.fwconfigpath+self.xmlconfig
            else:
                self.abyle_config = xml.dom.minidom.parse(self.fwconfigpath+'interfaces/'+self.pinterface+'/'+self.xmlconfig)
                self.xmlfile = self.fwconfigpath+'interfaces/'+self.pinterface+'/'+self.xmlconfig
        except (IOError):
            abyle_output(self.interface+"_config_xmlwriter", "", "", str(sys.exc_info()[1]))

    def buildNewNode(self, nodename, value="", attributes={}):

        doc = Document()

        # create new node object
        newnode = doc.createElement(nodename)

        # create new text node object
        newnode_cdatavalue = doc.createTextNode(value)


        # add the textnode to the xml node
        newnode.appendChild(newnode_cdatavalue)

        # add attributes to xml node
        for attribute in attributes.keys():
            attribute_node = doc.createAttribute(attribute)
            newnode.setAttributeNode(attribute_node)
            newnode.setAttribute(attribute, attributes[attribute])

        self.buildednode = newnode

        return



    def AddBuildedNode(self,xpathstring):

        if not self.buildednode == "":

            parentnode = xpath.Evaluate(xpathstring , self.abyle_config)
            newnode_blanktextnode = self.abyle_config.createTextNode("\n")
            parentnode[0].appendChild(self.buildednode)
            parentnode[0].appendChild(newnode_blanktextnode)

            xmlfileWriteHandle = open(self.xmlfile,"wb+")
            writer = codecs.lookup('utf-8')[3](xmlfileWriteHandle)
            self.abyle_config.writexml(writer, encoding='utf-8', newl="")
            writer.close()

        else:
            abyle_output("error abyle_xml_writer has not created a new node yet.", "", "", str(msg), "red")
            sys.exit(1)

        return
