#!/usr/bin/env python
# EyeRCbot setup script
# subEyeRCbot derived from version 0.9.9.1
# Will ask bot set up questions
# Then will connect to server and open communication with the user to set password and hostmask
# This is a minimal version of the EyeRCbot and the User plugin

print 'Loading...'
import sys
sys.path.append('lib')
import ircbot
import yaml
import re
import hashlib

user_password = ''
user_hostmask = ''
new_user = {}

class subEyeRCbot (ircbot.SingleServerIRCBot):
	x = 1
	def launch(self):
		# Launching sequence
		print '<' + bot_memory['name'] + '> Hey! Me again. I just started trying to connect.  Lets see how slow this server is!'
		self._connect()
		print '<' + bot_memory['name'] + "> I connected just dandy!"
		# Enters final bot launch and infinite loop
		self.runtime()
	
	# Infinite runtime loop
	def runtime(self):
		# The infinite loop
		while self.x == 1:
			# Socket data processing
			self.ircobj.process_once(0.2)


	# Connection protocol from ircbot as ircbot's implementation does not lead to what we want at this time.  
	# Will need to start customizing libraries as features become more advanced
	def _connect(self):
		"""[Internal]"""
		ircpassword = None
		if len(self.server_list[0]) > 2:
			ircpassword = self.server_list[0][2]
		try:
			self.connect(self.server_list[0][0], self.server_list[0][1], self._nickname, ircpassword, ircname=self._realname)
		except ServerConnectionError:
			print 'I had an error connecting to the server ' + bot_memory['server'] + ' on port ' + str(bot_memory['port']) + '.'
			return

	# Join channel when welcomed (?)
	def on_welcome (self, connection, event):
		print '<' + bot_memory['name'] + '> I am now trying to message you through IRC.'
		connection.privmsg(user_nick, 'Hello? Hope you can hear me.  And I hope you are you.  Otherwise I will have to be erased and start over!  What I need you to do, and this is very important, is to type in your user password.  This password is encrypted, that is how important it is.  This password will let me know that you are really you.  Just type in and send your password to me.')

	# Reacts to private messages
	def on_privmsg (self, connection, event):
		# Removes formatting as it inhibits commands
		new_user['password'] = hashlib.sha224(re.compile('[\x02\x1f\x16\x0f \x03[0-9]{1,2}(,[0-9]{1,2})?]').sub('',event.arguments()[0])).hexdigest()
		new_user['hostmasks'] = [event.source().split('!')[1],]
		connection.privmsg(user_nick, 'I have your password and host mask!  I am going to disconnect now and communicate with you by the command prompt again.')
		self.x = 0



print '<EyeRCbot> Hello.  I am EyeRCbot.  To make me more personable please give me a name'
bot_name = raw_input('Name: ')
print '<' + bot_name + '> Thank you! In order to generate the configuration files I will need some information from you on how to connect.  Then I will send you a private message by IRC to ask for your password and hostmask to establish you as my owner.'
print '<' + bot_name + '> First I need the address of the server.'
server = raw_input('Server: ')
print '<' + bot_name + '> And what port?  The default is usually 6667 so if you have no idea what it is, it is probably 6667'
port = int(raw_input('Port: '))
print '<' + bot_name + "> I am going to need a name that people will see me as in the channels.  There can't be any spaces!"
bot_nick = raw_input('Nick: ')
print '<' + bot_name + '> I wont be joining any channels for the setup, but how many channels will I be connecting to?'
number = int(raw_input('Number: '))
n = 0
channels = []
while n < number:
	print '<' + bot_name + '> What is the name (with #) of channel number ' + str(n+1) + '?'
	a = raw_input('Channel ' + str(n+1) + ': ')
	channels.append(a)
	n = n + 1
print channels
print '<' + bot_name + "> For this version you need to tell me a special password by CTCP to reload my plugins. What do you want this password to be? (FYI: I am too lazy to encrypt this password yet, so make sure it isn't something too important!)"
scan_password = raw_input('Password: ')
print '<' + bot_name + '> Got it. Make sure you are connected to the server NOW because right after this step I am going online to try and message you.  What is your nick on the server?'
user_nick = raw_input('Your nick: ')
print '<' + bot_name + '> Alright.  Time to go online the first time as me!!!!'
print 'Generating bot memory dictionary.'
bot_memory = {'server': server, 'port': port, 'nick': bot_nick, 'name': bot_name, 'channels': channels, 'password': scan_password}
print 'Creating instance of subEyeRCbot class. Loading memory dictionary.'
subBot = subEyeRCbot( [(bot_memory['server'], bot_memory['port'])], bot_memory['nick'], bot_memory['name'])
print 'Initiating connection sequence. Transferring control back to ' + bot_memory['name'] + '.'
subBot.launch()

print '<' + bot_name + '> Ok I am back.  I am now going to save the configuration files.'

new_user['name'] = user_nick
new_user['group'] = 'owner'
new_user['permissions'] = ['']
new_user['is_registered'] = True
stream = file('users/' + user_nick + '.yaml', 'w')
yaml.dump(new_user, stream)
stream.close()
stream = file(bot_nick + '.yaml', 'w')
yaml.dump(bot_memory, stream)
stream.close()
print 'Alright!  I am so done with this set up gig.  Lets get me started! On Windows you can start me by command prompt with: python EyeRCbot ' + bot_nick + '.yaml | On linux with ./EyeRCbot ' + bot_nick + '.yaml'
