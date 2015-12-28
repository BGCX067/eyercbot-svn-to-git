# MadLibs plugin
# story = {'text': 'I %s cheese and %s', 'list':['verb','noun']}
# words = [list, of, words, generated]
# story['text']%tuple(words) will be the story with the user words
'''Madlibs! Help goes here'''
import time
import threading
import random
import urllib
import urllib2
import sys
import yaml
import re

import EyeRClib.NLPlib.NLPlib as NLPlib
import EyeRClib.html2irc as html2irc

# --------------------
# Configuration
# How long to wait before skipping user (in seconds)
wait = 10.0
# How long to wait for users to join
join_wait = 60.0
# 1/n chance that wiki word will be madlib word
n = 7
# --------------------
agame = None
games = {}
in_progress = False
joining = False

class Game:
	def __init__(self, bot, channel,  story,  nick, title):
		self.user_list = []
		self.story = story
		self.words = []
		self.list_index = 0
		self.in_progress = False
		self.allow_join = False
		self.channel = channel
		self.bot = bot
		self.owner = nick
		self.title = title
	def start(self):
		self.allow_join = False
		self.bot.msg(self.channel,  'Let the game begin!')
		self.ask()
	def changeUser(self):
		self.user_list.append(self.user_list.pop(0))
	def addUser(self,  nick):
		if self.allow_join == True:
			self.user_list.append(nick)
			self.bot.msg(self.channel,  'Added user ' + nick + ' . Total users: ' + str(self.user_list))
	def ask(self):
		print self.story['list']
		self.bot.msg(self.channel,  self.user_list[0] +  ': ' +  self.story['list'][self.list_index])
	def addWord(self, nick, word):
		if nick == self.user_list[0]:
			self.words.append(word)
			self.changeUser()
			self.list_index = self.list_index + 1
			if self.list_index == len(self.story['list']):
				self.printStory()
				endGame(self.bot, self.owner)
				return None
			self.ask()
	def printStory(self):
		self.bot.msg(self.channel, 'Title: ' + self.title + ', ' + self.story['text']%tuple(self.words))

def load(bot):
	pass

def unload(bot):
	pass

def main(bot, user, target, msg):	
	user_nick = user.split('!')[0]
	if len(msg.split()) == 1:
		return None
	if msg.split()[1].upper() == 'NEW' or len(msg.split()) == 1 :
		#Alright, now pull text from a random wiki
		a = False
		while a == False:
			text, title = wiki()
			a = wikicheck(text)
		text = html2irc.html2irc(text)
		if len(text) > 400:
				text = text[0:400]
		wiki_story = [[], []]
		while len(wiki_story[1]) < 2:
			wiki_story =  encodetext(text)
		story = {'text':wiki_story[0], 'list':wiki_story[1]}
		stream = file('madlib.yaml', 'w')
		yaml.dump_all([story, title], stream)
		stream.close()
		if bot.memory.has_key('games') == False:
			bot.memory['games'] = {}
		bot.memory['games']['madlib'] = Game(bot, target,  story,  user_nick,  title)
		bot.memory['games']['madlib'].allow_join = True
		bot.msg(target, 'A new game of Madlibs is starting Please type !madlib join to join the game. The game owner can type !madlib start to start the game.')
		return None
		
	if msg.split()[1].upper() == 'JOIN':
		bot.memory['games']['madlib'].addUser(user_nick)
		return None
		
	if msg.split()[1].upper() == 'START':
		#if games.has_key(user_nick) == True and games[user_nick].allow_join == True:
			#games[user_nick].start()
		if bot.memory['games']['madlib'].allow_join == True: bot.memory['games']['madlib'].start()
		return None
		
	if msg.split()[1].upper() == 'WORD' and len(msg.split()) == 3:
		bot.memory['games']['madlib'].addWord(user_nick,  msg.split()[2])
		return None
		
	if len(emsg.split()) > 1:
		if 'games' in bot.memory:
			if 'madlib' in bot.memory['games']:
				bot.memory['games']['madlib'].addWord(user_nick,  msg.split()[2])
		return None
		
	return None
	
def endGame(bot, owner):
	del bot.memory['games']['madlib']


