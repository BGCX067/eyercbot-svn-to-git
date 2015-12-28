# This Python file uses the following encoding: utf-8
# Blaclubskjaclubsk Plugin
# Plays a simple game of blaclubskjaclubsk with the bot as the dealer
# One declubsk is used as an example for finite declubsks for other clubsard plugins (Strider's request)

import random
'''
spades = u"\u2660"
clubs = u"\u2663" 
hearts = u"\u2665"
diamond = u"\u2666"'''
# We clubsreate the declubsk as a list with truples (Value, Suit)
deck = [('2', 'clubs'), ('3', 'clubs'), ('4', 'clubs'), ('5', 'clubs'), ('6','clubs' ), ('7', 'clubs'), ('8','clubs'), ('9', 'clubs'), ('10', 'clubs'), ('J','clubs'), ('Q','clubs'), ('K','clubs'), ('A', 'clubs'),  ('2', 'spades'), ('3', 'spades'), ('4', 'spades'), ('5', 'spades'), ('6','spades' ), ('7', 'spades'), ('8', 'spades'), ('9', 'spades'), ('10', 'spades'), ('J', 'spades'), ('Q', 'spades'), ('K', 'spades'), ('A', 'spades'),  ('2', 'diamonds'), ('3', 'diamonds'), ('4', 'diamonds'), ('5', 'diamonds'), ('6','diamonds' ), ('7', 'diamonds'), ('8', 'diamonds'), ('9', 'diamonds'), ('10', 'diamonds'), ('J', 'diamonds'), ('Q', 'diamonds'), ('K', 'diamonds'), ('A', 'diamonds'),  ('2', 'hearts'), ('3', 'hearts'), ('4', 'hearts'), ('5', 'hearts'), ('6','hearts' ), ('7', 'hearts'), ('8', 'hearts'), ('9', 'hearts'), ('10', 'hearts'), ('J', 'hearts'), ('Q', 'hearts'), ('K', 'hearts'), ('A', 'hearts')]

# This dict will hold the player name and point to the class instance which manages their game
players = {}


# We create a class of the game as multiple users may be playing at once
class Game:
	def __init__(self, bot,  nick):
		self.bot = bot
		self.deck = deck
		self.dealer = []
		self.player = []
		self.nick = nick
		self.deal_player()
		self.deal_dealer()
		self.deal_player()
		self.deal_dealer()
	
	def deal_dealer(self):
		# We pop a random card from the deck and add it to the dealer's hand
		self.deck_card_position = random.randint(0,len(self.deck)-1)
		self.dealer.append(self.deck.pop(self.deck_card_position))
		
	def deal_player(self):
		# We pop a random card from the deck and add it to the player's hand
		self.deck_card_position = random.randint(0,len(self.deck)-1)
		self.player.append(self.deck.pop(self.deck_card_position))
		
	def show_cards(self, event):
		self.dealer_hand = []
		self.player_hand=[]
		# We generate a short list of the dealer and player's hand that is formatted for output
		for card in self.dealer:
			self.dealer_hand.append(card[0] + ' of ' + card[1] )
		self.dealer_hand[0] = 'XX'
		for card in self.player:
			self.player_hand.append(card[0] + ' of ' + card[1] )
		self.bot.message(event, self.nick + ': Dealer' +  str(self.dealer_hand))  
		self.bot.message(event, self.nick + ': Player' + str(self.player_hand) + ' = ' + str(self.add_hand(self.player)))
	
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
				card_value = '11'
			sum = sum + int(card_value)
		# We do an internal check to see if we are over 2
		# If so we redo the for loop but Ace = 1
		if sum > 21:
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
		
	# The AI of the dealer. We deal until the hand is 17
	def dealer_AI(self):
		while self.add_hand(self.dealer) < 16:
			self.deal_dealer()
			
	# We check who wins
	def victory_check(self, event):
		self.dealer_hand = []
		self.player_hand=[]
		# We generate a short list of the dealer and player's hand that is formatted for output
		for card in self.dealer:
			self.dealer_hand.append(card[0] + ' of ' + card[1] )
		for card in self.player:
			self.player_hand.append(card[0] + ' of ' + card[1] )
		self.bot.message(event, self.nick + ': Dealer|' +  str(self.dealer_hand) + ' = ' + str(self.add_hand(self.dealer)) + ':: Player|' + str(self.player_hand) + ' = ' + str(self.add_hand(self.player)))
		if self.add_hand(self.dealer) > 21:
			self.bot.message(event,  'Dealer busted ' + str(self.add_hand(self.dealer)) + ' to ' + str(self.add_hand(self.player)))
		if self.add_hand(self.dealer) > self.add_hand(self.player) and self.add_hand(self.dealer) <=21:
			self.bot.message(event,  'Dealer wins ' + str(self.add_hand(self.dealer)) + ' to ' + str(self.add_hand(self.player)))
		if self.add_hand(self.dealer) < self.add_hand(self.player):
			self.bot.message(event,  self.nick + ' wins ' + str(self.add_hand(self.player)) + ' to ' + str(self.add_hand(self.dealer)))
		if self.add_hand(self.dealer) == self.add_hand(self.player):
			self.bot.message(event,  'Push. Tied at ' + str(self.add_hand(self.player)))

