#from xml.dom.minidom import *
import re
import sys
#from xml.dom.minidom import Node
from abyle_output import abyle_output

try:
    from lxml import etree
except (ImportError):
    abyle_output("xml parser import error, please install python lxml package", "", "", str(sys.exc_info()[1]), "red")
    sys.exit(1)

class abyleparse:
    def __init__(self, fwconfigpath, interface, rulesfile, ipt_xmlconfig, excludedInterfaces, verbose=True):
        self.classname = "abyleparse"
        self.verbose=verbose
        self.fwconfigpath = fwconfigpath
        self.pinterface = interface
        self.rulesfile = rulesfile
        self.iptflagsfile = ipt_xmlconfig
        self.rulesarray = []
        self.iptflags_dict = {}
        self.excludedInterfaces = excludedInterfaces
        self.allowping = ""

        if self.verbose:
           abyle_output("abyle_xml_parser ("+self.pinterface+")", "", "", self.classname+" object created.")

        try:
            #old            self.iptflags_config = xml.dom.minidom.parse(self.fwconfigpath+self.iptflagsfile).documentElement
            self.iptflags_config = etree.parse(self.fwconfigpath+self.iptflagsfile)
            if self.excludedInterfaces.count(self.pinterface) > 0:
               #old self.rules_config = xml.dom.minidom.parse(self.fwconfigpath+self.rulesfile)
               self.rules_config = etree.parse(self.fwconfigpath+self.rulesfile)

            elif self.pinterface == "default":
                #old self.rules_config = xml.dom.minidom.parse(self.fwconfigpath+self.rulesfile)
                self.rules_config = etree.parse(self.fwconfigpath+self.rulesfile)
            else:
                # old self.rules_config = xml.dom.minidom.parse(self.fwconfigpath+'interfaces/'+self.pinterface+'/'+self.rulesfile)
                self.rules_config = etree.parse(self.fwconfigpath+'interfaces/'+self.pinterface+'/'+self.rulesfile)
        except (IOError):
            abyle_output(self.pinterface+"_xmlparsing", "", "", sys.exc_info()[1])

    def getIpTablesFlags(self):
        self.methodname="getIpTablesFlags(self)"

        if self.verbose:
           abyle_output("abyle_xml_parser", "", "", "launched "+self.methodname+" of "+self.classname+".")

        iptflags_dict_temp = {}

        subflag_dict_temp = {}
        subflag_cliswitch_dict_temp = {}

        interface_flag = self.iptflags_config.xpath('/flags/flag/cfgname[text()="interface"]/@cli_switch')
        interface_flag = interface_flag[0]


        portforwarding_destination_flag = self.iptflags_config.xpath('/flags/flag/cfgname[text()="destination_portforwarding"]/@cli_switch')
        portforwarding_destination_flag = portforwarding_destination_flag[0]

        transparent_toport_flag = self.iptflags_config.xpath('/flags/flag/cfgname[text()="toport_transproxy"]/@cli_switch')
        transparent_toport_flag = transparent_toport_flag[0]

        outside_interface_flag = self.iptflags_config.xpath('/flags/flag/cfgname[text()="outside_interface"]/@cli_switch')
        outside_interface_flag = outside_interface_flag[0]

        # get all flag nodes by xpath
        iptflag_nodes = self.iptflags_config.xpath("/flags/flag")

        # get all index attributes from flag tag nodes
        # fill dict with: index -> flag value (e.g. 1 -> interface)
        cnt = 0
        for node in iptflag_nodes:
            subflags = ""
            attribute_nodes = iptflag_nodes[cnt].xpath("./@index")
            self.attributestr = ""
            for attribute in attribute_nodes:
#                tempAtrribute = iptflag_nodes[cnt].SubElement.tag #.SubElement('cfgname')[0].firstChild.nodeValue
                tempAtrribute = iptflag_nodes[cnt][:1]
                #print (etree.tostring(tempAtrribute))
                iptflags_dict_temp[attribute]=tempAtrribute
                subflags = self.iptflags_config.xpath('/flags/flag/cfgname[text()="'+tempAtrribute[0].text+'"]/../subflag[text()]')

                if len(subflags) > 0:
                    tempSubflags = ""
                    tempSubflagsCliSwitch = ""
                    sfcnt = 0
                    for subflag in subflags:
                        if sfcnt == 0:
                            tempSubflags = subflags[sfcnt].text
                            tempSubflagsCliSwitch = subflags[sfcnt].get("cli_switch").strip()
                        else:
