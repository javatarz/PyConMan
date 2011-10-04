#-------------------------------------------------------------------------------
# Name:        SpeedManager
# Purpose: To run the RouterManager class
#
# Author:      Karun AB
#
# Created:     19/09/2011
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

from RouterManager import RouterManager

def main():
    routerMgr = RouterManager()

    isDslConnected = routerMgr.isDslUp()
    if isDslConnected:
        isConnectionSpeedCorrect = routerMgr.isSpeedCorrect()

        if isConnectionSpeedCorrect:
            isConnected = routerMgr.isInterfaceUp()
            if isConnected:
                print "Everything is peachy!"
            else:
                print "Attempting to connect to the internet.."
                routerMgr.routerConnect()
        else:
            print "Speed is below par. Rebooting router."
            routerMgr.routerReboot()
    else:
        print "DSL is not connected. Check the cable and then raise a trouble ticket."
    pass

if __name__ == '__main__':
    main()