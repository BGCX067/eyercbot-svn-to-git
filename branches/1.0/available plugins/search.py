# Search plugin to interface with different search services
# Requires the xrl plugin
# Some regular expressions taken from the incith-google.tcl script for eggdrop
# Services: 	
#	!google
#		Todo:
#		All other google searches 
#	!wikipedia
#		Todo:
#		
# Todo:	Internationalization of all searches
#	http://www.noslang.com/
#	Convert html into irc friendly language

import urllib2
import re
import sys
sys.path.append('plugins')
sys.path.append('lib')
import yaml
import xrl
# This will prittyfy url
import urllib

# -------
# Config
# -------

# Defines the maximum length returned
# Later this will be expanded into two options, total maximum length and length per return
length = 400

'''
# 0 will typically disable an option, otherwise a value 1 or
# above will enable it.
#
namespace eval incith {
  namespace eval google {
    # set this to the command character you want to use for the binds
    variable command_char "!"

    # set these to your preferred binds ("one two" - space delimited!)
    variable google_binds "g google"
    variable image_binds "gi image images"
    variable local_binds "gl local"
    variable group_binds "gg group groups"
    variable news_binds "gn news"
    variable books_binds "gb books"
    variable video_binds "gv video"
    variable fight_binds "gf fight googlefight"

    # To restrict input queries to Ops (+o), Halfops (+h) or Voiced (+v) users on
    #  any +google channel, use this setting.
    # Set the variable to one of the following to achieve the desired filtering:
    # At least Op - 3
    # At least Halfop - 2  (will also allow ops)
    # At least Voice - 1   (will also allow halfops and ops)
    # Everyone - 0         (no filtering)
    #
    # Note: this does NOT apply to private messages, use the below setting for them.
    #
    variable chan_user_level 0

    # if you want to allow users to search via private /msg, enable this
    variable private_messages 1

    # as per emailed & forum requests, use the next two variables together
    # to determine the output type like so:
    #  notice_reply 1 & force_private 1 = private notice reply only (this is as requested)
    #  notice_reply 0 & force_private 1 = private msg reply only
    #  notice_reply 1 & force_private 0 = regular channel OR private NOTICE
    #  notice_reply 0 & force_private 0 = regular channel OR private MSG (default)

    # set to 1 to enable a /notice reply instead, 0 for normal text
    variable notice_reply 0
    # set to 1 to force all replies to be private
    variable force_private 0


    # set this to the language you want results in! use 2 letter form.
    #   "all" is the default/standard google.com search.
    #   See http://www.google.com/advanced_search for a list.  You have to use
    #   the 'Language' dropdown box, perform a search, and find a line in the URL
    #   that looks like "&lr=lang_en" (for English). "en" is your language code.
    # Popular Ones: it (italian), da (danish), de (german), es (spanish), fr (french)
    # please note, this does not 'translate', it searches Google in a
    #   language of choice, which means you can still get English results.
    variable language "all"

    # set this to "on" to let google filter "adult content" from any of your search results
    #  "off" means results will not be filtered at all
    #  note: this is only applicable to !google, !images and !groups
    variable safe_search "off"

    # number of search results/image links to return, 'define:' is always 1 as some defs are huge
    variable search_results 4
    variable image_results 4
    variable local_results 4
    variable group_results 3
    variable news_results 3
    variable books_results 4
    variable video_results 4

		# set this to 1 to only return a single result on these 'special' matches in google:
		#  time in <blah>, weather in <blah>, population of <blah>, <blah> airport
    variable break_on_special 1

    # set this to 0 to turn google fight off (it is a tad slow after all ...)
    variable google_fight 1

    # what to use to seperate results, set this to "\n" and it will output each result
    #  on a line of its own. the seperator will be removed from the end of the last result.
    variable seperator " | "

    # ** this is not an optional setting, if a string is too long to send, it won't be sent! **
    # It should be set to the max amount of characters that will be received in a public
    #   message by your IRC server.  If you find you aren't receiving results, try lowering this.
    variable split_length 443

    # trimmed length of returned descriptions, only for standard searches.
    variable description_length 40

    # set these to 0 to turn off either the source web link or google.com define: link for a define:<blah> search
    variable define_weblinks 1
    variable define_googlelinks 1
    
    # set this to 1 to enable returning sub/secondary results from the same site from google as per forum req
    variable subresults 0

    # replace search terms appearing in the description as bolded words?
    # - does not bold entire description, just the matching search words
    # - this is ignored if desc_modes contains the Bold mode below
    variable bold_descriptions 1

    # Use these two settings to set colours, bold, reverse, underline etc on either descriptions or links
    # The following modes apply and you can use any combination of them: (NO SPACES!)
    #
    #  Bold = \002
    #  Underline = \037
    #  Reverse = \026
    #  Colours:                 #RGB/Html code:
    #   White = \0030           #FFFFFF
    #   Black = \0031           #000000
    #   Blue = \0032            #00007F
    #   Green = \0033           #008F00
    #   Light Red = \0034       #FF0000
    #   Brown = \0035           #7F0000
    #   Purple = \0036          #9F009F
    #   Orange = \0037          #FF7F00
    #   Yellow = \0038          #F0FF00
    #   Light Green = \0039     #00F700
    #   Cyan = \00310           #008F8F
    #   Light Cyan = \00311     #00F7FF
    #   Light Blue = \00312     #0000FF
    #   Pink = \00313           #FF00FF
    #   Grey = \00314           #7F7F7F
    #   Light Grey = \00315     #CFCFCF
    #
    # This example will do Bold, Underline and Light Blue: "\002\037\00312"
    # Note: This will affect *ALL* descs or links. Dont forget to use the \ too !
    # Also note, abusing this this heavily increases the number of characters per line,
    #  so your output lines will increase somewhat.
    variable desc_modes ""
    variable link_modes ""

    # number of minute(s) to ignore flooders, 0 to disable flood protection
    variable ignore 1

    # how many requests in how many seconds is considered flooding?
    # by default, this allows 3 queries in 10 seconds, the 4th being ignored
    #   and ignoring the flooder for 'variable ignore' minutes
    variable flood 4:10
  }
}
'''

