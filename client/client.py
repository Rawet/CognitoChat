#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# CognitoChat Client
# Written by Cognito
# 2011


# TO WOODY *****************************
# 
# Försök gärna svara på din mail, och kommentera koden mer! haha
# Vi borde även försöka fixa nån slags lista vad vi gör i koden, så vi har koll på vad vi gör.
# 
# 



HOST = "localhost"
PORT = 1025
USERNAME = raw_input("Username: ")
clientsOnline = []

from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ClientFactory
from twisted.internet import stdio
from twisted.protocols import basic

import datetime
now = datetime.datetime.now()

class StdioProto(basic.LineReceiver):
	from os import linesep as delimiter

	clientProto = None

	def lineReceived(self, line):
		global clientsOnline
		if self.clientProto is not None:
			if line[0] == "/":  #Huh? Vad gör den här biten? Svar: Kollar så att / är satt.
				if line[1] == "o":
					print clientsOnline
			else:
				self.clientProto.transport.write(line+"\r\n")
			
			


class ClientProto(basic.LineReceiver):
	clientsOnline = [] #list of clients online
	
	from os import linesep as delimiter

	def __init__(self, stdioProto):
		self.stdioProto = stdioProto

	def lineReceived(self, line):
		global USERNAME
		if line[0] == "/":
			if line[1] == "p": #private server-client message
				privMsg = line.split(" ") #Ex. 0:/p 1:Bob 2:/u 3:bam 4:bam 5:bam 6:bam
				if privMsg[1] == USERNAME:
					if privMsg[2] == "/u":
						privMsg.pop("/p")
						privMsg.pop(USERNAME)
						privMsg.pop("/u")
						for i in privMsg:
							clientsOnline.append(i) #add client to list of online clients
						
			if line[1] == "u" :
				u = line.split(" ")
				#self.stdioProto.transport.write(u[1]+" has logged in.\r\n")
				clientsOnline.append(u[1]) #adds new client to the list of online clients
			if line[1] == "q":
				u = line.split(" ")
				self.stdioProto.transport.write(u[1]+" has just logged out.\r\n")
		else:
			self.stdioProto.transport.write(""+now.strftime("%H:%M")+" < "+USERNAME+"> "+line+"\r\n")			

	def connectionMade(self):
		self.stdioProto.clientProto = self
		self.transport.write("/u "+USERNAME+" \r\n")		# Skickar med användarnamn

	def connectionLost(self, reason):
		self.stdioProto.clientProto = None
		print "Error: ", reason



class EchoClientFactory(ClientFactory):
	
	def __init__(self, stdioProto):
		self.stdioProto = stdioProto

	def buildProtocol(self, addr):
		p = ClientProto(self.stdioProto)
		p.factory = self # by convention a protocol should have a 'factory' attribute
		return p
		print "Connected to "+HOST



def main():
	stdioProto = StdioProto()
	stdio.StandardIO(stdioProto)

	f = EchoClientFactory(stdioProto)
	reactor.connectTCP("localhost", 1025, f)
	reactor.run()

if __name__ == '__main__':
	main()


