# Search plugin for civfanatics.com
# Requires the xrl plugin
'''Civfanatics search plugin. !civfanatics searchterm will search the civfanatics forums and return the first result.'''
import urllib2
import re
import plugins.xrl as xrl
import EyeRClib.webbot as webbot

def load(bot):
	pass

def unload(bot):
	pass

def main(bot, user, target, msg):
	if len(msg.split()) == 1:
		bot.message(user, target, __doc__)
	
	if len(msg.split()) > 1:
		search_string = event.arguments()[0].split(' ', 1)[1]
		url = 'http://www.google.com/custom?q=' + search_string.replace(' ','+') + '&domains=forums.civfanatics.com&btnG=Search&sitesearch=forums.civfanatics.com'
		html = webbot.bot(url)
		try:
			hits = re.search('Results <b>1</b> - <b>10</b> of about <b>(?P<hit>.+?)</b> from', html)
			#results = hits.group('hit')[0] + ' Results' #breaks in a search for python
			results = hits.group('hit') + ' Results'
			#entry = re.search('<div class=g style=\x22margin-left:.*?\x22.*?</div>',html)
			entry = re.search('<div class=g(>| ).*?\x22.*?</div>',html)
			link =  re.search('(http|ftp|https):\/\/[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?', entry.group())
			test = re.search('class=l>(?P<title>.+?)</a>', entry.group())
			title = test.group('title')
			test = re.search('<div class=std>(?P<tag>.+?)<br>', entry.group())
			tag = test.group('tag')
			results = url_encode(results + ' | ' + title + ': ' + link.group() + ' - ' + tag)
			bot.message(user, target, results)
			bot.message(user, target, 'Results: ' + xrl.xrl_encoder('%sq=%s'%(url, search_string.replace(' ','+'))))
		except:
			message = 'There has been an error in the search processor.  A report file called google_dump.html has been created.  Please upload it to the issue tracker at: http://code.google.com/p/eyercbot/issues/'
			dump_file = open('google_dump.html', 'w')
			dump_file.write('<!-- Command: ' + msg + ' Search string: ' + search_string + ' -->\n' + html)
			bot.msg(target, message)
			print message

# Converts html to IRC, does not process search string like the variable alludes to
# unicode() fails for some characters, I'm going to have to investigate this more. Until then each odd character will be parsed out by hand
def url_encode(search_string):
	search_string = search_string.replace('&middot;', '*')
	search_string = search_string.replace('<b>','')
	search_string = search_string.replace('</b>','')
	search_string = search_string.replace('<em>','')
	search_string = search_string.replace('</em>','')
	search_string = re.sub('<a.*?>', '', search_string)
	search_string = search_string.replace('</a>','')
	search_string = search_string.replace('&#39;', "'")
	return search_string
				
	