def on_load(connection):
	pass

def on_unload(connection):
	pass

def index(connection, event, channels):
	search_string = ''
	results = ''
	# Creates search string


	# Prints help
	if len(event.arguments()[0].split()) == 1:
		connection.privmsg(event.target(), 'Search plugin. !search google searchterm will search google with searchterm and return the first result. !search wikipedia searchterm will search wikipedia and return the first paragraph of the closest match.')


	if len(event.arguments()[0].split()) > 2:
		search_string = event.arguments()[0].split(' ', 2)[2]
		# GOOGLE
		if event.arguments()[0].split()[1].upper() == 'GOOGLE':
			url = 'http://www.google.com/search?'
			bot = urllib2.Request('%sq=%s'%(url, search_string.replace(' ','+')))
			bot.add_header('User-Agent','')
			sock = urllib2.urlopen(bot)
			html = sock.read()
			sock.close()

			# Error handeling that leaves a dump file for the user to upload so we can study it
			try:
				hits = re.search('Results <b>1</b> - <b>10</b> of about <b>(?P<hit>.+?)</b> for <b>', html)
				#results = hits.group('hit')[0] + ' Results' #breaks in a search for python
				results = hits.group('hit') + ' Results'
				#entry = re.search('<div class=g style=\x22margin-left:.*?\x22.*?</div>',html)
				entry = re.search('<div class=g(>| ).*?\x22.*?</div>',html)
				link =  re.search('(http|ftp|https):\/\/[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?', entry.group())
				test = re.search('class=l>(?P<title>.+?)</a>', entry.group())
				title = test.group('title')
				test = re.search('<div class=std>(?P<tag>.+?)<br>', entry.group())
				tag = test.group('tag')
				results = html2irc(results + ' | ' + title + ': ' + link.group() + ' - ' + tag)
				connection.privmsg(event.target(), results)
				connection.privmsg(event.target(), 'Results: ' + xrl.xrl_encoder(connection, event, '%sq=%s'%(url, search_string.replace(' ','+'))))
			except:
				message = 'There has been an error in the search processor.  A report file called google_dump.html has been created.  Please upload it to the issue tracker at: http://code.google.com/p/eyercbot/issues/'
				dump_file = open('google_dump.html', 'w')
				dump_file.write('<!-- Command: ' + event.arguments()[0] + ' Search string: ' + search_string + ' -->\n' + html)
				connection.privmsg(event.target(), message)
				print message
				
	
		# WIKIPEDIA
		if event.arguments()[0].split()[1].upper() == 'WIKI' or event.arguments()[0].split()[1].upper() == 'WIKIPEDIA':
			# New searching engine using the API
			# At some point allow people to search in their language
			# list=random will also be a fun feature
			wiki_url = 'http://en.wikipedia.org/w/api.php?format=yaml'
			wiki_search = '&action=query&list=search&srwhat=text&srlimit=1&srsearch='
			wiki_page = '&action=parse&prop=text&page='
			redirect = ''
			# Wikipedia does not like odd characters'
			search_string = re.sub('<|>|[|]|{|}|\|', '', search_string)


			# We are going to see if our page exists first
			# If so, respond and return
			# If not, we search and continue
			url = wiki_url + wiki_page + urllib.quote(search_string)
			bot = urllib2.Request(url)
			bot.add_header('User-Agent','EyeRCbot')
			sock = urllib2.urlopen(bot)
			wiki_yaml = sock.read()
			sock.close()
			wiki_yaml = wiki_yaml.replace('*', 'text', 1)
			html = yaml.load(wiki_yaml)
			# If there is no redirect
			if html['parse']['text']['text'].find('noarticletext') and html['parse']['text']['text'].find('REDIRECT') == -1:
				text_temp = re.search('<p>(?P<text>.+)</p>', html['parse']['text']['text'])
				text = text_temp.group('text')
				wiki_title=search_string
				results = html2irc(wiki_title + ': ' + text).encode('utf-8')
				# Trims results down to length
				if len(results) > length:
					results = results[0:length]
				connection.privmsg(event.target(), results)
				return None
			# If there is a redirect
			if html['parse']['text']['text'].find('REDIRECT') != -1:
				wiki_title = re.search('<li>REDIRECT <a .+>(?P<title>.+)</a>', html['parse']['text']['text']).group('title')
				url = wiki_url + wiki_page + urllib.quote(wiki_title)
				bot = urllib2.Request(url)
				bot.add_header('User-Agent','EyeRCbot')
				sock = urllib2.urlopen(bot)
				wiki_yaml = sock.read()
				sock.close()
				wiki_yaml = wiki_yaml.replace('*', 'text', 1)
				html = yaml.load(wiki_yaml)
				text_temp = re.search('<p>(?P<text>.+)</p>', html['parse']['text']['text'])
				text = text_temp.group('text')
				redirect = ' (redirected from ' + search_string + ')'
				results = html2irc(wiki_title + redirect +': ' + text).encode('utf-8')
				# Trims results down to length
				if len(results) > length:
					results = results[0:length]
				connection.privmsg(event.target(), results)
				return None


			url = wiki_url + wiki_search + urllib.quote(search_string)
			# This will pull the search page for Wikipedia
			bot = urllib2.Request(url)
			bot.add_header('User-Agent','')
			sock = urllib2.urlopen(bot)
			wiki_search_results = sock.read()
			sock.close()
			wiki_search_results = yaml.load(wiki_search_results)

			# See if our direct result is availible
			# If not we report as such
			# Otherwise we now head to the title!
			if wiki_search_results['query']['search'] == None:
				connection.privmsg(event.target(), 
				'No matches found for your search')
				return None		

			wiki_title = wiki_search_results['query']['search'][0]['title']
			url = wiki_url + wiki_page + urllib.quote(wiki_title)
			bot = urllib2.Request(url)
			bot.add_header('User-Agent','EyeRCbot')
			sock = urllib2.urlopen(bot)
			wiki_yaml = sock.read()
			sock.close()
			wiki_yaml = wiki_yaml.replace('*', 'text', 1)
			html = yaml.load(wiki_yaml)
			text_temp = re.search('<p>(?P<text>.+)</p>', html['parse']['text']['text'])
			text = text_temp.group('text')

			results = html2irc(wiki_title + redirect + ': ' + text).encode('utf-8')
			if len(results) > length:
				results = results[0:length]
			connection.privmsg(event.target(), results)

# Converts html to IRC, does not process search string like the variable alludes to
# unicode() fails for some characters, I'm going to have to investigate this more. Until then each odd character will be parsed out by hand
def html2irc(html):
	html = html.replace('&middot;', '*')
	html = html.replace('<b>','')
	html = html.replace('</b>','')
	html = html.replace('<em>','')
	html = html.replace('</em>','')
	html = re.sub('<a.*?>', '', html)
	html = html.replace('</a>','')
	html = html.replace('&#39;', "'")
	return html
