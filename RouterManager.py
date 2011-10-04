#-------------------------------------------------------------------------------
# Name:        PyConMan
# Purpose: To manage the WAG120N by checking it's DSL speed and resetting it if it's too low
#
# Author:      Karun
#
# Created:     18/09/2011
# Copyright:   (c) Karun 2011
# Licence:     Beerware Rev. 42 (http://en.wikipedia.org/wiki/Beerware)
#
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# "THE BEER-WARE LICENSE" (Revision 42):
# <me@karunab.com> wrote this file. As long as you retain this notice you can
# do whatever you want with this stuff. If we meet some day, and you think this
# stuff is worth it, you can buy me a beer in return - Karun AB (JAnderton)
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import urllib2
import logging
from BeautifulSoup import BeautifulSoup

class RouterManager:
    # Config
    __minSpeedUp = 500
    __minSpeedDown = 1000
    # Constants
    __urlPrefix = "http://"
    __urlSuffix = "/setup.cgi?";
    __pageStatus = "Status.htm"
    __pageDslStatus = "DSL_status.htm"
    __todoReboot = "reboot"
    __todoConnect = "connect"
    __indicatorNextFile = "next_file="
    __indicatorTodo = "todo="
    __tagNameDownSpeed = "vt_dsr"
    __tagNameUpSpeed = "vt_usr"
    __tagNameInterface = "vt_if"
    __tagNameDslStatus = "vstatus"
    __parseKBits = " kbps"
    __textDslUp = "Up"
    __textInterfaceConnected = "Connected"

    # Public functions
    def isDslUp(self):
        isDslConnected = self.__parseDslStatusPageForStatus()
        if  isDslConnected == True:
            self.__log("DSL is connected!")
        else:
            self.__log("DSL is not connected. Check cable/raise a TT.")
        return isDslConnected

    def isSpeedCorrect(self):
        isDslSpeedCorrect = self.__parseDslStatusPageForSpeed()
        if  isDslSpeedCorrect == True:
            self.__log("DSL connection is up to speed.")
        else:
            self.__log("DSL connection is below speed. Needs reboot.")
        return isDslSpeedCorrect

    def isInterfaceUp(self):
        isInternetConnected = self.__parseStatusPageForInterfaceStatus()
        if  isInternetConnected == True:
            self.__log("Internet is connected!")
        else:
            self.__log("Internet is not connected. Triggering connect.")
        return isInternetConnected

    def routerReboot(self):
        self.__performAction(self.__todoReboot)

    def routerConnect(self):
        self.__performAction(self.__todoConnect)

    # Constructor
    def __init__(self, url="192.168.1.1", username="admin", password="admin", resetOnDownload=True, resetOnUpload=False, debugMode=False):
        self.__url = self.__padURL(url)
        self.__username = username
        self.__password = password

        self.__resetOnDownload = resetOnDownload
        self.__resetOnUpload = resetOnUpload
        self.__debugMode = debugMode

    # Private Functional Functions
    def __parseStatusPageForInterfaceStatus(self):
        page = self.__getStatusPage()
        table = BeautifulSoup(self.__getConnection(page).urlopen(page))('table', {'class' : 'std'})[1]

        for tRows in table.findAll('tr'):
            tDefs = tRows.findAll('td')
            if self.__tagNameInterface in `tDefs[0]`:
                interfaceStatus = self.__stripUsing(tDefs[1], None)
                self.__log("Interface Status = " + interfaceStatus)
                break;

        return True if interfaceStatus == self.__textInterfaceConnected else False

    def __parseDslStatusPageForStatus(self):
        page = self.__getDslStatusPage()
        table = BeautifulSoup(self.__getConnection(page).urlopen(page))('table', {'class' : 'std'})[0]
        isResetRequired = False

        for tRows in table.findAll('tr'):
            tDefs = tRows.findAll('td')
            if self.__tagNameDslStatus in `tDefs[0]`:
                dslStatus = self.__stripUsing(tDefs[1], None)
                self.__log("DSL Status = " + dslStatus)
                break;
        
        return True if dslStatus == self.__textDslUp else False

    def __parseDslStatusPageForSpeed(self):
        page = self.__getDslStatusPage()
        table = BeautifulSoup(self.__getConnection(page).urlopen(page))('table', {'class' : 'std'})[0]
        isResetRequired = False

        for tRows in table.findAll('tr'):
            tDefs = tRows.findAll('td')
            if self.__tagNameDownSpeed in `tDefs[0]`:
                downSpeed = self.__getSpeedFromTD(tDefs[1])
                if int(downSpeed) < self.__minSpeedDown:
                    self.__log("ERROR! Down speed (" + downSpeed + " is less than minimum value (" + str(self.__minSpeedDown) + ")")
                    if self.__resetOnDownload == True:
                        isResetRequired = True
                else:
                    self.__log("Down speed is fine (" + downSpeed + ")")
            elif self.__tagNameUpSpeed in `tDefs[0]`:
                upSpeed = self.__getSpeedFromTD(tDefs[1])
                if int(upSpeed) < self.__minSpeedUp:
                    self.__log("WARNING! Upload speed (" + upSpeed + " is less than minimum value (" + str(self.__minSpeedUp) + ")")
                    if self.__resetOnUpload == True:
                        isResetRequired = True
                else:
                    self.__log("Upload speed is fine (" + upSpeed + ")")

        return False if isResetRequired else True

    def __performAction(self, action):
        page = self.__getActionPage(action)
        self.__log("Performed Action to: " + page)
        #self.__getConnection(page).urlopen(page)

    # Private Utility Functions
    def __getConnection(self, page):
        password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        password_mgr.add_password(None, page, self.__username, self.__password)
        urllib2.install_opener(urllib2.build_opener(urllib2.HTTPBasicAuthHandler(password_mgr)))

        return urllib2

    def __padURL(self, url):
        url = url.rstrip("/")
        if "/" not in url.replace("//", ""):
            url += self.__urlSuffix
        if "http" not in url:
            url = self.__urlPrefix + url

        return url

    def __log(self, message):
        if self.__debugMode:
            print ">>>>>", message
    
    def __getSpeedFromTD(self, td):
        return self.__stripUsing(td, self.__parseKBits)

    def __stripUsing(self, htmlText, textToStrip):
        return ''.join(htmlText.findAll(text=True)).strip().rstrip(textToStrip)

    def __getStatusPage(self):
        return self.__url + self.__indicatorNextFile + self.__pageStatus

    def __getDslStatusPage(self):
        return self.__url + self.__indicatorNextFile + self.__pageDslStatus

    def __getActionPage(self, action):
        return self.__url + self.__indicatorTodo + action