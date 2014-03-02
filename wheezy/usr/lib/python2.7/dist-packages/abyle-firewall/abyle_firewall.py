import re
import os
import string
import time
import datetime
import sys
from abyle_xmlparser import abyleparse
from abyle_execute import abyle_execute
from abyle_config_xmlparser import abyle_config_parse
from xml.sax.handler import ContentHandler
from xml.sax import make_parser
from abyle_log import logger

control = logger("abyle-control")

class abyle_firewall:
    def __init__(self, dryrun, iptablesbin, fwconfigpath, rulesfile, ipt_xmlconfig, xmlconfig, echocmd, logfile, verbose):
        self.naptime = 10 # milliseconds
        self.dryrun = dryrun
        self.iptablesbin = iptablesbin
        self.fwconfigpath = fwconfigpath
        self.rulesfile = rulesfile
        self.ipt_xmlconfig = ipt_xmlconfig
        self.xmlconfig = xmlconfig
        self.logfile = logfile
        self.verbose = verbose

        self.executioner = abyle_execute()

        self.echocmd = echocmd

        global_config = abyle_config_parse(fwconfigpath, "default", xmlconfig, self.verbose)

        self.excludedInterfaces = global_config.getConfig("excluded_interfaces")

        try:
            self.tcpabort_file = global_config.getConfig("tcpabortfile")
        except IndexError:
            self.tcpabort_file = "/proc/sys/net/ipv4/tcpicmpbcastfile_abort_on_overflow"

        try:
            self.icmpbcastreply_file = global_config.getConfig("icmpbcastfile")
        except IndexError:
            self.icmpbcastreply_file = "/proc/sys/net/ipv4/icmp_echo_ignore_broadcasts"

        try:
            self.dynaddresshack_file = global_config.getConfig("dynaddresshackfile")
        except IndexError:
            self.dynaddresshack_file = "/proc/sys/net/ipv4/ip_dynaddr"

        try:
            self.ipv4conf_path = global_config.getConfig("ipv4confpath")
        except IndexError:
            self.ipv4conf_path = "/proc/sys/net/ipv4/conf/"

        try:
            self.antispoofing_file = global_config.getConfig("antispoofingfile")
        except IndexError:
            self.antispoofing_file = "rp_filter"

        try:
            self.syncookiefile =  global_config.getConfig("syncookiefile")
        except IndexError:
            self.syncookiefile = "/proc/sys/net/ipv4/tcp_syncookies"

        try:
            self.ipv4forwardfile = global_config.getConfig("ipv4forwardfile")
        except IndexError:
            self.ipv4forwardfile = "/proc/sys/net/ipv4/ip_forward"

        try:
            self.syncookie = str(global_config.getConfig("syncookie")).upper()
        except IndexError:
            self.syncookie = "YES"

        try:
            self.ipv4forward = str(global_config.getConfig("ipv4forward")).upper()
        except IndexError:
            self.syncookie = "NO"

        try:
            self.tcpabort = str(global_config.getConfig("aborttcp")).upper()
        except IndexError:
            self.tcpabort = "NO"

        try:
            self.icmpbcastreply = str(global_config.getConfig("answericmpbroadcast")).upper()
        except IndexError:
            self.icmpbcastreply = "NO"

        try:
            self.dynaddresshack = str(global_config.getConfig("dynaddresshack")).upper()
        except IndexError:
            self.dynaddresshack = "NO"


        try:
            self.proxyarp_file = global_config.getConfig("proxyarpfile")
        except IndexError:
            self.proxyarp_file = "proxy_arp"

        try:
            self.srouting_file = global_config.getConfig("sroutingfile")
        except IndexError:
            self.srouting_file = "accept_source_route"

        try:
            self.icmpredirects_file = global_config.getConfig("icmprdrsfile")
        except IndexError:
            self.icmpredirects_file = "accept_redirects"

        try:
            self.secureicmpredirects_file = global_config.getConfig("icmpsecurerdrsfile")
        except IndexError:
            self.secureicmpredirects_file = "secure_redirects"

        try:
            self.martians_file = global_config.getConfig("martiansfile")
        except IndexError:
            self.martians_file = "log_martians"

        try:
            self.bootprelay_file = global_config.getConfig("bootprelayfile")
        except IndexError:
            self.bootprelay_file = "bootp_relay"

        log = logger("firewall")

        if not self.tcpabort == "NO":
            stdOut, stdErr = self.executioner.run(self.echocmd+' 1 > '+self.tcpabort_file, self.dryrun)
            log.info("ipv4 send TCP-RST on full buffer is activated")
        else:
            stdOut, stdErr = self.executioner.run(self.echocmd+' 0 > '+self.tcpabort_file, self.dryrun)
            log.info("ipv4 send TCP-RST on full buffer is deactivated")


        if not self.icmpbcastreply == "NO":
            stdOut, stdErr = self.executioner.run(self.echocmd+' 1 > '+self.icmpbcastreply_file, self.dryrun)
            log.info("ipv4 reply to ICMP Broadcasts is deactivated")
        else:
            stdOut, stdErr = self.executioner.run(self.echocmd+' 0 > '+self.icmpbcastreply_file, self.dryrun)
            log.info("ipv4 reply to ICMP Broadcasts is activated")


        if not self.dynaddresshack == "NO":
            stdOut, stdErr = self.executioner.run(self.echocmd+' 1 > '+self.dynaddresshack_file, self.dryrun)
            log.info("ipv4 dynamic address hack activated")
        else:
            stdOut, stdErr = self.executioner.run(self.echocmd+' 0 > '+self.dynaddresshack_file, self.dryrun)
            log.info("ipv4 dynamic address hack deactivated")

        if not self.ipv4forward == "NO":
            stdOut, stdErr = self.executioner.run(self.echocmd+' 1 > '+self.ipv4forwardfile, self.dryrun)
            log.info("ipv4 forwarding activated")
        else:
            stdOut, stdErr = self.executioner.run(self.echocmd+' 0 > '+self.ipv4forwardfile, self.dryrun)
            log.info("ipv4 forwarding deactivated")

        if not self.syncookie == "NO":
            stdOut, stdErr = self.executioner.run(self.echocmd+' 1 > '+self.syncookiefile, self.dryrun)
            log.info("syncookie activated")
        else:
            stdOut, stdErr = self.executioner.run(self.echocmd+' 0 > '+self.syncookiefile, self.dryrun)
            log.info("syncookie deactivated")

        self.default_config = abyleparse(self.fwconfigpath, "default", self.rulesfile, self.ipt_xmlconfig, self.excludedInterfaces, self.verbose)
        self.defaultrules =  self.default_config.getDefaultRules("head")
        self.defaultrules =  self.default_config.getBypassRules("bypass")

        for drule in self.defaultrules:
            log.info("default-rule: "+drule)
            stdOut, stdErr = self.executioner.run(self.iptablesbin+' '+drule, self.dryrun)


    def check_well_formedness(self, file):
        try:
            saxparser = make_parser()
            saxparser.setContentHandler(ContentHandler())
            saxparser.parse(file)
            return "ok"
        except (Exception):
            return str(file) + " is NOT well-formed! " + sys.exc_info()[1]


    def buildUpFinish(self, verbose):
        self.verbose = verbose

        log = logger("abyle-firewall")

        self.defaultrules =  self.default_config.getDefaultRules("foot")
        log.info("SETTING UP DEFAULT RULES:")
        for drule in self.defaultrules:
            log.info("default-rule: "+drule)
            stdOut, stdErr = self.executioner.run(self.iptablesbin+' '+drule, self.dryrun)

    def buildUp(self,protectedif,fwconfigpath, verbose):
        self.verbose = verbose

        self.protectedif = protectedif
        self.fwconfigpath = fwconfigpath

        log = logger("abyle-firewall")
	self.control = control
        if self.protectedif in self.excludedInterfaces:
            log.start_stop("securing "+self.protectedif, "EXCLUDED")
        else:
            log.start_stop("securing "+self.protectedif)

        if os.path.exists(self.fwconfigpath+'/'+'interfaces/'+self.protectedif) or self.excludedInterfaces.count(self.protectedif) > 0:

            if self.excludedInterfaces.count(self.protectedif) == 0:

                tempFileStr = self.fwconfigpath+'interfaces/'+self.protectedif+'/'+self.xmlconfig
                checkWellformed = self.check_well_formedness(tempFileStr)
                if checkWellformed != "ok":
                    log.error(checkWellformed)
                    sys.exit(1)
                else:
                    log.info(self.fwconfigpath+"interfaces/"+self.protectedif+"/"+self.xmlconfig+" is a well-formed xml")

                #parse the config file
                self.if_config = abyle_config_parse(self.fwconfigpath, self.protectedif, self.xmlconfig, self.verbose)

                try:
                    self.antispoofing = self.if_config.getConfig("antispoofing")
                except IndexError:
                    self.antispoofing = "NO"

                try:
                    self.proxyarp = self.if_config.getConfig("proxyarp")
                except IndexError:
                    self.proxyarp = "NO"

                try:
                    self.srouting = self.if_config.getConfig("sourcerouting")
                except IndexError:
                    self.srouting = "NO"

                try:
                    self.icmprdrs = self.if_config.getConfig("icmpredirects")
                except IndexError:
                    self.icmprdrs = "NO"

                try:
                    self.sicmprdrs = self.if_config.getConfig("secureicmpredirects")
                except IndexError:
                    self.sicmprdrs  = "NO"

                try:
                    self.martians = self.if_config.getConfig("martianslogging")
                except IndexError:
                    self.martians = "NO"

                try:
                    self.bootprelay = self.if_config.getConfig("drop0slash8packets")
                except IndexError:
                    self.bootprelay = "NO"

                try:
                    self.logging = self.if_config.getConfig("logging")
                except IndexError:
                    self.logging = "NO"

                try:
                    self.allowping = self.if_config.getConfig("allowping")
                except IndexError:
                    self.allowping = "NO"

                try:
                    self.masquerading = self.if_config.getConfig("masquerading")
                except IndexError:
                    self.masquerading = "NO"

                try:
                    self.portforwarding = self.if_config.getConfig("portforwarding")
                except IndexError:
                    self.portforwarding = "NO"

                try:
                    self.tproxy = self.if_config.getConfig("transparent_proxy")
                except IndexError:
                    self.tproxy = "NO"

                # end parse the config file



                self.antispoofing = str(self.antispoofing).upper()
                self.proxyarp = str(self.proxyarp).upper()
                self.srouting = str(self.srouting).upper()
                self.icmprdrs = str(self.icmprdrs).upper()
                self.sicmprdrs = str(self.sicmprdrs).upper()
                self.martians = str(self.martians).upper()
                self.bootprelay = str(self.bootprelay).upper()
                self.logging = str(self.logging).upper()
                self.allowping = str(self.allowping).upper()
                self.masquerading = str(self.masquerading).upper()
                self.portforwarding = str(self.portforwarding).upper()
                self.tproxy = str(self.tproxy).upper()


                # interface specific protections

                if self.proxyarp == "YES":
                    stdOut, stdErr = self.executioner.run(self.echocmd+' 1 > '+self.ipv4conf_path+self.protectedif+'/'+self.proxyarp_file, self.dryrun)
                    log.info("proxy arp activated for "+self.protectedif)
                else:
                    stdOut, stdErr = self.executioner.run(self.echocmd+' 0 > '+self.ipv4conf_path+self.protectedif+'/'+self.proxyarp_file, self.dryrun)
                    log.info("proxy arp deactivated for "+self.protectedif)

                if self.srouting == "YES":
                    stdOut, stdErr = self.executioner.run(self.echocmd+' 1 > '+self.ipv4conf_path+self.protectedif+'/'+self.srouting_file, self.dryrun)
                    log.info("allow source routing activated for "+self.protectedif)
                else:
                    stdOut, stdErr = self.executioner.run(self.echocmd+' 0 > '+self.ipv4conf_path+self.protectedif+'/'+self.srouting_file, self.dryrun)
                    log.info("allow source routing deactivated for "+self.protectedif)

                if self.icmprdrs == "YES":
                    stdOut, stdErr = self.executioner.run(self.echocmd+' 1 > '+self.ipv4conf_path+self.protectedif+'/'+self.icmpredirects_file, self.dryrun)
                    log.info("icmp redirects activated for "+self.protectedif)
                else:
                    stdOut, stdErr = self.executioner.run(self.echocmd+' 0 > '+self.ipv4conf_path+self.protectedif+'/'+self.icmpredirects_file, self.dryrun)
                    log.info("icmp redirects deactivated for "+self.protectedif)

                if self.sicmprdrs == "YES":
                    stdOut, stdErr = self.executioner.run(self.echocmd+' 1 > '+self.ipv4conf_path+self.protectedif+'/'+self.secureicmpredirects_file, self.dryrun)
                    log.info("secure icmp redirects activated for "+self.protectedif)
                else:
                    stdOut, stdErr = self.executioner.run(self.echocmd+' 0 > '+self.ipv4conf_path+self.protectedif+'/'+self.secureicmpredirects_file, self.dryrun)
                    log.info("secure icmp redirects deactivated for "+self.protectedif)

                if self.martians == "YES":
                    stdOut, stdErr = self.executioner.run(self.echocmd+' 1 > '+self.ipv4conf_path+self.protectedif+'/'+self.martians_file, self.dryrun)
                    log.info("martians logging activated for "+self.protectedif)
                else:
                    stdOut, stdErr = self.executioner.run(self.echocmd+' 0 > '+self.ipv4conf_path+self.protectedif+'/'+self.martians_file, self.dryrun)
                    log.info("martians logging deactivated for "+self.protectedif)

                if self.bootprelay == "YES":
                    stdOut, stdErr = self.executioner.run(self.echocmd+' 1 > '+self.ipv4conf_path+self.protectedif+'/'+self.bootprelay_file, self.dryrun)
                    log.info("dropping packets from 0/8 activated for "+self.protectedif)
                else:
                    stdOut, stdErr = self.executioner.run(self.echocmd+' 0 > '+self.ipv4conf_path+self.protectedif+'/'+self.bootprelay_file, self.dryrun)
                    log.info("dropping packets from 0/8 deactivated for "+self.protectedif)

                if self.antispoofing == "YES":
                    stdOut, stdErr = self.executioner.run(self.echocmd+' 1 > '+self.ipv4conf_path+self.protectedif+'/'+self.antispoofing_file, self.dryrun)
                    log.info("anti spoofing activated for "+self.protectedif)
                else:
                    stdOut, stdErr = self.executioner.run(self.echocmd+' 0 > '+self.ipv4conf_path+self.protectedif+'/'+self.antispoofing_file, self.dryrun)
                    log.info("anti spoofing deactivated for "+self.protectedif)


            self.if_config = abyleparse(self.fwconfigpath, self.protectedif, self.rulesfile, self.ipt_xmlconfig, self.excludedInterfaces, self.verbose)
            self.rules =  self.if_config.getRules()
            log_rules = logger("firewall-rule")
            
            for rule in self.rules:
                time.sleep(self.naptime / 1000.0)
                log_rules.info(self.protectedif+" "+rule)
                stdOut, stdErr = self.executioner.run(self.iptablesbin+' '+rule, self.dryrun)

            if self.excludedInterfaces.count(self.protectedif) == 0:
                if self.portforwarding == "YES":
                    self.portforwarding = self.if_config.getPortforwarding()
                    for portfwd in self.portforwarding:
                        log.info(self.protectedif+" "+portfwd)
                        stdOut, stdErr = self.executioner.run(self.iptablesbin+' '+portfwd, self.dryrun)
                else:
                    log.info(self.protectedif+" "+"PORTFORWARDING DISABLED")

                if self.tproxy == "YES":
                    self.tproxy = self.if_config.getTproxy()
                    for transproxy in self.tproxy:
                        log.info(self.protectedif+" "+transproxy)
                        stdOut, stdErr = self.executioner.run(self.iptablesbin+' '+transproxy, self.dryrun)
                else:
                    log.info(self.protectedif+" "+"TRANSPARENT PROXY DISABLED")

                if self.logging == "YES":
                    self.logging = self.if_config.getLogging()
                    for log in self.logging:
                        log.info(self.protectedif+" "+log)
                        stdOut, stdErr = self.executioner.run(self.iptablesbin+' '+log, self.dryrun)
                else:
                    log.info(self.protectedif+" "+"LOGGING DISABLED")

                if self.allowping == "YES":
                    self.allowping = self.if_config.getAllowPing()
                    for ap in self.allowping:
                        log.info(self.protectedif+" "+ap)
                        stdOut, stdErr = self.executioner.run(self.iptablesbin+' '+ap, self.dryrun)
                else:
                    log.info(self.protectedif+" "+"ALLOWPING DISABLED")

                if self.masquerading == "YES":
                    self.masquerading = self.if_config.getMasquerading()
                    for mg in self.masquerading:
                        log.info(self.protectedif+" "+mg)
                        stdOut, stdErr = self.executioner.run(self.iptablesbin+' '+mg, self.dryrun)
                else:
                    log.info(self.protectedif+" "+"MASQUERADING DISABLED")

        else:
            log.error("no directory found for interface "+self.protectedif+" in "+self.fwconfigpath+"interfaces/")