# Here is the experimental code which will import a random entry from wikipedia as story
# We will then run is through the NLPlib parser as a for loop for each word, a random (1/10?) chance the word will be removed
# %s is inserted in {text: <>} and word type is appended in {list:[]}
def wiki():
	# Alright, we pull a random title from the 0 namespace (real articles)
	wiki_randomurl = 'http://en.wikipedia.org/w/api.php?format=yaml&action=query&list=random&rnnamespace=0'
	url = wiki_randomurl
	webbot = urllib2.Request(url)
	webbot.add_header('User-Agent','EyeRCbot')
	sock = urllib2.urlopen(webbot)
	wiki_yaml = sock.read()
	sock.close()
	wiki_yaml = wiki_yaml.replace('*', 'text', 1)
	html = yaml.load(wiki_yaml)
	# We want to hang onto the title for output later
	wiki_title = html['query']['random'][0]['title']
	# Now we go for title
	wiki_url = 'http://en.wikipedia.org/w/api.php?format=yaml'
	wiki_page = '&action=parse&prop=text&page='
	url = wiki_url + wiki_page + urllib.quote(wiki_title)
	webbot = urllib2.Request(url)
	webbot.add_header('User-Agent','EyeRCbot')
	sock = urllib2.urlopen(webbot)
	wiki_yaml = sock.read()
	sock.close()
	wiki_yaml = wiki_yaml.replace('*', 'text', 1)
	html = yaml.load(wiki_yaml)
	text_temp = re.search('<p>(?P<text>.+)</p>', html['parse']['text']['text'])
	text = text_temp.group('text')
	return text, wiki_title

# If the page is a list, we say "Oh HELL no" and redo
def wikicheck(text):
	# Switch to lower?  Looks more friendly and in python style
	if text.split()[0].lower() == 'list':
		return False
	if text.split()[1] == 'may' and text.split()[2] ==  'stand':
		return False
	return True

# Here is the parser for loop
def encodetext(text):
	encoder = NLPlib.NLPlib()
	split_text = text.split()
	word_list = []
	for word in split_text:
		wordtype = encoder.tag([word])
		wordtype = wordtype[0]
		if wordtype != []:
			x = random.randint(1, n)
			if x == 1:
				word_key = split_text.index(word)
				split_text[word_key] = '%s'
				#http://www.mozart-oz.org/mogul/doc/lager/brill-tagger/penn.html
				if wordtype == 'CC':	split_text[word_key] = word
				if wordtype == 'CD': 
					word_list.append('a number')
				if wordtype == 'DT': 	split_text[word_key] = word
				if wordtype == 'EX': 	
					word_list.append('existential there')
				if wordtype == 'FW': 
					word_list.append('foreign word')
				if wordtype == 'IN':  	split_text[word_key] = word
				if wordtype == 'JJ': 
					word_list.append('adjective')
				if wordtype == 'JJR': 
					word_list.append('adjective, comparative')
				if wordtype == 'JJS': 
					word_list.append('adjective, superlative')
				if wordtype == 'LS': 
					word_list.append('list marker')
				if wordtype == 'MD': 
					word_list.append('modal')
				if wordtype == 'NN': 
					word_list.append('noun, singular')
				if wordtype == 'NNS': 
					word_list.append('noun plural')
				if wordtype == 'NNP': 
					word_list.append('proper noun, singular')
				if wordtype == 'NNPS': 
					word_list.append('proper noun, plural')
				if wordtype == 'PDT': 
					word_list.append('predeterminer')
				if wordtype == 'POS': 
					word_list.append('possessive ending')
				if wordtype == 'PRP': 	
					word_list.append('personal pronoun ')
				if wordtype == 'PRP$': 	word_list.append('possessive pronoun')
				if wordtype == 'RB': 	word_list.append('adverb')
				if wordtype == 'RBR': 	word_list.append('adverb, comparative')
				if wordtype == 'RBS': 	word_list.append('adverb, superlative')
				if wordtype == 'RP': 	word_list.append('particle')
				if wordtype == 'TO': 	split_text[word_key] = 'to'
				if wordtype == 'UH':	word_list.append('interjection')
				if wordtype == 'VB': 	word_list.append('verb')
				if wordtype == 'VBD': 	word_list.append('verb, past tense ')
				if wordtype == 'VBG':	word_list.append('verb ending in "ing"')
				if wordtype == 'VBN': 	word_list.append('verb, past participle')
				if wordtype == 'VBP': 	word_list.append('verb, sing')
				if wordtype == 'VBZ': 	word_list.append('verb, 3rd person')
				if wordtype == 'WDT': 	word_list.append('wh-determiner')
				if wordtype == 'WP': 	word_list.append('wh-pronoun')
				if wordtype == 'WP$': 	word_list.append('possessive wh-pronoun')
				if wordtype == 'WRB': 	word_list.append('wh-abverb')
				
	text = ' '.join(split_text)
	return text,  word_list

#
