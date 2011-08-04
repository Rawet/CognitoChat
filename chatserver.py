#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# CognitoChat Server
# Written by Cognito
# 2010

"""The most basic chat protocol possible.
 
run me with twistd -y chatserver.py, and then connect with multiple
telnet clients to port 1025

http://twistedmatrix.com/trac/browser/trunk/doc/core/examples/chatserver.py

Protocol: encrypted[[time][user][message]]


"""

from twisted.protocols import basic
import crypt, hashlib, base64 #crypt?

onlineClients = []

class MyChat(basic.LineReceiver):
	def connectionMade(self):
		print "Got new client!"
		self.factory.clients.append(self)

	def connectionLost(self, reason):
		print "Lost a client!"
		self.factory.clients.remove(self)

	def lineReceived(self, line):
		print "received", repr(line)
		
		if line[0] == "/":
				if line[1] == "u":
					u = line.split(" ")
					onlineClients.append(u[1])
					for c in self.factory.clients:
						c.message(u[1]+" Has logged in.")
		
		if line[0] == "#": #encrypted message incoming
			#####The code that follows is this complicated simply because I'm too lazy
			#####to rewrite pyAES.py...it's a temporary solution, okay...
			encMsg = line.split("#", 2) #split into 1: sender, 2: aes(msg)
			msgHash = hashlib.md5(encMsg).hexdigest()
			incomingMsg = open("input/"+msgHash+".aes","w") #save encrypted incoming to temporary file
			incomingMsg.write(base64.decodestring(encMsg[2])) #write binary, not base64
			incomingMsg.close()
			pyAES.decrypt("input/"+msgHash+".aes", "aeskeys/"+encMsg[1]+".key", "output/"+msgHash+".msg")
			for i in onlineClients:
				pyAES.encrypt("output/"+msgHash+".msg", "aeskeys/"+i+".key", "temp/toSend.aes")
				outgoingMsg = open("temp/toSend.aes","r") #read outgoing message from temporary file
				msgOut = base64.encodestring(outgoingMsg.readline()) #send message as base64 again, not binary
				outgoingMsg.close()
				for c in self.factory.clients: #spaaaaam
					c.message(msgOut)
				
		for c in self.factory.clients:
			c.message(line)

	def message(self, message):
		self.transport.write(message + '\r\n')


from twisted.internet import protocol
from twisted.application import service, internet

factory = protocol.ServerFactory()
factory.protocol = MyChat
factory.clients = []

application = service.Application("chatserver")
internet.TCPServer(1025, factory).setServiceParent(application)
