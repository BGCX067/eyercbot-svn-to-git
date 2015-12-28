# Notes plugin
# Users can send notes to each other
'''Notes plugin. !note index will list notes in the inbox. !note read #/all read that entry or all notes. !note erase #/all will erase that note or all notes. !note to user message will sent a note with a given message to that user.'''
# MUST MAKE SURE USER PLUGIN DOES NOT OVERWRITE NOTES WHEN REGISTERING OR ANY DISK WRITE

# notes = [{from: user, date: date sent (in int form to allow more advanced stuff later), message: message string, read: T/F},]

# -----
# Configuration
path_users = 'users/'
# -----

'''!notes index - Lists all notes for your handle
!notes read #/all - PM or notices notes. # can also be list or range
!notes erase #/all - Erases notes
!notes to Username message - Sends note to the user
'''

import glob
import random
import yaml
import time

def load(bot):
	pass

def unload(bot):
	#save_notes()
	pass

def main(bot, user, target, msg):
	user = user.split('!')[0]
	if len(msg.split()) == 1:
		bot.message(user, target, __doc__)
		return None

	if msg.split()[1].upper() == 'HELP':
		bot.message(user, target, __doc__)
		return None

	if msg.split()[1].upper() == 'INDEX':
		
		if bot.users[user].has_key('notes') == False:
			bot.message(user, target,  'There are no notes in your inbox')
			return None
		if bot.users[user]['notes'] == []:
			bot.message(user, target,  'There are no notes in your inbox')
			return None
		bot.message(user, target,  'There are ' + str(len(bot.users[user]['notes'])) + ' note(s) in your inbox.')
		n = 1
		for note in bot.users[user]['notes']:
			#{from: user, date: date sent (in int form to allow more advanced stuff later), message: message string, read: T/F}
			bot.notice(user.split('!')[0],  str(n) + bot.users[user]['notes'][note]['from'])
			n = n+1
			time.sleep(1)
			
	if msg.split()[1].upper() == 'READ' and len(msg.split()) == 3:
		index =msg.split()[2].upper()
		if bot.users[user.split('!')[0]].has_key('notes') == False:
			bot.message(user, target,  'I have no notes for you')
			return None
		if bot.users[user.split('!')[0]]['notes'] == []:
			bot.message(user, target,  'I have no notes for you')
			return None
		if index == 'ALL':
			n = 1
			for note in bot.users[user]['notes']:
				#{from: user, date: date sent (in int form to allow more advanced stuff later), message: message string, read: T/F}
				bot.notice(user,  str(n) + ':' + 'From: ' + note['from'] + ' :: ' +  [note]['message'])
				#bot.users[user]['notes'][note]['read'] = True
				n = n+1
				time.sleep(1)
			return None
		try: 
			index = int(msg.split()[2])-1
		except:
			bot.notice(user.split('!')[0],  'I can only look up messages by a number or ALL.')
			return None
		if len(bot.users[user]['notes']) < index:
			bot.notice(user.split('!')[0], 'I have no messages for you in that index.')
		bot.notice(user,  msg.split()[2] + ':' + 'From: ' + bot.users[user]['notes'][index]['from'] + ' :: ' +  bot.users[user]['notes'][index]['message'])
		bot.users[user]['notes'][index]['read'] = True
		
	if msg.split()[1].upper() == 'ERASE' and len(msg.split()) == 3:
		if bot.users[user.split('!')[0]].has_key('notes') == False:
			bot.notice(user.split('!')[0],  'I have no notes for you')
			return None
		if bot.users[user.split('!')[0]]['notes'] == []:
			bot.notice(user.split('!')[0],  'I have no notes for you')
			return None
		if msg.split()[2].upper() == 'ALL':
			del bot.users[user.split('!')[0]]['notes']
			bot.notice(user.split('!')[0], 'Deleted all notes')
			return None
		if len(bot.users[user]['notes']) < msg.split()[2]:
			bot.notice(user.split('!')[0], 'I have no message for you in that index.')
		try: 
			index = int(msg.split()[2])
		except:
			bot.notice(user.split('!')[0],  'I can only look up messages by a number or ALL.')
			return None
		del bot.users[user]['notes'][index]
		bot.notice(user.split('!')[0],  'Note removed')
	
	if msg.split()[1].upper() == 'TO' and len(msg.split()) > 3:
		nick = event.arguments()[0].split()[2]
		if nick not in bot.users:
			bot.users[nick] = {}
		if 'notes' not in bot.users[nick]:
			bot.users[msg.split()[2]]['notes'] = []
		bot.users[msg.split()[2]]['notes'].append({'from': user.split('!')[0], 'date': None, 'message': msg.split(' ',  3)[3], 'read': False})
		bot.message(user, target, 'I put the note into their inbox for you')

#def on_join(connection,  event,  channels):
#	if EyeRCbot.bot.user_list.has_key(event.source().split('!')[0]):
#		pass