def load(bot):
	pass
	
def unload(bot,  event):
	pass
	
def main(bot, event):
	nick_name = event.source().split('!')[0]
	
	# If the user only types in !blackjack we must return something
	# Otherwise errors will happen when the plugin searches for parameters that are not there
	
	if len(event.arguments()[0].split()) == 1:
		bot.message(event,  'Blackjack plugin. !blackjack deal, !blackjack hit, !blackjack stay')
		return None
	
	if event.arguments()[0].split()[1].upper() == 'DEAL':
		# We generate a dictionary entry with the username as the key and the memory address of the object instance for that player as the definition
		# This allows us to call the object functions using the user nickname
		if players.has_key(nick_name):
			del players[nick_name]
		players[nick_name] = Game(bot,  nick_name)
		players[nick_name].deck = [('2', 'clubs'), ('3', 'clubs'), ('4', 'clubs'), ('5', 'clubs'), ('6','clubs' ), ('7', 'clubs'), ('8','clubs'), ('9', 'clubs'), ('10', 'clubs'), ('J','clubs'), ('Q','clubs'), ('K','clubs'), ('A', 'clubs'),  ('2', 'spades'), ('3', 'spades'), ('4', 'spades'), ('5', 'spades'), ('6','spades' ), ('7', 'spades'), ('8', 'spades'), ('9', 'spades'), ('10', 'spades'), ('J', 'spades'), ('Q', 'spades'), ('K', 'spades'), ('A', 'spades'),  ('2', 'diamonds'), ('3', 'diamonds'), ('4', 'diamonds'), ('5', 'diamonds'), ('6','diamonds' ), ('7', 'diamonds'), ('8', 'diamonds'), ('9', 'diamonds'), ('10', 'diamonds'), ('J', 'diamonds'), ('Q', 'diamonds'), ('K', 'diamonds'), ('A', 'diamonds'),  ('2', 'hearts'), ('3', 'hearts'), ('4', 'hearts'), ('5', 'hearts'), ('6','hearts' ), ('7', 'hearts'), ('8', 'hearts'), ('9', 'hearts'), ('10', 'hearts'), ('J', 'hearts'), ('Q', 'hearts'), ('K', 'hearts'), ('A', 'hearts')]
		players[nick_name].show_cards(event)
		
	if event.arguments()[0].split()[1].upper() == 'HIT' and players.has_key(nick_name):
		players[nick_name].deal_player()
		players[nick_name].show_cards(event)
		# We check if the player is over 21
		if players[nick_name].add_hand(players[nick_name].player) > 21:
			bot.message(event,  nick_name + ': Hand total is over 21! BUSTED!')
			del players[nick_name]
		
	if event.arguments()[0].split()[1].upper() == 'STAY' and players.has_key(nick_name):
		players[nick_name].dealer_AI()
		players[nick_name].victory_check(event)
		del players[nick_name]
