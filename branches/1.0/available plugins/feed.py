# RSS/ATOM feed reader
# We will want to find a way to only output new feeds for automatic systems
# User calls can specify how many recent feed entries
# We will need a config of some sort that stores the feed url's in a dict or list

# ---------------
# Configuration
# Feed url
feed_url = 'http://example.com/feed.rss'
# ---------------

import sys
sys.path.append('lib')
import feedparser

# Outputs xrl for the java people
sys.path.append('plugins')
import xrl

def on_load(connection):
	# We will want to add to the scheduler to read the feeds at certain intervals
	pass

def on_unload(connection, event):
	pass

def index(connection, event, channels):	
	feed = feedparser.parse(feed_url)
	
	connection.privmsg(event.target(), feed.feed.title + ' :: ' + feed.entries[0].title + ': ' + feed.entries[0].summary_detail.value + ' - ' + feed.entries[0].updated + ' - ' + xrl.xrl_encoder(connection, event, feed.entries[0].link))
