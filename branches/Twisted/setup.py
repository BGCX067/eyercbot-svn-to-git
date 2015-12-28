#!/usr/bin/env python
# EyeRCbot setup script
# subEyeRCbot derived from version 1.9.0.0
# Will ask bot set up questions
# Then will connect to server and open communication with the user to set password and hostmask
# This is a minimal version of the EyeRCbot and the User plugin

print 'Loading...'
# For bot configuration
import yaml
# We import the eyercbot library
import EyeRClib.diskio as diskio
import sys
import glob

def main():
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
	channels = {}
	while n < number:
		print 
		a = raw_input('<' + bot_name + '> What is the name (with #) of channel number ' + str(n+1) +  ': ')
		channels[a] = {}
		n = n + 1
	print channels
	print '<' + bot_name + '> I am now going to save the current configuration files. But we arnt done yet!'
	print 'Generating bot memory dictionary.'
	bot_memory = {'server': server, 'port': port, 'nick': bot_nick, 'name': bot_name, 'channels': channels, 'plugins': [], 'isNew': True}

	print 'Initiating save.'
	stream = file(bot_nick + '.yaml', 'w')
	yaml.dump(bot_memory, stream)
	stream.close()
	print 'Save completed.'
	print '<' + bot_name + '> Now we need to me up so I can actually do something.  This is another very important question.  Do you want user and group permission so you can control access to me and my plugins?  These functions are not necissary if I am to be a simple logging bot or some basic search plugins that you dont mind anyone using. If you want me to do anything more advanced where users can write or delete data then it is a real good idea to have user and group permission controls.'
	x = True
	while x:
		response = raw_input('Do you want user/group permissions? Please type Yes or No: ')
		if response[0].lower() == 'n':
			bot_memory['selfPlugins'] = ['owner', ]
			print '<' + bot_name + '> Remember,  anyone will be able to access the plugins you add in the following promps.'
			for chan in bot_memory['channels']:
				bot_memory['channels'][chan]['plugins'] = bot_memory['plugins'] 
			x = False
		elif response[0].lower() == 'y':
			bot_memory['selfPplugins'] = ['admin', 'user']
			for chan in bot_memory['channels']:
				bot_memory['channels'][chan]['plugins'] = bot_memory['plugins'] 
			x = False
		else: 
			print '<' + bot_name + '> Erm. I have no idea what you mean.'
	
	print 'Generating plugin list.'
	plugins = []
	for plug in glob.glob ( 'plugins/*/' ):
		plugname = plug.lstrip('plugins').lstrip('/').rstrip('/')
		plugins.append(plugname)
	if 'admin' in plugins: plugins.remove('admin')
	if 'user' in plugins: plugins.remove('user')
	if 'owner' in plugins: plugins.remove('owner')
	
	print '<' + bot_name + '> Here is the list of plugins I have avalable.  Please type in a list of numbers, seperated by a space, of the plugins that users can access by private message. The proper permission plugins have already been added.'
	for plug in plugins:
		print str(plugins.index(plug)) + ' ' + str(plug)
	response = raw_input('Type in a list of plugin numbers seperated by spaces.  Type in -1 for none: ')
	splitresponse = response.split()
	for resp in splitresponse:
		bot_memory['selfPlugins'].append(plugins[int(resp)])
	
	for chan in bot_memory['channels']:
		print '<' + bot_name + '> Which plugins do you want accessable in ' + chan + '?'
		for plug in plugins:
			print str(plugins.index(plug)) + ' ' + str(plug)
		response = raw_input('Type in a list of plugin numbers seperated by spaces.  Type in -1 for none: ')
		splitresponse = response.split()
		for resp in splitresponse:
			bot_memory['channels'][chan]['plugins'].append(plugins[int(resp)])
	
	
	print '<' + bot_name + '> Sweet. We are almost all done.  I am now saving the updated configurations.'
	print 'Opening file stream.'
	stream = file(bot_nick + '.yaml', 'w')
	yaml.dump(bot_memory, stream)
	stream.close()
	print 'Saving completed.'
	print  '<' + bot_name + '> Alright!  I am so done with this set up gig.  Lets get me started! On Windows you can start me by command prompt with: python EyeRCbot ' + bot_nick + '.yaml | On linux with ./EyeRCbot ' + bot_nick + '.yaml'
	print  '<' + bot_name + '> What I need you to do when I join the channel, and this is very important, is to private message me the following: password: yourpassword .  This password is encrypted, that is how important it is.  This password will let me know that you are really you and you are my owner.  Respond with just your password.'

if __name__ == '__main__':
	try:
		main()
	except:
		print 'You cancled or there was a major error before I was done.  Nothing was saved of your progress, so you will need to run setup again.'
		import traceback
		traceback.print_exc(file=open("errlog.txt","w"))
	
