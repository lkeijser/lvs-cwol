#!/usr/bin/env python

#--------- PREFERENCES ---------#
# Bind to IP/port
serverIP = '192.168.122.42'
serverPort = 12219
# Set thresholds
LoadAvg_crit_threshold = '0.80'
LoadAvg_warn_threshold = '0.50'
# 
#------- END PREFERENCES -------#


from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
import string,socket

# convert hex2dec
def hex2dec(s):
    return int(s, 16)

def readLines(filename):
    f = open(filename, "r")
    lines = f.readlines()
    return lines

# Get realserver IP-addresses from /proc/net/ip_vs and build an ACL
# This ACL should be built with the following format:
# VIP:RIP:WEIGHT:WEIGHTCURRENT (initially, WEIGHTCURRENT is the same as WEIGHT)
# Right now it's built as RIP:WEIGHT:WEIGHTCURRENT
accessList={}
for line in readLines('/proc/net/ip_vs'):
	if line.split()[0] == '->':
		if len(str(line.split()[1])) == 13:
			rsIP = line.split()[1].split(':')[0]
			rsIPfst = rsIP[0:2]	# first octet
			rsIPscd = rsIP[2:4]	# second octet
			rsIPtrd = rsIP[4:6]	# third octet
			rsIPfth = rsIP[6:8]	# fourth octet
			# compile IP
			realserverIP = str(hex2dec(rsIPfst)) + "." + str(hex2dec(rsIPscd)) + "." + str(hex2dec(rsIPtrd)) + "." + str(hex2dec(rsIPfth))
			# compile weight
			realserverWeight = [line.split()[3]]
			realserverWeight.append(line.split()[3])
			# add keypair (ip:weight)  to ACL
			accessList[realserverIP] = realserverWeight
			print "Storing IP:weightOrig:weightChange as  " + str(realserverIP) + ":" + str(accessList[realserverIP][0]) + ":" + str(accessList[realserverIP][1])

# Test function pushLoad
def pushLoad_function(LoadAvg, clientIP):
    LoadAvg1 = LoadAvg.split()[0]
    # print "DEBUG: Client reports IP:  %s " % clientIP
    # Determine original weight
    rsWeightOriginal = accessList[clientIP][0]
    # print "DEBUG: Original weight of rs: %s " % rsWeightOriginal
    # Determine changed weight
    rsWeightCurrent = accessList[clientIP][1]
    # print "DEBUG: Current weight of rs: %s " % rsWeightCurrent
    # Determine if CRITICAL threshold is reached
    if float(LoadAvg1) >= float(LoadAvg_crit_threshold):
    	print "CRITICAL: Load Average (1min) threshold (" + str(LoadAvg_crit_threshold) + ") reached: " + LoadAvg1
	rsWeightHalf = int(rsWeightOriginal) - int(rsWeightOriginal)/2
	# Only change weight if not already changed
	if not int(rsWeightCurrent) == int(rsWeightHalf):
    	    print "Changing realserver's weight to 50% of original"
	    print "ipvsadm -e -t vip:port -r ip:port -w " + str(rsWeightHalf)
	    # Setting new weight in list
	    accessList[clientIP][1] = rsWeightHalf
	else:
	    print "Weight already changed. Doing nothing."
    # Determine if WARNING threshold is reached
    elif float(LoadAvg1) >= float(LoadAvg_warn_threshold):
    	print "WARNING: Load Average (1min) threshold (" + str(LoadAvg_warn_threshold) + ") reached: " + LoadAvg1
	rsWeightQuart = int(rsWeightOriginal) - int(rsWeightOriginal)/4
	# Only change weight if not already changed
        if not int(rsWeightCurrent) == int(rsWeightQuart):
            print "Changing realserver's weight to 75% of original"
            print "ipvsadm -e -t vip:port -r ip:port -w " + str(rsWeightQuart)
            # Setting new weight in list
            accessList[clientIP][1] = rsWeightQuart
        else:
            print "Weight already changed. Doing nothing."

    else:
    	print "OK: Load Average (1min) threshold normal: " + LoadAvg1
	# Setting weight back to original value if not already set
	if not int(rsWeightCurrent) == int(rsWeightOriginal):
	    print "Setting weight back to original value of " + str(rsWeightOriginal)
	    print "ipvsadm -e -t vip:port -r ip:port -w " + str(rsWeightOriginal)
	    accessList[clientIP][1] = rsWeightOriginal
    return LoadAvg1

# Define server
class Server(SimpleXMLRPCServer):
    def __init__(self,*args):
        SimpleXMLRPCServer.__init__(self,(args[0],args[1]))
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        SimpleXMLRPCServer.server_bind(self)
    def verify_request(self,request, client_address):
        print "\n"
	cip = client_address[0]
	if accessList.has_key(cip):
       	    print "Client (" + cip + ") in LVS table."
            return 1
	else:
	    print "Client (" + cip + ") NOT in LVS table."
	return 0

if __name__ == "__main__":
    server = Server(serverIP,serverPort)
    server.register_function(pushLoad_function, 'pushLoad')
    server.logRequests = 0
    server.serve_forever()

