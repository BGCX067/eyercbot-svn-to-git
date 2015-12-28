# RSS/ATOM feed reader
# We will want to find a way to only output new feeds for automatic systems
# User calls can specify how many recent feed entries
# We will need a config of some sort that stores the feed url's in a dict or list

# Configuration
# --------------------
feeds = {'civfanatics': {'url':'http://forums.civfanatics.com/external.php?type=RSS2&forumids=208',  'last_title': '', 'channels': ['#civfanatics']}}
# This may be better served by objects

import EyeRClib.feedparser as feedparser
# Outputs xrl for the java people
import plugins.xrl as xrl

def load(bot):
	# We will want to add to the scheduler to read the feeds at certain intervals
	# We will also want to build the dict from the configuration file and place it into the bot memory
	bot.memory['feeds'] = feeds

def unload(bot):
	pass

def main(bot, user, target, msg):	
	feed = feedparser.parse(bot.memory['feeds']['civfanatics']['url'])
	bot.message(user, target, feed.feed.title + ' :: ' + feed.entries[0].title + ': ' + feed.entries[0].summary_detail.value + ' - ' + feed.entries[0].updated + ' - ' + xrl.xrl_encoder(connection, event, feed.entries[0].link))
	bot.memory['feeds']['civfanatics']['last_title'] = feed.feed.title
	
def autofeed(bot):
	for feed in feeds:
		rss = feedparser.parse(feeds[feed]['url'])
		if bot.memory['feeds'][feed]['last_title'] == feed.feed.title:
			pass
		else:
			bot.msg(feeds[feed], feed.feed.title + ' :: ' + feed.entries[0].title + ': ' + feed.entries[0].summary_detail.value + ' - ' + feed.entries[0].updated + ' - ' + xrl.xrl_encoder(feed.entries[0].link))
			feeds[feed]['last_title'] = feed.feed.title