#                            tempSubflags = tempSubflags+";"+subflags[sfcnt].firstChild.nodeValue
                            tempSubflags = tempSubflags+";"+subflags[sfcnt].text
                            tempSubflagsCliSwitch = tempSubflagsCliSwitch+";"+subflags[sfcnt].get("cli_switch").strip()
                        sfcnt = sfcnt+1
                    subflag_dict_temp[attribute]=tempSubflags
                    subflag_cliswitch_dict_temp[attribute]=tempSubflagsCliSwitch

            cnt = cnt + 1

        if self.verbose:
           abyle_output("abyle_xml_parser", "", "", self.methodname+" (iptflags_dict_temp) "+str(iptflags_dict_temp))
           abyle_output("abyle_xml_parser", "", "", self.methodname+" (interface_flag) "+str(interface_flag))
           abyle_output("abyle_xml_parser", "", "", self.methodname+" (portforwarding_destination_flag) "+str(portforwarding_destination_flag))
           abyle_output("abyle_xml_parser", "", "", self.methodname+" (transparent_toport_flag) "+str(transparent_toport_flag))
           abyle_output("abyle_xml_parser", "", "", self.methodname+" (outside_interface_flag) "+str(outside_interface_flag))
           abyle_output("abyle_xml_parser", "", "", self.methodname+" (subflag_dict_temp) "+str(subflag_dict_temp))
           abyle_output("abyle_xml_parser", "", "", self.methodname+" (subflag_cliswitch_dict_temp) "+str(subflag_cliswitch_dict_temp))


        return iptflags_dict_temp, interface_flag, portforwarding_destination_flag, transparent_toport_flag, outside_interface_flag, subflag_dict_temp, subflag_cliswitch_dict_temp


    def flagCheck(self,flagvalue,flagname, indexNumber, iptflags_config):
        self.methodname="flagCheck(self,"+str(flagvalue)+","+str(flagname)+","+str(indexNumber)+","+str(iptflags_config)+")"
        self.flagvalue = flagvalue
        self.flagname = flagname
        valueSupport = ""
        if self.verbose:
           abyle_output("abyle_xml_parser", "", "", "launched "+self.methodname+" of "+self.classname+".")

        # check if this flag supports values

        # this xpath expression selects the value arguemnt of the given cli_switch argument under the given index number
        valueSupport = iptflags_config.xpath('/flags/flag[@index="'+str(indexNumber)+'"]//*[@cli_switch="'+flagname+'"]/@value')
        valueSupport = valueSupport[0]

        if valueSupport == "no":
            self.flagstr = self.flagname+' '
        else:

            if not self.flagvalue:
                self.flagstr = ''
            else:
                self.flagstr = self.flagname+' '+self.flagvalue+' '

        return self.flagstr

    # an abstract method to parse xml traffic rules or portforwarding rules ...
    def getAbstractXmlRules(self, xpathToMainNode):
        self.methodname="getAbstractXmlRules(self,"+xpathToMainNode+")"

        if self.verbose:
           abyle_output("abyle_xml_parser", "", "", "launched "+self.methodname+" of "+self.classname+".")

        # xpathToMainNode example for access rules: "/interface/rules/traffic"

        self.abstractRulesArray = []
        self.iptflags_indecies = []

        if self.allowping == "yes":
            self.rules_config = etree.parse(self.fwconfigpath+self.rulesfile)

        if xpathToMainNode.find("masquerading") > 0:
            self.rules_config = etree.parse(self.fwconfigpath+'interfaces/'+self.pinterface+'/'+self.rulesfile)

        # parse the iptables flags config file, getIpTablesFlags returns:
        # -  a dict of iptablesflags e.g.: 11 -> destination or 12 -> destination-port
        # -  a sorted array of all available index numbers e.g: 1,2,3,...,12
        # -  the iptables cli switch for the interface argument: e.g: -i
        # -  special flag iptables cli switch for portforwarding destination
        # -  transparent proxy to-port flag
        # -  masquerading interface flag (outside instead of inside)
        # -  subflag dictionary
        self.iptflags_dict, interface, portfwdDestFlag, transproxyToPortFlag, outsideInterfaceFlag, subflags_dict, subflags_cliswitch_dict = self.getIpTablesFlags()

        # extract keys (index numbers) in an array and sort it
        #self.iptflags_indecies = list(self.iptflags_dict.keys())
        for tempIndex in list(self.iptflags_dict.keys()):
               self.iptflags_indecies.append(int(tempIndex))
        self.iptflags_indecies.sort()

        if self.verbose:
           abyle_output("abyle_xml_parser", "", "", self.methodname+" - self.iptflags_indecies (sorted) "+str(self.iptflags_indecies)+".")

        if xpathToMainNode.find("head") > 0:
            blockchain = self.rules_config.xpath("/interface/blockruleshead/@blockchain")
            blockchain = blockchain[0]
            blockchain_create_string = " -N "+blockchain
            self.abstractRulesArray.append(blockchain_create_string)


        if xpathToMainNode.find("masquerading") > 0:
            self.interfacestr = outsideInterfaceFlag+' '+self.pinterface+' '
        else:
            # set the interface string to e.g.: -i eth0
            self.interfacestr = interface+' '+self.pinterface+' '

        # get list of rules e.g. all traffic nodes or all portforwarding nodes
        abstractNodes = self.rules_config.xpath(xpathToMainNode)


        if self.verbose:
           abyle_output("abyle_xml_parser", "", "", self.methodname+" - abstractNodes "+str(abstractNodes)+".")

        cnt=0
        for node in abstractNodes:
            # get list of all attributes of an rule node
            #abstractAttributeNodes = abstractNodes[cnt].xpath("./@*")
            abstractAttributeNodes = abstractNodes[cnt].keys()
            if self.verbose:
                abyle_output("abyle_xml_parser", "", "", self.methodname+" - "+str(node.tag)+" abstractNode AttributeNames "+str(abstractNodes[cnt].keys())+".")
