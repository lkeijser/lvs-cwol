#!/usr/bin/env python

#--------- PREFERENCES ---------#
# Bind to IP/port
serverIP = 'localhost'
serverPort = 12219
# Set thresholds
LoadAvg_crit_threshold = '0.80'
LoadAvg_warn_threshold = '0.50'
# 
#------- END PREFERENCES -------#


from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
import string,socket

accessList=(
    '127.0.0.1',
    '10.1.4.165'
)

# Test function pushLoad
def pushLoad_function(LoadAvg, clientIP):
    LoadAvg1 = LoadAvg.split()[0]
    print "TEST: connect from %s " % clientIP
    # Determine if CRITICAL threshold is reached
    if float(LoadAvg1) >= float(LoadAvg_crit_threshold):
    	print "CRITICAL: Load Average (1min) threshold (" + str(LoadAvg_crit_threshold) + ") reached: " + LoadAvg1
    	print "Lowering realserver's weight with 50%"
    # Determine if WARNING threshold is reached
    elif float(LoadAvg1) >= float(LoadAvg_warn_threshold):
    	print "WARNING: Load Average (1min) threshold (" + str(LoadAvg_warn_threshold) + ") reached: " + LoadAvg1
    	print "Lowering realserver's weight with 25%"
    else:
    	print "OK: Load Average (1min) threshold normal: " + LoadAvg1
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
        if client_address[0] in accessList:
            print "Client (" + client_address[0] + ") in ACL."
            return 1
        else:
            print "Client (" + client_address[0] + ") NOT in ACL."
            return 0

if __name__ == "__main__":
    server = Server(serverIP,serverPort)
    server.register_function(pushLoad_function, 'pushLoad')
    server.logRequests = 0
    server.serve_forever()



