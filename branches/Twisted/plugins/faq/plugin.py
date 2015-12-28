# FAQ script
# Calls FAQ based on key
# Can Add a FAQ
# Natural language search some day
'''FAQ plugin.  !faq add title:title of entry text:text of entry will add a faq with that title and text.  !faq title:title user:nick will call that entry and the optional user parameter will pm that entry to the user directly.  !faq delete title will delete that entry.'''
import yaml
import EyeRClib.diskio as diskio


def load(bot):
	# Load DB
	pass

def unload(bot):
	# Save DB
	pass
def main (bot, event):
	if len(event.arguments()[0].split()) == 1:
		bot.message(user, target, __doc__)
		return None
	
	if event.arguments()[0].split()[1].upper() == 'HELP':
		bot.message(user, target, __doc__)
		return None
	
	# Lets add a FAQ
	# If the entry title exists we will tell the user to either delete it or pick a new title
	if msg.split()[1].upper() == 'ADD':
		# Going to pull the line into sub components
		if msg.find('title:') != -1 and msg.find('text:') != -1:
			# Remove commands
			line = msg.replace('!faq add ','')
			title_index = line.find('title:')
			text_index = line.find('text:')
			if title_index < text_index:
				title = line[title_index:text_index].replace('title:', '').strip()
				text = line[text_index:len(line)].replace('text:', '').strip()
			elif title_index > text_index:
				text = line[text_index:title_index].replace('text:', '').strip()
				title = line[text_index:len(line)].replace('title:', '').strip()
			if bot.memory.has_key('faq') == False:
				bot.memory['faq'] = {}
			if bot.memory['faq'].has_key(title):
				bot.message(user, target,'There is already an entry by that title.  Please delete the existing entry first or use a different title.')
				return None
			else:
				addfaq(bot, title, text)
				bot.message(user, target,'FAQ entry added.')
		return None
	
	if msg.split()[1].upper() == 'DELETE':
		title = msg.split(' ', 2)[2]
		if bot.memory.has_key('faq'):
			if bot.memory['faq'].has_key(title):
				bot.message(user, entry,'Entry deleted.')
		else:
			bot.message(user, entry,'Unable to delete entry.')
		return None

	if msg.find('title:') != -1 and msg.find('user:') == -1:
		print bot.memory['faq']
		line = msg.replace('!faq ','')
		title_index = line.find('title:')
		title = line[title_index:len(line)].replace('title:', '').lstrip()
		if bot.memory['faq'].has_key(title):
			bot.message(user, target, title + ': ' + bot.memory['faq'][title])
		else:
			bot.message(user, target,'No FAQ entry by that title.')
	if msg.find('title:') != -1 and msg.find('user:') != -1:
		line = msg.replace('!faq ','')
		title_index = line.find('title:')
		user_index = line.find('user:')
		if title_index < user_index:
			title = line[title_index:user_index].replace('title:', '').strip()
			user = line[user_index:len(line)].replace('user:', '').strip()
		elif title_index > user_index:
			user = line[user_index:title_index].replace('user:', '').strip()
			title = line[title_index:len(line)].replace('title:', '').strip()
		if bot.memory['faq'].has_key(title):
			bot.msg(user, target, title + ': ' + bot.memory['faq'][title])
		else:
			bot.message(user,target ,'No FAQ entry by that title.')
	

def addfaq(bot, title, text):
	bot.memory['faq'][title] = text