#                abyle_output("abyle_xml_parser", "", "", self.methodname+" - "+str(node.tag)+" attributes "+str(abstractAttributeNodes)+".")
            self.attributestr = ""
            tempDestIpStr = ""
            tempDestPortStr = ""
            tempForwardPortStr = ""




            # loop through iptables flags index number list to build the right order
            for indexNumber in self.iptflags_indecies:

                # get the value of a flag out if the iptables flag dict, e.g.: indexNumber=12 then flag_value = destination
                flag_value = self.iptflags_dict[str(indexNumber)][0].text

                # loop through all found attribute nodes
                for attribute in abstractAttributeNodes:

                    # test if the attribute name is equal to the string in flag value
                    if attribute == flag_value:

                        try:
                            # parse the file with xpath and get the attributenode cli_switch under cfgname which has the searched indexNumber
                            flag_cli_arg_node = self.iptflags_config.xpath("/flags/flag[@index="+str(indexNumber)+"]/cfgname/@cli_switch")

                            #print (flag_cli_arg_node)
                            # extract the value if the attribute node [0] = assuming that the index is unique
                            flag_cli_arg = flag_cli_arg_node[0]


                            # check and build the attribute string with flagCheck()
                            attributeTmpstr = self.flagCheck(str(abstractNodes[cnt].get(attribute)),flag_cli_arg, indexNumber, self.iptflags_config)



                        except (KeyError):
                            abyle_output("abyle_xmlparser.py: parsing error @ iptables flags:", "", "", sys.exc_info()[1], "red")
                            sys.exit(1)

                        if xpathToMainNode.find("portforwarding") > 0 and attribute.name == "destination" :
                            tempDestIpStr = attribute.value

                        elif xpathToMainNode.find("portforwarding") > 0 and attribute.name == "destination-port":
                            tempDestPortStr = attribute.value

                        elif xpathToMainNode.find("portforwarding") > 0 and attribute.name == "forward-port":
                            tempForwardPortStr = attribute.value

                        elif xpathToMainNode.find("transparentproxy") > 0 and attribute.name == "destination":
                            tempDestIpStr = attribute.value

                        elif xpathToMainNode.find("transparentproxy") > 0 and attribute.name == "destination-port":
                            tempDestPortStr = attribute.value

                        else:
                            # append the temp string to the self.attributestr
                            self.attributestr = self.attributestr+attributeTmpstr

                        hasSubflags = "no"
                        for key in subflags_dict.keys():
                            if str(key) == str(indexNumber):
                                hasSubflags = "yes"

                        if hasSubflags == "yes":
                            subattributeTmpstr = ""
                            tempSubflagsArray = subflags_dict[indexNumber].split(';')
                            tempSubflagsCliswitchArray = subflags_cliswitch_dict[indexNumber].split(';')

                            subflagcnt = 0
                            for subflag_value in tempSubflagsArray:

                                for attribute in abstractAttributeNodes:

                                    if attribute.name == subflag_value:

                                        subattributeTmpstr = self.flagCheck(attribute.value,tempSubflagsCliswitchArray[subflagcnt], indexNumber, self.iptflags_config)
                                        self.attributestr = self.attributestr+subattributeTmpstr

                                subflagcnt = subflagcnt + 1


            cnt = cnt + 1

            self.attributestrForward = ""

            if xpathToMainNode.find("portforwarding") > 0:

                # append interface string to the attribute string

                # build the iptablescommand for the PREROUTING chain of the nat table and the FORWARD chain
                if not self.pinterface == "default":
                    self.attributestr = self.interfacestr+self.attributestr


                self.attributestrForward = self.attributestr
                self.attributestrForward = re.sub("PREROUTING","FORWARD",self.attributestrForward)
                self.attributestrForward = re.sub("DNAT","ACCEPT",self.attributestrForward)
                self.attributestrForward = re.sub("-t nat","",self.attributestrForward)
                self.attributestrForward = re.sub("--dport \d{1,5}","",self.attributestrForward)
                self.attributestrForward = self.attributestrForward+" --destination-port "+tempDestPortStr+" --destination "+tempDestIpStr

                self.attributestr = self.attributestr+"--dport "+tempForwardPortStr+" "+portfwdDestFlag+' '+tempDestIpStr+":"+tempDestPortStr



            elif xpathToMainNode.find("transparentproxy") > 0:
                self.attributestr = self.interfacestr+self.attributestr+transproxyToPortFlag+' '+tempDestPortStr

            else:
                if not self.pinterface == "default":
                    self.attributestr = self.interfacestr+self.attributestr

            # append the string to the rules array
            self.abstractRulesArray.append(self.attributestr)

            if not self.attributestrForward == "":
                self.abstractRulesArray.append(self.attributestrForward)




        return self.abstractRulesArray





    def getRules(self):

        self.rulesarray = []
        if self.excludedInterfaces.count(self.pinterface) > 0:
            self.rulesarray = self.getAbstractXmlRules("/interface/excluderule/traffic")
        else:
            self.rulesarray = self.getAbstractXmlRules("/interface/rules/traffic")
        return  self.rulesarray

    def getPortforwarding(self):

        self.rulesarray = []
        self.rulesarray = self.getAbstractXmlRules("/interface/portforwarding/traffic")

        return  self.rulesarray

    def getTproxy(self):

        self.rulesarray = []

        self.rulesarray = self.getAbstractXmlRules("/interface/transparentproxy/traffic")

        return self.rulesarray


    def getLogging(self):

        self.rulesarray = []

        self.rulesarray = self.getAbstractXmlRules("/interface/logging/traffic")

        return self.rulesarray

    def getDefaultRules(self, headOrFoot):

        self.rulesarray = []


        self.rulesarray = self.getAbstractXmlRules("/interface/blockrules"+headOrFoot+"/traffic")


        return self.rulesarray


    def getAllowPing(self):

        self.rulesarray = []

        self.allowping = "yes"

        self.rulesarray = self.getAbstractXmlRules("/interface/pingrule/traffic")

        self.allowping = ""


        return self.rulesarray

    def getMasquerading(self):

        self.allowping = ""

        self.rulesarray = []

        self.rulesarray = self.getAbstractXmlRules("/interface/masquerading/traffic")

        return self.rulesarray
