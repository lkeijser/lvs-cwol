#!/usr/bin/env python

import xmlrpclib
import socket

# Connect to server
s = xmlrpclib.ServerProxy('http://localhost:12219')

# Implement timeout (else RPC request will hang indefinately)
#socket.setdefaulttimeout(60)

def readLine(filename):
    f = open(filename, "r")
    lines = f.readline()
    return lines

LoadAvg = readLine('/proc/loadavg')

myIP = socket.gethostbyname(socket.gethostname())
myLoad = s.pushLoad(LoadAvg,myIP)

print "Pushed current load: " + str(myLoad)

