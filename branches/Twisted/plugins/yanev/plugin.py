# Yanev
# By croxis
# Stolen from Uno game written by vbraun

from random import randrange
import random

deck = [('2', 'c'), ('3', 'c'), ('4', 'c'), ('5', 'c'), ('6','c' ), ('7', 'c'), ('8','c'), ('9', 'c'), ('10', 'c'), ('J','c'), ('Q','c'), ('K','c'), ('A', 'c'),  ('2', 's'), ('3', 's'), ('4', 's'), ('5', 's'), ('6','s' ), ('7', 's'), ('8', 's'), ('9', 's'), ('10', 's'), ('J', 's'), ('Q', 's'), ('K', 's'), ('A', 's'),  ('2', 'd'), ('3', 'd'), ('4', 'd'), ('5', 'd'), ('6','d' ), ('7', 'd'), ('8', 'd'), ('9', 'd'), ('10', 'd'), ('J', 'd'), ('Q', 'd'), ('K', 'd'), ('A', 'd'),  ('2', 'h'), ('3', 'h'), ('4', 'h'), ('5', 'h'), ('6','h' ), ('7', 'h'), ('8', 'h'), ('9', 'h'), ('10', 'h'), ('J', 'h'), ('Q', 'h'), ('K', 'h'), ('A', 'h')]

class DeckEmpty(Exception):
	pass

class Yanev:
	def __init__(self,connection,channel):
		#list of players, in order of play
		self.deck= deck
		self.connection = connection
		self.channel = channel
		self.can_join = True
		self.players = []
		self.discard = []
		self.say("Yanev is starting, '!yanev join' to join!")

	def join(self,input):
		#input = (player)
		player = input
		if self.can_join:
			if player in self.players:
				self.say("Sorry " + player + ", you can't join more than once!")
			else:
				self.players.append(player)
				self.say(player + " has joined Yanev! Current players: " + str(self.players))
		else:
			self.say("Sorry " + player + ", you can't join right now")
			
	def start(self,input):
		#input = nothing important
		self.can_join = False
		self.player_record = {}
		self.player_cards = {}
		self.current_player = self.players[0]
		for name in self.players:
			self.player_cards[name] = []
			for i in range(5):
				self.player_cards[name].append(self.draw_card())
		self.discard.append(self.draw_card())
		
		player = self.current_player
		self.say("Starting card is " + str(self.discard[len(self.discard)-1]))
		self.next_player(player)
		
		for player in self.players:
			self.hand(player)
			self.player_record[player] = 'p'
			
		self.say(self.current_player + ", it is your turn!")

	
	def play(self, player, card, draw='deck'):
		#print input
		#input = (card, player)
		#card, player = input
		card = (card[0], card[1])
		if player == self.current_player:
			if card in self.player_cards[player]:
				try:
					self.player_record[player] = 'p'
					self.play_stuff(card,player)
					self.draw(player, draw)
					self.next_player(player)
					self.next_turn()
				except IndexError:
					self.say(player + " tried to play a " + str(card) + ", but is not allowed to!")
			else:
				self.say(player + " does not have a " + str(card))
		else:
			self.say(player + ", it is not your turn!")
			
	def set(self, player, cards, draw='deck'):
		cards = cards.split(',')
		filtered = filter(lambda item: item.startswith(cards[0][0]), cards)
		if len(filtered) != len(cards):
			self.say(player + " tried to play a set, but not all values match!")
			return None
		# Do we have a flush?
		filtered = filter(lambda item: item.endswith(cards[0][1]), cards)
		if len(filtered) != len(cards):
			self.say(player + " tried to play a set, but not all suits match!")
			return None
		# Do we have a straight?
		cards
		c = []
		for card in cards:
			card_value = card[0]
			if card[0] == 'J':
				card_value = '11'
			if card[0] == 'Q':
				card_value = '12'
			if card[0] == 'K':
				card_value = '13'
			if card[0] == 'A':
				c.append(card_value)
			else:
				c.append(int(card_value))
		# Is there an Ace?
		if c.count('A') > 0:
			pass
		
		cardList = []
		for card in cards:
			cardList.append (card[0], card[1])
		if player == self.current_player:
			if card in self.player_cards[player]:
				try:
					self.player_record[player] = 'p'
					self.play_stuff(card,player)
					self.draw(player, draw)
					self.next_player(player)
					self.next_turn()
				except IndexError:
					self.say(player + " tried to play a " + str(card) + ", but is not allowed to!")
			else:
				self.say(player + " does not have a " + str(card))
		else:
			self.say(player + ", it is not your turn!")
	
	def draw(self,player, draw):
		if draw == 'discard':
			pass
		else:
			card = self.draw_card()
			self.player_cards[player].append(card)
			self.notice(player,"You drew a " + str(card))
			self.player_record[player] = 'd'
			self.say(player + " drew!")
	
	def hand(self,input):
		#input = (player)
		player = input
		self.notice(player,str(self.player_cards[player]))
	
	def top_card(self,input):
		#input = nothing important
		self.say("The last card played is: " + str(self.discard[len(self.discard)-1]))
	
	def order(self,input):
		#input = nothing important
		self.say("Current Player is: " + self.current_player)
		self.say(str(self.players))
			

