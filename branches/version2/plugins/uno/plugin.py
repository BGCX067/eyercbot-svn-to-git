#Uno game
#written by vbraun
#Version A.B
'''Uno!  Place help here.'''

from random import randrange
import random

class DeckEmpty(Exception):
	pass

class Deck:
	def __init__(self):
		self.colors = ['r','g','b','y']
		self.numbers = range(1,10)
		self.numbers.extend(['r', 's','dt'])
		self.cards = []
		for color in self.colors:
			current = []
			for i in self.numbers:
				card = color + str(i)
				current.append(card)
			current.extend(current)
			current.append(color + '0')
			self.cards.extend(current)
		for i in range(4):
			self.cards.append('w')
			self.cards.append('wdf')
		print self.cards
		for i in range(7):
			random.shuffle(self.cards)
	
	def draw_card(self):
		try: 
			return self.cards.pop()
		except IndexError:
			raise DeckEmpty()

class Uno:
	def __init__(self,bot,channel):
		#list of players, in order of play
		self.current_color = False
		self.commands = {'s': self.skip, 'r': self.reverse, 'dt': self.draw_two, 'w': self.wild, 'wdf': self.wild_draw_four}
		self.c = bot
		self.channel = channel
		self.can_join = True
		self.players = []
		self.say("Uno is starting, '!uno join' to join!")

	def join(self,input):
		#input = (player)
		player = input
		if self.can_join:
			if player in self.players:
				self.say("Sorry " + player + ", you can't join more than once!")
			else:
				self.players.append(player)
				self.say(player + " has joined Uno! Current players: " + str(self.players))
		else:
			self.say("Sorry " + player + ", you can't join right now")
			
	def start(self,input):
		#input = nothing important
		if len(self.players) > 1:
			self.can_join = False
			self.player_record = {}
			self.player_cards = {}
			self.current_player = self.players[0]
			self.deck = Deck()
			for name in self.players:
				self.player_cards[name] = []
				for i in range(7):
					self.player_cards[name].append(self.draw_card())
			
			self.commands = {'s': self.skip, 'r': self.reverse, 'dt': self.draw_two, 'w': self.wild, 'wdf': self.wild_draw_four}
			self.discard = [self.draw_card()]
			card = self.discard[0]
			player = self.current_player
			while card == 'wdf':
				self.say("A wdf was turned over! Starting with a new card!")
				card = self.draw_card()
				self.discard.append(card)
			self.say("Starting card is " + self.discard[len(self.discard)-1])
			if card == 'w':
				self.wild(player)
				self.player_record[player] = 'w'
			else:
				self.next_player(player)
				try:
					self.commands[card[1:len(card)]](player)
				except KeyError:
					pass
			
			for player in self.players:
				self.hand(player)
				self.player_record[player] = 'p'
				
			self.say(self.current_player + ", it is your turn!")
		else:
			self.say("We need at least 2 players to play uno! Currenty there are: " + str(len(self.players)))
	
	def play(self,input):
		print str(self.current_color)
		print input
		#input = (card, player)
		card, player = input
		if player == self.current_player:
			if card in self.player_cards[player]:
				try:
					print str(self.current_color) + card + self.discard[len(self.discard)-1]
					if card == 'w' or card == 'wdf':
						self.player_record[player] = 'w'
						self.play_stuff(card,player)
						self.commands[card](player)
					elif self.current_color == card[0]:
						self.player_record[player] = 'p'
						self.play_stuff(card,player)
						self.next_player(player)
						try:
							self.commands[card[1:len(card)]](player)
						except KeyError:
							pass

						self.next_turn()
						self.current_color = False						
					elif card[0] == self.discard[len(self.discard) - 1][0] or card[1] == self.discard[len(self.discard) - 1][1]:
						self.player_record[player] = 'p'
						self.play_stuff(card,player)
						self.next_player(player)
						try:
							self.commands[card[1:len(card)]](player)
						except KeyError:
							pass

						self.next_turn()
					else:
						self.say(player + " tried to play a " + card + ", but is not allowed to!")
				except IndexError:
					self.say(player + " tried to play a " + card + ", but is not allowed to!")
			else:
				self.say(player + " does not have a " + card)
		else:
			self.say(player + ", it is not your turn!")
		
