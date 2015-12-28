'''Search plugin. !search google searchterm will search google with searchterm and return the first result. @wikipedia searchterm will search wikipedia and return the first paragraph of the closest match. !search imdb movie title searches for movie title. !search noslang word will try to translate word.'''
# MadLibs plugin
# story = {'text': 'I %s cheese and %s', 'list':['verb','noun']}
# words = [list, of, words, generated]
# story['text']%tuple(words) will be the story with the user words
import eyercbot
import eyercbot.NLPlib.NLPlib as NLPlib

import random
import re
import urllib.request
import urllib.parse
import yaml
import eyercbot.log as log
# Bold: 

# -------
# Config
# -------

# Defines the maximum length returned
# Later this will be expanded into two options, total maximum length and length per return

HAS_CONFIG = True
CONFIG_VERSION = 1
# Wait: how long to wait before skipping user
# Join wait: how long to wait for users to join game
# Chance: Chance word will be mad lib word
config = {"wait": 10, 'join_wait': 60, 'chance': 7}

#agame = None
#games = {}
in_progress = False
joining = False
eyercbot.memory['madlibs'] = None

class Game:
    def __init__(self, server, channel,  story,  nick, title):
        self.user_list = []
        self.story = story
        self.words = []
        self.list_index = 0
        self.in_progress = False
        self.allow_join = False
        self.server = server
        self.channel = channel
        self.owner = nick
        self.title = title
    def start(self):
        self.allow_join = False
        self.in_progress = True
        eyercbot.send('sendMsg', self.server, self.channel,  'Let the game begin!')
        self.ask()
    def changeUser(self):
        self.user_list.append(self.user_list.pop(0))
    def add_user(self,  nick):
        if self.allow_join == True:
            self.user_list.append(nick)
            eyercbot.send('sendMsg', self.server, self.channel,  'Added user ' + nick + ' . Total users: ' + str(self.user_list))
    def ask(self):
        #print self.story['list']
        eyercbot.send('sendMsg', self.server, self.channel,  self.user_list[0] +  ': ' +  self.story['list'][self.list_index])
    def add_word(self, nick, word):
        if nick == self.user_list[0]:
            self.words.append(word)
            self.changeUser()
            self.list_index = self.list_index + 1
            if self.list_index == len(self.story['list']):
                self.printStory()
                del_game()
                return None
            self.ask()
    def printStory(self):
        eyercbot.send('sendMsg', self.server, self.channel, 'Title: ' + self.title + ', ' + self.story['text']%tuple(self.words))

default_headers = {
    'User-agent': 'Mozilla/5.0 (compatible; utils.web python module)'
    }

def publicmsg(server, user, channel, message):
    if eyercbot.memory['madlibs'] != None:
        if eyercbot.memory['madlibs'].in_progress:
            eyercbot.memory['madlibs'].add_word(user.split('!')[0],  message)

def new(server, user, target, message):
    a = False
    while a == False:
        text, title = wiki()
        a = wikicheck(text)
    text = eyercbot.html2irc(text)
    if len(text) > 450:
        text = text[0:450]
    wiki_story = [[], []]
    while len(wiki_story[1]) < 2:
        wiki_story =  encodetext(text)
    story = {'text':wiki_story[0], 'list':wiki_story[1]}
    #stream = file('madlib.yaml', 'w')
    #yaml.dump_all([story, title], stream)
    #stream.close()
    eyercbot.memory['madlibs'] = Game(server, target,  story,  user.split('!')[0],  title)
    eyercbot.memory['madlibs'].allow_join = True
    eyercbot.send('sendMsg', server, target, 'A new game of Madlibs is starting Please type @join madlib to join the game. The game owner can type @start madlib to start the game.')

def join(server, user, target, message):
    eyercbot.memory['madlibs'].add_user(user.split('!')[0])

def start(server, user, target, message):
    if eyercbot.memory['madlibs']:
        if eyercbot.memory['madlibs'].allow_join and eyercbot.memory['madlibs'].owner == user.split('!')[0]:
            eyercbot.memory['madlibs'].start()

def add_word(user, target, message):
    if eyercbot.games['madlibs']:
        eyercbot.games['madlibs'].add_word(user.split('!')[0], message.split()[1])

def del_game():
    eyercbot.memory['madlibs'] = None

# The function maps the function to the input
# These need to be unique names, otherwise undesired plugin may be called!
alias_map = {"join madlib": join, "start madlib": start, "new madlib": new, "word": add_word}


# Here is the experimental code which will import a random entry from wikipedia as story
# We will then run is through the NLPlib parser as a for loop for each word, a random (1/10?) chance the word will be removed
# %s is inserted in {text: <>} and word type is appended in {list:[]}
def wiki():
    # Alright, we pull a random title from the 0 namespace (real articles)
    wiki_randomurl = 'http://en.wikipedia.org/w/api.php?format=yaml&action=query&list=random&rnnamespace=0'
    url = wiki_randomurl
    wiki_yaml = urllib.request.urlopen(url).read().decode().replace('*', 'text', 1)
    html = yaml.load(wiki_yaml)
    # We want to hang onto the title for output later
    wiki_title = html['query']['random'][0]['title']
    # Now we go for title
    wiki_url = 'http://en.wikipedia.org/w/api.php?format=yaml'
    wiki_page = '&action=parse&prop=text&page='
    url = wiki_url + wiki_page + urllib.parse.quote(wiki_title)
    wiki_yaml = urllib.request.urlopen(url).read().decode().replace('*', 'text', 1)
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
                        x = random.randint(1, eyercbot.config["plugin_config"]["madlibs"]["chance"])
                        if x == 1:
                                word_key = split_text.index(word)
                                split_text[word_key] = '%s'
                                #http://www.mozart-oz.org/mogul/doc/lager/brill-tagger/penn.html
                                if wordtype == 'CC':    split_text[word_key] = word
                                if wordtype == 'CD': 
                                        word_list.append('a number')
                                if wordtype == 'DT':    split_text[word_key] = word
                                if wordtype == 'EX':    
                                        word_list.append('existential there')
                                if wordtype == 'FW': 
                                        word_list.append('foreign word')
                                if wordtype == 'IN':    split_text[word_key] = word
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
                                if wordtype == 'PRP$':  word_list.append('possessive pronoun')
                                if wordtype == 'RB':    word_list.append('adverb')
                                if wordtype == 'RBR':   word_list.append('adverb, comparative')
                                if wordtype == 'RBS':   word_list.append('adverb, superlative')
                                if wordtype == 'RP':    word_list.append('particle')
                                if wordtype == 'TO':    split_text[word_key] = 'to'
                                if wordtype == 'UH':    word_list.append('interjection')
                                if wordtype == 'VB':    word_list.append('verb')
                                if wordtype == 'VBD':   word_list.append('verb, past tense ')
                                if wordtype == 'VBG':   word_list.append('verb ending in "ing"')
                                if wordtype == 'VBN':   word_list.append('verb, past participle')
                                if wordtype == 'VBP':   word_list.append('verb, sing')
                                if wordtype == 'VBZ':   word_list.append('verb, 3rd person')
                                if wordtype == 'WDT':   word_list.append('wh-determiner')
                                if wordtype == 'WP':    word_list.append('wh-pronoun')
                                if wordtype == 'WP$':   word_list.append('possessive wh-pronoun')
                                if wordtype == 'WRB':   word_list.append('wh-abverb')
                                
        text = ' '.join(split_text)
        return text,  word_list