# INTERNAL COMMANDS

	def next_turn(self):
		self.say(self.current_player + ", it is your turn!")
		self.top_card('spam')
		self.hand(self.current_player)

	def play_stuff(self,card,player):
		self.say(player + " plays " + str(card))
		self.discard_card(card,player)
		if self.player_record[player] == 'p':
			self.next_player(player)
		elif self.player_record[player] == 'w':
			pass

	def draw_card(self):
		self.deck_card_position = random.randint(0,len(self.deck)-1)
		return self.deck.pop(self.deck_card_position)
		
	def say(self,string):
		print string
		self.connection.privmsg(self.channel, string)
		
	def notice(self,nick,string):
		print "Notice: " + string
		self.connection.notice(nick, string)
		
	def discard_card(self,card,player):
		self.player_cards[player].remove(card)
		self.discard.append(card)
		
	def next_player(self,player):
		try:
			reciever = self.players.index(player)+1
			self.current_player = self.players[reciever]
		except IndexError:
			self.current_player = self.players[0]
	# Adds the hand and returns the sum.  We process Aces as 1 or 11 here
	def add_hand(self,  hand):
		sum = 0
		for card in hand:
			card_value = card[0]
			# We replace the letter values with point values
			if card_value == 'J':
				card_value = '10'
			if card_value == 'Q':
				card_value = '10'
			if card_value == 'K':
				card_value = '10'
			if card_value == 'A':
				card_value = '1'
			sum = sum + int(card_value)
		return sum
		
	# We check who wins
	def win(self, nick):
		playerTotal = {}
		for name in self.players:
			playerTotal[nick] = self.add_hand(self.player_cards[nick])
		self.say(playerTotal)
	
#BOT INTERFACE

def load(b):
	pass
	
def unload(b,e):
	pass
	
def main(bot,e):
	nick = e.source().split('!')[0]
	args = e.arguments()[0].split()
	print args
	if len(args) == 1:
		#on "!yanev" start joining process
		if bot.memory.has_key('games') == False:
			bot.memory['games'] = {}
		bot.memory['games']['yanev'] = Yanev(bot.connection, e.target())
	if bot.memory['games']['yanev']:
		commands = {'join': bot.memory['games']['yanev'].join, 'start': bot.memory['games']['yanev'].start, 'play': bot.memory['games']['yanev'].play, 'set': bot.memory['games']['yanev'].set,'hand':bot.memory['games']['yanev'].hand, 'card':bot.memory['games']['yanev'].top_card ,'order': bot.memory['games']['yanev'].order,  'yanev': bot.memory['games']['yanev'].win}
		if len(args) == 2:
			try:
				commands[args[1]](nick)
			except KeyError:
				bot.connection.privmsg(e.target(), "Sorry " + nick + ", I don't know the command " + args[1])
		elif len(args) == 3:
			try:
				commands[args[1]](nick, args[2])
			except KeyError:
				bot.connection.privmsg(e.target(), "Sorry " + nick + ", I don't know the command " + args[1])
		elif len(args) == 4:
			try:
				commands[args[1]](nick, args[2],args[3])
			except KeyError:
				bot.connection.privmsg(e.target(), "Sorry " + nick + ", I don't know the command " + args[1])
	else: 
		bot.connection.privmsg(e.target(), "Uno hasn't started yet! Type '!uno' to start!")

	