#		return False
		
	def pas(self,input):
		'''pass'''
		#input = (player)
		player = input
		if player == self.current_player:
			if self.player_record[player] == 'd':
				self.next_player(player)
				self.next_turn()
				self.player_record[player] = 'p'
				self.say(player + " passes!")
			else:
				self.say("Either draw or play, " + player + ".")
		else:
			self.say(player + ", it is not your turn!")
			
	def draw(self,input):
		#input = (player)
		player = input
		if player == self.current_player:
			if self.player_record[player] == 'p':
				card = self.draw_card()
				self.player_cards[player].append(card)
				self.notice(player,"You drew a " + card)
				self.player_record[player] = 'd'
				self.say(player + " drew!")
			else:
				self.say("Sorry " + player + ", you can only draw once. Pass or play." )
		else:
			self.say(player + ", it is not your turn!")

	def color(self,input):
		print str(self.current_color)
		#input = (color,player)
		color, player = input
		print color
		if player == self.current_player:
			if self.player_record[player][0] == 'w':
				if color in self.deck.colors:
					self.say(player + " sets the color to " + color)
					self.current_color = color
					if self.player_record[player] == 'wdf':
						self.next_player(player)
					self.next_player(player)
					self.next_turn()
					self.player_record[player] = 'p'
				else:
					self.say(color + " is not a valid color")
			else:
				self.say("You did not just play a wild!")
		else:
			self.say(player + ", it is not your turn!")
			
	def hand(self,input):
		print str(self.current_color)
		#input = (player)
		player = input
		self.notice(player,str(self.player_cards[player]))
	
	def top_card(self,input):
		print str(self.current_color)
		#input = nothing important
		self.say("The last card played is: " + self.discard[len(self.discard)-1])
	
	def order(self,input):
		print str(self.current_color)
		#input = nothing important
		self.say("Current Player is: " + self.current_player)
		self.say(str(self.players))
			
#CARD COMMANDS
			
	def skip(self,player):
		#self.print_skip(player)
		self.say(self.current_player + ' is skipped!')
		self.next_player(self.current_player)
	
	def reverse(self,player):
		#self.print_reverse(player)
		if len(self.players) > 2:
			self.players.reverse()
			for i in range(2):
				self.next_player(self.current_player)
			self.say("The order has been reversed!")
		elif len(self.players) == 2:
			self.skip(player)
	
	def draw_two(self,player):
		#self.print_draw_two(player)
		self.say(player + ' makes ' + self.current_player + ' draw two!')
		string = ''
		for i in range(2):
			self.player_cards[self.current_player].append(self.draw_card())
			string = string + str(self.player_cards[self.current_player][-1]) + ' '
		self.notice(self.current_player, 'You drew ' + string + 'and was skipped!')
		self.skip(player)
		
	def wild(self,player):
		#self.print_wild(player)
		self.current_player = player
		self.say(player + ", please select a color now!")
	
	def wild_draw_four(self,player):
		self.next_player(player)
		#self.print_wild_draw_four(player)
		self.say(player + ' makes ' + self.current_player + ' draw four!')
		string = ''
		for i in range(4):
			self.player_cards[self.current_player].append(self.draw_card())
			string = string + str(self.player_cards[self.current_player][-1]) + ' '
		self.notice(self.current_player, 'You drew ' + string + 'and was skipped!')
		self.wild(player)
				
# INTERNAL COMMANDS

	def next_turn(self):
		self.say(self.current_player + ", it is your turn!")
		self.top_card('spam')
		self.hand(self.current_player)

	def play_stuff(self,card,player):
		self.say(player + " plays " + card)
		self.discard_card(card,player)
		self.check_for_win(player)
		if self.player_record[player] == 'p':
			self.next_player(player)
		elif self.player_record[player] == 'w':
			pass

	def draw_card(self):
		try:
			return self.deck.draw_card()
		except DeckEmpty:
			self.deck.cards = self.discard[0:len(self.discard)-1]
			random.shuffle(self.deck.cards)
			return self.deck.draw_card()
			
	def say(self,string):
		print string
		self.c.message(user, self.channel, string)
		
	def notice(self,nick,string):
		print "Notice: " + string
		self.c.notice(nick, string)
		
	def discard_card(self,card,player):
		self.player_cards[player].remove(card)
		self.discard.append(card)
		
	def next_player(self,player):
		try:
			reciever = self.players.index(player)+1
			self.current_player = self.players[reciever]
		except IndexError:
			self.current_player = self.players[0]
			
	def check_for_win(self,player):
		cards_left = len(self.player_cards[player]) 
		if cards_left == 1:
			self.say(player + " has UNO!")
		elif cards_left == 0:
			self.say(player + " has won!")
			
#BOT INTERFACE

def load(b):
	pass
	
def unload(b,e):
	pass
	
def main(bot,user,target, msg):
	nick = user
	args = msg.split()
	print args
	if len(args) == 1:
		#on "!uno" start joining process
		if bot.memory.has_key('games') == False:
			bot.memory['games'] = {}
		bot.memory['games']['uno'] = Uno(bot, target)
	if bot.memory['games']['uno']:
		commands = {'join': bot.memory['games']['uno'].join, 'start': bot.memory['games']['uno'].start, 'play': bot.memory['games']['uno'].play, 'pass': bot.memory['games']['uno'].pas,'draw': bot.memory['games']['uno'].draw, 'color': bot.memory['games']['uno'].color, 'hand':bot.memory['games']['uno'].hand, 'card':bot.memory['games']['uno'].top_card ,'order': bot.memory['games']['uno'].order}
		if len(args) == 2:
			try:
				commands[args[1]](nick)
			except KeyError:
				bot.message(user,target, "Sorry " + nick + ", I don't know the command " + args[1])
		elif len(args) == 3:
			try:
				commands[args[1]]((args[2],nick))
			except KeyError:
				bot.meessage(user,target, "Sorry " + nick + ", I don't know the command " + args[1])
	else: 
		bot.message(user,target, "Uno hasn't started yet! Type '!uno' to start!")

	




